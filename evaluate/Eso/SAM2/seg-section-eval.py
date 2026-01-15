""""
基于SAM2间隔给mask提示，分段统计平均3d dice（排除手动给提示的切片）
"""

import numpy as np
import pandas as pd
import SimpleITK as sitk
from pathlib import Path
import re
import warnings

# ======================================================
# IO
# ======================================================
def load_nii(path: Path) -> np.ndarray:
    img = sitk.ReadImage(str(path))
    return sitk.GetArrayFromImage(img)  # (Z, H, W)

# ======================================================
# Dice
# ======================================================
def dice_3d(a, b, eps=1e-5):
    a = a.astype(bool)
    b = b.astype(bool)
    inter = np.logical_and(a, b).sum()
    s = a.sum() + b.sum()
    if s == 0:
        return 1.0
    return (2.0 * inter + eps) / (s + eps)

# ======================================================
# EXACT SAME as your inference logic
# ======================================================
def choose_prompt_slices(z_len: int, num_prompts: int):
    if num_prompts == 1:
        return [z_len // 2]
    idx = np.linspace(0, z_len - 1, num_prompts).round().astype(int).tolist()
    return sorted(set(idx))

# ======================================================
# 打印手动 prompt slice 的 Dice（不进 Excel）
# ======================================================
def print_prompt_slice_dice(pred, gt, prompt_slices, pid, K):
    print(f"\n[K={K}] {pid} manual prompt slice Dice:")
    for s in prompt_slices:
        d = dice_3d(pred[s:s+1], gt[s:s+1])
        print(f"  slice {s:4d}  dice={d:.3f}")

# ======================================================
# 分段 + 严格核对
# ======================================================
def segmented_dice_by_prompts(pred, gt, num_prompts: int, strict_check=True):
    Z = pred.shape[0]
    prompts = choose_prompt_slices(Z, num_prompts)
    prompts_set = set(prompts)

    if len(prompts) != num_prompts:
        warnings.warn(
            f"Z={Z}, K={num_prompts}, prompts reduced to {len(prompts)}: {prompts}"
        )

    # overall（排除 prompt slices）
    valid_all = [z for z in range(Z) if z not in prompts_set]
    overall = np.nan
    if len(valid_all) > 0:
        overall = dice_3d(pred[valid_all], gt[valid_all])

    seg_dices = []
    seg_union = set()

    if len(prompts) >= 2:
        for i in range(len(prompts) - 1):
            a, b = prompts[i], prompts[i + 1]
            valid = list(range(a + 1, b))  # 开区间
            valid = [z for z in valid if z not in prompts_set]
            if len(valid) == 0:
                seg_dices.append(np.nan)
            else:
                seg_dices.append(dice_3d(pred[valid], gt[valid]))
                seg_union.update(valid)

    if strict_check:
        expected = set(valid_all)
        if expected != seg_union:
            missing = sorted(list(expected - seg_union))[:10]
            extra = sorted(list(seg_union - expected))[:10]
            raise RuntimeError(
                f"[SEGMENT CHECK FAILED]\n"
                f"Z={Z}, K={num_prompts}\n"
                f"Prompts: {prompts}\n"
                f"Missing: {missing}\nExtra: {extra}"
            )

    return seg_dices, overall, prompts

# ======================================================
# Main
# ======================================================
def run(gt_dir, pred_root, out_xlsx, strict_check=True):
    gt_dir = Path(gt_dir)
    pred_root = Path(pred_root)

    cfg_dirs = []
    for d in pred_root.iterdir():
        if d.is_dir():
            m = re.fullmatch(r"(\d+)s_mask.*", d.name)
            if m:
                cfg_dirs.append((int(m.group(1)), d.name, d))
    cfg_dirs.sort(key=lambda x: x[0])

    gt_files = sorted(gt_dir.glob("CTV_*.nii.gz"))

    summary_rows = []
    per_cfg_tables = {}

    for K, cfg_name, cfg_path in cfg_dirs:
        rows = []
        max_seg = 0

        for gt_path in gt_files:
            pid = gt_path.stem
            pred_path = cfg_path / gt_path.name
            if not pred_path.exists():
                continue

            gt = load_nii(gt_path) > 0
            pred = load_nii(pred_path) > 0

            seg_dices, overall, prompts = segmented_dice_by_prompts(
                pred, gt, num_prompts=K, strict_check=strict_check
            )

            print_prompt_slice_dice(pred, gt, prompts, pid, K)

            max_seg = max(max_seg, len(seg_dices))

            row = {"PatientID": pid, "All": overall}
            for i, v in enumerate(seg_dices, start=1):
                row[f"Seg{i}"] = v
            rows.append(row)

        df = pd.DataFrame(rows)

        for i in range(1, max_seg + 1):
            if f"Seg{i}" not in df.columns:
                df[f"Seg{i}"] = np.nan

        per_cfg_tables[cfg_name] = df.copy()

        # ---- Summary (mean±std) ----
        s = {"NumMasks": K}

        def mean_pm_std(series):
            series = series.dropna()
            if len(series) == 0:
                return ""
            return f"{series.mean():.2f}±{series.std():.2f}"

        s["All"] = mean_pm_std(df["All"])
        for i in range(1, max_seg + 1):
            s[f"Seg{i}"] = mean_pm_std(df[f"Seg{i}"])

        summary_rows.append(s)

        # round Sheet2+ to 2 decimals
        per_cfg_tables[cfg_name] = per_cfg_tables[cfg_name].round(2)

    df_summary = pd.DataFrame(summary_rows).sort_values("NumMasks").reset_index(drop=True)

    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="Summary", index=False)
        for name, df in per_cfg_tables.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)

    print(f"\n✔ Saved to: {out_xlsx}")

# ======================================================
# EDIT HERE
# ======================================================
if __name__ == "__main__":
    GT_DIR = r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\labelsTs"  # 放 CTV_XXX.nii.gz
    PRED_ROOT = r"C:\Users\dell\Desktop\SAM2data\inference_mask\nnUNet-prompt"  # 里面有 2s_mask / 3s_mask / ...
    OUT_XLSX = r"C:\Users\dell\Desktop\SAM2data\inference_mask\SAM2_nnUNet-Dice3d.xlsx"

    run(GT_DIR, PRED_ROOT, OUT_XLSX, strict_check=True)


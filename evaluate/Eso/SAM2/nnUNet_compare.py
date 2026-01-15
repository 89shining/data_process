"""
以SAM2同样的分段和计算方式统计nnUNet3d的结果
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
# EXACT SAME as SAM2 inference
# ======================================================
def choose_prompt_slices(z_len: int, num_prompts: int):
    if num_prompts == 1:
        return [z_len // 2]
    idx = np.linspace(0, z_len - 1, num_prompts).round().astype(int).tolist()
    return sorted(set(idx))

# ======================================================
# 分段（假装 nnUNet 也按 SAM2 分段）
# ======================================================
def segmented_dice_like_sam2(pred, gt, num_prompts: int, strict_check=True):
    Z = pred.shape[0]
    prompts = choose_prompt_slices(Z, num_prompts)
    prompts_set = set(prompts)

    if len(prompts) != num_prompts:
        warnings.warn(
            f"Z={Z}, K={num_prompts}, prompts reduced to {len(prompts)}: {prompts}"
        )

    # overall（排除分段点）
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

    # 严格核对（与你 SAM2 版一致）
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
# 主流程：生成与 SAM2 一模一样结构的表
# ======================================================
def run(gt_dir, nnunet_pred_dir, K_list, out_xlsx, strict_check=True):
    gt_dir = Path(gt_dir)
    nnunet_pred_dir = Path(nnunet_pred_dir)

    gt_files = sorted(gt_dir.glob("CTV_*.nii.gz"))
    if not gt_files:
        raise RuntimeError("No GT files found.")

    summary_rows = []
    per_cfg_tables = {}

    for K in K_list:
        rows = []
        max_seg = 0

        for gt_path in gt_files:
            pid = gt_path.stem
            pred_path = nnunet_pred_dir / gt_path.name
            if not pred_path.exists():
                continue

            gt = load_nii(gt_path) > 0
            pred = load_nii(pred_path) > 0

            if gt.shape != pred.shape:
                raise ValueError(f"Shape mismatch: {pid}")

            seg_dices, overall, prompts = segmented_dice_like_sam2(
                pred, gt, num_prompts=K, strict_check=strict_check
            )

            max_seg = max(max_seg, len(seg_dices))

            row = {
                "PatientID": pid,
                "Z": pred.shape[0],
                "NumPromptsUsed": len(prompts),
                "All": overall,
            }

            for i, v in enumerate(seg_dices, start=1):
                row[f"Seg{i}"] = v

            rows.append(row)

        df = pd.DataFrame(rows).sort_values("PatientID").reset_index(drop=True)

        # 补齐 Seg 列（对齐 SAM2）
        for i in range(1, max_seg + 1):
            if f"Seg{i}" not in df.columns:
                df[f"Seg{i}"] = np.nan

        df = df[["PatientID", "Z", "NumPromptsUsed"] +
                [f"Seg{i}" for i in range(1, max_seg + 1)] +
                ["All"]]

        per_cfg_tables[f"{K}s_mask"] = df.round(2)

        # ---------- Summary（mean ± std） ----------
        def mean_pm_std(series):
            series = series.dropna()
            if len(series) == 0:
                return ""
            return f"{series.mean():.2f}±{series.std():.2f}"

        s = {"NumMasks": K, "All": mean_pm_std(df["All"])}
        for i in range(1, max_seg + 1):
            s[f"Seg{i}"] = mean_pm_std(df[f"Seg{i}"])

        summary_rows.append(s)

    df_summary = pd.DataFrame(summary_rows).sort_values("NumMasks").reset_index(drop=True)

    # 写 Excel（结构完全对齐 SAM2）
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="Summary", index=False)
        for name, df in per_cfg_tables.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)

    print(f"✔ nnUNet SAM2-style tables saved to: {out_xlsx}")

# ======================================================
# 你只改这里
# ======================================================
if __name__ == "__main__":
    GT_DIR = r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\labelsTs"
    NNUNET_PRED_DIR = r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\nnUNet_3D"
    K_LIST = [2, 3, 4, 5, 6, 7, 8, 9, 10]
    OUT_XLSX = r"C:\Users\dell\Desktop\SAM2data\inference_mask\\nnUNet_Dice3d.xlsx"

    run(GT_DIR, NNUNET_PRED_DIR, K_LIST, OUT_XLSX, strict_check=True)

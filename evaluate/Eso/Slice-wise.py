"""
计算每个case的每一个GT-slice的评估指标
绘制逐层指标图
"""

import os
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt

# =========================
# Dice 计算
# =========================
def dice_coef(pred, gt, smooth=1e-5):
    pred = pred.astype(bool)
    gt = gt.astype(bool)
    inter = np.logical_and(pred, gt).sum()
    return (2 * inter + smooth) / (pred.sum() + gt.sum() + smooth)


# =========================
# 单病例：画 slice-wise Dice 曲线
# =========================
def plot_slice_dice_curve(case_id, gt_path, model_paths, save_png):
    gt_vol = sitk.GetArrayFromImage(sitk.ReadImage(gt_path))
    model_vols = {}
    for name, path in model_paths.items():
        model_vols[name] = sitk.GetArrayFromImage(sitk.ReadImage(path))

    z_list = []
    dice_dict = {name: [] for name in model_paths}

    for z in range(gt_vol.shape[0]):
        gt = gt_vol[z] > 0
        if gt.sum() == 0:
            continue   # 只分析 GT slice


        z_list.append(z)

        for name, vol in model_vols.items():
            pred = vol[z] > 0
            dice_dict[name].append(dice_coef(pred, gt))

        if len(z_list) == 0:
            print(f"[Warning] {case_id}: no GT slice found")
            return

        # 上界编号为0
        z_max = max(z_list)
        z_rel = [z_max - z for z in z_list]   # 上界编号为0


    # -------- plot --------
    plt.figure(figsize=(8, 4))
    markers = ['o', 's', '^', 'D', 'v', '<', '>']

    for i, (name, dice_list) in enumerate(dice_dict.items()):
        plt.plot(
            z_rel,
            dice_list,
            marker=markers[i % len(markers)],
            markersize=4,
            linewidth=1.5,
            label=name
        )

    plt.xlabel('Slice index (S-I)')
    plt.ylabel('Dice coefficient')
    plt.ylim(0, 1.0)
    plt.title(f'Slice-wise Dice Curve (Case {case_id})')

    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_png, dpi=300)
    plt.close()


# =========================
# 主程序：批量处理所有患者
# =========================
if __name__ == "__main__":

    # ======== 改这 3 个路径 ========
    gt_dir = r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\labelsTs"

    model_dirs = {
        # "SAM": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\SAM",
        "nnUNet_2D": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\nnUNet_2D",
        "nnUNet_3D": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\nnUNet_3D",
        # "2_slices": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\Num_box_prompts\2_slices",
        # "3_sllices": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\Num_box_prompts\3_slices",
        "5_slices": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\Num_box_prompts\5_slices",
        # "7_slices": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\Num_box_prompts\7_slices",
    }

    out_dir = r"C:\Users\dell\Desktop\slice_dice_curves4"
    # ===============================

    os.makedirs(out_dir, exist_ok=True)

    cases = [f for f in os.listdir(gt_dir) if f.endswith(".nii.gz")]
    cases.sort()

    print(f"Found {len(cases)} cases")

    for fname in cases:
        case_id = fname.replace(".nii.gz", "")

        gt_path = os.path.join(gt_dir, fname)

        model_paths = {}
        skip_case = False

        for model_name, model_dir in model_dirs.items():
            pred_path = os.path.join(model_dir, fname)
            if not os.path.exists(pred_path):
                print(f"[Skip] {case_id}: missing {model_name}")
                skip_case = True
                break
            model_paths[model_name] = pred_path

        if skip_case:
            continue

        save_png = os.path.join(out_dir, f"{case_id}_slice_dice.png")

        print(f"Processing {case_id}")
        plot_slice_dice_curve(
            case_id,
            gt_path,
            model_paths,
            save_png
        )

    print("All done.")
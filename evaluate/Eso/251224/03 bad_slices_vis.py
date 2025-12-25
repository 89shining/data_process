"""
将低于阈值的slice全部可视化
"""

import os
import numpy as np
import pandas as pd
import SimpleITK as sitk
import matplotlib.pyplot as plt
from skimage import measure

# =========================
# 路径配置（按你自己的数据改）
# =========================
CSV_PATH = r"C:\Users\dell\Desktop\slice_wise_all_models.csv"

CT_DIR = r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\imagesTs"
GT_DIR = r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\labelsTs"

MODEL_PRED_DIRS = {
    "nnUNet_2D": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\nnUNet_2D",
    "nnUNet_3D": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\nnUNet_3D",
    "SAM": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\SAM",
}

OUT_ROOT = r"C:\Users\dell\Desktop\bad_slices_all_models"
DICE_THRESHOLD = 0.7

# =========================
# CT 窗宽窗位
# =========================
def window_ct(img, center=40, width=400):
    img = img.astype(np.float32)
    low = center - width / 2
    high = center + width / 2
    img = np.clip(img, low, high)
    img = (img - low) / (high - low)
    return img

# =========================
# 主流程
# =========================
df = pd.read_csv(CSV_PATH)

for model_name, pred_dir in MODEL_PRED_DIRS.items():

    print(f"\nProcessing model: {model_name}")

    df_model = df[(df["model"] == model_name) & (df["dice"] < DICE_THRESHOLD)].copy()
    print(f"  Bad slices: {len(df_model)}")

    if df_model.empty:
        print("  No bad slices, skip.")
        continue

    out_dir = os.path.join(OUT_ROOT, model_name)
    os.makedirs(out_dir, exist_ok=True)

    for _, row in df_model.iterrows():
        case_id = row["case_id"]
        z = int(row["slice_index"])
        dice = row["dice"]

        ct_path = os.path.join(CT_DIR, f"{case_id}_0000.nii.gz")
        gt_path = os.path.join(GT_DIR, f"{case_id}.nii.gz")
        pred_path = os.path.join(pred_dir, f"{case_id}.nii.gz")

        if not (os.path.exists(ct_path) and os.path.exists(gt_path) and os.path.exists(pred_path)):
            print(f"[Skip] Missing files for case {case_id}")
            continue

        ct_vol = sitk.GetArrayFromImage(sitk.ReadImage(ct_path))
        gt_vol = sitk.GetArrayFromImage(sitk.ReadImage(gt_path)) > 0
        pred_vol = sitk.GetArrayFromImage(sitk.ReadImage(pred_path)) > 0

        # 安全检查
        if z < 0 or z >= ct_vol.shape[0]:
            print(f"[Skip] Invalid slice index z={z} for case {case_id}")
            continue

        ct_slice = window_ct(ct_vol[z], center=40, width=400)
        gt_slice = gt_vol[z].astype(np.uint8)
        pred_slice = pred_vol[z].astype(np.uint8)

        # =========================
        # 绘图（关键：定义 fig, ax）
        # =========================
        fig, ax = plt.subplots(1, figsize=(4, 4))
        ax.imshow(ct_slice, cmap="gray")

        # --- GT contour（绿）---
        for c in measure.find_contours(gt_slice, 0.5):
            ax.plot(c[:, 1], c[:, 0], linewidth=0.8, color="lime")

        # --- Pred contour（红）---
        for c in measure.find_contours(pred_slice, 0.5):
            ax.plot(c[:, 1], c[:, 0], linewidth=0.8, color="red")

        ax.set_axis_off()
        ax.set_title(f"{model_name} | p{case_id} | z={z} | Dice={dice:.2f}", fontsize=8)

        save_name = f"p{case_id}_slice_{z:03d}_dice_{dice:.2f}.png"
        save_path = os.path.join(out_dir, save_name)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close(fig)

print("\nAll bad slices exported.")

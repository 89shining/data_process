"""
计算测试数据的slice dice
按SI顺序百分比展示分段
"""

import os
import numpy as np
import SimpleITK as sitk
import pandas as pd
from tqdm import tqdm

# =========================
# Dice 计算函数
# =========================
def dice_coef(pred, gt, smooth=1e-5):
    pred = pred.astype(bool)
    gt = gt.astype(bool)
    inter = np.logical_and(pred, gt).sum()
    return (2 * inter + smooth) / (pred.sum() + gt.sum() + smooth)


# =========================
# 路径配置（你只需要改这里）
# =========================
gt_dir = r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\labelsTs"

model_dirs = {
    "nnUNet_2D": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\nnUNet_2D",
    "nnUNet_3D": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\nnUNet_3D",
    "SAM": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\SAM",
    "SAM_2slices": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\Num_box_prompts\2_slices",
    "SAM_3slices": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\Num_box_prompts\3_slices",
    "SAM_5slices": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\Num_box_prompts\5_slices",
    "SAM_7slices": r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\Num_box_prompts\7_slices",
}

out_csv = r"C:\Users\dell\Desktop\slice_wise_all_models.csv"

# =========================
# 主逻辑
# =========================
records = []

cases = [f for f in os.listdir(gt_dir) if f.endswith(".nii.gz")]
cases.sort()

print(f"Found {len(cases)} cases")

for fname in tqdm(cases):
    case_id = fname.replace(".nii.gz", "")
    gt_path = os.path.join(gt_dir, fname)

    # 读取 GT
    gt_vol = sitk.GetArrayFromImage(sitk.ReadImage(gt_path))
    gt_vol = gt_vol > 0

    # 找 GT 非空 slice
    gt_slice_indices = np.where(gt_vol.sum(axis=(1, 2)) > 0)[0]
    if len(gt_slice_indices) == 0:
        print(f"[Warning] {case_id}: no GT slices")
        continue

    z_min = gt_slice_indices.min()
    z_max = gt_slice_indices.max()
    z_range = max(z_max - z_min, 1)  # 防止除 0

    # 遍历模型
    for model_name, model_dir in model_dirs.items():
        pred_path = os.path.join(model_dir, fname)
        if not os.path.exists(pred_path):
            print(f"[Skip] {case_id}: missing {model_name}")
            continue

        pred_vol = sitk.GetArrayFromImage(sitk.ReadImage(pred_path))
        pred_vol = pred_vol > 0

        # 遍历 GT slice
        for z in gt_slice_indices:
            gt_slice = gt_vol[z]
            pred_slice = pred_vol[z]

            dice = dice_coef(pred_slice, gt_slice)

            # zmin——下界
            z_norm = 1.0 - (z - z_min) / z_range   # 按SI顺序

            records.append({
                "case_id": case_id,
                "model": model_name,
                "slice_index": int(z),
                "z_norm": round(float(z_norm), 2),
                "dice": round(float(dice), 2)
            })

# =========================
# 保存为 DataFrame / CSV
# =========================
df = pd.DataFrame.from_records(records)

print("Total rows:", len(df))
print(df.head())

df.to_csv(out_csv, index=False)
print(f"Saved to {out_csv}")

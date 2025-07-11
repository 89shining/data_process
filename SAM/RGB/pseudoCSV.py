"""
生成伪rgb_image.png和对应mask.nii的对应关系CSV文件
"""

import os
import pandas as pd

# 根目录路径
root_dir = "C:/Users/dell/Desktop/20250711/dataset/test"
pseudo_dir = os.path.join(root_dir, "pseudo_rgb_images")
mask_dir = os.path.join(root_dir, "masks")

records = []

# 遍历 pseudo_rgb_images 下所有子文件夹和 .png 文件
for patient_id in sorted(os.listdir(pseudo_dir), key=lambda x: int(x.lstrip("p_"))):
    patient_folder = os.path.join(pseudo_dir, patient_id)
    if not os.path.isdir(patient_folder):
        continue

    for file in sorted(os.listdir(patient_folder), key=lambda x: int(os.path.splitext(x)[0])):
        if not file.endswith(".png"):
            continue
        slice_id = file.replace(".png", "")
        pseudo_rel = f"/pseudo_rgb_images/{patient_id}/{file}"
        mask_rel = f"/masks/{patient_id}/{slice_id}.nii"

        # 检查 mask 是否存在
        mask_full = os.path.join(root_dir, mask_rel.lstrip("/\\"))
        if os.path.exists(mask_full):
            records.append((pseudo_rel, mask_rel))
        else:
            print(f"[WARN] 跳过缺失的 mask 文件: {mask_rel}")

# 构造 DataFrame 并保存
df = pd.DataFrame(records)
csv_path = os.path.join(root_dir, "test_pseudo_rgb.csv")
df = pd.DataFrame(records, columns=["image", "mask"])
df.to_csv(csv_path, index=False, header=False)

print(f"✅ CSV 已生成，共 {len(df)} 条样本，保存于：{csv_path}")

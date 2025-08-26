"""
自动读取pseudoCSV，2D nii切片 -> 窗宽窗位变化，0-255 -> 拼接伪RGB图像
"""
import os
import SimpleITK as sitk
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm

root_dir = "C:/Users/WS/Desktop/dataset"
csv_path = os.path.join(root_dir, "pseudo_train_nii.csv")
save_dir = os.path.join(root_dir, "pseudo_rgb_images")
os.makedirs(save_dir, exist_ok=True)

# 窗宽窗位转换函数
def window_level_transform(img, window_center, window_width):
    img = img.astype(np.float32)
    lower = window_center - window_width / 2
    upper = window_center + window_width / 2
    img = np.clip(img, lower, upper)
    img = ((img - lower) / window_width) * 255.0
    return img.astype(np.uint8)

# 读取 CSV
df = pd.read_csv(csv_path)

# -------------------------
# 批量处理并保存伪RGB图像
for idx in tqdm(range(len(df))):
    nii_paths = df.iloc[idx]["nii_paths"].split(";")
    slices = []
    for path in nii_paths:
        full_path = os.path.join(root_dir, path.lstrip("/\\"))
        img_2d = sitk.GetArrayFromImage(sitk.ReadImage(full_path))
        if img_2d.ndim == 3:
            img_2d = img_2d[0]
        img_255 = window_level_transform(img_2d, window_center=40, window_width=350)
        slices.append(img_255)

    rgb_image = np.stack(slices, axis=-1).astype(np.uint8)
    rgb_pil = Image.fromarray(rgb_image, mode="RGB")

    # 从 image 路径中提取患者ID和切片编号
    image_path = df.iloc[idx]["image"]  # 例：/images/p_0/35.nii
    parts = image_path.strip("/").split("/")  # ['images', 'p_0', '35.nii']
    patient_id = parts[1]  # 'p_0'
    slice_num = parts[2].replace('.nii', '')  # '35'

    # 构造保存路径：pseudo_rgb_images/p_0/35.png
    save_folder = os.path.join(save_dir, patient_id)
    os.makedirs(save_folder, exist_ok=True)

    save_path = os.path.join(save_folder, f"{slice_num}.png")

    rgb_pil.save(save_path)
"""
自动读取CSV,对image.nii进行预处理（窗宽窗位，0-255，转RGB)-> rgb_image.png
"""
import os
import SimpleITK as sitk
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm

root_dir = "C:/Users/WS/Desktop/20250604/dataset/test"
csv_path = os.path.join(root_dir, "test_nii.csv")
save_dir = os.path.join(root_dir, "rgb_images")
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
df = pd.read_csv(csv_path, header=None, names=["image", "mask"])

for idx in tqdm(range(len(df))):
    image_rel = df.iloc[idx]["image"]  # e.g., /images/p_0/35.nii
    image_path = os.path.join(root_dir, image_rel.lstrip("/\\"))

    # 提取患者ID和切片编号
    parts = image_rel.strip("/\\").split("/")
    patient_id = parts[-2]  # e.g., "p_0"
    slice_name = os.path.splitext(parts[-1])[0]  # e.g., "35"

    # 读取并处理图像
    img = sitk.GetArrayFromImage(sitk.ReadImage(image_path))
    img_255 = window_level_transform(img, window_center=40, window_width=350)
    img_rgb = Image.fromarray(img_255).convert("RGB")

    # 创建患者目录并保存
    patient_folder = os.path.join(save_dir, patient_id)
    os.makedirs(patient_folder, exist_ok=True)

    save_path = os.path.join(patient_folder, f"{slice_name}.png")
    img_rgb.save(save_path)

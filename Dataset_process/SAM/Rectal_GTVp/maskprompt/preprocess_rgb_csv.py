"""
将image预处理为rgb，并生成新的CSV文件
"""
import os
import SimpleITK as sitk
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm

root_dir = "C:/Users/WS/Desktop/MRI_mask/dataset"
csv_path = os.path.join(root_dir, "train_nii.csv")
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
df = pd.read_csv(csv_path, header=None, names=["image", "mask", "prompt", "prompt_available"])

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

records = []

# 遍历 rgb_images 下所有子文件夹和 .png 文件
for patient_id in sorted(os.listdir(save_dir), key=lambda x: int(x.lstrip("p_"))):
    patient_folder = os.path.join(save_dir, patient_id)
    if not os.path.isdir(patient_folder):
        continue

    for file in sorted(os.listdir(patient_folder), key=lambda x: int(os.path.splitext(x)[0])):
        if not file.endswith(".png"):
            continue
        slice_id = file.replace(".png", "")
        rgb_rel = f"/rgb_images/{patient_id}/{file}"
        mask_rel = f"/masks/{patient_id}/{slice_id}.nii"
        prompt_rel = f"prompts/{patient_id}/{slice_id}.nii"

        match_suffix = f"{patient_id}/{slice_id}.nii"

        row_match = df[
            df["image"].str.endswith(match_suffix) &
            df["mask"].str.endswith(match_suffix) &
            df["prompt"].str.endswith(match_suffix)
            ]

        if row_match.empty:
            print(f"[WARN] 未在原CSV中找到：{patient_id}/{slice_id}，跳过")
            continue

        prompt_available = int(row_match.iloc[0]["prompt_available"])

        # 检查 mask 是否存在
        mask_full = os.path.join(root_dir, mask_rel.lstrip("/\\"))
        if os.path.exists(mask_full):
            records.append((rgb_rel, mask_rel, prompt_rel, prompt_available))
        else:
            print(f"[WARN] 跳过缺失的 mask 文件: {mask_rel}")

# 构造 DataFrame 并保存
df = pd.DataFrame(records)
csv_path = os.path.join(root_dir, "rgb_dataset.csv")
df = pd.DataFrame(records, columns=["image", "mask", "prompt", "prompt_available"])
df.to_csv(csv_path, index=False, header=False)

print(f"✅ CSV 已生成，共 {len(df)} 条样本，保存于：{csv_path}")
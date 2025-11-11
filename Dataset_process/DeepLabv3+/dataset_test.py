"""
将 test_nii.gz 格式的测试集转换为 DeeplabV3+ 的预测输入格式
✅ 窗宽窗位调整 (WL=40, WW=350)
✅ 归一化到 [0,255]
✅ 保存为灰度 JPG
✅ 直接放入 deeplabv3-plus-pytorch/img/ 文件夹可预测
"""

import os
import SimpleITK as sitk
import numpy as np
from PIL import Image
from tqdm import tqdm

# ===================== 参数设置 =====================
test_root = r"D:\SAM\GTVp_CTonly\20250809\datanii\test_nii"  # 原始测试集路径（含多个患者子文件夹）
save_dir = r"D:\project\deeplabv3-plus-pytorch\img"          # Deeplab 项目下 img 目录
os.makedirs(save_dir, exist_ok=True)

# 窗宽窗位设置（腹部软组织窗）
WL, WW = 40, 350
vmin, vmax = WL - WW / 2, WL + WW / 2

# ===================== 功能函数 =====================
def apply_window(image):
    """窗宽窗位裁剪 + 线性归一化到 [0,255]"""
    image = np.clip(image, vmin, vmax)
    image = (image - vmin) / (vmax - vmin)
    image = (image * 255).astype(np.uint8)
    return image

# ===================== 主流程 =====================
patients = [p for p in os.listdir(test_root) if os.path.isdir(os.path.join(test_root, p))]
total_slices = 0

for pid in tqdm(patients, desc="Converting test patients"):
    image_path = os.path.join(test_root, pid, "image.nii.gz")
    if not os.path.exists(image_path):
        print(f"[跳过] {pid} 缺少 image.nii.gz 文件。")
        continue

    img = sitk.ReadImage(image_path)
    img_arr = sitk.GetArrayFromImage(img)  # [D, H, W]

    for i in range(img_arr.shape[0]):
        img_slice = apply_window(img_arr[i])
        save_name = f"{pid}_slice{i:03d}.jpg"
        Image.fromarray(img_slice).convert("L").save(os.path.join(save_dir, save_name))
        total_slices += 1

print(f"\n✅ 转换完成，共生成 {total_slices} 张切片。")
print(f"✅ 窗宽窗位: WL={WL}, WW={WW}")
print(f"✅ 已保存至: {save_dir}")
print("可以直接运行 predict.py 进行推理。")

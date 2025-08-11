import os

import matplotlib.pyplot as plt
import SimpleITK as sitk
import pandas as pd
from PIL import Image
import numpy as np
import numpy as np
import torch
from torchvision.transforms.functional import resize
from tqdm import tqdm


def window_level_transform(img, window_center, window_width):
    """
    根据窗宽窗位调整CT图像像素值，转换到0-255
    img: numpy array，float32
    window_center: 窗位
    window_width: 窗宽
    """
    lower = window_center - window_width / 2
    upper = window_center + window_width / 2
    img_clipped = np.clip(img, lower, upper)  # 限制像素值在窗宽范围内

    # 线性映射到0-255
    img_normalized = (img_clipped - lower) / window_width
    img_255 = (img_normalized * 255).astype(np.uint8)
    return img_255
#
# image_path= "C:/Users\dell\Desktop\SAM_GTVp\GTVp_CTonly/20250604\dataset/train\images\p_0/34.nii"
# image = sitk.GetArrayFromImage(sitk.ReadImage(image_path))
# # print(image.shape, image.dtype, image.mode)
# # 调整窗宽窗位， 0-255
# img_255 = window_level_transform(image, window_center=40, window_width=350)
#
# Image.fromarray(img_255).save("converted_gray.png")
#
# image_rgb = Image.fromarray(img_255).convert("RGB")  # RGB格式
# image_rgb.save("converted_rgb.png")
#
# image = image_rgb.resize((1024,1024), resample=Image.BILINEAR)  # (1024,1024)
# image.save("resize.png")
# image = np.array(image).astype(np.float32)  # float 32
# image = torch.from_numpy(image).permute(2, 0, 1)  # [H,W,3] -> [3,H,W]
#
#
# 三张相邻图像生成伪rgb
# 手动输入三张 2D NIfTI 图像路径
# nii_paths = [
#     "C:/Users/dell/Desktop/SAM_GTVp/GTVp_CTonly/20250604/dataset/train/images/p_0/34.nii",
#     "C:/Users/dell/Desktop/SAM_GTVp/GTVp_CTonly/20250604/dataset/train/images/p_0/35.nii",
#     "C:/Users/dell/Desktop/SAM_GTVp/GTVp_CTonly/20250604/dataset/train/images/p_0/36.nii",
# ]

# slices = []
# for i, path in enumerate(nii_paths):
#     img_2d = sitk.GetArrayFromImage(sitk.ReadImage(path))  # shape: [1, H, W] 或 [H, W]
#     if img_2d.ndim == 3:
#         img_2d = img_2d[0]  # 取出第一张 2D 图像
#     assert img_2d.ndim == 2, f"Image at {path} has invalid shape {img_2d.shape}"
#     img_255 = window_level_transform(img_2d, window_center=40, window_width=350)
#     # 保存每张窗宽窗位后的灰度图像
#     Image.fromarray(img_255).save(f"slice_{i}_windowed.png")
#     slices.append(img_255)
# # 合并成伪 RGB 图像
# rgb_image = np.stack(slices, axis=-1).astype(np.uint8)  # shape: [H, W, 3]
# rgb_pil = Image.fromarray(rgb_image, mode="RGB")
# rgb_pil.save("pseudo_rgb.png")

# # resize 并转成 PyTorch tensor
# rgb_pil_resized = rgb_pil.resize((1024, 1024), resample=Image.BILINEAR)
# rgb_pil_resized.save("pseudo_rgb_resize.png")
# rgb_np = np.array(rgb_pil_resized).astype(np.float32)
# rgb_tensor = torch.from_numpy(rgb_np).permute(2, 0, 1)  # shape: [3, H, W]
#
"""
查看图像通道
"""
# image_path = 'pseudo_rgb.png'
# img = Image.open(image_path)
# # print(f"文件路径: {image_path}")
# # print(f"图像模式: {img.mode}")         # 如 RGB, L, P, RGBA
# # print(f"图像尺寸: {img.size}")         # (width, height)
# # print(f"图像通道数: {len(img.getbands())}")  # 例如 RGB → 3
# # print(f"通道名称: {img.getbands()}")   # 例如 ('R', 'G', 'B')
# img_np = np.array(img)  # shape: [H, W, 3]
#
# # 拆分通道
# R = img_np[:, :, 0]
# G = img_np[:, :, 1]
# B = img_np[:, :, 2]
# Image.fromarray(R).save("C:/Users\dell\Desktop/channel_R.png")
# Image.fromarray(G).save("C:/Users\dell\Desktop/channel_G.png")
# Image.fromarray(B).save("C:/Users\dell\Desktop/channel_B.png")




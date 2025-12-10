# 对nnunet做基于中心的剪裁 128 128 128

import os
import glob
import numpy as np
import SimpleITK as sitk
from scipy.ndimage import zoom


# ============================================
# 关键函数：专门处理 CTV_001_0000 → CTV_001 的命名匹配
# ============================================
def infer_mask_path(img_path, mask_dir):
    fname = os.path.basename(img_path)

    if fname.endswith("_0000.nii.gz"):
        mask_name = fname.replace("_0000", "")
        mask_path = os.path.join(mask_dir, mask_name)
        if os.path.exists(mask_path):
            return mask_path

    # 如果还找不到，直接报错
    return None


# ------------------------------
# 中心裁剪
# ------------------------------
def center_crop_xy(img_np, mask_np, crop_h=160, crop_w=128):
    Z, H, W = img_np.shape
    cy, cx = H // 2, W // 2

    y1 = max(0, cy - crop_h // 2)
    y2 = min(H, y1 + crop_h)
    x1 = max(0, cx - crop_w // 2)
    x2 = min(W, x1 + crop_w)

    img_np = img_np[:, y1:y2, x1:x2]
    mask_np = mask_np[:, y1:y2, x1:x2]
    return img_np, mask_np


# ------------------------------
# resize 到 128³
# ------------------------------
def resize_3d(img_np, mask_np, target_size=(128,128,128)):
    Z, H, W = img_np.shape
    td, th, tw = target_size
    zoom_f = (td / Z, th / H, tw / W)

    img_np = zoom(img_np, zoom_f, order=1)
    mask_np = zoom(mask_np, zoom_f, order=0)
    return img_np, mask_np


# ------------------------------
# 食管窗
# ------------------------------
def apply_esophagus_window(img, w_center=40, w_width=400):
    low = w_center - w_width // 2
    high = w_center + w_width // 2
    img = np.clip(img, low, high)
    return (img - low) / (high - low)


# ------------------------------
# 主处理函数
# ------------------------------
def preprocess_nnunet_to_128(img_dir, mask_dir, out_img_dir, out_mask_dir,
                                  crop_h=160, crop_w=128, target=(128,128,128)):

    os.makedirs(out_img_dir, exist_ok=True)
    os.makedirs(out_mask_dir, exist_ok=True)

    img_paths = sorted(glob.glob(os.path.join(img_dir, "*.nii.gz")))

    for img_path in img_paths:
        fname = os.path.basename(img_path)

        # ========== 关键部分（名称匹配）==========
        mask_path = infer_mask_path(img_path, mask_dir)
        if mask_path is None:
            print(f"❌ 未找到对应 mask：{fname}")
            continue

        # ========== 读取 ==========
        img_sitk = sitk.ReadImage(img_path)
        mask_sitk = sitk.ReadImage(mask_path)

        img_np = sitk.GetArrayFromImage(img_sitk).astype(np.float32)
        mask_np = sitk.GetArrayFromImage(mask_sitk).astype(np.float32)

        # ========== 食管窗 ==========
        img_np = apply_esophagus_window(img_np)

        # ========== 中心裁剪 ==========
        img_np, mask_np = center_crop_xy(img_np, mask_np, crop_h, crop_w)

        # ========== resize ==========
        img_np, mask_np = resize_3d(img_np, mask_np, target)

        # ========== 保存 ==========
        out_img = sitk.GetImageFromArray(img_np)
        out_mask = sitk.GetImageFromArray(mask_np.astype(np.uint8))

        sitk.WriteImage(out_img, os.path.join(out_img_dir, fname))
        sitk.WriteImage(out_mask, os.path.join(out_mask_dir, os.path.basename(mask_path)))

        print(f"✔ 成功处理：{fname} → {os.path.basename(mask_path)}")

# ------------------------------
# 5) 运行
# ------------------------------
if __name__ == "__main__":
    # === 修改成你 nnUNet 的路径 ===
    input_img_dir = r"/home/wusi/nnUNet/nnUNetFrame/DATASET/nnUNet_raw/Dataset006_EsoCTV/imagesTr"
    input_mask_dir = r"/home/wusi/nnUNet/nnUNetFrame/DATASET/nnUNet_raw/Dataset006_EsoCTV/labelsTr"

    # === 输出路径（SAM-Med3D 的新数据集） ===
    output_img_dir = r"/home/wusi/nnUNet/nnUNetFrame/DATASET/nnUNet_raw/Dataset007_EsoCTV128/imagesTr"
    output_mask_dir = r"/home/wusi/nnUNet/nnUNetFrame/DATASET/nnUNet_raw/Dataset007_EsoCTV128/labelsTr"

    preprocess_nnunet_to_128(input_img_dir, input_mask_dir,
                                  output_img_dir, output_mask_dir)

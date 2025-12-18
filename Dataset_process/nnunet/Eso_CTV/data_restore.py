# 将预测结果恢复至原尺寸

import os
import glob
import SimpleITK as sitk
import numpy as np
from scipy.ndimage import zoom


# ======================================================
# 单个 case 的恢复函数
# ======================================================
def restore_pred_to_original(pred_128, original_shape, crop_h=160, crop_w=128):
    """
    pred_128: nnUNet 输出 mask (128,128,128)
    original_shape: 原图 (Z,H,W)
    """
    Z0, H0, W0 = original_shape
    D1, H1, W1 = pred_128.shape  # (128,128,128)

    # Step 1: 128³ -> (Z0, 160, 128)
    zoom_factors = (
        Z0 / D1,
        crop_h / H1,
        crop_w / W1
    )
    pred_crop = zoom(pred_128, zoom_factors, order=0)

    # Step 2: 裁剪区域贴回原图大小
    full_pred = np.zeros((Z0, H0, W0), dtype=np.uint8)

    cy, cx = H0 // 2, W0 // 2
    y1 = cy - crop_h // 2
    y2 = y1 + crop_h
    x1 = cx - crop_w // 2
    x2 = x1 + crop_w

    full_pred[:, y1:y2, x1:x2] = pred_crop

    return full_pred


# ======================================================
# 批量恢复函数（适配 预测：CTV_001  → 原图：CTV_001_0000）
# ======================================================
def batch_restore(pred_dir, orig_dir, save_dir,
                  crop_h=160, crop_w=128):

    os.makedirs(save_dir, exist_ok=True)

    pred_paths = sorted(glob.glob(os.path.join(pred_dir, "CTV_*.nii.gz")))

    print(f"找到 {len(pred_paths)} 个预测文件，开始恢复...\n")

    for pred_path in pred_paths:
        pred_name = os.path.basename(pred_path)      # CTV_001.nii.gz
        case_id = pred_name.replace(".nii.gz", "")   # CTV_001

        # -------------------------------
        # 匹配原图：CTV_001_0000.nii.gz
        # -------------------------------
        orig_name = f"{case_id}_0000.nii.gz"
        orig_path = os.path.join(orig_dir, orig_name)

        if not os.path.exists(orig_path):
            print(f"❌ 原图不存在：{orig_path}")
            continue

        # ---- 读取预测（128³）----
        pred_sitk = sitk.ReadImage(pred_path)
        pred_np = sitk.GetArrayFromImage(pred_sitk).astype(np.uint8)

        # ---- 读取原图 ----
        orig_sitk = sitk.ReadImage(orig_path)
        orig_np = sitk.GetArrayFromImage(orig_sitk)

        # ---- 恢复 ----
        restored_np = restore_pred_to_original(
            pred_128=pred_np,
            original_shape=orig_np.shape,
            crop_h=crop_h,
            crop_w=crop_w
        )

        # ---- 保存（保持预测名称不变）----
        out_sitk = sitk.GetImageFromArray(restored_np)
        out_sitk.CopyInformation(orig_sitk)

        save_path = os.path.join(save_dir, pred_name)
        sitk.WriteImage(out_sitk, save_path)

        print(f"✔ 已恢复：{pred_name} → {orig_name}")

    print("\n🎉 所有预测已成功恢复！")


# ======================================================
# 主入口：请修改路径
# ======================================================
if __name__ == "__main__":
    pred_dir = "/home/wusi/nnunet_output/"             # CTV_001.nii.gz
    orig_dir = "/home/wusi/nnUNet/nnUNetFrame/DATASET/nnUNet_raw/Dataset006_EsoCTV/imagesTr/"         # CTV_001_0000.nii.gz
    save_dir = "/home/wusi/nnunet_restore/"            # 输出仍为 CTV_001.nii.gz

    batch_restore(pred_dir, orig_dir, save_dir)

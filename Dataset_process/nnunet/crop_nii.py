"""
crop后只保留CTV切片
"""
import os
import numpy as np
import nibabel as nib


def crop_ct_and_mask(ct_path, mask_path, save_ct_path, save_mask_path):
    """
    自动识别切片方向 (Z = 最后一个维度)，只保留 mask 有前景的切片
    """

    ct_nii = nib.load(ct_path)
    mask_nii = nib.load(mask_path)

    ct = ct_nii.get_fdata()
    mask = mask_nii.get_fdata()

    affine_ct = ct_nii.affine
    affine_mask = mask_nii.affine

    # ---- 自动判断 Z 轴（切片个数最小的一维一般就是Z）
    # 常规 CT 是 (H, W, Z)
    z_axis = 2

    # 将 mask 展平到 H*W，按 Z 统计前景
    nonzero_slices = np.where(mask.reshape(-1, mask.shape[z_axis]).sum(axis=0) > 0)[0]

    if len(nonzero_slices) == 0:
        print("mask 完全为空，跳过")
        return False

    z_min = int(nonzero_slices[0])
    z_max = int(nonzero_slices[-1])

    print(f"裁剪切片范围 (Z): {z_min} 到 {z_max}")

    # ---- 在 Z 轴方向裁剪
    cropped_ct = ct[:, :, z_min:z_max+1]
    cropped_mask = mask[:, :, z_min:z_max+1]

    # ---- 保存为整数类型
    nib.save(nib.Nifti1Image(cropped_ct.astype(np.float32), affine_ct), save_ct_path)
    nib.save(nib.Nifti1Image(cropped_mask.astype(np.uint8), affine_mask), save_mask_path)

    return True


# =============== 批处理 ===============
root_dir = r"C:\Users\dell\Desktop\Eso-CTV\20251217\datanii\train_nii"  # <-- 你的 p_001/p_002/... 的上级目录
output_root = r"C:\Users\dell\Desktop\Eso-CTV\20251217\nnUNet\cropnii\train_nii"   # 最终统一保存的位置
os.makedirs(output_root, exist_ok=True)

patient_dirs = sorted([
    os.path.join(root_dir, d)
    for d in os.listdir(root_dir)
    if os.path.isdir(os.path.join(root_dir, d)) and d.startswith("p_")
])

print(f"共检测到 {len(patient_dirs)} 个患者文件夹")

for p_dir in patient_dirs:
    p_name = os.path.basename(p_dir)
    print("\n==============================")
    print(f"处理患者: {p_name}")

    ct_path = os.path.join(p_dir, "image.nii.gz")
    mask_path = os.path.join(p_dir, "CTV.nii.gz")

    if not (os.path.exists(ct_path) and os.path.exists(mask_path)):
        print("缺少 image.nii.gz 或 GTVp.nii.gz，跳过")
        continue

    # 输出目录为 crop_results/p_XXX/
    out_dir = os.path.join(output_root, p_name)
    os.makedirs(out_dir, exist_ok=True)

    save_ct_path = os.path.join(out_dir, "image.nii.gz")
    save_mask_path = os.path.join(out_dir, "CTV.nii.gz")

    ok = crop_ct_and_mask(ct_path, mask_path, save_ct_path, save_mask_path)

    if ok:
        print(f" 保存到: {out_dir}")
    else:
        print(f" 跳过（mask 无前景）")

print("\n 全部患者裁剪完成！")

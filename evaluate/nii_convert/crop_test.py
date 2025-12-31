"""
将测试结果Nii裁掉空切片层
"""

"""
批量裁剪 CTV 掩码（无 CT）
只保留 mask 有前景的切片（Z 方向）
"""

import os
import numpy as np
import nibabel as nib


def crop_mask(mask_path, save_mask_path):
    """
    自动裁剪，仅保留 mask 有前景的 Z 范围
    """
    mask_nii = nib.load(mask_path)
    mask = mask_nii.get_fdata()
    affine = mask_nii.affine

    # 一般为 (H, W, Z)
    z_axis = 2

    # 找到含前景的切片
    nonzero_slices = np.where(mask.reshape(-1, mask.shape[z_axis]).sum(axis=0) > 0)[0]

    if len(nonzero_slices) == 0:
        print(f"[跳过] {os.path.basename(mask_path)}：mask 完全为空")
        return False

    z_min = int(nonzero_slices[0])
    z_max = int(nonzero_slices[-1])

    print(f"  裁剪 Z 范围: {z_min} → {z_max}")

    cropped_mask = mask[:, :, z_min:z_max+1]

    nib.save(
        nib.Nifti1Image(cropped_mask.astype(np.uint8), affine),
        save_mask_path
    )

    return True


# ======================== 批处理目录结构 ========================

input_dir = r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\SAM_traindata2"   # A 文件夹
output_dir = r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\SAM_traindata"  # 输出 B 文件夹
os.makedirs(output_dir, exist_ok=True)

# 找到所有 .nii.gz 文件
files = sorted([
    f for f in os.listdir(input_dir)
    if f.endswith(".nii.gz")
])

print(f"共检测到 {len(files)} 个 CTV 掩码文件\n")

for fname in files:
    print(f"=============================")
    print(f"处理: {fname}")

    in_path = os.path.join(input_dir, fname)
    out_path = os.path.join(output_dir, fname)

    ok = crop_mask(in_path, out_path)

    if ok:
        print(f"  ✔ 已保存到: {out_path}")
    else:
        print(f"  ✘ 无前景，跳过")

print("\n全部处理完成！")

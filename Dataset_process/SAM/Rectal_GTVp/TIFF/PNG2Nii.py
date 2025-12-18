"""
将png 2D切片转为nii.gz 用于可视化
"""
import os
import shutil
import csv
import numpy as np
import nibabel as nib
from PIL import Image

def pngs_to_nii(png_dir, reference_nii_path, output_nii_path, patient_id, all_mappings):
    # 读取参考NIfTI图像，提取空间信息
    ref_nii = nib.load(reference_nii_path)
    affine = ref_nii.affine
    header = ref_nii.header
    shape = ref_nii.shape  # (H, W, D)
    # print(shape)

    # 初始化全 0 体积，shape 为 (D, H, W)
    volume = np.zeros((shape[2], shape[0], shape[1]), dtype=np.uint8)

    # 存储索引和对应文件名
    slice_mapping = []

    for f in sorted(os.listdir(png_dir), key=lambda x: int(os.path.splitext(x)[0]) if x.endswith(".png") and os.path.splitext(x)[0].isdigit() else float('inf')):
        if not f.endswith(".png"):
            continue
        try:
            # 提取数字作为切片索引
            slice_idx = int(os.path.splitext(f)[0])
        except ValueError:
            print(f"跳过无法识别的文件名：{f}")
            continue

        img = Image.open(os.path.join(png_dir, f)).convert('L')
        arr = np.array(img)
        arr = np.rot90(arr, k=3)
        arr = np.fliplr(arr)

        if slice_idx >= volume.shape[0]:
            print(f"切片编号 {slice_idx} 超出体积深度 {volume.shape[0]}，跳过。")
            continue

        volume[slice_idx] = arr
        slice_mapping.append((patient_id, slice_idx, f))

        # 转换为 (H, W, D)
    volume = np.transpose(volume, (1, 2, 0))

    nii_img = nib.Nifti1Image(volume, affine=affine, header=header)
    nib.save(nii_img, output_nii_path)
    print(f"Saved NIfTI: {output_nii_path}")

    all_mappings.extend(slice_mapping)


# 示例调用
datanii_dir = "C:/Users/dell/Desktop/20250604/datanii/test_nii"   # 原始测试数据nii目录
pred_dir = "C:/Users/dell/Desktop/20250604/testresults/pseudorgb/pseudorgb_0_pixel/masks_pred"  # 预测mask结果png目录
vis_dir = "C:/Users/dell/Desktop/20250604/testresults//pseudorgb/pseudorgb_0_pixel/vis_nii"   # pred_nii拟储存目录
os.makedirs(vis_dir, exist_ok=True)
all_slice_mappings = []

for pa in os.listdir(datanii_dir):
    pa_path = os.path.join(datanii_dir, pa)
    image_nii_path = os.path.join(pa_path, "image.nii.gz")
    pre_png_dir = os.path.join(pred_dir, pa)
    output_dir = os.path.join(vis_dir, pa)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "pred.nii.gz")
    pngs_to_nii(
    png_dir=pre_png_dir,
    reference_nii_path=image_nii_path,
    output_nii_path=output_path,
    patient_id=pa,
    all_mappings=all_slice_mappings
    )

    for filename in ["image.nii.gz", "GTVp.nii.gz"]:
        src_file = os.path.join(pa_path, filename)
        tgt_file = os.path.join(output_dir, filename)

        if os.path.exists(src_file):
            shutil.copy(src_file, tgt_file)
            print(f"Copied {filename} to {output_dir}")
        else:
            print(f"源文件缺失: {src_file}")

# 保存为总的 CSV
output_csv = os.path.join(vis_dir, "all_slice_orders.csv")
with open(output_csv, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["patient_id", "slice_index", "file_name"])
    writer.writerows(sorted(all_slice_mappings))

print(f"所有患者堆叠顺序已保存至：{output_csv}")

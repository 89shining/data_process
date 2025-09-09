"""
计算每个mask切片的长度宽度和面积
"""

import os
import numpy as np
import pandas as pd
from PIL import Image
import SimpleITK as sitk


# 计算单层mask的长宽，以及最大最小的xy坐标点，中心点坐标
def get_width_height(mask_np, spacing_x, spacing_y):
    y_indices, x_indices = np.where(mask_np > 0)
    if len(x_indices) == 0 or len(y_indices) == 0:
        return None, None, None, None, None, None
    x_min = np.min(x_indices)
    x_max = np.max(x_indices)
    y_min = np.min(y_indices)
    y_max = np.max(y_indices)

    x_mid_pixel = (x_min + x_max) / 2.0
    y_mid_pixel = (y_min + y_max) / 2.0

    x_mid_mm = x_mid_pixel * spacing_x
    y_mid_mm = y_mid_pixel * spacing_y

    width_pixel = x_max - x_min + 1
    height_pixel= y_max - y_min + 1

    width_mm = width_pixel * spacing_x
    height_mm = height_pixel * spacing_y

    return width_mm, height_mm, x_min, x_max, y_min, y_max, x_mid_mm, y_mid_mm

if __name__ == "__main__":
    mask_dir = "C:/Users/dell/Desktop/SAM/GTVp_CTonly/20250515/Dataset/train/masks"  # mask.png目录
    nii_dir = "C:/Users/dell/Desktop/SAM/GTVp_CTonly/20250515/datanii/traindatanii" # nii数据文件夹 nii.gz
    output_path = "C:/Users/dell/Desktop/slice_info.csv"

    info = []

    for pa in sorted(os.listdir(mask_dir), key=lambda x: int(x.lstrip("p_"))):
        pa_mask_dir = os.path.join(mask_dir, pa)
        image_nii_path = os.path.join(nii_dir, pa, "image.nii.gz")
        # print(image_nii_path)

        # 读取 NIfTI 图像
        ct_img = sitk.ReadImage(image_nii_path)
        spacing = ct_img.GetSpacing()  # (spacing_x, spacing_y, spacing_z)
        spacing_x, spacing_y = spacing[0], spacing[1]

        # 读取mask3Dnii
        mask_nii_path = os.path.join(nii_dir, pa, "GTVp.nii.gz")
        mask_nii_img = sitk.ReadImage(mask_nii_path)
        mask_nii_np = sitk.GetArrayFromImage(mask_nii_img)

        coords = np.argwhere(mask_nii_np > 0)
        # 提取所有的 x/y 坐标
        ys = coords[:, 1]  # H
        xs = coords[:, 2]  # W

        # 计算3D最大投影 W H
        x_min_full, x_max_full = np.min(xs), np.max(xs)
        y_min_full, y_max_full = np.min(ys), np.max(ys)

        for i in sorted(os.listdir(pa_mask_dir), key=lambda x: int(os.path.splitext(x)[0])):
            if not i.endswith(".png"):
                continue
            mask_path = os.path.join(pa_mask_dir, i)
            mask = Image.open(mask_path).convert("L")
            mask_np = (np.array(mask) > 0).astype(np.uint8)
            # 计算单层的mask面积
            area_pixel = np.sum(mask_np > 0)
            area_mm2 = area_pixel * spacing_x * spacing_y

            width_mm, height_mm, x_min, x_max, y_min, y_max = get_width_height(mask_np, spacing_x, spacing_y)

            if width_mm is None:
                continue

            # 计算单层mask对比3D最大投影框的四个边外扩边界值
            left_ext = (x_min - x_min_full) * spacing_x
            right_ext = (x_max_full - x_max) * spacing_x
            up_ext = (y_min - y_min_full) * spacing_y
            down_ext = (y_max_full - y_max) * spacing_y

            slice_id = f"{pa}/{os.path.splitext(i)[0]}"
            info.append([
                slice_id,
                round(width_mm, 2),
                round(height_mm, 2),
                round(area_mm2, 2),
                # round(left_ext, 2),
                # round(right_ext, 2),
                # round(up_ext, 2),
                # round(down_ext, 2)
            ])


    columns = ["slice_id", "width_mm", "height_mm", "mask面积（mm2)",
               #"左扩mm", "右扩mm", "上扩mm", "下扩mm"
                ]
    # 创建 DataFrame 并保存为 Excel
    df = pd.DataFrame(info, columns=columns)
    # df.to_excel(output_excel, index=False, engine='openpyxl')
    df.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"已保存 {len(info)} 条记录到 {output_path}")
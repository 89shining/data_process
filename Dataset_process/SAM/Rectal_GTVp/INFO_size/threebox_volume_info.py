"""
上下界+中间mask面积最大层给框，一共三个手动提示框
"""

import pandas as pd
import os
import SimpleITK as sitk
import numpy as np

# 找到外扩最小边界，使合成框等效覆盖3D最大投影框
def find_min_margin(three_box, full_box):
    x_min_prompt, y_min_prompt, x_max_prompt, y_max_prompt = three_box
    x_min_full, y_min_full, x_max_full, y_max_full = full_box

    for margin in range(0, 100):  # 100为上限，理论不会超过
        x_min_ext = x_min_prompt - margin
        y_min_ext = y_min_prompt - margin
        x_max_ext = x_max_prompt + margin
        y_max_ext = y_max_prompt + margin

        # 判断是否包含 full_box
        if (x_min_ext <= x_min_full and y_min_ext <= y_min_full and
            x_max_ext >= x_max_full and y_max_ext >= y_max_full):
            return margin  # 找到最小 margin
    return -1  # 如果到100都不满足


nii_dir = "C:/Users/dell/Desktop/SAM/GTVp_CTonly/20250515/datanii/traindatanii"   # masknii目录
output_path = "C:/Users/dell/Desktop/train_statistics.csv"
info = []

for pa in sorted(os.listdir(nii_dir), key=lambda x: int(x.lstrip("p_"))):
    mask_path = os.path.join(nii_dir, pa, "GTVp.nii.gz")
    mask_img = sitk.ReadImage(mask_path)
    mask_np = sitk.GetArrayFromImage(mask_img)  # shape: (Z, H, W)
    print(mask_np.shape)
    spacing_x, spacing_y = mask_img.GetSpacing()[:2]  # [W, H, D]
    # print(spacing_x)
    # print(spacing_y)

    coords = np.argwhere(mask_np > 0)
    # 提取所有的 x/y 坐标
    zs = coords[:, 0]   # Z
    ys = coords[:, 1]   # H
    xs = coords[:, 2]   # W

    # 计算3D最大投影 W H
    x_min_full, x_max_full = np.min(xs), np.max(xs)
    y_min_full, y_max_full = np.min(ys), np.max(ys)
    width_px = x_max_full - x_min_full + 1
    height_px = y_max_full - y_min_full + 1
    width_mm = width_px * spacing_x
    height_mm = height_px * spacing_y
    # print(width_mm)
    # print(height_mm)

    # 计算 2D mask 最大面积 和 层数id
    max_area_mm2 = 0
    z_max = 0
    for z in range(mask_np.shape[0]):
        area_pixel = np.sum(mask_np[z] > 0)
        area_mm2 = area_pixel * spacing_x * spacing_y
        if area_mm2 > max_area_mm2:
            max_area_mm2 = area_mm2
            z_max = z

    # 记录上下界层号id
    z_top = np.min(zs)      # 靠近脚方向
    z_bottom = np.max(zs)   # 靠近头方向

    # top层坐标
    mask_top = mask_np[z_top]
    coords_top = np.argwhere(mask_top > 0)
    # bottom层坐标
    mask_bottom = mask_np[z_bottom]
    coords_bottom = np.argwhere(mask_bottom > 0)
    # mid层坐标
    mask_mid = mask_np[z_max]
    coords_mid = np.argwhere(mask_mid > 0)

    # 合并所有坐标点,计算三个层面的最大投影
    all_coords = np.vstack([coords_top, coords_bottom, coords_mid])  # shape: (N, 2), [y, x]
    y_min_prompt, x_min_prompt= np.min(all_coords, axis=0)
    y_max_prompt, x_max_prompt = np.max(all_coords, axis=0)
    proj_width_px = x_max_prompt - x_min_prompt + 1
    proj_height_px = y_max_prompt - y_min_prompt + 1
    proj_width_mm = proj_width_px * spacing_x
    proj_height_mm = proj_height_px * spacing_y

    # 计算中心点（单位：像素）
    center_x_full = (x_min_full + x_max_full + 1) / 2
    center_y_full = (y_min_full + y_max_full + 1) / 2
    center_x_prompt = (x_min_prompt + x_max_prompt + 1) / 2
    center_y_prompt = (y_min_prompt + y_max_prompt + 1) / 2
    # 框中心偏移（像素）
    delta_x = center_x_prompt - center_x_full
    delta_y = center_y_prompt - center_y_full
    offset_px = np.sqrt(delta_x**2 + delta_y**2)
    # 框中心偏移（毫米）
    offset_mm = np.sqrt((delta_x * spacing_x)**2 + (delta_y * spacing_y)**2)

    # 计算合成框相较于3D最大投影框的 4个方向外扩值
    left_ext = (x_min_prompt - x_min_full) * spacing_x
    right_ext = (x_max_full - x_max_prompt) * spacing_x
    up_ext = (y_min_prompt - y_min_full) * spacing_y
    down_ext = (y_max_full - y_max_prompt) * spacing_y

    # 框中心偏移方向
    threshold = 2  # 设置为像素偏移容差
    # 偏移方向标签判断
    if abs(delta_x) <= threshold and abs(delta_y) <= threshold:
        direction = "居中"
    elif delta_x > threshold and abs(delta_y) <= threshold:
        direction = "右"
    elif delta_x < -threshold and abs(delta_y) <= threshold:
        direction = "左"
    elif delta_y > threshold and abs(delta_x) <= threshold:
        direction = "下"
    elif delta_y < -threshold and abs(delta_x) <= threshold:
        direction = "上"
    elif delta_x > threshold and delta_y > threshold:
        direction = "右下"
    elif delta_x > threshold and delta_y < -threshold:
        direction = "右上"
    elif delta_x < -threshold and delta_y > threshold:
        direction = "左下"
    elif delta_x < -threshold and delta_y < -threshold:
        direction = "左上"
    else:
        direction = "不确定"

    # 计算框外扩边界
    three_box = [x_min_prompt, y_min_prompt, x_max_prompt, y_max_prompt]
    full_box = [x_min_full, y_min_full, x_max_full, y_max_full]
    best_margin = find_min_margin(three_box, full_box)

    info.append([
        pa,
        spacing_x,
        spacing_y,
        z_bottom,
        z_top,
        z_max,
        round(max_area_mm2, 2),
        round(width_mm, 2),
        round(height_mm, 2),
        round(proj_width_mm, 2),
        round(proj_height_mm, 2),
        round(left_ext, 2),
        round(right_ext, 2),
        round(up_ext, 2),
        round(down_ext, 2),
        best_margin,
        round(delta_x, 2),
        round(delta_y, 2),
        round(offset_mm, 2),
        direction
    ])

columns = [
    "pa_id",
    "像素x_mm",
    "像素y_mm"
    "上界层_id",
    "下界层_id",
    "最大面积层_id",
    "mask_slice最大面积mm2",
    "mask_volume最大投影width_mm",
    "mask_volume最大投影height_mm",
    "合成框投影width_mm",
    "合成框投影height_mm",
    "左扩mm",
    "右扩mm",
    "上扩mm",
    "下扩mm",
    "合成框最小外扩边界px",
    "中心偏移width_px",
    "中心偏移height_px",
    "中心偏移mm",
    "偏移方向"
]
df = pd.DataFrame(info, columns=columns)
# df.to_excel(output_path, index=False, engine='openpyxl')
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"已保存 {len(info)} 条记录到 {output_path}")

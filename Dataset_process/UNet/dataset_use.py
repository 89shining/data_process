import os
import glob
import numpy as np
import SimpleITK as sitk
from tqdm import tqdm
from imageio import imwrite

# ================= 参数设置 =================
root_dir = '/home/wusi/SAMdata/20250711_GTVp/datanii'      # 原始数据路径（包含 train/ 和 test/）
save_root = '/home/wusi/UNet/images' # 输出路径
os.makedirs(os.path.join(save_root, 'imagesTr'), exist_ok=True)
os.makedirs(os.path.join(save_root, 'labelsTr'), exist_ok=True)
os.makedirs(os.path.join(save_root, 'imagesTs'), exist_ok=True)
os.makedirs(os.path.join(save_root, 'labelsTs'), exist_ok=True)

window_width = 350
window_level = 40

# ================= 窗宽窗位 =================
def apply_window(img, ww, wl):
    """应用窗宽窗位并归一化到 0–255"""
    lower, upper = wl - ww / 2, wl + ww / 2
    img = np.clip(img, lower, upper)
    img = (img - lower) / ww * 255.0
    return img.astype(np.uint8)

def to_rgb(gray):
    """灰度转三通道 RGB"""
    if gray.ndim == 2:
        rgb = np.stack([gray] * 3, axis=-1)
    else:
        rgb = gray
    return rgb

def process_case(img_path, mask_path, save_img_dir, save_lab_dir, pid):
    """处理单个病例（.nii.gz → 多张 PNG）"""
    img_nii = sitk.ReadImage(img_path)
    mask_nii = sitk.ReadImage(mask_path)

    img_arr = sitk.GetArrayFromImage(img_nii)   # [z, y, x]
    mask_arr = sitk.GetArrayFromImage(mask_nii)

    # 应用窗宽窗位
    img_arr = apply_window(img_arr, window_width, window_level)

    for i in range(img_arr.shape[0]):
        rgb = to_rgb(img_arr[i])
        mask = mask_arr[i].astype(np.uint8)

        img_name = f"{pid}_slice{i:03d}.png"
        imwrite(os.path.join(save_img_dir, img_name), rgb)
        imwrite(os.path.join(save_lab_dir, img_name), mask)

# ================= 处理 Train =================
train_patients = sorted(glob.glob(os.path.join(root_dir, 'train_nii', '*')))
print(f"共发现 {len(train_patients)} 个训练病例")
for p in tqdm(train_patients, desc='Processing Train'):
    pid = os.path.basename(p)
    img_path = os.path.join(p, 'image.nii.gz')
    mask_path = os.path.join(p, 'GTVp.nii.gz')
    if os.path.exists(img_path) and os.path.exists(mask_path):
        process_case(img_path, mask_path,
                     os.path.join(save_root, 'imagesTr'),
                     os.path.join(save_root, 'labelsTr'),
                     pid)
    else:
        print(f"[警告] {pid} 缺失影像或标签文件，已跳过。")

# ================= 处理 Test =================
test_patients = sorted(glob.glob(os.path.join(root_dir, 'test_nii', '*')))
print(f"共发现 {len(test_patients)} 个测试病例")
for p in tqdm(test_patients, desc='Processing Test'):
    pid = os.path.basename(p)
    img_path = os.path.join(p, 'image.nii.gz')
    mask_path = os.path.join(p, 'GTVp.nii.gz')
    if os.path.exists(img_path) and os.path.exists(mask_path):
        process_case(img_path, mask_path,
                     os.path.join(save_root, 'imagesTs'),
                     os.path.join(save_root, 'labelsTs'),
                     pid)
    else:
        print(f"[警告] {pid} 缺失影像或标签文件，已跳过。")

print("✅ 全部病例已转换完成，RGB 图像可直接用于 U-Net 训练。")

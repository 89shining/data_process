"""
将 train_nii.gz 转为 VOC 数据集格式
✅ 窗宽窗位 (WL=40, WW=350)
✅ 归一化到 [0,255]
✅ 随机划分 train/val/test
"""

import os
import random
import numpy as np
import SimpleITK as sitk
from PIL import Image
from tqdm import tqdm

# ===================== 参数设置 =====================
root_dir = r"D:\SAM\Rectal\GTVp_CTonly\20251128-crop\cropnii\train_nii"
save_root = r"D:/project/deeplabv3-plus-pytorch/VOCdevkit/VOC2007"
trainval_percent = 1.0
train_percent = 0.9
WL, WW = 40, 350

# 计算窗宽窗位范围
vmin, vmax = WL - WW / 2, WL + WW / 2

# 输出路径
os.makedirs(os.path.join(save_root, "JPEGImages"), exist_ok=True)
os.makedirs(os.path.join(save_root, "SegmentationClass"), exist_ok=True)
os.makedirs(os.path.join(save_root, "ImageSets/Segmentation"), exist_ok=True)

# ===================== 功能函数 =====================
def apply_window(image):
    image = np.clip(image, vmin, vmax)
    image = (image - vmin) / (vmax - vmin)
    return (image * 255).astype(np.uint8)

def nii_to_voc(image_path, mask_path, save_root, pid, keep_margin=1):
    """将单个患者的 NIfTI 转为 VOC，跳过空切片"""
    img = sitk.ReadImage(image_path)
    msk = sitk.ReadImage(mask_path)
    img_arr = sitk.GetArrayFromImage(img)
    msk_arr = sitk.GetArrayFromImage(msk)

    if img_arr.shape != msk_arr.shape:
        raise ValueError(f"[错误] 尺寸不一致: {pid}, image={img_arr.shape}, mask={msk_arr.shape}")

    # # 找出非空切片索引
    # nonzero_idx = np.where(msk_arr.reshape(msk_arr.shape[0], -1).sum(axis=1) > 0)[0]
    # if len(nonzero_idx) == 0:
    #     print(f"[跳过] {pid} 全部为空 mask。")
    #     return []
    # # 保留边界邻层（上下各 keep_margin 层）
    # start = max(0, nonzero_idx[0] - keep_margin)
    # end = min(msk_arr.shape[0], nonzero_idx[-1] + keep_margin + 1)
    # slice_range = range(start, end)

    # 🚫 不再筛选非空切片，保留全部层
    slice_range = range(msk_arr.shape[0])

    slice_names = []
    for i in slice_range:
        img_slice = apply_window(img_arr[i])
        mask_slice = (msk_arr[i] > 0).astype(np.uint8) * 1

        # if np.sum(mask_slice) == 0:
        #     continue  # 跳过空切片

        img_name = f"{pid}_slice{i:03d}"
        Image.fromarray(img_slice).convert("L").save(
            os.path.join(save_root, "JPEGImages", f"{img_name}.jpg"))
        Image.fromarray(mask_slice).convert("L").save(
            os.path.join(save_root, "SegmentationClass", f"{img_name}.png"))

        slice_names.append(img_name)

    return slice_names

# ===================== 主流程 =====================
print("Step 1: 转换为 VOC 格式中 ...")
patient_list = [p for p in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, p))]
all_names = []

for pid in tqdm(patient_list, desc="Processing patients"):
    image_path = os.path.join(root_dir, pid, "image.nii.gz")
    mask_path  = os.path.join(root_dir, pid, "GTVp.nii.gz")
    if not os.path.exists(image_path) or not os.path.exists(mask_path):
        print(f"[跳过] {pid} 缺失 image 或 GTVp 文件。")
        continue
    all_names.extend(nii_to_voc(image_path, mask_path, save_root, pid))

# ===================== 划分 train/val/test =====================
print("Step 2: 生成 ImageSets/Segmentation/*.txt ...")
random.seed(0)
num = len(all_names)
tv = int(num * trainval_percent)
tr = int(tv * train_percent)
trainval = random.sample(all_names, tv)
train = random.sample(trainval, tr)

set_dir = os.path.join(save_root, "ImageSets/Segmentation")
with open(os.path.join(set_dir, "trainval.txt"), "w") as ftrainval, \
     open(os.path.join(set_dir, "train.txt"), "w") as ftrain, \
     open(os.path.join(set_dir, "val.txt"), "w") as fval, \
     open(os.path.join(set_dir, "test.txt"), "w") as ftest:
    for name in all_names:
        if name in trainval:
            ftrainval.write(name + "\n")
            if name in train:
                ftrain.write(name + "\n")
            else:
                fval.write(name + "\n")
        else:
            ftest.write(name + "\n")

print(f"✅ 转换完成！共 {num} 张有效切片（已跳过空层）")
print(f"✅ 窗宽窗位: WL={WL}, WW={WW}")
print(f"✅ 保存路径: {save_root}")

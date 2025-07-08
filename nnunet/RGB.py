"""
伪RGB输入
"""

import os
import shutil
import os
import nibabel as nib
import numpy as np
import SimpleITK as sitk

def GetSubFolders(file_dir):
    subfolder = []
    nStop = 0
    # os.walk 遍历file_dir及其子目录
    for root, dirs, files in os.walk(file_dir):

        for item in dirs:
            subfolder.append(item)   # 将文件名item添加到列表中保存

        nStop = 1
        if nStop > 0:
            break

    return subfolder


"""
相邻三张合成伪RGB.nii.gz
"""
def create_pseudo_rgb_nii(image_nii_path, output_nii_path):
    img_nii = nib.load(image_nii_path)
    volume = img_nii.get_fdata()  # shape: (H, W, D)
    affine = img_nii.affine
    header = img_nii.header

    H, W, D = volume.shape
    pseudo_rgb_volume = np.zeros((H, W, D, 3), dtype=np.float32)  # 用float32而非uint8

    for z in range(D):
        z0 = max(z - 1, 0)
        z1 = z
        z2 = min(z + 1, D - 1)

        pseudo_rgb_volume[:, :, z, 0] = volume[:, :, z0]  # HU值
        pseudo_rgb_volume[:, :, z, 1] = volume[:, :, z1]
        pseudo_rgb_volume[:, :, z, 2] = volume[:, :, z2]

    # 转换维度为 (H, W, D * 3) → 因为 RGB 通道 nnUNet 不支持，需要融合为单通道
    # 我们转置为 (D, H, W, 3) → 再转换为 (H, W, D*3)
    pseudo_rgb_volume = np.transpose(pseudo_rgb_volume, (3, 0, 1, 2))  # (D, H, W, 3)
    # 保存为 NIfTI
    nib_img = nib.Nifti1Image(pseudo_rgb_volume, affine=affine, header=header)
    nib.save(nib_img, output_nii_path)
    print(f"✅ Saved pseudo-RGB nii.gz for nnU-Net: {output_nii_path}")

# 示例调用（循环多个患者）
input_root = "C:/Users/dell/Desktop/20250707/datanii/test_nii"  # nii.gz原文件
output_root = "C:/Users/dell/Desktop/Dataset002_RGB"
three_channels_root = os.path.join(output_root, "images")
os.makedirs(output_root, exist_ok=True)
os.makedirs(three_channels_root, exist_ok=True)

palist = GetSubFolders(input_root)
for pa in palist:
    print(pa)
    nid = pa.split('_', -1)[-1]
    input_path = os.path.join(input_root, pa, "image.nii.gz")
    images_path = os.path.join(three_channels_root, f"RGB_{int(nid):03d}_0000.nii.gz")
    print(images_path)
    if os.path.exists(input_path):
        create_pseudo_rgb_nii(input_path, images_path)
    else:
        print(f"Missing image.nii.gz for {pa}")



"""
将伪RGB.nii.gz分别拆分为R G B.nii.gz
"""
input_dir = three_channels_root   #   伪RGB图像路径
single_channel_dir = os.path.join(output_root, "imagesTs")  #  单通道结果的路径
os.makedirs(single_channel_dir, exist_ok=True)

for filename in sorted(os.listdir(input_dir)):
    if not filename.endswith(".nii.gz"):
        continue

    input_path = os.path.join(input_dir, filename)
    img = nib.load(input_path)
    data = img.get_fdata()  # shape: (3, H, W, D)
    affine = img.affine
    header = img.header

    if data.shape[0] != 3:
        print(f"⚠️ 非三通道图像，跳过: {filename}")
        continue

    # 提取编号（如 GTVp_003_0000.nii.gz → 003）
    base_id = filename.split("_")[1]
    print(base_id)

    # ch=0,1,2,代表三个通道
    for ch in range(3):
        print(ch)
        out_data = data[ch]  # 第ch个通道， shape: (H, W, D)
        out_img = nib.Nifti1Image(out_data, affine=affine, header=header)
        out_name = f"RGB_{base_id}_{ch:04d}.nii.gz"
        print(out_name)
        out_path = os.path.join(single_channel_dir, out_name)
        nib.save(out_img, out_path)

    print(f"✅ 拆分完成: {filename}")


"""
提取GTVp.nii.gz，俺Dataset格式改名
"""
input_dir = input_root
GT_dir = os.path.join(output_root, "labelsTs")
os.makedirs(GT_dir, exist_ok=True)

# 对pa列表按数字排序，确保顺序为p_0, p_1, ..., p_n
pa_list = sorted(os.listdir(input_dir), key=lambda x: int(x.split('_')[1]))

for idx, pa in enumerate(pa_list):
    # print(pa)
    GT_path = os.path.join(input_dir, pa, "GTVp.nii.gz")
    if os.path.exists(GT_path):
        output_name = f"RGB_{idx:03d}.nii.gz"
        # print(output_name)
        output_path = os.path.join(GT_dir, output_name)
        shutil.copy(GT_path, output_path)
        print(f"Copied: {GT_path} -> {output_path}")
    else:
        print(f"Warning: {GT_path} does not exist.")

shutil.rmtree(three_channels_root)
print(f"🧹 已删除临时目录: {three_channels_root}")

# # # 检查图像
# import nibabel as nib
#
# img_path = "C:/Users/dell/Desktop/Dataset002_test/imagesTr/RGB_000_0000.nii.gz"
# seg_path = "C:/Users/dell/Desktop/Dataset002_test/labelsTr/RGB_000.nii.gz"
#
# img = nib.load(img_path)
# seg = nib.load(seg_path)
#
# img_data = img.get_fdata()
# seg_data = seg.get_fdata()
#
# print("Image shape:", img_data.shape)  # ✅ 应该是 (3, 512, 512, 73)
# print("Seg shape:", seg_data.shape)    # ✅ 应该是 (512, 512, 73)

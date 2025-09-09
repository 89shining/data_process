"""
查看png-nii图像空间信息是否一致
"""
import numpy as np

from PIL import Image
import nibabel as nib
#
# ref = nib.load("C:/Users/dell/Desktop/SAM_GTVp/GTVp_CTonly/Data/Data_nii/p_65/image.nii.gz")
# ref_shape = ref.shape[:2]
#
# png = Image.open("C:/Users/dell/Desktop/SAM_GTVp/GTVp_CTonly/testresults/finetune1.1/masks_pred/p_65/21.png")
# print("PNG size:", png.size)
# print("Reference slice size:", ref_shape)

# """
# 查看image 和 mask affine是否一致
# """
# import nibabel as nib
#
# img_affine = nib.load("C:/Users/dell/Desktop/image.nii.gz").affine
# mask_affine = nib.load("C:/Users/dell/Desktop/mask.nii.gz").affine
#
# print("Image affine:\n", img_affine)
# print("Mask affine:\n", mask_affine)
#
"""
查看二维坐标是否一致
"""
# import nibabel as nib
# import matplotlib.pyplot as plt
#
# img = nib.as_closest_canonical(nib.load("C:/Users/dell/Desktop/SAM_GTVp/GTVnd/testresults_fold3/vis_nii/p_15/image.nii.gz")).get_fdata()
# pred = nib.as_closest_canonical(nib.load("C:/Users/dell/Desktop/SAM_GTVp/GTVnd/testresults_fold3/vis_nii/p_15/pred.nii.gz")).get_fdata()
# gt = nib.as_closest_canonical(nib.load("C:/Users/dell/Desktop/SAM_GTVp/GTVnd/testresults_fold3/vis_nii/p_15/GTVnd.nii.gz")).get_fdata()
#
# print((nib.load("C:/Users/dell/Desktop/SAM_GTVp/GTVnd/testresults_fold3/vis_nii/p_15/image.nii.gz")).affine)
# print((nib.load("C:/Users/dell/Desktop/SAM_GTVp/GTVnd/testresults_fold3/vis_nii/p_15/GTVnd.nii.gz")).affine)
# print((nib.load("C:/Users/dell/Desktop/SAM_GTVp/GTVnd/testresults_fold3/vis_nii/p_15/pred.nii.gz")).affine)
#
# z = 51  # 任意层号
# plt.imshow(img[:, :, z], cmap='gray')
# plt.imshow(gt[:, :, z], alpha=0.4, cmap='Reds')
# plt.imshow(pred[:, :, z], alpha=0.4, cmap='Greens')
# plt.title(f"Slice {z}")
# plt.show()

"""
查看两张image方位是否一致
"""
# img1 = nib.load('C:/Users/dell/Desktop/image.nii.gz')
# img2 = nib.load('C:/Users/dell/Desktop/compare.nii.gz')
#
# affine1 = img1.affine
# affine2 = img2.affine
#
# print("Affine matrix of image1:\n", affine1)
# print("Affine matrix of image2:\n", affine2)

# import SimpleITK as sitk
#
# image = sitk.ReadImage("C:/Users\WS\Desktop/20250604\datanii/train_nii\p_0/image.nii.gz")
# mask = sitk.ReadImage("C:/Users\WS\Desktop/20250604\datanii/train_nii\p_0/GTVp.nii.gz")
#
# def check_meta_consistency(img1, img2):
#     return (img1.GetSize() == img2.GetSize() and
#             img1.GetSpacing() == img2.GetSpacing() and
#             img1.GetOrigin() == img2.GetOrigin() and
#             img1.GetDirection() == img2.GetDirection())
#
# print("是否一致:", check_meta_consistency(image, mask))
#


"""
检查文件大小
"""
# import os
# import pandas as pd
#
# csv_path = "C:/Users/dell/Desktop/20250604/dataset/train/train_rgb_dataset.csv"
# root_dir = "C:/Users/dell/Desktop/20250604/dataset/train"   # images目录
#
# df = pd.read_csv(csv_path, header=None, names=["image", "mask"])
# sizes = [os.path.getsize(os.path.join(root_dir, path.strip("/"))) for path in df["image"]]
# print(f"Average size: {sum(sizes)/len(sizes)/1024:.2f} KB")


"""
查看z方向大小与头脚关系
"""
import SimpleITK as sitk

nii_path = r"C:\Users\dell\Desktop\SAM\GTVp_CTonly\20250809\datanii\test_nii/p_1/image.nii.gz"  # 修改为你的路径
img = sitk.ReadImage(nii_path)
arr = sitk.GetArrayFromImage(img)

size = arr.shape[0]  # Z 轴方向的层数

print(f"图像总共有 {size} 层 (Z)")

# 验证前几层的物理 z 坐标
for z_index in [0, size // 2, size - 1]:
    # 注意 SimpleITK 的 TransformIndexToPhysicalPoint 用的是 (x, y, z)
    physical_z = img.TransformIndexToPhysicalPoint((0, 0, z_index))[2]
    print(f"z_index={z_index} → 物理z坐标: {physical_z:.2f}")

"""
查看nii空间位置信息
"""
import nibabel as nib
from nibabel.orientations import aff2axcodes

# 快速查看是否处于标准医学方向
nii = nib.load('C:/Users/WS/Desktop/p_0/slicer-GTVp.nii.gz')
print("Orientation:", aff2axcodes(nii.affine))


# 查看空间位置
nii = nib.load('C:/Users/WS/Desktop/p_0/slicer-GTVp.nii.gz')  # 或 .nii
print("Shape:", nii.shape)
print("Affine:\n", nii.affine)

# nii = nib.load('C:/Users/WS/Desktop/p_0/image.nii.gz')  # 或 .nii
# print("Shape:", nii.shape)
# print("Affine:\n", nii.affine)


# import SimpleITK as sitk
#
# img = sitk.ReadImage('C:/Users/WS/Desktop/p_0/pred.nii.gz')
# print("Size:", img.GetSize())
# print("Spacing:", img.GetSpacing())
# print("Origin:", img.GetOrigin())
# print("Direction:", img.GetDirection())

# # 查看image和 mask空间信息是否一致
# import nibabel as nib
# import numpy as np
# img = nib.load('C:/Users/WS/Desktop/p_0/image.nii.gz')
# mask = nib.load('C:/Users/WS/Desktop/p_0/GTVp.nii.gz')
# pred = nib.load('C:/Users/WS/Desktop/p_0/pred.nii.gz')
#
# print(np.allclose(img.affine, mask.affine))

# # 查看tiff和png
# import matplotlib.pyplot as plt
# from PIL import Image
# import numpy as np
#
# img = np.array(Image.open("C:/Users/WS/Desktop/Rectal_GTVp/GTVp_CTonly/20250515/Dataset/test/images/p_0/37.tiff"))
# mask = np.array(Image.open("C:/Users/WS/Desktop/Rectal_GTVp/GTVp_CTonly/20250515/testresults/20250522/masks_pred/p_0/37.png"))
#
# plt.imshow(img, cmap='gray')
# plt.imshow(mask, cmap='Reds', alpha=0.4)  # 半透明看是否重合
# plt.show()

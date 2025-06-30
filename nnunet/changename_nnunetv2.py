"""
将nii文件处理为2D切片并改规范格式名
"""
from __future__ import division
import csv
import os

import SimpleITK as sitk
import numpy as np
from PIL import Image
import shutil



# 获取file_dir中所有直接子目录名称，用列表subfolder保存
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



if __name__ == "__main__":

    ctdir = 'C:/Users/dell/Desktop/SAM/GTVp_CTonly/20250630/datanii/train_nii'   # 训练集 nii目录
    imadir = 'C:/Users/dell/Desktop/SAM/GTVp_CTonly/nnUNet/Dataset001_GTVp/imagesTr'    # 训练 images保存地址
    maskdir = 'C:/Users/dell/Desktop/SAM/GTVp_CTonly/nnUNet/Dataset001_GTVp/labelsTr'   # 训练 masks保存地址
    os.makedirs(imadir, exist_ok = True)
    os.makedirs(maskdir, exist_ok = True)

    palist = GetSubFolders(ctdir)
    for pa in palist:
        nid = pa.split('_', -1)[-1]    # 用_做分割，取最后一位元素即患者编号
        srcfile = ctdir + '/' + pa + '/image.nii.gz'       # 获取患者图像文件
        dstfile = f"{imadir}/GTVp_{int(nid):03d}_0000.nii.gz"    # 构建新文件
        shutil.copy(srcfile, dstfile)      # 文件复制

        srcfile = ctdir + '/' + pa + '/GTVp.nii.gz'
        dstfile = f"{maskdir}/GTVp_{int(nid):03d}.nii.gz"
        shutil.copy(srcfile, dstfile)  # 文件复制

    ctdir = 'C:/Users/dell/Desktop/SAM/GTVp_CTonly/20250630/datanii/test_nii'   # 测试集 nii目录
    imadir = 'C:/Users/dell/Desktop/SAM/GTVp_CTonly/nnUNet/Dataset001_GTVp/imagesTs'   # 测试 images保存地址
    maskdir = 'C:/Users/dell/Desktop/SAM/GTVp_CTonly/nnUNet/Dataset001_GTVp/labelsTs'      # 测试 masks保存地址，可选
    os.makedirs(imadir, exist_ok=True)
    os.makedirs(maskdir, exist_ok=True)

    palist = GetSubFolders(ctdir)
    for pa in palist:
        nid = pa.split('_', -1)[-1]
        srcfile = ctdir + '/' + pa + '/image.nii.gz'
        dstfile = f"{imadir}/GTVp_{int(nid):03d}_0000.nii.gz"
        shutil.copy(srcfile, dstfile)

        srcfile = ctdir + '/' + pa + '/GTVp.nii.gz'
        dstfile = f"{maskdir}/GTVp_{int(nid):03d}.nii.gz"
        shutil.copy(srcfile, dstfile)  # 文件复制
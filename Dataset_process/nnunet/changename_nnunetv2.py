"""
将nii文件改规范格式名
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

    ctdir = r'/home/wusi/SAMdata/Rectal/20251224_GTVp/datanii/test_nii'   # 训练集 nii目录
    imadir = r'/home/wusi/nnUNet/nnUNetFrame/DATASET/nnUNet_raw/Dataset001_GTVp/imagesTs'    # 训练 images保存地址
    maskdir = r'/home/wusi/nnUNet/nnUNetFrame/DATASET/nnUNet_raw/Dataset001_GTVp/labelsTs'   # 训练 masks保存地址
    os.makedirs(imadir, exist_ok = True)
    os.makedirs(maskdir, exist_ok = True)

    dataset_name = "GTVp"  # 数据集名称
    palist = GetSubFolders(ctdir)
    for pa in palist:
        print(pa)
        nid = pa.split('_', -1)[-1]    # 用_做分割，取最后一位元素即患者编号
        srcfile = ctdir + '/' + pa + '/image.nii.gz'       # 获取患者图像文件
        dstfile = f"{imadir}/{dataset_name}_{int(nid):03d}_0000.nii.gz"    # 构建新文件
        print(dstfile)
        shutil.copy(srcfile, dstfile)      # 文件复制

        srcfile = ctdir + '/' + pa + '/GTVp.nii.gz'   # 获取患者mask GT文件地址
        dstfile = f"{maskdir}/{dataset_name}_{int(nid):03d}.nii.gz"
        shutil.copy(srcfile, dstfile)  # 文件复制

    # ctdir = r'/home/wusi/SAMdata/Eso-CTV/20251217/cropnii_nnUNet/test_nii'   # 测试集 nii目录
    # imadir = r'/home/wusi/nnUNet/nnUNetFrame/DATASET/nnUNet_raw/Dataset008_EsoCTV73p/imagesTs'   # 测试 images保存地址
    # maskdir = r'/home/wusi/nnUNet/nnUNetFrame/DATASET/nnUNet_raw/Dataset008_EsoCTV73p/labelsTs'      # 测试 masks保存地址，可选
    # os.makedirs(imadir, exist_ok=True)
    # os.makedirs(maskdir, exist_ok=True)
    #
    # palist = GetSubFolders(ctdir)
    # for pa in palist:
    #     nid = pa.split('_', -1)[-1]
    #     srcfile = ctdir + '/' + pa + '/image.nii.gz'
    #     dstfile = f"{imadir}/{dataset_name}_{int(nid):03d}_0000.nii.gz"
    #     shutil.copy(srcfile, dstfile)
    #
    #     srcfile = ctdir + '/' + pa + '/CTV.nii.gz'
    #     dstfile = f"{maskdir}/{dataset_name}_{int(nid):03d}.nii.gz"
    #     shutil.copy(srcfile, dstfile)  # 文件复制
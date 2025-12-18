"""
提取2D切片
nii.gz -> nii
"""
import csv

import pydicom
import os
import numpy as np
import SimpleITK as sitk
from PIL import Image
import nibabel as nib


# 获取currentpath目录的所有子目录
def GetSubDirs(currentpath):
    subdir = []           # 用sudir列表储存子目录名称
    nStop = 0             # 计数器，控制目录遍历
    # root:当前遍历的目录路径 dirs:当前目录下的子目录列表  files:当前目录下的文件列表
    for root, dirs, files in os.walk(currentpath):

        for patient in dirs:    # 遍历所有子目录
            subdir.append(patient)       # 将patient添加到sudir列表中

        nStop = nStop + 1
        if nStop > 0:
            break          # 当nstop>0时，跳出for循环，即只遍历当前一层子目录，不再深入
    return subdir

# 获取file_path路径下所有文件的完整路径，返回一个列表
def GetFilesinFolder(file_path):

    allfiles = []
    for root, dirs, files in os.walk(file_path):

        for item in files:
            tmppath = root.replace('\\', '/') + '/' + item     # 将文件名 item 添加到路径后面，构建出完整的文件路径
            allfiles.append(tmppath)

    return allfiles

# 获取file_dir下所有文件的名称，并用列表subfolder保存
def GetFilesInFolders(file_dir):
    subfolder = []
    nStop = 0
    for root, dirs, files in os.walk(file_dir):

        for item in files:
            subfolder.append(item)

        nStop = 1
        if nStop > 0:
            break

    return subfolder

# 根据srcdir下的文件列表排序，并生成一个新的文件列表
def GetSortedFileList(srcdir):
    unsort = GetFilesInFolders(srcdir)      # 获取未排序的文件列表
    nLen = len(unsort)                      # 获取文件列表的长度
    for i in range(0, nLen):                # 遍历文件列表中的每个文件
        info = unsort[i].split('/', -1)[-1]    # split('/', -1) 将文件路径按 / 分割，并获取最后一部分即文件名
        fileinfo = info.split('.', -1)         # 将文件名按 . 分割（最后一部分是文件扩展名）
        filename = str(i) + '.' + fileinfo[-1]    # 生成新的排序文件名，索引 i 作为文件名前缀，文件扩展名保持不变。
        unsort[i] = unsort[i].replace(info, filename)    # 替换文件名，原文件名 info 替换为新的排序文件名 filename

# 保存 2D numpy 数组为 NIfTI 文件
def SaveMatNII(slice_np, reference_img, save_path):
    slice_img = sitk.GetImageFromArray(slice_np)  # shape: [H, W]

    # 提取 spacing 和 origin 的前两个维度
    spacing = reference_img.GetSpacing()[:2]
    origin = reference_img.GetOrigin()[:2]

    # 提取 direction 中前2x2部分
    direction_full = reference_img.GetDirection()  # 3x3 = 9
    direction_2d = (
        direction_full[0], direction_full[1],
        direction_full[3], direction_full[4]
    )  # 只保留前两行前两列，转为 2×2 flatten 为长度为 4 的 tuple

    # 设置 2D 图像的空间信息
    slice_img.SetSpacing(spacing)
    slice_img.SetOrigin(origin)
    slice_img.SetDirection(direction_2d)

    # 保存为 NIfTI
    sitk.WriteImage(slice_img, save_path)


def GenerateNIICSV(rootdir, ctdir, maskdir, trainfile):
    # 打开CSV文件trainfile，准备将病人的 CT 图像和掩膜路径写入该文件
    fqingxi = open(trainfile, 'w', newline='')
    csv_qingxi = csv.writer(fqingxi, dialect='excel')

    # 获取CT 图像目录 ctdir 下所有的子文件夹名称，即每个病人的目录
    palist = sorted(GetSubDirs(ctdir),  key=lambda x: int(x.lstrip("p_")))

    for pa in palist:
        print(pa)
        padir = ctdir + '/' + pa     # 获取患者目录

        # 获取当前病人目录下所有文件 fi 的列表，用traininfo存储
        filist = sorted(GetFilesInFolders(padir), key=lambda x: int(os.path.splitext(x)[0]))
        for fi in filist:
            traininfo = []     # 存储当前患者图像和掩膜信息
            ctfile = ctdir + '/' + pa + '/' + fi   # CT图像地址
            maskfile = maskdir + '/' + pa + '/' + fi

            ima =  sitk.ReadImage(maskfile)
            tmask = sitk.GetArrayFromImage(ima)  #  (H, W)
            # 如果掩膜图像中存在有效的区域（即掩膜像素值大于 0），则将 CT 图像和掩膜的路径写入 CSV 文件
            if np.max(tmask) > 0:
                traininfo.append(ctfile.replace(rootdir, ''))   # 相对路径
                # traininfo.append(ctfile)   # 绝对路径
                traininfo.append(maskfile.replace(rootdir, ''))
                # traininfo.append(maskfile)
                csv_qingxi.writerow(traininfo)   # 写入CSV文件

    fqingxi.close()

if __name__ == "__main__":
    srcdir = r'C:\Users\dell\Desktop\Eso-CTV\20251217\datanii\test_nii'  # nii.gz主目录
    rootdir = r'C:\Users\dell\Desktop\Eso-CTV\20251217\dataset\test'   # dataset主目录
    csv_path = r'C:\Users\dell\Desktop\Eso-CTV\20251217\dataset\test/test_nii.csv'  # 保存csv地址
    imadir = r'C:\Users\dell\Desktop\Eso-CTV\20251217\dataset\test/images'   # image.nii保存地址
    maskdir = r'C:\Users\dell\Desktop\Eso-CTV\20251217\dataset\test/masks'
    os.makedirs(imadir, exist_ok=True)
    os.makedirs(maskdir, exist_ok=True)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    palist = GetSubDirs(srcdir)
    for pa in palist:
        print(pa)
        padir = os.path.join(srcdir, pa)

        # 读取 image 和 mask
        ctfile = os.path.join(padir, 'image.nii.gz')
        maskfile = os.path.join(padir, 'CTV.nii.gz')
        ct_img = sitk.ReadImage(ctfile)
        mask_img = sitk.ReadImage(maskfile)

        ct_data = sitk.GetArrayFromImage(ct_img)
        mask_data = sitk.GetArrayFromImage(mask_img)
        assert ct_data.shape == mask_data.shape, f"Shape mismatch in {pa}"

        # 创建目标子目录
        ct_dstdir = os.path.join(imadir, pa)
        mask_dstdir = os.path.join(maskdir, pa)
        os.makedirs(ct_dstdir, exist_ok=True)
        os.makedirs(mask_dstdir, exist_ok=True)

        # 同步遍历 image 和 mask
        for ni in range(mask_data.shape[0]):
            mask_slice = mask_data[ni]
            if np.max(mask_slice) == 0:
                continue  # 跳过空掩膜及其图像

            ct_slice = ct_data[ni]

            # 保存 image
            ct_save_path = os.path.join(ct_dstdir, f"{ni}.nii")
            SaveMatNII(ct_slice, ct_img, ct_save_path)

            # 保存 mask
            mask_save_path = os.path.join(mask_dstdir, f"{ni}.nii")
            SaveMatNII(mask_slice, mask_img, mask_save_path)

    # 生成 CSV（只记录非空掩膜）
    GenerateNIICSV(rootdir, imadir, maskdir, csv_path)

"""
提取2D切片
image：nii.gz -> .tiff
masks：nii.gz -> .png
"""

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

# 将mat（numpy数组）-> np.unit8（8位无符号整数PNG）
def SaveMatPNG(mat, img_path):
    mode = 'L'    # L 灰度图
    im = Image.fromarray(mat.astype(np.uint8), mode)   #  np.unit8（8位无符号整数）——灰度图像标准数据类型
    im.save(img_path)      # 保存图像到指定的路径 img_path

# ima（numpy数组）-> np.float32（32位浮点数TIFF）
def SaveMatTiff(ima, img_path):
    im = Image.fromarray(ima.astype(np.float32))
    im.save(img_path)        # 保存图像到指定路径


# SimpleITL读取filename(NIfTI文件） -> tima（NIfTI格式（.nii或.nii.gz））-> tdata(NumPy数组)
def SitkNII(filename):
    tima = sitk.ReadImage(filename)      # 用SimpleITK读取filename指定的NIfTI文件，并返回一个SimpleITK图像对象
    tdata = sitk.GetArrayFromImage(tima)   # 将tima中的SimpleITK图像对象转换为NumPy数组tdata
    return tdata

# Nibabel读取filename(NIfTI文件） -> nifti_img（NIfTI格式（.nii或.nii.gz））-> image_data(NumPy数组float64)
def NibabelNII(filename):

    nifti_img = nib.load(filename)

    # 获取图像数据
    image_data = nifti_img.get_fdata()
    return image_data


if __name__ == "__main__":

    srcdir = 'C:/Users\dell\Desktop\SAM\GTVp_CTonly/20250604/datanii/test_nii'      # nii数据， srcdir下一级子目录是患者文件夹
    imadir = 'C:/Users/dell/Desktop/SAM/GTVp_CTonly/20250604/dataset/test/images'    # images保存目录,不能在srcdir目录中，保存后子目录是患者文件夹
    maskdir = 'C:/Users/dell/Desktop/SAM/GTVp_CTonly/20250604/dataset/test/masks'    # masks同上
    os.makedirs(imadir, exist_ok=True)
    os.makedirs(maskdir, exist_ok=True)

    palist = GetSubDirs(srcdir)    # 遍历srcdir所有子目录列表palist
    for pa in palist:      # 获取palist每一个元素pa
        print(pa)
        padir = srcdir + '/' + pa   # 拼接出完整的子目录路径 padir

        ctfile = padir + '/image.nii.gz'   # 拼接出图像文件的路径 ctfile
        tdata = SitkNII(ctfile)    # 使用SitKNII函数，返回numpy数组tdata
        nslice = tdata.shape[0]    # 获取图像数据 tdata 的第一个维度的大小，这通常表示切片数

        dstdir = imadir + '/' + pa   # 目标目录 dstdir用于存放每个患者（pa）的图像切片。imadir 是存放图像切片的主目录，pa 是患者或数据集的子目录。
        if not os.path.exists(dstdir):   # 检查目标目录 dstdir 是否存在
            os.mkdir(dstdir)     # 如果目标目录不存在，创建该目录

        for ni in range(0, nslice):    # 遍历每个图像的切片数
            tmpslice = tdata[ni, ...]   # tdata中提取第ni个切片，... 是 NumPy 的切片语法，用来表示其他维度（通常是 Y 和 X 维度）
            tmpfile = dstdir + '/' + str(ni) + '.tiff'  # 构建目标文件的路径，以.tiff后缀保存
            SaveMatTiff(tmpslice, tmpfile)

        maskfile = padir + '/GTVp.nii.gz'   # 拼接出掩膜文件 GTV.nii.gz 的路径

        # 用SitkNII读取图像
        tdata = SitkNII(maskfile)       # 使用 SitkNII 函数读取掩膜文件，获取图像数据
        print(np.max(tdata))
        tdata = tdata * 255        # 掩膜像素值[0,255]
        nslice = tdata.shape[0]    # 获取掩膜切片数


        # # 用NibabelNII
        # image_data = NibabelNII(maskfile)
        # print(np.max(image_data))
        # image_data = image_data * 255
        # nslice = image_data.shape[0]

        dstdir = maskdir + '/' + pa   # 存储每个患者的掩膜切片
        if not os.path.exists(dstdir):   # 检查目录是否存在
            os.mkdir(dstdir)   # 若不存在，创建目录

        for ni in range(0, nslice):      # 遍历掩膜图像每个切片
            tmpslice = tdata[ni, ...]
            tmpfile = dstdir + '/' + str(ni) + '.png'
            SaveMatPNG(tmpslice, tmpfile)     # 调用SaveMatPNG函数，将当前切片数据tmpslice保存为PNG(uint8）


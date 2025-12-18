"""
生成单个训练CSV文件
image: .tiff
mask：.png
"""

import csv

import os
import numpy as np
from PIL import Image

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

#
def GenerateTiffCSV(rootdir, ctdir, maskdir, trainfile):
    # 打开CSV文件trainfile，准备将病人的 CT 图像和掩膜路径写入该文件
    fqingxi = open(trainfile, 'w', newline='')
    csv_qingxi = csv.writer(fqingxi, dialect='excel')

    # 获取CT 图像目录 ctdir 下所有的子文件夹名称，即每个病人的目录
    palist = sorted(GetSubFolders(ctdir),  key=lambda x: int(x.lstrip("p_")))

    for pa in palist:
        print(pa)
        padir = ctdir + '/' + pa     # 获取患者目录

        # 获取当前病人目录下所有文件 fi 的列表，用traininfo存储
        filist = sorted(GetFilesInFolders(padir), key=lambda x: int(os.path.splitext(x)[0]))
        for fi in filist:
            traininfo = []     # 存储当前患者图像和掩膜信息
            ctfile = ctdir + '/' + pa + '/' + fi   # CT图像地址
            maskfile = maskdir + '/' + pa + '/' + fi.replace('.tiff', '.png')   # 掩膜图像地址，后缀替换

            ima = Image.open(maskfile)
            tmask = np.array(ima)      # 掩膜图像并将其转换为 NumPy 数组 tmask
            # 如果掩膜图像中存在有效的区域（即掩膜像素值大于 0），则将 CT 图像和掩膜的路径写入 CSV 文件
            if np.max(tmask) > 0:
                traininfo.append(ctfile.replace(rootdir, ''))   # 相对路径
                # traininfo.append(ctfile)   # 绝对路径
                traininfo.append(maskfile.replace(rootdir, ''))
                # traininfo.append(maskfile)
                csv_qingxi.writerow(traininfo)   # 写入CSV文件

    fqingxi.close()


if __name__ == "__main__":
    trainfile = 'C:/Users/dell/Desktop/dataset/train_tiff.csv'   # 与图像和掩码位于同一主目录下
    ctdir = 'C:/Users/dell/Desktop/dataset/images'      # 存放图像的目录，子目录是患者文件夹
    maskdir = 'C:/Users/dell/Desktop/dataset/masks'     # 同上

    rootdir = 'C:/Users/dell/Desktop/dataset' # csv文件，images,masks的主目录
    GenerateTiffCSV(rootdir, ctdir, maskdir, trainfile)


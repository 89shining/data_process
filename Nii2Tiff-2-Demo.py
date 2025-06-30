"""
提取2D切片
"""

import pydicom
import os
import numpy as np
import SimpleITK as sitk
from PIL import Image
import nibabel as nib


def GetSubDirs(currentpath):
    subdir = []
    nStop = 0
    for root, dirs, files in os.walk(currentpath):

        for patient in dirs:
            subdir.append(patient)

        nStop = nStop + 1
        if nStop > 0:
            break
    return subdir


def GetFilesinFolder(file_path):

    allfiles = []
    for root, dirs, files in os.walk(file_path):

        for item in files:
            tmppath = root.replace('\\', '/') + '/' + item
            allfiles.append(tmppath)

    return allfiles


def SaveMatPNG(mat, img_path):
    mode = 'L'
    im = Image.fromarray(mat.astype(np.uint8), mode)
    im.save(img_path)


def SaveMatTiff(ima, img_path):
    im = Image.fromarray(ima.astype(np.float32))
    im.save(img_path)


def SitkNII(filename):
    tima = sitk.ReadImage(filename)
    tdata = sitk.GetArrayFromImage(tima)
    return tdata


def NibabelNII(filename):

    nifti_img = nib.load(filename)

    # 获取图像数据
    image_data = nifti_img.get_fdata()
    return image_data


if __name__ == "__main__":

    srcdir = 'C:/Users/dell/Desktop/test46/test_1'
    imadir = 'C:/Users/dell/Desktop/test46/single_img'
    maskdir = 'C:/Users/dell/Desktop/test46/single_mask'

    palist = GetSubDirs(srcdir)
    for pa in palist:
        print(pa)
        padir = srcdir + '/' + pa

        ctfile = padir + '/image.nii.gz'
        tdata = SitkNII(ctfile)
        nslice = tdata.shape[0]

        dstdir = imadir + '/' + pa
        if not os.path.exists(dstdir):
            os.mkdir(dstdir)

        for ni in range(0, nslice):
            tmpslice = tdata[ni, ...]
            tmpfile = dstdir + '/' + str(ni) + '.tiff'
            SaveMatTiff(tmpslice, tmpfile)

        maskfile = padir + '/GTVp.nii.gz'
        tdata = SitkNII(maskfile)
        print(np.max(tdata))
        tdata = tdata * 255
        nslice = tdata.shape[0]

        dstdir = maskdir + '/' + pa
        if not os.path.exists(dstdir):
            os.mkdir(dstdir)

        for ni in range(0, nslice):
            tmpslice = tdata[ni, ...]
            tmpfile = dstdir + '/' + str(ni) + '.png'
            SaveMatPNG(tmpslice, tmpfile)


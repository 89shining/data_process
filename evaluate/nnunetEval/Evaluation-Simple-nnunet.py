import numpy as np
import os
import SimpleITK as sitk

# 评价标准 DICE

# added on 20/12/1
def GetSubFolders(file_dir):
    subfolder = []
    nStop = 0
    for root, dirs, files in os.walk(file_dir):

        for item in dirs:
            subfolder.append(item)

        nStop = 1
        if nStop > 0:
            break

    return subfolder


def GetFileList(file_dir, suffix):
    imaFiles = []

    nStop = 0
    for root, dirs, files in os.walk(file_dir):

        for item in files:
            if suffix in item.lower():
                test_file = file_dir + '/' + item
                imaFiles.append(test_file)

        nStop = 1
        if nStop > 0:
            break

    return imaFiles

def DiceCoefficient(a, b):
    """dice coefficient 2nt/na + nb."""
    # SMOOTH = 1e-5
    SMOOTH = 1e-5
    a = a > 0.5
    b = b > 0.5
    intersection = np.sum(np.logical_and(a, b))
    return (2. * intersection + SMOOTH) / (np.sum(a) + np.sum(b) + SMOOTH)


def GetFilesInFolder(file_dir, suffix):
    file_list = []
    nStop = 0
    for root, dirs, files in os.walk(file_dir):

        for item in files:
            if suffix in item.lower():
                file_list.append(item)
        nStop = 1
        if nStop > 0:
            break

    return file_list


def ComputeDSCVolume(gtDir, predDir):
    gtVolume = sitk.GetArrayFromImage(sitk.ReadImage(gtDir))
    predVolume = sitk.GetArrayFromImage(sitk.ReadImage(predDir))
    gtVolume[gtVolume>0]=1
    predVolume[predVolume>0]=1

    # file_list = GetFileList(predDir, '.png')
    # dice = 0.0
    # iNum = 0
    #
    # predVolume = []
    # gtVolume = []
    # for filename in file_list:
    #     from scipy.misc import imread
    #     predMat = imread(filename, mode='L')
    #     predMat[np.where(predMat > 0)] = 1
    #
    #     filename = filename.replace(predDir, gtDir)
    #     gtMat = imread(filename, mode='L')
    #     gtMat[np.where(gtMat > 0)] = 1
    #
    #     predVolume.append(predMat)
    #     gtVolume.append(gtMat)



    predVolume = np.array(predVolume)
    gtVolume = np.array(gtVolume)
    dice = DiceCoefficient(predVolume, gtVolume)
    return dice


def ComputeDSC2D(gtDir, predDir):
    gtVolume = sitk.GetArrayFromImage(sitk.ReadImage(gtDir))
    predVolume = sitk.GetArrayFromImage(sitk.ReadImage(predDir))

    # file_list = GetFileList(predDir, '.png')

    dice = 0.0
    iNum = 0
    for i in range(predVolume.shape[0]):
        predMat = predVolume[i]
        predMat[np.where(predMat > 0)] = 1
        gtMat = gtVolume[i]
        gtMat[np.where(gtMat > 0)] = 1
        iNum += 1
        dice += DiceCoefficient(predMat, gtMat)

    if iNum == 0:
        return 0
    dice = dice / iNum
    return dice


if __name__ == "__main__":
    import csv

    # organlist = ['ctv','gtv']

    organlist =["CTV"]
    # gtDir = 'E:/multi-time/mask-1'
    # predDir = 'E:/multi-time/Tumor-1min/mask-1'
    # filename = 'E:/multi-time/result-1min.csv'

    # gtDir = 'E:/multi-time/mask-3'
    # predDir = 'E:/multi-time/Tumor-3min/mask-3'
    # filename = 'E:/multi-time/result-3min.csv'

    # gtDir = r'F:\Challenge\Dataset001_Rectum\labelsTr'
    gtDir = r'F:\Challenge\Dataset001_Rectum\labelsTs'
    # predDir = '/data1/zhangyimeng/3dmodelBDSZ/resultsCrop'
    predDir = r'F:\Challenge\Dataset001_Rectum\testResult'
    # filename = 'F:/Challenge/3dmodelRectumCTV/Unet_Dice.csv'


    # gtDir = 'E:/Zym/prancreas/data/mask'
    # predDir = 'E:/Zym/prancreas/Result-All/mask'
    # filename = 'E:/Zym/prancreas/Result-All/result11.csv'

    #
    # gtDir = 'E:/multi-time/mask-10'
    # predDir = 'E:/multi-time/Tumor-10min/mask-10'
    # filename = 'E:/multi-time/result-10min.csv'
    #
    # gtDir = 'E:/multi-time/mask-18'
    # predDir = 'E:/multi-time/Tumor-18min/mask-18'
    # filename = 'E:/multi-time/result-18min.csv'
    #
    # gtDir = 'E:/multi-time/mask-20'
    # predDir = 'E:/multi-time/Tumor-20min/mask-20'
    # filename = 'E:/multi-time/result-20min.csv'

    # ftest = open(filename, 'w', newline='')
    # csv_test = csv.writer(ftest, dialect='excel')
    # traininfo = []
    # traininfo.append('PatientID')
    # traininfo.append('OrganName')
    # traininfo.append('2D DSC')
    # traininfo.append('3D DSC')
    # csv_test.writerow(traininfo)
    #
    all2D = []
    all3D = []
    #
    # mean2D = {}
    # mean3D = {}
    #
    # Dice2D = {}
    # Dice3D = {}
    # for organ in organlist:
    #     Dice2D[organ] = []
    #     Dice3D[organ] = []

    palist = os.listdir(predDir)
    print(palist)
    for pa in palist:
        print("pa",pa)
        # traininfo = []
        # traininfo.append(str(pa))
        # print("traininfo",traininfo)
        # for organ in organlist:
        tmpPred = predDir + '/' + pa + '/CTV.nii.gz'
        tmpGT = gtDir + '/' + pa + '/CTV.nii.gz'

        tmpPred = predDir + '/' + pa
        tmpGT = gtDir + '/' + pa

        ret2D = ComputeDSC2D(tmpGT, tmpPred)
        ret3D = ComputeDSCVolume(tmpGT, tmpPred)
        all2D.append(ret2D)
        all3D.append(ret3D)

        print(f"{pa}:(2d dice={np.round(ret2D, 3)}),(3d dice={np.round(ret3D, 3)})")

    mean2D = np.round(np.mean(all2D),3)
    mean3D = np.round(np.mean(all3D),3)

    print(f"mean:(2d dice={mean2D}),(3d dice={mean3D})")

    #
    #     traininfo.append(organ)
    #     traininfo.append(str(np.round(ret2D, 3)))
    #     traininfo.append(str(np.round(ret3D, 3)))
    #     csv_test.writerow(traininfo)
    #     traininfo = traininfo[0:1]
    #
    #     Dice2D[organ].append(np.round(ret2D, 3))
    #     Dice3D[organ].append(np.round(ret3D, 3))
    #
    #
    # # ftest.close()
    #
    # print("2D Dice")
    # print(Dice2D)
    #
    # # csv_test.writerow()
    # # 计算mean Dice
    # info = ["mean 2D"]
    #
    # info2d=[]
    # info3d=[]
    # csv_test.writerow(info)
    # for organ in organlist:
    #     mean2D[organ] =np.round(np.mean(Dice2D[organ]),3)
    #     info2d.append(organ)
    #     info2d.append(str(mean2D[organ]))
    #     csv_test.writerow(info2d)
    #     info2d.clear()
    #
    # # csv_test.writerow()
    # info = ["mean 3D"]
    # csv_test.writerow(info)
    # for organ in organlist:
    #     mean3D[organ] =np.round(np.mean(Dice3D[organ]),3)
    #     info3d.append(organ)
    #     info3d.append(str(mean3D[organ]))
    #     csv_test.writerow(info3d)
    #     info3d.clear()
    #
    # print("3D Dice")
    # print(Dice3D)
    #
    #
    #
    # print("mean 2D")
    # print(mean2D)
    # print("mean 3D")
    # print(mean3D)
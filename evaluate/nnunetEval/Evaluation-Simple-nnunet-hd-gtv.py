import numpy as np
import os
import SimpleITK as sitk
from medpy import metric
from surface_distance.metrics import compute_surface_distances, compute_robust_hausdorff, compute_average_surface_distance

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

    # gtVolume[np.where(gtVolume==1)] = 0
    # predVolume[np.where(predVolume==1)] = 0

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
        # predMat[np.where(predMat == 1)] = 0
        predMat[predMat>0]=1
        gtMat = gtVolume[i]
        # gtMat[np.where(gtMat == 1)] = 0
        gtMat[gtMat>0]=1
        iNum += 1
        dice += DiceCoefficient(predMat, gtMat)

    if iNum == 0:
        return 0
    dice = dice / iNum
    return dice


def ComputeHD952D(gtDir, predDir):
    oridata = sitk.ReadImage(gtDir)
    fColSpacing = oridata.GetSpacing()[1]
    gtVolume = sitk.GetArrayFromImage(oridata)
    predVolume = sitk.GetArrayFromImage(sitk.ReadImage(predDir))

    hdResult = []
    for i in range(predVolume.shape[0]):
        predMat = predVolume[i]
        # predMat[np.where(predMat == 1)] = 0
        predMat[predMat>0]=1
        gtMat = gtVolume[i]
        # gtMat[np.where(gtMat == 1)] = 0
        gtMat[gtMat>0]=1

        if np.max(gtMat) > 0 and np.max(predMat) > 0:
            hdcoeff = metric.binary.hd95(predMat, gtMat) * fColSpacing
            hdResult.append(hdcoeff)

    result = np.mean(hdResult)
    return result

def CalHausdorfDistance3D(gtDir, predDir):
    oridata = sitk.ReadImage(gtDir)
    spacing_3D =[oridata.GetSpacing()[2],oridata.GetSpacing()[0],oridata.GetSpacing()[1]]
    gtVolume = sitk.GetArrayFromImage(oridata)
    predVolume = sitk.GetArrayFromImage(sitk.ReadImage(predDir))

    gt = np.array(gtVolume)
    # gt[np.where(gt==1)] = 0
    gt[gt>0]=1
    gt = gt > 0
    pred = np.array(predVolume)
    # pred[np.where(pred==1)] = 0
    pred[pred>0]=1
    pred = pred > 0

    surface_distances = compute_surface_distances(gt, pred, spacing_mm=spacing_3D)
    hd_dist_95 = compute_robust_hausdorff(surface_distances, 95)
    return hd_dist_95


def CalSurfaceDistance3D(gtDir, predDir):
    oridata = sitk.ReadImage(gtDir)
    spacing_3D = [oridata.GetSpacing()[2], oridata.GetSpacing()[0], oridata.GetSpacing()[1]]
    gtVolume = sitk.GetArrayFromImage(oridata)
    predVolume = sitk.GetArrayFromImage(sitk.ReadImage(predDir))

    # gt = np.array(gt3D)
    # gt = gt > 0
    # pred = np.array(pred3D)
    # pred = pred > 0
    gt = np.array(gtVolume)
    # gt[np.where(gt == 1)] = 0
    gt[gt > 0] = 1
    gt = gt > 0
    pred = np.array(predVolume)
    # pred[np.where(pred == 1)] = 0
    pred[pred > 0] = 1
    pred = pred > 0


    surface_distances = compute_surface_distances(gt, pred, spacing_mm=spacing_3D)
    # avg_surf_dist有两个参数，第一个参数是average_distance_gt_to_pred，第二个参数是average_distance_pred_to_gt
    surf_dist = compute_average_surface_distance(surface_distances)
    avg_surf_dist = (surf_dist[0] + surf_dist[1]) / 2
    return avg_surf_dist














if __name__ == "__main__":
    import csv
    import re

    # organlist = ['ctv','gtv']

    organlist =["tumor"]
    # gtDir = 'E:/multi-time/mask-1'
    # predDir = 'E:/multi-time/Tumor-1min/mask-1'
    # filename = 'E:/multi-time/result-1min.csv'

    # gtDir = 'E:/multi-time/mask-3'
    # predDir = 'E:/multi-time/Tumor-3min/mask-3'
    # filename = 'E:/multi-time/result-3min.csv'

    # gtDir = r'F:\Challenge\Dataset001_Rectum\labelsTr'
    gtDir = r'D:\eso_XJH\T-260716\TestResults\labelsTs_4'
    # gtDir = r'F:\Challenge\Dataset001_Rectum\labelsTs100'
    # predDir = '/data1/zhangyimeng/3dmodelBDSZ/resultsCrop'
    # predDir = r'F:\LITS\LITS\result_nnunet3d_liverprompt'
    predDir = r'D:\eso_XJH\T-260716\TestResults\Eso_fine4_pixel'
    # filename = 'F:/Challenge/3dmodelRectumCTV/Unet_Dice.csv'

    #
    all2D = []
    all3D = []
    allhd95_2d = []
    allhd95_3d = []
    allasd_3d = []
    csv_rows = []
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
        # tmpPred = predDir + '/' + pa + '/CTV.nii.gz'
        # tmpGT = gtDir + '/' + pa + '/CTV.nii.gz'

        tmpPred = predDir + '/' + pa
        name = pa

        tmpGT = gtDir + '/' + name

        ret2D = ComputeDSC2D(tmpGT, tmpPred)
        ret3D = ComputeDSCVolume(tmpGT, tmpPred)
        hd95_2d = ComputeHD952D(tmpGT, tmpPred)
        hd95_3d = CalHausdorfDistance3D(tmpGT, tmpPred)
        asd_3d = CalSurfaceDistance3D(tmpGT, tmpPred)

        number_groups = re.findall(r"\d+", pa)
        if not number_groups:
            raise ValueError(f"无法从文件名中提取患者编号: {pa}")
        patient_id = f"p_{number_groups[-1][-2:].zfill(2)}"

        all2D.append(ret2D)
        all3D.append(ret3D)
        allhd95_2d.append(hd95_2d)
        allhd95_3d.append(hd95_3d)
        allasd_3d.append(asd_3d)

        csv_rows.append([
            patient_id,
            np.round(ret2D, 4),
            np.round(ret3D, 4),
            np.round(hd95_2d, 4),
            np.round(hd95_3d, 4),
            np.round(asd_3d, 4),
        ])

        print(f"{pa}:(2d dice={np.round(ret2D, 4)}),(3d dice={np.round(ret3D, 4)}),(hd95_2d={np.round(hd95_2d, 4),}),(hd95_3d={np.round(hd95_3d, 4)}),(asd_3d={np.round(asd_3d, 4)})")

    mean2D = np.round(np.mean(all2D),4)
    mean3D = np.round(np.mean(all3D),4)
    meanhd95_2d = np.round(np.mean(allhd95_2d),4)
    meanhd95_3d = np.round(np.mean(allhd95_3d),4)
    meanasd_3d = np.round(np.mean(allasd_3d),4)

    print(f"mean:(2d dice={mean2D}),(3d dice={mean3D}),(hd95_2d={meanhd95_2d}),(hd95_3d={meanhd95_3d}),(asd_3d={meanasd_3d})")

    csv_rows.append([
        "mean", mean2D, mean3D, meanhd95_2d, meanhd95_3d, meanasd_3d
    ])
    csv_filename = f"evaluation_gtv_{os.path.basename(os.path.normpath(predDir))}.csv"
    csv_path = os.path.join(os.path.dirname(os.path.normpath(predDir)), csv_filename)
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            "patient_id", "dice_2d", "dice_3d",
            "hd95_2d_mm", "hd95_3d_mm", "asd_3d_mm"
        ])
        csv_writer.writerows(csv_rows)
    print(f"CSV saved to: {csv_path}")

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

import numpy as np
import os
import pydicom
from medpy import metric
from surface_distance.metrics import compute_surface_distances, compute_robust_hausdorff, compute_average_surface_distance
import SimpleITK as sitk


# 95%Hausdorff distance 豪斯多夫距离
def CalHausdorfDistance3D(gt3D, pred3D, spacing_3D):

    gt = np.array(gt3D)
    gt = gt > 0
    pred = np.array(pred3D)
    pred = pred > 0

    surface_distances = compute_surface_distances(gt, pred, spacing_mm=spacing_3D)
    hd_dist_95 = compute_robust_hausdorff(surface_distances, 95)
    return hd_dist_95


# Average surface distance 平均表面距离
def CalSurfaceDistance3D(gt3D, pred3D, spacing_3D):

    gt = np.array(gt3D)
    gt = gt > 0
    pred = np.array(pred3D)
    pred = pred > 0
    surface_distances = compute_surface_distances(gt, pred, spacing_mm=spacing_3D)
    # avg_surf_dist有两个参数，第一个参数是average_distance_gt_to_pred，第二个参数是average_distance_pred_to_gt
    surf_dist = compute_average_surface_distance(surface_distances)
    avg_surf_dist = (surf_dist[0] + surf_dist[1]) / 2
    return avg_surf_dist


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


def LoadPNGMask(pngDir, organList):

    # compare the test results and ground truth, there is no test part
    maskDict = {}
    for organ in organList:
        srcDir = pngDir + '/' + organ

        allSlice = []
        fiList = GetFileList(srcDir, '.png')
        nFile = len(fiList)
        for ni in range(0, nFile):
            from scipy.misc import imread
            filename = srcDir + '/' + str(ni) + '.png'
            mask = imread(filename, mode='L')
            mask = np.array(mask).astype(np.uint8)
            allSlice.append(mask)

        maskDict[organ] = np.array(allSlice)
    return maskDict


def LoadNiiMask(niiDir,organList):
    maskDict = {}
    for organ in organList:
        srcDir = niiDir + '/' + organ
        gtVolume = sitk.GetArrayFromImage(sitk.ReadImage(srcDir + '.nii.gz'))
        maskDict[organ] = np.array(gtVolume)
    return maskDict



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


def SeperateModalityN(dcmdir):
    filist = GetFileList(dcmdir, '.dcm')
    patientInfo = {}
    patientInfo['ct'] = []
    patientInfo['mr'] = []

    for fi in filist:
        ds = pydicom.dcmread(fi)
        if 'mr' in ds.Modality.lower():
            patientInfo['mr'].append(fi)
        elif 'ct' in ds.Modality.lower():
            patientInfo['ct'].append(fi)
        else:
            continue
    return patientInfo


def MyLoadDCM(dcmDir, modality):
    """Get the data of the selected patient from the DICOM importer dialog."""
    patientInfo = SeperateModalityN(dcmDir)
    filearray = patientInfo[modality]
    patient = []
    # print('Importing patient. Please wait...')
    imaposx = []
    imaposy = []
    imaposz = []

    for n in range(0, len(filearray)):
        dcmfile = filearray[n]
        # if '.dcm' in dcmfile.lower():
        ds = pydicom.dcmread(dcmfile, defer_size=100, stop_before_pixels=True, force=True)

        modalityinfo = ds.get("Modality")
        if modalityinfo in ['RTPLAN', 'RTDOSE', 'RTSTRUCT']:
            continue

        if (modalityinfo in ['CT', 'MR']):
            patient.append(ds)
            imaposx.append(np.float32(ds.get('ImagePositionPatient')[0]))
            imaposy.append(np.float32(ds.get('ImagePositionPatient')[1]))
            imaposz.append(np.float32(ds.get('ImagePositionPatient')[2]))

    imaposx = np.array(imaposx)
    imaposy = np.array(imaposy)
    imaposz = np.array(imaposz)

    diffx = np.max(imaposx) - np.min(imaposx)
    diffy = np.max(imaposy) - np.min(imaposy)
    diffz = np.max(imaposz) - np.min(imaposz)

    if diffz > diffx:
        if diffz > diffy:
            checkpos = imaposz
        else:
            checkpos = imaposy
    else:
        if diffx > diffy:
            checkpos = imaposx
        else:
            checkpos = imaposy

    sortedidx = np.argsort(checkpos)
    sortedima = []
    for idx in sortedidx:
        sortedima.append(patient[idx])
    # Save the images back to the patient dictionary
    dcmlist = sortedima
    # print('Importing patient complete.')
    return dcmlist


def GetTagInfo(dcmlist):
    xspacing = np.float(dcmlist[0].PixelSpacing[0])
    yspacing = np.float(dcmlist[0].PixelSpacing[1])
    imapos0 = np.array(dcmlist[0].ImagePositionPatient)
    nSlice = len(dcmlist)
    imapos1 = np.array(dcmlist[nSlice-1].ImagePositionPatient)
    posdiff = imapos1 - imapos0
    zspacing = np.sum(posdiff ** 2) ** 0.5 / (nSlice - 1)
    spacingvec = np.array([zspacing, yspacing, xspacing])
    return spacingvec


def MeanHD953D(gtDir, predDir, dcmDir, modality, OrganNames):

    # compare the test results and ground truth, there is no test part
    hdDict = {}
    for organ in OrganNames:
        hdDict[organ] = []

    patientName = GetSubFolders(predDir)
    for p in patientName:

        tmpDcm = dcmDir + '/' + p
        dcmlist = MyLoadDCM(tmpDcm, modality)
        spacingvec = GetTagInfo(dcmlist)

        gtPath = gtDir + '/' + p
        gtMaskDict = LoadNiiMask(gtPath, OrganNames)

        predPath = predDir + '/' + p
        predMaskDict = LoadNiiMask(predPath, OrganNames)

        for organ in OrganNames:
            tmpHD = CalHausdorfDistance3D(gtMaskDict[organ], predMaskDict[organ], spacingvec)
            hdDict[organ].append(tmpHD)

    resultDictDSC = {}
    for organ in OrganNames:
        print(organ)
        tmpvec = np.array(hdDict[organ])
        print(tmpvec)
        resultDictDSC[organ] = {}
        resultDictDSC[organ]['mean'] = np.mean(tmpvec)
        print('mean:' + str(resultDictDSC[organ]['mean']))
        resultDictDSC[organ]['std'] = np.std(tmpvec)
        print('std:' + str(resultDictDSC[organ]['std']))
    return resultDictDSC


def MeanASD3D(gtDir, predDir, dcmDir, modality, OrganNames):
    asdDict = {}
    for organ in OrganNames:
        asdDict[organ] = []

    patientName = GetSubFolders(predDir)
    for p in patientName:

        tmpDcm = dcmDir + '/' + p
        dcmlist = MyLoadDCM(tmpDcm, modality)
        spacingvec = GetTagInfo(dcmlist)

        gtPath = gtDir + '/' + p
        gtMaskDict = LoadNiiMask(gtPath, OrganNames)

        predPath = predDir + '/' + p
        predMaskDict = LoadNiiMask(predPath, OrganNames)

        for organ in OrganNames:
            tmpASD = CalSurfaceDistance3D(gtMaskDict[organ], predMaskDict[organ], spacingvec)
            asdDict[organ].append(tmpASD)

    resultDictASD = {}
    for organ in OrganNames:
        print(organ)
        tmpvec = np.array(asdDict[organ])
        print(tmpvec)
        resultDictASD[organ] = {}
        resultDictASD[organ]['mean'] = np.mean(tmpvec)
        print('mean:' + str(resultDictASD[organ]['mean']))
        resultDictASD[organ]['std'] = np.std(tmpvec)
        print('std:' + str(resultDictASD[organ]['std']))
    return resultDictASD


if __name__ == "__main__":
    # OrganNames = ['Bladder-lxy', 'Bone Marrow-lxy', 'Bowel Bag-lxy', 'Femoral Head L-lxy',
    #               'Femoral Head R-lxy', 'Kidney L-lxy', 'Kidney R-lxy', 'Rectum-lxy']
    # OrganNames = ['ctv2']
    OrganNames = ["bz_vm_over", "im","sm"]
    # OrganNames = ['Bladder-lxy', 'Bone Marrow-lxy', 'Bowel Bag-lxy', 'Femoral Head L-lxy',
    #               'Femoral Head R-lxy', 'Kidney L-lxy', 'Kidney R-lxy', 'Rectum-lxy']

    modality = 'ct'

    # dcmDir = 'E:/BZ22/mr rectum/test221109/dcm'
    # gtDir = 'E:/BZ22/mr rectum/test221109/CT-mask'
    # predDir = 'E:/BZ22/mr rectum/test221109/CT-Result/MRCT'
    # gtDir = 'E:/Zym/ESO_CTV/data/gt'
    # predDir = 'E:/Zym/ESO_CTV/test_rtmind5mm_new'
    # dcmDir = 'E:/Zym/ESO_CTV/testdata_dcm'

    # predDir = r"F:\fujian_GTV\data\fujian_all_ctv2_exp01_test\fujian_ctv2_exp01\mask_png_genzhi_gt"
    # gtDir = r"F:\fujian_GTV\data\testdataGENZHI\mask_png_genzhi_gt"

    gtDir = 'F:/BDSZ/3dData/NiiData/newGT'
    predDir = 'F:/BDSZ/resultsResUnet'
    dcmDir = 'E:/yzyProject/BeidaShenzhen/testDCM'



    print('test patient:')
    patientName = GetSubFolders(predDir)
    for p in patientName:
        print(p)

    print('3D HD95 Results:')
    ret = MeanHD953D(gtDir, predDir, dcmDir, modality, OrganNames)

    print('3D ASD Results:')
    ret = MeanASD3D(gtDir, predDir, dcmDir, modality, OrganNames)



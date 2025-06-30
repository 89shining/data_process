# 生成CSV文件
# 分训练集和测试集

from __future__ import division
from PIL import Image
import os

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


def GetFilesWithSuffix(file_dir, suffix):
    filelist = []
    nStop = 0
    for root, dirs, files in os.walk(file_dir):

        for item in files:
            if suffix.lower() in item.lower():
                filelist.append(item)

        nStop = 1
        if nStop > 0:
            break

    return filelist


def TrainList(rootDir, rootdatadir, rootmaskdir, trainSavePath):

    patient_list = GetSubFolders(rootdatadir)

    import csv
    f = open(trainSavePath, 'w', newline='')
    csv_write = csv.writer(f, dialect='excel')
    for pa in patient_list:
        print(pa)
        datapath = rootdatadir + '/' + pa
        maskpath = rootmaskdir + '/' + pa
        maskpath = maskpath.replace(rootDir, '')
        filelist = GetFilesWithSuffix(datapath, '.tiff')


        for j in range(len(filelist)):
            tmpline = []
            filename = datapath + '/' + filelist[j]
            fileinfo = filename.replace(rootDir, '')
            tmpline.append(fileinfo)
            tmpline.append(maskpath)
            csv_write.writerow(tmpline)

    f.close()


def TrainList2(rootDir, validpalist, rootdatadir, rootmaskdir, trainFile, testFile):

    nValid = len(validpalist)
    patient_list = GetSubFolders(rootdatadir)

    import csv
    f_train = open(trainFile, 'w', newline='')
    csv_train = csv.writer(f_train, dialect='excel')

    f_test = open(testFile, 'w', newline='')
    csv_test = csv.writer(f_test, dialect='excel')
    nID = 0
    for pa in patient_list:

        if nValid > 0 and (pa in validpalist):
            nID = nID + 1
            datapath = rootdatadir + '/' + pa
            maskpath = rootmaskdir + '/' + pa
            maskpath = maskpath.replace(rootDir, '')
            filelist = GetFilesWithSuffix(datapath, '.tiff')

            for j in range(len(filelist)):
                tmpline = []
                filename = datapath + '/' + filelist[j]
                fileinfo = filename.replace(rootDir, '')
                tmpline.append(fileinfo)
                tmpline.append(maskpath)
                if nID % 10 == 1:
                    csv_test.writerow(tmpline)
                else:
                    csv_train.writerow(tmpline)
        elif nValid == 0:
            nID = nID + 1
            datapath = rootdatadir + '/' + pa
            maskpath = rootmaskdir + '/' + pa
            maskpath = maskpath.replace(rootDir, '')
            filelist = GetFilesWithSuffix(datapath, '.tiff')

            for j in range(len(filelist)):
                tmpline = []
                filename = datapath + '/' + filelist[j]
                fileinfo = filename.replace(rootDir, '')
                tmpline.append(fileinfo)
                tmpline.append(maskpath)
                if nID % 10 == 1:
                    csv_test.writerow(tmpline)
                else:
                    csv_train.writerow(tmpline)

    f_train.close()
    f_test.close()

if __name__ == "__main__":

    # tmpDir = 'E:/internship/Lisenlin-3tube/3tube/dcm/空心'
    # validlist = GetSubFolders(tmpDir)
    validlist = []

    rootDir = "C:/Users/dell/Desktop/test46"
    dataDir = "C:/Users/dell/Desktop/test46/single_img"
    maskDir = "C:/Users/dell/Desktop/test46/single-mask"
    trainFile = "C:/Users/dell/Desktop/test46/Train_all.csv"
    testFile = "C:/Users/dell/Desktop/test46/Test_all.csv"

    TrainList2(rootDir, validlist, dataDir, maskDir, trainFile, testFile)


    # rootDir = "E:/zhuqizhen"
    # dataDir = "E:/zhuqizhen/ima"
    # maskDir = "E:/zhuqizhen/mask"
    # saveFile = "E:/zhuqizhen/Train_list11.csv"
    #
    # TrainList(rootDir, dataDir, maskDir, saveFile)

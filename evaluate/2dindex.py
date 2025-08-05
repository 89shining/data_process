"""
计算GT和pred均>0的切片
"""


import numpy as np
import os
import SimpleITK as sitk
from medpy import metric
import pandas as pd

def DiceCoefficient(a, b):
    """dice coefficient 2nt/na + nb."""
    SMOOTH = 1e-5
    a = a > 0.5
    b = b > 0.5
    intersection = np.sum(np.logical_and(a, b))
    return (2. * intersection + SMOOTH) / (np.sum(a) + np.sum(b) + SMOOTH)

def ComputeDSC2D(gtDir, predDir):
    gtVolume = sitk.GetArrayFromImage(sitk.ReadImage(gtDir))
    predVolume = sitk.GetArrayFromImage(sitk.ReadImage(predDir))
    dice = 0.0
    iNum = 0
    for i in range(predVolume.shape[0]):
        gtMat = gtVolume[i]
        predMat = predVolume[i]

        if np.max(gtMat) == 0 or np.max(predMat) == 0:
            continue  # 跳过空结构的切片

        gtMat[gtMat > 0] = 1
        predMat[predMat > 0] = 1

        dice += DiceCoefficient(predMat, gtMat)
        iNum += 1
    if iNum == 0:
        return 0
    dice = dice / iNum
    return dice

def ComputeHD95(gtDir, predDir):
    oridata = sitk.ReadImage(gtDir)
    fColSpacing = oridata.GetSpacing()[1]
    gtVolume = sitk.GetArrayFromImage(oridata)
    predVolume = sitk.GetArrayFromImage(sitk.ReadImage(predDir))

    hdResult = []
    for i in range(predVolume.shape[0]):
        predMat = predVolume[i]
        predMat[np.where(predMat > 0)] = 1
        gtMat = gtVolume[i]
        gtMat[np.where(gtMat > 0)] = 1

        if np.max(gtMat) > 0 and np.max(predMat) > 0:
            try:
                hdcoeff = metric.binary.hd95(predMat, gtMat) * fColSpacing
                hdResult.append(hdcoeff)
            except:
                pass

    result = np.mean(hdResult)
    return result

def evaluate_model_to_excel(gtDir, predDir, model_name, excel_path):
    """
       将某个模型的 2D Dice 和 HD95 评估写入 Excel 的一个 sheet
       """
    print(f"\n📊 正在评估模型: {model_name}")
    ids, dices, hd95s = [], [], []

    palist = [f for f in os.listdir(predDir) if f.endswith('.nii.gz')]
    for pa in palist:
        pred_path = os.path.join(predDir, pa)
        gt_path = os.path.join(gtDir, pa)

        dice = ComputeDSC2D(gt_path, pred_path)
        hd95 = ComputeHD95(gt_path, pred_path)

        patient_num = int(pa.split('_')[-1].split('.')[0])
        patient_id = f"p_{patient_num}"

        ids.append(patient_id)
        dices.append(dice)
        hd95s.append(hd95)

        print(f"  {patient_id}: Dice={np.round(dice, 2)}, HD95={np.round(hd95, 2)}")

    # 添加平均值
    ids.append("Mean")
    dices.append(np.mean(dices))
    hd95s.append(np.mean(hd95s))

    df = pd.DataFrame({
        'ID': ids,
        '2D DSC': np.round(dices, 2),
        '2D HD95': np.round(hd95s, 2)
    })

    # 写入 Excel，追加 sheet
    with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a' if os.path.exists(excel_path) else 'w') as writer:
        df.to_excel(writer, index=False, sheet_name=model_name)

    print(f"写入完成 → Sheet: {model_name}")

if __name__ == "__main__":
    # GT文件目录
    gtDir = r'C:\Users\dell\Desktop\20250711\nnUNet\Dataset001_GTVp\labelsTs'
    # excel文件保存地址
    excel_path = r'C:\Users\dell\Desktop/2D_eval.xlsx'
    # 模型及其预测路径配置
    model_paths = {
        # "nnUNet_3d": r'C:\Users\dell\Desktop\testresults\nnUNet_3d',
        "SAM_trainall_pseudorgb_0p": r'C:\Users\dell\Desktop\testresults\TrainAll_pseudoRGB/expand_0p',
        "SAM_trainall_pseudorgb_3p": r'C:\Users\dell\Desktop\testresults\TrainAll_pseudoRGB/expand_3p',
        "SAM_trainall_pseudorgb_5p": r'C:\Users\dell\Desktop\testresults\TrainAll_pseudoRGB/expand_5p',
        "SAM_trainall_pseudorgb_7p": r'C:\Users\dell\Desktop\testresults\TrainAll_pseudoRGB/expand_7p',
        "SAM_trainall_pseudorgb_9p": r'C:\Users\dell\Desktop\testresults\TrainAll_pseudoRGB/expand_9p'
    }
    # 依次写入每个模型评估结果
    for model_name, predDir in model_paths.items():
        evaluate_model_to_excel(gtDir, predDir, model_name, excel_path)

    print(f"\n 所有模型评估完成，结果保存在：{excel_path}")



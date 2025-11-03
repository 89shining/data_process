"""
批量输出dicom文件的spacing和size
"""

import os
import SimpleITK as sitk
import csv

def get_dicom_info(dicom_folder):
    """读取单个病人的 DICOM 序列，返回 spacing 和 size"""
    try:
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(dicom_folder)
        if not dicom_names:
            return None, None
        reader.SetFileNames(dicom_names)
        image = reader.Execute()
        spacing = image.GetSpacing()  # (x, y, z)
        size = image.GetSize()        # (x, y, z)
        return spacing, size
    except Exception as e:
        print(f"[错误] {dicom_folder}: {e}")
        return None, None

# ===== 主程序 =====
root_dir = r"C:\Users\dell\Desktop\SAM\GTVp_CTonly\rawdata_80例\testrawdata"   # ← 修改为你的A文件夹路径

results = []
for patient_folder in sorted(os.listdir(root_dir)):
    patient_path = os.path.join(root_dir, patient_folder)
    if not os.path.isdir(patient_path):
        continue

    spacing, size = get_dicom_info(patient_path)
    if spacing and size:
        print(f"{patient_folder}: spacing = {spacing}, size = {size}")
        results.append((patient_folder, *spacing, *size))
    else:
        print(f"{patient_folder}: 未能读取 DICOM 信息")

# ===== 保存结果到 CSV =====
save_path = os.path.join(root_dir, "dicom_info_summary.csv")
with open(save_path, "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        "Patient_ID",
        "Spacing_X(mm)", "Spacing_Y(mm)", "Spacing_Z(mm)",
        "Size_X", "Size_Y", "Size_Z"
    ])
    for row in results:
        writer.writerow(row)

print(f"\n✅ 统计完成，共 {len(results)} 个患者，结果已保存到：{save_path}")

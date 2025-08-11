"""
检查RS文件下的ROI信息
"""

import os
import pydicom
from rt_utils import RTStructBuilder

def list_all_roi_names_in_folder(root_dir):
    """
    扫描每个患者文件夹，打印每个RTSTRUCT文件中的所有ROI名称
    """
    for patient in sorted(os.listdir(root_dir)):
        patient_path = os.path.join(root_dir, patient)
        if not os.path.isdir(patient_path):
            continue

        for file in os.listdir(patient_path):
            file_path = os.path.join(patient_path, file)
            try:
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                if ds.Modality == "RTSTRUCT":
                    print(f"\n📁 患者目录：{patient}")
                    print(f"  📄 RTSTRUCT文件：{file}")

                    # 尝试加载结构信息
                    rtstruct = RTStructBuilder.create_from(dicom_series_path=patient_path, rt_struct_path=file_path)
                    roi_names = rtstruct.get_roi_names()
                    for roi in roi_names:
                        print(f"    └─ ROI: {roi}")
            except Exception as e:
                continue

# 示例调用
list_all_roi_names_in_folder("C:/Users/WS/Desktop/GTVp_MRI/rawdata")

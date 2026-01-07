"""
检查DICOM中是否有该ROI名称
"""

import os
import pydicom
from rt_utils import RTStructBuilder


def get_rtstruct_path(pa_path):
    """找到患者目录下的 RTSTRUCT 文件"""
    for file in os.listdir(pa_path):
        file_path = os.path.join(pa_path, file)
        try:
            ds = pydicom.dcmread(file_path, stop_before_pixels=True)
            if ds.get("Modality", "").upper() == "RTSTRUCT":
                return file_path
        except:
            continue
    return None


def check_roi_in_patient(pa_path, roi_name, missing_list):
    """检查某个患者 RTSTRUCT 中是否存在指定 ROI"""
    rts_path = get_rtstruct_path(pa_path)
    patient_name = os.path.basename(pa_path)

    if rts_path is None:
        print(f"[NO RTSTRUCT] {patient_name}")
        missing_list.append(patient_name)
        return

    try:
        rtstruct = RTStructBuilder.create_from(
            dicom_series_path=pa_path,
            rt_struct_path=rts_path
        )
        roi_names = rtstruct.get_roi_names()
    except Exception as e:
        print(f"[ERROR] {patient_name}  failed to read RTSTRUCT: {e}")
        missing_list.append(patient_name)
        return

    if roi_name in roi_names:
        print(f"[OK]   {patient_name}  -> contains ROI: {roi_name}")
    else:
        print(f"[MISS] {patient_name}  -> does NOT contain ROI: {roi_name}")
        print(f"       Available ROIs: {roi_names}")
        missing_list.append(patient_name)


if __name__ == "__main__":
    root_dir = r"C:\Users\dell\Desktop\Eso-CTV\Rawdata"
    roi_name = "Heart"

    missing_patients = []

    for pa in sorted(os.listdir(root_dir)):
        pa_path = os.path.join(root_dir, pa)
        if os.path.isdir(pa_path):
            check_roi_in_patient(pa_path, roi_name, missing_patients)

    # ===== 最后汇总打印 =====
    print("\n========== ROI MISSING SUMMARY ==========")
    print(f"ROI name: {roi_name}")
    print(f"Total patients checked: {len(os.listdir(root_dir))}")
    print(f"Patients missing this ROI: {len(missing_patients)}")

    if missing_patients:
        print("Missing patient list:")
        for p in missing_patients:
            print(f"  - {p}")
    else:
        print("All patients contain this ROI.")

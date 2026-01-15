"""
同时提取多个roi
"""
import csv
import nibabel as nib
import os
import SimpleITK as sitk
import numpy as np
import pydicom
from rt_utils import RTStructBuilder

# 获取患者目录
def GetSubDirs(root_dir):
    palist = []
    for pa in os.listdir(root_dir):
        pa_path = os.path.join(root_dir, pa)
        palist.append(pa_path)
    return palist

# 单个患者文件夹路径下所有文件的完整路径，返回ct列表和rs
def GetFilesinFolder(pa_path):
    ct_files = []
    rts_dir = None
    for file in os.listdir(pa_path):
        file_path = os.path.join(pa_path, file)
        ds = pydicom.dcmread(file_path, stop_before_pixels=True)
        modality = ds.get("Modality", "").upper()
        if modality == "CT":
            ct_files.append(file_path)
        if modality == "RTSTRUCT":
            rts_dir = file_path
    return ct_files, rts_dir

# 将CT切片排序
def sort_ct_files(ct_files):
    def get_z(file_path):
        try:
            ds = pydicom.dcmread(file_path, stop_before_pixels=True)
            return float(ds.ImagePositionPatient[2])
        except:
            return 0.0
    return sorted(ct_files, key=get_z)

# 将2d CT切片转为nii.gz
def convert_image_to_nii(ct_files_sorted, image_path):
    reader = sitk.ImageSeriesReader()
    reader.SetFileNames(ct_files_sorted)
    image = reader.Execute()
    sitk.WriteImage(image, image_path)

def extract_mask(pa_path, rts_dir, mask_path, roi_name, ct_files_sorted):
    """
        尝试提取 ROI
        若不存在则返回 False
        """
    try:
        rtstruct = RTStructBuilder.create_from(
            dicom_series_path=pa_path,
            rt_struct_path=rts_dir
        )

        if roi_name not in rtstruct.get_roi_names():
            print(f"    [Skip] ROI '{roi_name}' not found.")
            return False

        mask = rtstruct.get_roi_mask_by_name(roi_name)
        # unit8
        mask = mask.astype(np.uint8).transpose(2,0,1)
        # nii.gz
        mask = sitk.GetImageFromArray(mask)
        # print(mask.GetSize())

        reader = sitk.ImageSeriesReader()
        reader.SetFileNames(ct_files_sorted)
        ct_img = reader.Execute()
        # print(ct_img.GetSize())

        # 手动赋值空间信息（而不是 CopyInformation）
        mask.SetSpacing(ct_img.GetSpacing())
        mask.SetOrigin(ct_img.GetOrigin())
        mask.SetDirection(ct_img.GetDirection())

        sitk.WriteImage(mask, mask_path)
        return True

    except Exception as e:
        print(f"    [Error] ROI '{roi_name}' extraction failed: {e}")
        return False

# # 图像方向标准化LPS方向
# def canonicalize_nifti(nifti_path):
#     img = nib.load(nifti_path)
#     img_can = nib.as_closest_canonical(img)
#     nib.save(img_can, nifti_path)


if __name__ == "__main__":

    root_dir = r"D:\SAM\Esophagus\20251217\Rawdata"
    output_dir = r"D:\SAM\Esophagus\20251217\Seperate\Nii"
    csv_path = r"D:\SAM\Esophagus\20251217\Seperate\patient_id.csv"

    # 同时提取的多个 ROI
    roi_names = [
        "CTV",
        "GTV",
        "GTVp",
        # "GTVnd",
    ]

    os.makedirs(output_dir, exist_ok=True)

    palist = sorted(GetSubDirs(root_dir))
    patient_id = []
    i = 0

    for pa in palist:
        print(f"\nProcessing: {pa}")

        ct_files, rts_dir = GetFilesinFolder(pa)
        if len(ct_files) == 0 or rts_dir is None:
            print("    [Skip] Missing CT or RTSTRUCT.")
            continue

        ct_files_sorted = sort_ct_files(ct_files)

        new_name = f"p_{i}"
        sub_path = os.path.join(output_dir, new_name)
        os.makedirs(sub_path, exist_ok=True)

        # ===== 保存 CT =====
        image_path = os.path.join(sub_path, "image.nii.gz")
        convert_image_to_nii(ct_files_sorted, image_path)

        # ===== 保存多个 ROI =====
        any_roi_saved = False
        for roi_name in roi_names:
            mask_path = os.path.join(sub_path, f"{roi_name}.nii.gz")
            success = extract_mask(
                pa_path=pa,
                rts_dir=rts_dir,
                mask_path=mask_path,
                roi_name=roi_name,
                ct_files_sorted=ct_files_sorted
            )
            any_roi_saved = any_roi_saved or success

        if not any_roi_saved:
            print("    [Warning] No ROI extracted for this patient.")

        # ===== 记录映射 =====
        original_name = os.path.basename(pa)
        patient_id.append([original_name, new_name])
        i += 1

    # ===== 保存 CSV =====
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["original_folder_name", "renamed_folder_name"])
        writer.writerows(patient_id)

    print(f"\n患者文件名映射表已保存到：{csv_path}")


















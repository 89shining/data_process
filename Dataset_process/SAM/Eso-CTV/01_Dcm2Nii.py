"""
根据 train_test_split.xlsx
1) 按 train / test 划分 raw DICOM
2) 转换为 NIfTI（沿用已验证正确的实现）
3) 生成 p_n 映射
4) 将 mapped_id 写回原 Excel（原地更新）
"""

import os
import numpy as np
import pandas as pd
import SimpleITK as sitk
import pydicom
from rt_utils import RTStructBuilder

# =========================
# 路径配置
# =========================
RAW_ROOT = r"C:\Users\dell\Desktop\Eso-CTV\Rawdata"
EXCEL_PATH = r"C:\Users\dell\Desktop\Eso-CTV\20251224\train_test_split2.xlsx"
OUT_ROOT = r"C:\Users\dell\Desktop\Eso-CTV\20251224\datanii"

ROI_NAME = "CTV"
COL_ID = "放疗号"
COL_PID = "mapped_id"

# =========================
# 你原有的函数（完全保留）
# =========================
def GetFilesinFolder(pa_path):
    ct_files = []
    rts_dir = None
    for file in os.listdir(pa_path):
        file_path = os.path.join(pa_path, file)
        ds = pydicom.dcmread(file_path, stop_before_pixels=True)
        modality = ds.get("Modality", "").upper()
        if modality == "CT":
            ct_files.append(file_path)
        elif modality == "RTSTRUCT":
            rts_dir = file_path
    return ct_files, rts_dir


def sort_ct_files(ct_files):
    def get_z(file_path):
        ds = pydicom.dcmread(file_path, stop_before_pixels=True)
        return float(ds.ImagePositionPatient[2])
    return sorted(ct_files, key=get_z)


def convert_image_to_nii(ct_files_sorted, image_path):
    reader = sitk.ImageSeriesReader()
    reader.SetFileNames(ct_files_sorted)
    image = reader.Execute()
    sitk.WriteImage(image, image_path)


def extract_mask(pa_path, rts_dir, mask_path, roi_name, ct_files_sorted):
    rtstruct = RTStructBuilder.create_from(
        dicom_series_path=pa_path,
        rt_struct_path=rts_dir
    )

    mask = rtstruct.get_roi_mask_by_name(roi_name)
    mask = mask.astype(np.uint8).transpose(2, 0, 1)

    mask_img = sitk.GetImageFromArray(mask)

    reader = sitk.ImageSeriesReader()
    reader.SetFileNames(ct_files_sorted)
    ct_img = reader.Execute()

    mask_img.SetSpacing(ct_img.GetSpacing())
    mask_img.SetOrigin(ct_img.GetOrigin())
    mask_img.SetDirection(ct_img.GetDirection())

    sitk.WriteImage(mask_img, mask_path)


# =========================
# 辅助：按放疗号找 raw 文件夹
# =========================
def find_raw_folder(raw_root, radiotherapy_id):
    radiotherapy_id = str(radiotherapy_id).strip()
    matches = []
    for name in os.listdir(raw_root):
        full = os.path.join(raw_root, name)
        if not os.path.isdir(full):
            continue
        if name.startswith(radiotherapy_id):
            matches.append(full)
    return matches


# =========================
# 主流程
# =========================
def main():
    df_train = pd.read_excel(EXCEL_PATH, sheet_name="train")
    df_test  = pd.read_excel(EXCEL_PATH, sheet_name="test")

    split_out_root = {
        "train": os.path.join(OUT_ROOT, "train_nii"),
        "test": os.path.join(OUT_ROOT, "test_nii"),
    }

    os.makedirs(split_out_root["train"], exist_ok=True)
    os.makedirs(split_out_root["test"], exist_ok=True)

    pid_counter = {"train": 0, "test": 0}

    for split, df in [("train", df_train), ("test", df_test)]:
        mapped_ids = []

        for _, row in df.iterrows():
            rid = row[COL_ID]
            matches = find_raw_folder(RAW_ROOT, rid)

            if len(matches) == 0:
                print(f"[Skip] 找不到 DICOM 文件夹：{rid}")
                mapped_ids.append("")
                continue

            pid = f"p_{pid_counter[split]}"
            pid_counter[split] += 1
            mapped_ids.append(pid)

            for pa_path in matches:
                out_dir = os.path.join(split_out_root[split], pid)
                os.makedirs(out_dir, exist_ok=True)

                ct_files, rts_dir = GetFilesinFolder(pa_path)
                ct_files_sorted = sort_ct_files(ct_files)

                convert_image_to_nii(
                    ct_files_sorted,
                    os.path.join(out_dir, "image.nii.gz")
                )
                extract_mask(
                    pa_path,
                    rts_dir,
                    os.path.join(out_dir, "CTV.nii.gz"),
                    ROI_NAME,
                    ct_files_sorted
                )

                print(f"[{split}] {os.path.basename(pa_path)} → {pid}")

        df[COL_PID] = mapped_ids

    # ===== 原地写回 Excel（只新增 mapped_id 列）=====
    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl", mode="w") as writer:
        df_train.to_excel(writer, sheet_name="train", index=False)
        df_test.to_excel(writer, sheet_name="test", index=False)

    print("\n 完成：")
    print("1) DICOM → NIfTI 已完成")
    print("2) train_test_split.xlsx 已新增 mapped_id 列")


if __name__ == "__main__":
    main()

import os
import SimpleITK as sitk
import pandas as pd
import numpy as np

# =========================
# 路径配置
# =========================
pred_dir = r"C:\Users\dell\Desktop\Eso-CTV\20260319\testresult"   # 文件夹A：SAM2预测结果
gt_dir   = r"C:\Users\dell\Desktop\Eso-CTV\20260319\labelsTs"     # 文件夹B：原始mask
out_csv  = r"C:\Users\dell\Desktop\Eso-CTV\20260319\shape_check_report.csv"


def safe_read_nii(path):
    try:
        img = sitk.ReadImage(path)
        arr = sitk.GetArrayFromImage(img)
        return img, arr, None
    except Exception as e:
        return None, None, str(e)


def tuple_equal(a, b, tol=1e-6):
    if len(a) != len(b):
        return False
    return all(abs(x - y) < tol for x, y in zip(a, b))


def main():
    pred_files = sorted([f for f in os.listdir(pred_dir) if f.endswith(".nii.gz")])
    gt_files = sorted([f for f in os.listdir(gt_dir) if f.endswith(".nii.gz")])

    pred_set = set(pred_files)
    gt_set = set(gt_files)

    all_files = sorted(pred_set | gt_set)

    records = []

    print("=" * 100)
    print("开始检查预测结果和GT的一致性")
    print("=" * 100)

    for fname in all_files:
        pred_path = os.path.join(pred_dir, fname)
        gt_path = os.path.join(gt_dir, fname)

        pred_exists = fname in pred_set
        gt_exists = fname in gt_set

        row = {
            "file_name": fname,
            "pred_exists": pred_exists,
            "gt_exists": gt_exists,
            "pred_shape": "",
            "gt_shape": "",
            "same_shape": "",
            "pred_z": "",
            "gt_z": "",
            "same_z": "",
            "pred_spacing": "",
            "gt_spacing": "",
            "same_spacing": "",
            "pred_origin": "",
            "gt_origin": "",
            "same_origin": "",
            "pred_direction": "",
            "gt_direction": "",
            "same_direction": "",
            "pred_nonzero": "",
            "gt_nonzero": "",
            "pred_error": "",
            "gt_error": "",
            "final_status": ""
        }

        if not pred_exists:
            row["final_status"] = "GT有，预测缺失"
            print(f"❌ {fname}: GT有，预测缺失")
            records.append(row)
            continue

        if not gt_exists:
            row["final_status"] = "预测有，GT缺失"
            print(f"❌ {fname}: 预测有，GT缺失")
            records.append(row)
            continue

        pred_img, pred_arr, pred_err = safe_read_nii(pred_path)
        gt_img, gt_arr, gt_err = safe_read_nii(gt_path)

        row["pred_error"] = pred_err if pred_err else ""
        row["gt_error"] = gt_err if gt_err else ""

        if pred_err or gt_err:
            row["final_status"] = "读取失败"
            print(f"❌ {fname}: 读取失败 | pred_err={pred_err} | gt_err={gt_err}")
            records.append(row)
            continue

        pred_shape = tuple(pred_arr.shape)
        gt_shape = tuple(gt_arr.shape)

        pred_spacing = tuple(pred_img.GetSpacing())
        gt_spacing = tuple(gt_img.GetSpacing())

        pred_origin = tuple(pred_img.GetOrigin())
        gt_origin = tuple(gt_img.GetOrigin())

        pred_direction = tuple(pred_img.GetDirection())
        gt_direction = tuple(gt_img.GetDirection())

        pred_nonzero = int(np.sum(pred_arr > 0))
        gt_nonzero = int(np.sum(gt_arr > 0))

        same_shape = pred_shape == gt_shape
        same_z = pred_shape[0] == gt_shape[0]
        same_spacing = tuple_equal(pred_spacing, gt_spacing)
        same_origin = tuple_equal(pred_origin, gt_origin)
        same_direction = tuple_equal(pred_direction, gt_direction)

        row["pred_shape"] = str(pred_shape)
        row["gt_shape"] = str(gt_shape)
        row["same_shape"] = same_shape

        row["pred_z"] = pred_shape[0]
        row["gt_z"] = gt_shape[0]
        row["same_z"] = same_z

        row["pred_spacing"] = str(pred_spacing)
        row["gt_spacing"] = str(gt_spacing)
        row["same_spacing"] = same_spacing

        row["pred_origin"] = str(pred_origin)
        row["gt_origin"] = str(gt_origin)
        row["same_origin"] = same_origin

        row["pred_direction"] = str(pred_direction)
        row["gt_direction"] = str(gt_direction)
        row["same_direction"] = same_direction

        row["pred_nonzero"] = pred_nonzero
        row["gt_nonzero"] = gt_nonzero

        issues = []
        if not same_shape:
            issues.append("shape不一致")
        if not same_z:
            issues.append("z层数不一致")
        if not same_spacing:
            issues.append("spacing不一致")
        if not same_origin:
            issues.append("origin不一致")
        if not same_direction:
            issues.append("direction不一致")

        if len(issues) == 0:
            row["final_status"] = "一致"
            print(f"✅ {fname}: 一致")
        else:
            row["final_status"] = " | ".join(issues)
            print(f"❌ {fname}: {row['final_status']}")
            print(f"   GT   shape={gt_shape}, spacing={gt_spacing}")
            print(f"   Pred shape={pred_shape}, spacing={pred_spacing}")

        records.append(row)

    df = pd.DataFrame(records)
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 100)
    print("检查完成")
    print(f"结果已保存到: {out_csv}")

    if not df.empty:
        print("\n问题统计：")
        print(df["final_status"].value_counts(dropna=False))


if __name__ == "__main__":
    main()
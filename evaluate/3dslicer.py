import os
import subprocess
import re
import csv
import SimpleITK as sitk

# 设置路径
gt_dir = r"C:\Users\dell\Desktop\20250707\nnUNet_3d\Dataset003_ThreeD\labelsTs"
pred_dir = r"C:\Users\dell\Desktop\20250707\nnUNet_3d\testResult"
output_csv = r"C:\Users\dell\Desktop\evaluation_results_final.csv"

cases = sorted([f for f in os.listdir(pred_dir) if f.endswith(".nii.gz")])

with open(output_csv, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Case", "Dice", "HD95", "SE", "SP", "TP", "TN", "FP", "FN", "Ref_volume_mm3", "Pred_volume_mm3"])

    for case_file in cases:
        case_name = os.path.splitext(os.path.splitext(case_file)[0])[0]
        print(f"🔍 Processing: {case_name}")

        gt_path = os.path.join(gt_dir, case_file)
        pred_path = os.path.join(pred_dir, case_file)

        if not os.path.exists(gt_path):
            print(f"⚠️ Missing GT for: {case_file}")
            writer.writerow([case_name] + [""] * 11)
            continue

        # 初始化各项指标为空
        dice = se = sp = tp = tn = fp = fn = hd95 = ref_vol = pred_vol = ""

        try:
            # Step 1: 提取 Dice/SE/SP/TP/TN/FP/FN
            cmd_metrics = f'plastimatch dice "{gt_path}" "{pred_path}"'
            result_metrics = subprocess.run(cmd_metrics, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, check=True)
            output_metrics = result_metrics.stdout

            dice_match = re.search(r"DICE:\s*([0-9.]+)", output_metrics)
            se_match = re.search(r"SE:\s*([0-9.]+)", output_metrics)
            sp_match = re.search(r"SP:\s*([0-9.]+)", output_metrics)
            tp_match = re.search(r"TP:\s*([0-9.]+)", output_metrics)
            tn_match = re.search(r"TN:\s*([0-9.]+)", output_metrics)
            fp_match = re.search(r"FP:\s*([0-9.]+)", output_metrics)
            fn_match = re.search(r"FN:\s*([0-9.]+)", output_metrics)

            dice = dice_match.group(1) if dice_match else ""
            se = se_match.group(1) if se_match else ""
            sp = sp_match.group(1) if sp_match else ""
            tp = tp_match.group(1) if tp_match else ""
            tn = tn_match.group(1) if tn_match else ""
            fp = fp_match.group(1) if fp_match else ""
            fn = fn_match.group(1) if fn_match else ""

            # Step 2: 提取 HD95（boundary）
            cmd_hd = f'plastimatch dice --hausdorff "{gt_path}" "{pred_path}"'
            result_hd = subprocess.run(cmd_hd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, check=True)
            output_hd = result_hd.stdout
            hd95_match = re.search(r"Percent \(0.95\) Hausdorff distance \(boundary\)\s*=\s*([0-9.]+)", output_hd)
            hd95 = f"{float(hd95_match.group(1)):.4f}" if hd95_match else ""

            # Step 3: 体积计算
            gt_img = sitk.ReadImage(gt_path)
            pred_img = sitk.ReadImage(pred_path)
            spacing = gt_img.GetSpacing()
            voxel_volume = spacing[0] * spacing[1] * spacing[2]

            gt_array = sitk.GetArrayFromImage(gt_img)
            pred_array = sitk.GetArrayFromImage(pred_img)
            ref_vol = f"{int((gt_array > 0).sum()) * voxel_volume:.2f}"
            pred_vol = f"{int((pred_array > 0).sum()) * voxel_volume:.2f}"

        except Exception as e:
            print(f"❌ Error in {case_name}:\n{str(e)}")

        writer.writerow([case_name, dice, hd95, se, sp, tp, tn, fp, fn, ref_vol, pred_vol])

# import SimpleITK as sitk
#
# ref = sitk.ReadImage(r"C:\Users\dell\Desktop\SAM\GTVp_CTonly\20250809\datanii\test_nii/p_0/image.nii.gz")
# pred = sitk.ReadImage(r"C:\Users\dell\Desktop\TransUNet\p_0_img.nii.gz")
#
# print("原始CT spacing:", ref.GetSpacing())
# print("预测mask spacing:", pred.GetSpacing())
# print("原始CT origin:", ref.GetOrigin())
# print("预测mask origin:", pred.GetOrigin())
# print("原始CT direction:", ref.GetDirection())
# print("预测mask direction:", pred.GetDirection())
# print("尺寸对比：", ref.GetSize(), pred.GetSize())


import os
import SimpleITK as sitk

# === 修改为你的路径 ===
gt_dir = r'C:\Users\dell\Desktop\SAM\GTVp_CTonly\20250809\nnUNet\Dataset001_GTVp\labelsTs'
pred_dir = r'C:\Users\dell\Desktop\deeplabv3+'

# 只检测 nii.gz 文件
gt_files = sorted([f for f in os.listdir(gt_dir) if f.endswith('.nii.gz')])
pred_files = sorted([f for f in os.listdir(pred_dir) if f.endswith('.nii.gz')])

print(f"共找到 GT={len(gt_files)} 个，Pred={len(pred_files)} 个\n")

mismatch_cases = []

for f in gt_files:
    gt_path = os.path.join(gt_dir, f)
    pred_path = os.path.join(pred_dir, f)

    if not os.path.exists(pred_path):
        print(f"❌ 预测结果缺失: {f}")
        continue

    gt = sitk.ReadImage(gt_path)
    pred = sitk.ReadImage(pred_path)
    gt_arr = sitk.GetArrayFromImage(gt)
    pred_arr = sitk.GetArrayFromImage(pred)

    gt_slices = gt_arr.shape[0]
    pred_slices = pred_arr.shape[0]

    if gt_slices != pred_slices:
        print(f"⚠️ 层数不一致: {f} → GT={gt_slices}, Pred={pred_slices}")
        mismatch_cases.append((f, gt_slices, pred_slices))

print("\n✅ 检查完成！")
if len(mismatch_cases) == 0:
    print("所有病例层数完全一致。")
else:
    print(f"共有 {len(mismatch_cases)} 个病例层数不匹配：")
    for f, g, p in mismatch_cases:
        print(f"  {f}: GT={g}, Pred={p}")

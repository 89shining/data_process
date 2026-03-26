"""
将nnunet结果改名为prompt
"""

import os
import re
import shutil
from pathlib import Path

# =========================
# 1. 这里改成你的实际路径
# =========================
src_dir = Path(r"/home/wusi/nnUNet/nnUNetFrame/DATASET/nnUNet_results/Dataset014_RectalCTV60pCrop/nnUNetTrainer__nnUNetPlans__3d_fullres/testResult_fold2")   # A文件夹：放 nnunet预测结果 CTV_000.nii.gz 这些文件
dst_root = Path(r"/home/wusi/segment-anything/SAMdata/Rectal/20260325_CTV/Cropdatanii")  # B文件夹：里面训练测试数据，有 train_nii 和 test_nii

# =========================
# 2. 正则：提取 CTV_xxx 中的数字
# =========================
pattern = re.compile(r"^CTV_(\d+)\.nii\.gz$")

# =========================
# 3. 收集 B 中所有 p_x 子文件夹
#    key = 数字编号(int)
#    value = 该子文件夹路径
# =========================
target_map = {}

for split_name in ["train_nii", "test_nii"]:
    split_dir = dst_root / split_name
    if not split_dir.exists():
        print(f"⚠️ 不存在文件夹: {split_dir}")
        continue

    for subfolder in split_dir.iterdir():
        if subfolder.is_dir() and subfolder.name.startswith("p_"):
            try:
                idx = int(subfolder.name.split("_")[1])   # p_12 -> 12
                if idx in target_map:
                    print(f"⚠️ 编号重复: p_{idx} 已存在于 {target_map[idx]}，又发现 {subfolder}")
                target_map[idx] = subfolder
            except ValueError:
                print(f"⚠️ 跳过非法文件夹名: {subfolder.name}")

print(f"共找到目标子文件夹 {len(target_map)} 个")

# =========================
# 4. 遍历 A 中所有 nii.gz 文件并 copy
# =========================
copied = 0
skipped = 0

for fname in os.listdir(src_dir):
    match = pattern.match(fname)
    if not match:
        continue

    idx = int(match.group(1))   # CTV_012.nii.gz -> 12
    src_path = src_dir / fname

    if idx not in target_map:
        print(f"⚠️ 未找到对应目标文件夹: {fname} -> p_{idx}")
        skipped += 1
        continue

    dst_folder = target_map[idx]
    dst_path = dst_folder / "prompt.nii.gz"

    shutil.copy2(src_path, dst_path)
    print(f"✅ 已复制: {src_path.name} -> {dst_path}")

    copied += 1

# =========================
# 5. 总结
# =========================
print("\n===== 复制完成 =====")
print(f"成功复制: {copied}")
print(f"跳过数量: {skipped}")
"""
把CTV复制到GTV文件中
"""


import os
import shutil

# 文件A和文件B的根路径
src_root = r"C:/Users/dell/Desktop\CTV\datanii\train_nii"  # 你的CTV路径
dst_root = r"C:/Users/dell/Desktop\GTVp\datanii\train_nii"  # 你的GTVp路径

# 遍历文件A的子文件夹
for subdir in os.listdir(src_root):
    src_subdir = os.path.join(src_root, subdir)
    dst_subdir = os.path.join(dst_root, subdir)

    # 确保是文件夹
    if os.path.isdir(src_subdir):
        src_file = os.path.join(src_subdir, "CTV.nii.gz")
        dst_file = os.path.join(dst_subdir, "CTV.nii.gz")

        if os.path.exists(src_file):
            # 创建目标文件夹（如果不存在）
            os.makedirs(dst_subdir, exist_ok=True)
            shutil.copy2(src_file, dst_file)
            print(f"已复制: {src_file} → {dst_file}")
        else:
            print(f"⚠️ 找不到文件: {src_file}")

print("复制完成！")

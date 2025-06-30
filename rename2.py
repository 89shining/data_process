"""
01_00.nii.gz -> pelvis_01.nii.gz
"""

import os

# 设置文件夹路径
folder_path = 'D:/data/challenge/labelsTr'

# 遍历文件夹中的文件
for filename in os.listdir(folder_path):
    if filename.endswith('.nii.gz'):  # 确保只修改.nii.gz文件
        # 提取文件名前部分
        base_name = filename.split('.')[0]  # 获取不带扩展名的文件名
        parts = base_name.split('_')  # 按下划线分割
        if len(parts) == 2:  # 确保文件名符合预期格式
            new_base_name = f'pelvis_{parts[0]}.nii.gz'  # 构造新的文件名
            old_file = os.path.join(folder_path, filename)
            new_file = os.path.join(folder_path, new_base_name)
            # 重命名文件
            os.rename(old_file, new_file)

print("文件重命名完成！")

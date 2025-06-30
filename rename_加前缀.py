# 更改文件名：加前缀
# eg：01.nii.gz -> pelvis_01.nii.gz

import os

# 设置文件夹路径
folder_path = 'D:/data/challenge/imagesTs'

# 遍历文件夹中的文件
for filename in os.listdir(folder_path):
    if filename.endswith('.nii.gz'):  # 确保只修改.nii.gz文件
        # 构造新的文件名
        new_filename = 'pelvis_' + filename
        # 获取旧文件的完整路径和新文件的完整路径
        old_file = os.path.join(folder_path, filename)
        new_file = os.path.join(folder_path, new_filename)
        # 重命名文件
        os.rename(old_file, new_file)

print("文件重命名完成！")

import json
import os

# 定义目标文件夹路径和文件名
folder_path = 'D:/learning/nnUNet/nnUNetFrame/nnUNet_raw/Dataset001_pelvis'  # 修改为你的文件夹路径
json_file_path = os.path.join(folder_path, 'dataset.json')

# 创建空白文件
with open(json_file_path, 'w') as json_file:
    json.dump({}, json_file)  # 以空字典形式写入，创建一个空的 JSON 文件

print(f"空白的 dataset.json 文件已创建在 {json_file_path}")

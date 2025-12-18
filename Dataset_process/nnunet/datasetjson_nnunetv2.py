"""
创建nnuetv2数据集的dataset.json
"""

import os
import json
from pathlib import Path

# 数据集路径
dataset_dir = Path(r"/home/wusi/nnUNet/nnUNetFrame/DATASET/nnUNet_raw/Dataset008_EsoCTV73p")
images_tr_dir = dataset_dir / "imagesTr"

# 自动提取模态编号和病例数
modalities = set()
case_ids = set()

for filename in os.listdir(images_tr_dir):
    if filename.endswith(".nii.gz"):
        parts = filename.split("_")
        case_id = parts[1]  # 例如 "0000"
        modality = parts[2].split(".")[0]  # 例如 "0000"
        modalities.add(modality)
        case_ids.add(case_id)

num_training = len(case_ids)
modalities = sorted(modalities)  # 模态编号排序（如 "0000", "0001"）

# 手动填写 labels（根据你的数据集）
labels = {
    "background": 0,
    "CTV": 1,
    # 添加更多类别...
}

# 生成 channel_names（假设模态顺序为 0,1,2...）
channel_names = {str(i): f"Modality{i}" for i in range(len(modalities))}

# # 如果有已知模态名称（如 T1, FLAIR），需手动替换：
# channel_names = {
#     "0": "CT"
# }

# 多模态
channel_names = {
    "0": "CT",
    # "1": "MR"
}

# 构建 dataset.json
dataset_json = {
    "channel_names": channel_names,
    "labels": labels,
    "numTraining": num_training,
    "file_ending": ".nii.gz"
}

# 保存文件
with open(dataset_dir / "dataset.json", "w") as f:
    json.dump(dataset_json, f, indent=4)
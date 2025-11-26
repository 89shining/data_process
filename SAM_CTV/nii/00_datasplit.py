"""
随机划分数据集
"""

import os
import random
import shutil

# ==== 配置 ====
folderA = r"D:\SAM\Esophagus\Rawdata"   # 存放原始患者子文件夹的目录
train_out = r"D:\SAM\Esophagus\20251127\rawdata\train"  # 输出：训练集
test_out  = r"D:\SAM\Esophagus\20251127\rawdata\test"   # 输出：测试集

# ==== 创建输出文件夹 ====
os.makedirs(train_out, exist_ok=True)
os.makedirs(test_out, exist_ok=True)

# ==== 读取所有患者子文件夹 ====
patients = [d for d in os.listdir(folderA) if os.path.isdir(os.path.join(folderA, d))]
patients = sorted(patients)  # 可选：保证顺序可控

print(f"总患者数: {len(patients)}")   # 期望为 146

if len(patients) < 66:
    print("⚠️ 注意：患者数量似乎少于 66，请检查路径！")

# ==== 随机打乱 ====
random.seed(2025)  # 固定随机种子，使划分可复现
random.shuffle(patients)

# ==== 划分 ====
train_patients = patients[:50]
test_patients  = patients[50:50+16]

print(f"训练集: {len(train_patients)}")
print(f"测试集: {len(test_patients)}")

# ==== 复制（或移动）文件夹 ====
for p in train_patients:
    src = os.path.join(folderA, p)
    dst = os.path.join(train_out, p)
    shutil.copytree(src, dst)
    print(f"Train ← {p}")

for p in test_patients:
    src = os.path.join(folderA, p)
    dst = os.path.join(test_out, p)
    shutil.copytree(src, dst)
    print(f"Test ← {p}")

print("\n🎉 划分完成!")

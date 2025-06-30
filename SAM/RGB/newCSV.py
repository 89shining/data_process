"""
生成相邻三张image和伪RGB图像的对应关系CSV
"""
import pandas as pd
import os

# 加载原始 CSV，没有列名则添加
df = pd.read_csv("C:/Users/WS/Desktop/20250604/dataset/test/test_nii.csv", header=None, names=["image", "mask"])

# 提取患者ID和切片编号
df["patient"] = df["image"].str.extract(r"/(p_\d+)/")
df["slice_num"] = df["image"].str.extract(r"/(\d+)\.nii").astype(int)
df["patient_id"] = df["patient"].str.extract(r"p_(\d+)").astype(int)
# 排序保证顺序一致
df = df.sort_values(by=["patient_id", "slice_num"]).reset_index(drop=True)

# 先创建一个完整的 df_sorted 用于查找时使用正确顺序
df_sorted = df.copy()

# 构造三图路径
triplet_paths = []
for idx in df_sorted.index:
    row = df_sorted.loc[idx]
    patient = row["patient"]
    slice_num = row["slice_num"]

    # 当前患者所有图像（按slice_num排序）
    patient_df = df_sorted[df_sorted["patient"] == patient].sort_values(by="slice_num").reset_index(drop=True)
    pos = patient_df[patient_df["slice_num"] == slice_num].index[0]

    if pos == 0:
        neighbors = [pos, pos, pos + 1]
    elif pos == len(patient_df) - 1:
        neighbors = [pos - 1, pos, pos]
    else:
        neighbors = [pos - 1, pos, pos + 1]

    paths = patient_df.loc[neighbors, "image"].tolist()
    triplet_paths.append(paths)

df_sorted["nii_paths"] = [";".join(p) for p in triplet_paths]

df_sorted[["image", "mask", "nii_paths"]].to_csv("C:/Users/WS/Desktop/20250604/dataset/test/newtest_nii.csv", index=False)

"""
Friedman检验
P<0.05——有差异———事后检验 Nemenyi检验
"""

import pandas as pd
import numpy as np
from scipy.stats import friedmanchisquare
import scikit_posthocs as sp
import matplotlib.pyplot as plt
import seaborn as sns

# ========== 参数设置 ==========
# Num
file_path = r"C:\Users\WS\Desktop\统计分析\Num_box_prompts\num_eval_3d.xlsx"
sheets = ['SAM_2slices', 'SAM_3slices', 'SAM_5slices', 'SAM_7slices', 'SAM_all']
metric_cols = ['3d Dice', '3d HD95 (mm)', 'IoU']
#
# # Pos
# file_path = r"C:\Users\WS\Desktop\统计分析\Pos_box_prompts\pos_eval_3d.xlsx"
# sheets = ['SAM_max_area', 'SAM_mid_volume', 'SAM_mid_layer', 'SAM_random']
# metric_cols = '3d Dice'
patient_num = 20

# ========== 主循环 ==========
for metric_col in metric_cols:
    print(f"\n==================== 分析指标：{metric_col} ====================\n")

    # ======== 读取数据 ========
    data = []
    for s in sheets:
        df = pd.read_excel(file_path, sheet_name=s).iloc[:patient_num]
        df.columns = df.columns.str.strip()  # 去除列名空格
        if metric_col not in df.columns:
            print(f"[警告] {s} 表中未找到列名 {metric_col}，实际列名为：{df.columns.tolist()}")
        data.append(df[metric_col].astype(float).values)

    # 转为DataFrame格式（行为病例，列为模型）
    data_df = pd.DataFrame({sheets[i]: data[i] for i in range(len(sheets))})

    # ========== Friedman 检验 ==========
    stat, p = friedmanchisquare(*data)
    print(f"Friedman Test for {metric_col}: χ² = {stat:.4f}, p = {p:.6f}")
    if p < 0.05:
        print("→ 差异显著：进行 Nemenyi 事后检验。\n")
    else:
        print("→ 差异不显著。\n")

    # ========== Nemenyi 事后检验 ==========
    posthoc = sp.posthoc_nemenyi_friedman(data_df)
    print("=== Nemenyi 检验结果矩阵（p 值） ===")
    print(posthoc.round(4))

    # ========== 可视化显著性热力图 ==========
    plt.figure(figsize=(6,5))
    sns.heatmap(posthoc, annot=True, cmap='coolwarm_r', fmt=".3f",
                xticklabels=sheets, yticklabels=sheets, cbar_kws={'label': 'p-value'})
    plt.title(f"Nemenyi Post-hoc Test ({metric_col})")
    plt.tight_layout()
    plt.show()

    # ========== Friedman 平均秩次（Critical Difference Plot） ==========
    mean_ranks = data_df.rank(axis=1, method='average').mean().sort_values()
    plt.figure(figsize=(7, 1.2))
    plt.scatter(mean_ranks, np.zeros_like(mean_ranks), s=120, color='royalblue')

    for i, (name, rank) in enumerate(mean_ranks.items()):
        plt.text(rank, 0.03, name, ha='center', va='bottom', fontsize=10)

    plt.yticks([])
    plt.xlabel("Average Rank (Lower is Better)")
    plt.title(f"Critical Difference Diagram ({metric_col})")
    plt.tight_layout()
    plt.show()

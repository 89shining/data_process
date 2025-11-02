"""
Friedman检验：>2组少样本比较，非参数检验
p>0.05——差异无统计学意义
P<0.05——有差异———事后检验 Nemenyi检验
"""

import pandas as pd
import numpy as np
from scipy.stats import friedmanchisquare
import matplotlib.pyplot as plt

# ========== 参数设置 ==========
# Num
file_path = r"C:\Users\WS\Desktop\统计分析\Num_box_prompts\num_eval_3d.xlsx"  # 你的文件路径
sheets = ['SAM_2slices', 'SAM_3slices', 'SAM_5slices', 'SAM_7slices', 'SAM_all']  # sheet 名

# # Pos
# file_path = r"C:\Users\WS\Desktop\统计分析\Pos_box_prompts\pos_eval_3d.xlsx"  # 你的文件路径
# sheets = ['SAM_max_area', 'SAM_mid_volume', 'SAM_mid_layer', 'SAM_random']  # sheet 名

# metric_cols = ['2D DSC', '2D HD95']  # 要检验的指标名
metric_cols = ['3d Dice', '3d HD95 (mm)', 'IoU']  # 要检验的指标名
patient_num = 20  # 患者数量（不含Mean、Std行）

# ========== 数据读取 ==========
data_dict = {metric: [] for metric in metric_cols}

for s in sheets:
    df = pd.read_excel(file_path, sheet_name=s).iloc[:patient_num]
    df.columns = df.columns.str.strip()  # 去除列名首尾空格
    for metric in metric_cols:
        data_dict[metric].append(df[metric].astype(float))

# ========== Friedman 检验 ==========
print("=== Friedman Test Results ===\n")
for metric in metric_cols:
    stat, p = friedmanchisquare(*data_dict[metric])
    print(f"{metric}: χ² = {stat:.4f}, p = {p:.6f}")
    if p < 0.05:
        print("→ 差异显著：至少两组之间存在统计学差异。\n")
    else:
        print("→ 差异不显著：各组之间无显著统计学差异。\n")

# # ========== Num 趋势分析图（均值±标准差） ==========
# plt.figure(figsize=(7, 5))
# x = [2, 3, 5, 7, all]  # 对应 slices 数量 (All=9)
# for metric, color in zip(metric_cols, ['tab:blue', 'tab:red']):
#     means = [d.mean() for d in data_dict[metric]]
#     stds = [d.std() for d in data_dict[metric]]
#     plt.errorbar(x, means, yerr=stds, marker='o', capsize=4, label=metric, color=color)
#
# plt.xlabel("Number of Prompted Slices")
# plt.ylabel("Score / Distance")
# plt.title("Friedman Analysis: Dice and HD95 vs Prompt Layers")
# plt.grid(True, linestyle='--', alpha=0.6)
# plt.legend()
# plt.tight_layout()
# plt.show()
#
# # ========== Num 患者层级趋势图（个体变化） ==========
# plt.figure(figsize=(7, 5))
# x_labels = [2, 3, 5, 7, all]  # 对应 slices 数量 (All=9)
# for i in range(patient_num):
#     y = [data_dict['2D DSC'][k][i] for k in range(len(sheets))]
#     plt.plot(x_labels, y, alpha=0.5, linewidth=1)
# plt.title("Per-Patient Dice Trend across Prompt Numbers")
# plt.xlabel("Prompted Slices")
# plt.ylabel("2D Dice")
# plt.grid(True, linestyle='--', alpha=0.6)
# plt.tight_layout()
# plt.show()

# # ========== Pos 趋势分析图（均值±标准差） ==========
# plt.figure(figsize=(7, 5))
# x = ["max_area", "mid_volume", "mid_layer", "random"]  # 对应sheet
# for metric, color in zip(metric_cols, ['tab:blue', 'tab:red']):
#     means = [d.mean() for d in data_dict[metric]]
#     stds = [d.std() for d in data_dict[metric]]
#     plt.errorbar(x, means, yerr=stds, marker='o', capsize=4, label=metric, color=color)
#
# plt.xlabel("Position of Prompted Slices")
# plt.ylabel("Score / Distance")
# plt.title("Friedman Analysis: Dice and HD95 vs Prompt Position")
# plt.grid(True, linestyle='--', alpha=0.6)
# plt.legend()
# plt.tight_layout()
# plt.show()
#
# # ========== Pos 患者层级趋势图（个体变化） ==========
# plt.figure(figsize=(7, 5))
# x_labels = ["max_area", "mid_volume", "mid_layer", "random"]  # 对应sheet
#
# for i in range(patient_num):
#     y = [data_dict['2D DSC'][k][i] for k in range(len(sheets))]
#     plt.plot(x_labels, y, alpha=0.5, linewidth=1)
# plt.title("Per-Patient Dice Trend across Prompt Position")
# plt.xlabel("Prompted Position")
# plt.ylabel("2D Dice")
# plt.grid(True, linestyle='--', alpha=0.6)
# plt.tight_layout()
# plt.show()



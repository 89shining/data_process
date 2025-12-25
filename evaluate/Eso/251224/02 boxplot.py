"""
根据表来绘制分段箱式图（多模型）
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# =========================
# 路径配置
# =========================
csv_path = r"C:\Users\dell\Desktop\slice_wise_all_models.csv"

# 选择你要显示的模型（顺序就是显示顺序）
MODEL_LIST = [
    "nnUNet_2D",
    "nnUNet_3D",
    "SAM",
    "SAM_5slices",
    # "SAM_2slices",
]

# =========================
# 读取数据
# =========================
df = pd.read_csv(csv_path)

# 只保留感兴趣的模型
df_plot = df[df["model"].isin(MODEL_LIST)].copy()

if df_plot.empty:
    raise ValueError("No data found for selected models")

print("Models:", df_plot["model"].unique())
print("Total slices:", len(df_plot))

# =========================
# 均匀分成 5 段
# =========================
bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
labels = [
    "0–20%",
    "20–40%",
    "40–60%",
    "60–80%",
    "80–100%"
]

df_plot["z_segment"] = pd.cut(
    df_plot["z_norm"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

# =========================
# 绘制多模型箱式图
# =========================
plt.figure(figsize=(10, 4))

sns.boxplot(
    data=df_plot,
    x="z_segment",
    y="dice",
    hue="model",          # 按模型分组
    showfliers=True
)

plt.ylim(0, 1.0)
plt.xlabel("Longitudinal Segment (Uniform 5 bins)")
plt.ylabel("Dice")
plt.title("Slice-wise Dice Distribution (Multiple Models)")

plt.legend(title="Model", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.show()

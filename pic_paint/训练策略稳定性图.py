import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

# 数据
x = np.array([0, 0.3, 0.5, 0.7, 0.9])
models = {
    "Freeze_image_encoder": [2.64, 2.15, 2.26, 2.69, 3.17],
    "Freeze_mask_decoder": [3.64, 1.81, 2.24, 3.25, 4.46],
    "Freeze_encoder_ecoder": [4.16, 1.64, 2.11, 3.69, 5.11],
    "TrainAll": [4.04, 2.33, 2.72, 3.74, 4.78]
}

# 颜色更饱和的方案（论文和汇报均适用）
colors = {
    "Freeze_image_encoder": "#1f77b4",   # 深蓝
    "Freeze_mask_decoder": "#ff7f0e",    # 橙色
    "Freeze_encoder_ecoder": "#2ca02c",  # 深绿
    "TrainAll": "#d62728"       # 深红
}

plt.figure(figsize=(9,6))
plt.style.use('seaborn-v0_8-white')  # 白底、无背景网格

for label, y in models.items():
    # 平滑曲线
    x_smooth = np.linspace(x.min(), x.max(), 200)
    y_smooth = make_interp_spline(x, y, k=2)(x_smooth)

    plt.plot(x_smooth, y_smooth, color=colors[label], linewidth=2.2, label=label)
    plt.scatter(x, y, color=colors[label], marker='x', s=60)

# 图表样式
plt.title("2D Dice", fontsize=16, fontweight='bold')
plt.xlabel("Expansion", fontsize=13)
plt.ylabel("2D Dice", fontsize=13)
plt.xticks([0, 3, 5, 7, 9], fontsize=12)
plt.yticks(fontsize=12)
plt.legend(fontsize=11, loc='lower left', frameon=False)
plt.ylim(0, 5.5)


# 去掉所有边框的灰色背景线
plt.grid(False)
plt.tight_layout()
plt.show()

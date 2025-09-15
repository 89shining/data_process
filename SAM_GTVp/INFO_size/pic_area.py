import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# 文件路径
excel_path = 'C:/Users/dell/Desktop/train_slice_area_map.xlsx'
save_dir = 'C:/Users/dell/Desktop/train_plots'  # 输出文件夹
os.makedirs(save_dir, exist_ok=True)

# 读取 Excel（无表头，按实际内容处理）
df = pd.read_excel(excel_path, header=None)

# 遍历每个患者（每一行）
for i, row in df.iterrows():
    # 去掉 NaN 和空白（非数值）数据
    try:
        values = pd.to_numeric(row.dropna(), errors='coerce')
        values = values[~values.isna()].values
    except Exception as e:
        print(f"跳过第{i}行（转换失败）：{e}")
        continue

    if len(values) == 0:
        print(f"跳过第{i}行（无有效数值）")
        continue

    slice_indices = np.arange(1, len(values) + 1)
    areas = np.array(values)

    # Top 3 最大值索引
    top3_idx = np.argsort(areas)[-3:][::-1]  # 从大到小
    top3_shapes = ['o', 's', '^']
    top3_labels = ['Max area', '2nd max', '3rd max']

    # 中间层索引（偶数两个，奇数一个）
    mid = len(areas) // 2
    if len(areas) % 2 == 0:
        middle_indices = [mid - 1, mid]
    else:
        middle_indices = [mid]

    # 绘图
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(slice_indices, areas, '-o', color='orange', label=f'p_{i}', markersize=3)

    # 标记 top3 面积
    for j, idx in enumerate(top3_idx):
        ax.scatter(slice_indices[idx], areas[idx], s=70, c='black', marker=top3_shapes[j], label=top3_labels[j])

    # 标记中间层
    for k, idx in enumerate(middle_indices):
        ax.scatter(slice_indices[idx], areas[idx], s=70, c='red', marker='D', label='Middle slice' if k == 0 else "")

    # 图例去重
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys())

    ax.set_title(f'Slice area - p_{i}')
    ax.set_xlabel('Slice index')
    ax.set_ylabel('Area (mm²)')
    ax.set_xticks(slice_indices)
    ax.grid(True)

    # 保存图像
    save_path = os.path.join(save_dir, f'p_{i}.png')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

print(f"✅ 所有图像已保存至：{save_dir}")

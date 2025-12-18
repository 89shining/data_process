# # 以GTVp开头
#
# import os
#
# A = r"D:\SAM\Rectal\GTVp_CTonly\20251128-crop\UNet"   # 你的 A 文件夹路径
#
# files = sorted([
#     f for f in os.listdir(A)
#     if f.endswith(".nii.gz") and f.startswith("GTVp_")
# ])
#
# print(f"共找到 {len(files)} 个 GTVp 文件")
#
# for f in files:
#     old_path = os.path.join(A, f)
#
#     # ============ 关键：严格提取最后三位数字 ============
#     # 从末尾算起：".nii.gz" = 7 个字符，再往前 3 个字符就是编号
#     num = f[-10:-7]   # 例如 "GTVp_013.nii.gz" → "013"
#
#     new_name = f"GTVpCrop_{num}.nii.gz"
#     new_path = os.path.join(A, new_name)
#
#     print(f"重命名: {f} → {new_name}")
#
#     os.rename(old_path, new_path)
#
# print("\n全部重命名完成！")


# 改_xxx LLM
import os

# === 修改为你的文件夹路径 ===
folder = r"C:\Users\dell\Desktop\ESOTEXT\text2-preck"   # 或 "/home/wusi/.../folder"

for fname in os.listdir(folder):
    old_path = os.path.join(folder, fname)

    # 跳过子目录
    if not os.path.isfile(old_path):
        continue

    # -------- 1. 去掉常见后缀 --------
    base = fname
    if base.endswith(".nii.gz"):
        base = base[:-7]
    elif base.endswith(".nii"):
        base = base[:-4]

    # -------- 2. 去掉 "_" 后面的部分（如 noText）--------
    if "_" in base:
        base = base.split("_")[0]

    # -------- 3. 仅保留数字部分 --------
    # （如果你文件夹中只有数字，可以省略此检查）
    number = ''.join(filter(str.isdigit, base))
    if number == "":
        print(f"跳过：{fname}（找不到数字）")
        continue

    # -------- 4. 拼接新的名字：GTV_数字.nii.gz --------
    new_name = f"GTV_{number}.nii.gz"
    new_path = os.path.join(folder, new_name)

    print(f"Renaming: {fname} --> {new_name}")

    os.rename(old_path, new_path)


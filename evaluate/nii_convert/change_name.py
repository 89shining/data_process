import os

A = r"D:\SAM\Rectal\GTVp_CTonly\20251128-crop\UNet"   # 你的 A 文件夹路径

files = sorted([
    f for f in os.listdir(A)
    if f.endswith(".nii.gz") and f.startswith("GTVp_")
])

print(f"共找到 {len(files)} 个 GTVp 文件")

for f in files:
    old_path = os.path.join(A, f)

    # ============ 关键：严格提取最后三位数字 ============
    # 从末尾算起：".nii.gz" = 7 个字符，再往前 3 个字符就是编号
    num = f[-10:-7]   # 例如 "GTVp_013.nii.gz" → "013"

    new_name = f"GTVpCrop_{num}.nii.gz"
    new_path = os.path.join(A, new_name)

    print(f"重命名: {f} → {new_name}")

    os.rename(old_path, new_path)

print("\n全部重命名完成！")

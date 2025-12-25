"""
计算测试数据的平均分段dice
按SI百分比展示分段
"""

import os
import re
import hashlib
import pandas as pd
import SimpleITK as sitk
from pathlib import Path
from tqdm import tqdm

# =========================
# 你只需要改这 3 个路径
# =========================
PX_IMG_DIR   = r"C:\Users\dell\Desktop\Eso-CTV\TestResult\TestResult\imagesTs"   # 现在的 p_X 图像目录（p_0_0000.nii.gz）
REAL_IMG_DIR = r"C:\Users\dell\Desktop\Eso-CTV\RawImages"  # 原始放疗号图像目录（例如 123456_0000.nii.gz 或 123456.nii.gz）
OUT_XLSX     = r"C:\Users\dell\Desktop\Eso-CTV\pX_to_real_id.xlsx"

# 如果原始目录里也是 nnUNet 格式（xxx_0000.nii.gz），保持 True
REAL_HAS_MODAL_SUFFIX = True  # 改成 False 表示原始文件名没有 _0000

# =========================
# 工具：提取 p_X 的编号
# =========================
def extract_px_id(fname: str) -> str:
    # 兼容 p_12_0000.nii.gz / p12_0000.nii.gz / pCTV_012_0000.nii.gz
    m = re.search(r"(p[^_]*_?\d+)", fname)
    if m:
        return m.group(1)
    # fallback：取去掉后缀
    return Path(fname).stem

# =========================
# 工具：计算图像指纹（hash）
# 用：图像尺寸 + spacing + origin + direction + 像素bytes 的 md5
# =========================
def image_fingerprint(nii_path: str) -> str:
    img = sitk.ReadImage(nii_path)
    arr = sitk.GetArrayFromImage(img)

    md5 = hashlib.md5()
    # meta
    md5.update(str(img.GetSize()).encode())
    md5.update(str(img.GetSpacing()).encode())
    md5.update(str(img.GetOrigin()).encode())
    md5.update(str(img.GetDirection()).encode())
    # data
    md5.update(arr.tobytes())
    return md5.hexdigest()

# =========================
# 主流程
# =========================
def main():
    px_files = [f for f in os.listdir(PX_IMG_DIR) if f.endswith(".nii.gz")]
    if not px_files:
        raise RuntimeError(f"PX_IMG_DIR 里没有 nii.gz：{PX_IMG_DIR}")

    real_files = [f for f in os.listdir(REAL_IMG_DIR) if f.endswith(".nii.gz")]
    if not real_files:
        raise RuntimeError(f"REAL_IMG_DIR 里没有 nii.gz：{REAL_IMG_DIR}")

    print(f"[Info] p_X files: {len(px_files)}")
    print(f"[Info] real files: {len(real_files)}")

    # 1) 先把真实放疗号目录做成：fingerprint -> real_id
    real_map = {}
    dup_fp = 0

    for f in tqdm(real_files, desc="Hashing REAL images"):
        p = os.path.join(REAL_IMG_DIR, f)
        fp = image_fingerprint(p)

        # 从文件名提取真实放疗号（取第一个连续数字串）
        m = re.search(r"(\d+)", f)
        real_id = m.group(1) if m else Path(f).stem

        if fp in real_map and real_map[fp] != real_id:
            dup_fp += 1
        real_map[fp] = real_id

    if dup_fp > 0:
        print(f"[Warn] REAL 中出现 {dup_fp} 个 fingerprint 重复（可能文件重复或命名不同但内容相同）")

    # 2) 对每个 p_X 图像算 fingerprint，然后去 real_map 里找
    rows = []
    not_found = 0

    for f in tqdm(px_files, desc="Matching p_X -> REAL"):
        px_path = os.path.join(PX_IMG_DIR, f)
        fp = image_fingerprint(px_path)

        px_id = extract_px_id(f)
        real_id = real_map.get(fp, None)

        if real_id is None:
            not_found += 1

        rows.append({
            "p_id": px_id,
            "p_file": f,
            "real_id": real_id
        })

    df = pd.DataFrame(rows).sort_values("p_id")
    df.to_excel(OUT_XLSX, index=False)

    print(f"\n[Done] Saved mapping: {OUT_XLSX}")
    if not_found > 0:
        print(f"[Warn] 有 {not_found} 个 p_X 没匹配上真实放疗号。")
        print("       这通常是：原始目录缺文件 / 图像被重采样或裁剪过 / 两边不是同一版本。")
    else:
        print("[Info] 全部 p_X 都成功匹配到真实放疗号 ✅")

if __name__ == "__main__":
    main()

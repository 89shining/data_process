"""
检查nii.gz断层情况
"""

import os
import SimpleITK as sitk
import numpy as np

# =========================
# 配置路径
# =========================
DATA_ROOT = r"C:\Users\dell\Desktop\Eso-CTV\20251217\datanii\test_nii"
MASK_NAME = "CTV.nii.gz"

# =========================
# 核心检测函数
# =========================
def check_z_continuity(mask_3d):
    """
    mask_3d: numpy array, shape (Z, H, W), binary
    return:
        is_continuous: bool
        gap_slices: list of z indices where gap occurs
    """
    z_has_mask = (mask_3d.sum(axis=(1, 2)) > 0).astype(np.int32)

    nonzero_indices = np.where(z_has_mask == 1)[0]
    if len(nonzero_indices) == 0:
        return True, []  # 空 mask，不算断层

    z_start = nonzero_indices[0]
    z_end   = nonzero_indices[-1]

    gap_slices = []
    for z in range(z_start, z_end + 1):
        if z_has_mask[z] == 0:
            gap_slices.append(z)

    is_continuous = (len(gap_slices) == 0)
    return is_continuous, gap_slices


# =========================
# 主流程
# =========================
def main():
    problem_cases = []

    for pid in sorted(os.listdir(DATA_ROOT)):
        case_dir = os.path.join(DATA_ROOT, pid)
        if not os.path.isdir(case_dir):
            continue

        mask_path = os.path.join(case_dir, MASK_NAME)
        if not os.path.exists(mask_path):
            print(f"[Skip] {pid} 缺少 {MASK_NAME}")
            continue

        mask_img = sitk.ReadImage(mask_path)
        mask_np = sitk.GetArrayFromImage(mask_img)  # (Z, H, W)
        mask_np = (mask_np > 0).astype(np.uint8)

        is_ok, gaps = check_z_continuity(mask_np)

        if not is_ok:
            problem_cases.append(pid)
            print(f"[❌ Discontinuity] {pid}")
            print(f"    缺失 slice 索引: {gaps}")
        else:
            print(f"[OK призн] {pid}")

    print("\n========== Summary ==========")
    print(f"总病例数: {len(os.listdir(DATA_ROOT))}")
    print(f"存在断层不连续的病例数: {len(problem_cases)}")

    if problem_cases:
        print("问题病例列表：")
        for p in problem_cases:
            print("  ", p)
    else:
        print("✅ 未发现断层不连续病例")


if __name__ == "__main__":
    main()

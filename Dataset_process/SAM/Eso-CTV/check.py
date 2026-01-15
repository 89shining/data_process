"""
检查nii.gz断层情况
"""

import os
import SimpleITK as sitk
import numpy as np
import csv

# =========================
# 配置路径
# =========================
DATA_ROOT = r"D:\SAM\Esophagus\Extract_error\Nii"
MASK_NAME = "GTV.nii.gz"

# =========================
# 核心检测函数
# =========================
def analyze_gap_segments(gap_slices):
    """
    输入 gap_slices: e.g. [10,11,12, 20,21]
    返回:
        num_segments: 断层段数
        segment_lengths: 每段断层长度列表
    """
    if len(gap_slices) == 0:
        return 0, []

    segments = []
    current_len = 1

    for i in range(1, len(gap_slices)):
        if gap_slices[i] == gap_slices[i - 1] + 1:
            current_len += 1
        else:
            segments.append(current_len)
            current_len = 1

    segments.append(current_len)
    return len(segments), segments

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
    discontinuity_records = []

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
        gap_count = len(gaps)
        num_segments, segment_lengths = analyze_gap_segments(gaps)

        if not is_ok:
            problem_cases.append(pid)
            # ===== 记录到列表，供后面保存 =====
            discontinuity_records.append({
                "case_id": pid,
                "gap_slice_count": gap_count,
                "gap_segment_count": num_segments,
                "gap_segment_lengths": segment_lengths,
                "gap_slice_indices": gaps
            })

            print(f"[❌ Discontinuity] {pid}")
            print(f"    断层 slice 数: {gap_count}")
            print(f"    断层段数: {num_segments}")
            print(f"    每段断层长度: {segment_lengths}")
            print(f"    缺失 slice 索引: {gaps}")
        else:
            print(f"[OK] {pid}")

    print("\n========== Summary ==========")
    print(f"总病例数: {len(os.listdir(DATA_ROOT))}")
    print(f"存在断层不连续的病例数: {len(problem_cases)}")

    if problem_cases:
        print("问题病例列表：")
        for p in problem_cases:
            print("  ", p)
    else:
        print("✅ 未发现断层不连续病例")

    qc_csv_path = os.path.join(DATA_ROOT, "discontinuous_cases.csv")

    if discontinuity_records:
        with open(qc_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "case_id",
                    "gap_slice_count",
                    "gap_segment_count",
                    "gap_segment_lengths",
                    "gap_slice_indices"
                ]
            )
            writer.writeheader()

            for r in discontinuity_records:
                writer.writerow({
                    "case_id": r["case_id"],
                    "gap_slice_count": r["gap_slice_count"],
                    "gap_segment_count": r["gap_segment_count"],
                    # 转成字符串，Excel / pandas 都好读
                    "gap_segment_lengths": str(r["gap_segment_lengths"]),
                    "gap_slice_indices": str(r["gap_slice_indices"])
                })

        print(f"\n 不连续病例已保存到：{qc_csv_path}")
    else:
        print("\n 未发现不连续病例，未生成 CSV")


if __name__ == "__main__":
    main()

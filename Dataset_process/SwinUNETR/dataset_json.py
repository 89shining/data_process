"""
将nnUNet的数据集转为SwinUNETR格式
image命名：case_000_0000.nii.gz -> case_000.nii.gz
json文件格式修改
"""

import os
import re
import json
import random
import shutil
from glob import glob

def copy_structure(src_root, dst_root):
    """复制数据集目录结构（imagesTr、labelsTr、imagesTs、labelsTs）"""
    os.makedirs(dst_root, exist_ok=True)
    for sub in ["imagesTr", "labelsTr", "imagesTs", "labelsTs"]:
        src = os.path.join(src_root, sub)
        dst = os.path.join(dst_root, sub)
        if os.path.exists(src):
            os.makedirs(dst, exist_ok=True)
            files = glob(os.path.join(src, "*.nii*"))
            for f in files:
                shutil.copy2(f, dst)
    print(f"✅ 已复制原始数据到新目录: {dst_root}")


def rename_files(folder):
    """批量去掉 _0000 后缀"""
    nii_files = glob(os.path.join(folder, "*.nii*"))
    for f in nii_files:
        new_name = re.sub(r"_0000(?=\.nii(\.gz)?)", "", os.path.basename(f))
        new_path = os.path.join(folder, new_name)
        if new_name != os.path.basename(f):
            os.rename(f, new_path)
    if nii_files:
        print(f"✅ 已重命名: {folder} (共 {len(nii_files)} 个文件)")


def make_rectal_json(data_root, train_ratio=0.8, label_dict=None, seed=42):
    """根据 MONAI BTCV 格式生成 rectal_dataset.json"""
    random.seed(seed)

    img_tr = os.path.join(data_root, "imagesTr")
    lbl_tr = os.path.join(data_root, "labelsTr")
    img_ts = os.path.join(data_root, "imagesTs")
    lbl_ts = os.path.join(data_root, "labelsTs")

    assert os.path.exists(img_tr) and os.path.exists(lbl_tr), "❌ 缺少训练集文件夹"

    img_files = sorted(glob(os.path.join(img_tr, "*.nii*")))
    lbl_files = sorted(glob(os.path.join(lbl_tr, "*.nii*")))
    matched = sorted(list(set(os.path.basename(f) for f in img_files) & set(os.path.basename(f) for f in lbl_files)))
    if not matched:
        raise ValueError("❌ 未找到匹配的 image/label 文件，请检查命名。")

    random.shuffle(matched)
    n_train = int(len(matched) * train_ratio)
    train_cases = matched[:n_train]
    val_cases = matched[n_train:]

    def entry(name):
        return {"image": f"./imagesTr/{name}", "label": f"./labelsTr/{name}"}

    json_dict = {
        "name": "RectalCancer",
        "description": "Rectal cancer CT dataset for radiotherapy target segmentation",
        "tensorImageSize": "3D",
        "modality": {"0": "CT"},
        "labels": label_dict or {"0": "background", "1": "GTVp"},
        "numTraining": len(train_cases),
        "training": [entry(n) for n in train_cases],
        "validation": [entry(n) for n in val_cases],
        "test": [
            {"image": f"./imagesTs/{os.path.basename(f)}", "label": f"./labelsTs/{os.path.basename(f)}"}
            for f in sorted(glob(os.path.join(img_ts, "*.nii*")))
            if os.path.exists(os.path.join(lbl_ts, os.path.basename(f)))
        ],
    }

    save_path = os.path.join(data_root, "rectal_dataset.json")
    with open(save_path, "w") as f:
        json.dump(json_dict, f, indent=4)

    print(f"\n✅ JSON 已生成: {save_path}")
    print(f"训练集: {len(train_cases)}, 验证集: {len(val_cases)}, 测试集: {len(json_dict['test'])}")
    return save_path


if __name__ == "__main__":
    # -------------------
    # 修改路径
    # -------------------
    src_root = "/home/ws/nnUNet_raw/Dataset123_Rectal"
    dst_root = "/home/ws/Projects/RectalDataset_MONAI"   # 新的数据集目录
    label_dict = {"0": "background", "1": "GTVp"}

    # Step 1: 复制目录结构
    copy_structure(src_root, dst_root)

    # Step 2: 去掉 _0000 后缀
    for sub in ["imagesTr", "imagesTs"]:
        rename_files(os.path.join(dst_root, sub))

    # Step 3: 生成新的 rectal_dataset.json
    make_rectal_json(dst_root, train_ratio=0.8, label_dict=label_dict)

    # Step 4: 删除旧的 dataset.json（若存在）
    old_json = os.path.join(dst_root, "dataset.json")
    if os.path.exists(old_json):
        os.remove(old_json)
        print(f"🗑️ 已删除旧的 dataset.json，仅保留 rectal_dataset.json。")

    print("\n🎯 完成：新数据集已生成，可直接用于 MONAI SwinUNETR fine-tuning。")

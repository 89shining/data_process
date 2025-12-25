"""
对 Excel 表进行训练 / 测试数据划分（按分段等比划分）
最终输出：一个 Excel，两个 sheet（train / test）
每个 sheet 列为：放疗号 | 姓名 | 分段 | 淋巴引流区
"""

import pandas as pd
from pathlib import Path

# =========================
# 配置区
# =========================
EXCEL_PATH = r"C:\Users\dell\Desktop\Eso-CTV\ESCC根治性靶区data.xlsx" # 数据excel表
SHEET_NAME = 0
OUT_DIR = Path(r"C:\Users\dell\Desktop\Eso-CTV\20251224")  # 数据划分文件保存

SEED = 2025

# 测试集配额（合计20）
TEST_COUNTS = {
    "颈段": 2,
    "胸上段": 6,
    "胸中段": 7,
    "胸下段": 3,
}

# Excel 列名（中文）
COL_ID = "放疗号"
COL_NAME = "姓名"
COL_SUBSITE = "分段"
COL_LN = "淋巴引流区"


# =========================
# 工具函数
# =========================
def clean_str(x) -> str:
    """清理不可见空白 + strip（兼容 Excel 尾部空格 / 全角空格）"""
    if pd.isna(x):
        return ""
    s = str(x)
    s = s.replace("\u3000", "")
    s = s.replace("\xa0", "")
    s = s.replace("\t", "").replace("\r", "").replace("\n", "")
    return s.strip()


def normalize_subsite_cn(x: str) -> str:
    """
    把“分段”统一成：颈段 / 胸上段 / 胸中段 / 胸下段
    """
    x = clean_str(x).replace(" ", "")
    if x == "":
        return ""
    if x in ["胸上", "胸中", "胸下"]:
        x = x + "段"
    if x == "颈":
        x = "颈段"
    return x


def validate_quota(df: pd.DataFrame, quota: dict):
    for k, n in quota.items():
        have = (df[COL_SUBSITE] == k).sum()
        if have < n:
            raise ValueError(
                f"分段[{k}]数量不足：表中只有 {have} 例，但你要求 test 抽取 {n} 例"
            )


# =========================
# 主流程
# =========================
def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df0 = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)

    # 必要列检查
    for c in [COL_ID, COL_NAME, COL_SUBSITE, COL_LN]:
        if c not in df0.columns:
            raise KeyError(f"Excel 缺少列：{c}，当前列：{list(df0.columns)}")

    # 只取你需要的四列
    df = df0[[COL_ID, COL_NAME, COL_SUBSITE, COL_LN]].copy()

    # 文本清洗
    df[COL_ID] = df[COL_ID].apply(clean_str)
    df[COL_NAME] = df[COL_NAME].apply(clean_str)
    df[COL_SUBSITE] = df[COL_SUBSITE].apply(normalize_subsite_cn)
    df[COL_LN] = df[COL_LN].apply(clean_str)

    # 基本检查
    if (df[COL_ID] == "").any():
        bad = df[df[COL_ID] == ""]
        raise ValueError(f"发现放疗号为空的行：\n{bad.head(20)}")

    if (df[COL_SUBSITE] == "").any():
        bad = df[df[COL_SUBSITE] == ""]
        raise ValueError(
            f"发现分段为空的行（可能是合并单元格/公式空串）：\n{bad.head(20)}"
        )

    if df.duplicated(subset=[COL_ID]).any():
        dup = df[df.duplicated(subset=[COL_ID], keep=False)].sort_values(COL_ID)
        raise ValueError(f"发现放疗号重复：\n{dup}")

    print(f"[Info] 有效病例数：{len(df)}")
    print("[Info] 分段统计：\n", df[COL_SUBSITE].value_counts().to_string())

    # 校验 test 配额
    validate_quota(df, TEST_COUNTS)

    # =========================
    # 分层抽取 test
    # =========================
    test_parts = []
    for subsite, n in TEST_COUNTS.items():
        sub_df = df[df[COL_SUBSITE] == subsite]
        test_parts.append(sub_df.sample(n=n, random_state=SEED))

    test_df = (
        pd.concat(test_parts)
        .sample(frac=1, random_state=SEED)
        .reset_index(drop=True)
    )
    train_df = df[~df[COL_ID].isin(test_df[COL_ID])].reset_index(drop=True)

    print("\n=== Split Summary ===")
    print("Test:\n", test_df[COL_SUBSITE].value_counts().to_string())
    print("Train:\n", train_df[COL_SUBSITE].value_counts().to_string())
    print(f"Train={len(train_df)}, Test={len(test_df)}, Total={len(train_df)+len(test_df)}")

    # =========================
    # 输出 Excel（两个 sheet）
    # =========================
    out_xlsx = OUT_DIR / "train_test_split2.xlsx"
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        train_df[[COL_ID, COL_NAME, COL_SUBSITE, COL_LN]].to_excel(
            writer, sheet_name="train", index=False
        )
        test_df[[COL_ID, COL_NAME, COL_SUBSITE, COL_LN]].to_excel(
            writer, sheet_name="test", index=False
        )

    print("\n Done:", out_xlsx)


if __name__ == "__main__":
    main()

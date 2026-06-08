"""NBA Draft Data Processor

比赛日数据清洗与特征工程模块。
数据格式 6/16 培训解锁后，只需调整 COLUMN_MAPPING 和 FEATURE_COLS 即可运行。

Usage:
    from data_processor import DraftDataProcessor
    processor = DraftDataProcessor()
    df = processor.load("data.csv")
    X, y = processor.preprocess(df)
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Optional, Tuple, List

# ============================================
# TODO 6/16: 数据格式解锁后更新以下映射
# ============================================
COLUMN_MAPPING = {
    # "原始列名": "标准列名"
    "player": "player_name",
    "college": "college",
    "height_in": "height",
    "weight_lbs": "weight",
    # ... 培训后补充
}

TARGET_COL = "pick_number"  # 选秀顺位

DROP_COLS = ["player_name", "college", "team"]  # 非特征列


class DraftDataProcessor:
    """选秀数据处理器 — 比赛日直接复用"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders: dict = {}
        self.feature_names: List[str] = []

    def load(self, path: str) -> pd.DataFrame:
        """加载比赛数据"""
        df = pd.read_csv(path)
        df = df.rename(columns=COLUMN_MAPPING)
        print(f"  [DataProcessor] 加载 {len(df)} 行, {len(df.columns)} 列")
        return df

    def preprocess(self, df: pd.DataFrame, target_col: Optional[str] = TARGET_COL
                   ) -> Tuple[pd.DataFrame, Optional[np.ndarray]]:
        """完整预处理 → X特征矩阵, y目标值"""
        df = df.copy()
        y = df[target_col].values if target_col in df.columns else None

        # 1. 丢弃非特征列
        drop = [c for c in DROP_COLS if c in df.columns]
        if target_col and target_col in df.columns:
            drop.append(target_col)
        X = df.drop(columns=drop, errors="ignore")

        # 2. 只保留数值列 + 低基数分类列
        self.feature_names = []
        for col in X.columns:
            if X[col].dtype in (np.number,):
                self.feature_names.append(col)
            elif X[col].nunique() < 20:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                self.label_encoders[col] = le
                self.feature_names.append(col)

        X = X[self.feature_names]

        # 3. 填充缺失值
        X = X.fillna(X.median() if X.select_dtypes(include=[np.number]).shape[1] > 0 else 0)

        # 4. 特征工程
        X = self._engineer_features(X, df)

        # 5. 标准化
        X_scaled = self.scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

        print(f"  [DataProcessor] 生成 {X_scaled.shape[1]} 个特征, "
              f"{'有' if y is not None else '无'}目标列")
        return X_scaled, y

    def _engineer_features(self, X: pd.DataFrame, raw: pd.DataFrame) -> pd.DataFrame:
        """扩展特征工程 — 按实际数据调整"""
        X = X.copy()

        # 效率指标（如果原始数据包含基础统计）
        if all(c in raw.columns for c in ["pts", "fga", "fta"]):
            X["ts_pct"] = raw["pts"] / (2 * (raw["fga"] + 0.44 * raw["fta"] + 1))

        if all(c in raw.columns for c in ["fgm", "fg3m", "fga"]):
            X["efg_pct"] = (raw["fgm"] + 0.5 * raw["fg3m"]) / raw["fga"].clip(1)

        # 体型指数
        if "height" in X.columns and "weight" in X.columns:
            X["bmi"] = raw["weight"] / ((raw["height"] / 39.37) ** 2 + 1)

        # 年龄特征
        if "age" in X.columns:
            X["young_talent"] = ((raw["age"] <= 20).astype(int))

        return X

    def transform_new(self, df: pd.DataFrame) -> pd.DataFrame:
        """用已有 scaler/encoder 处理新数据（预测时用）"""
        X, _ = self.preprocess(df, target_col=None)
        return X

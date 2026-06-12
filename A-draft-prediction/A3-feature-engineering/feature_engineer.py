"""NBA Draft Feature Engineer

选秀预测特征工程模块 — 基于原始体测+统计数据生成模型特征。
与 data_processor 配合，提供 P0/P1/P2 三级特征。

Usage:
    from feature_engineer import FeatureEngineer
    fe = FeatureEngineer()
    X = fe.create_features(df)     # 全部特征
    X = fe.create_p0_features(df)  # 仅基础特征（比赛日保底）
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional


class FeatureEngineer:
    """选秀预测特征工程"""

    # ============================================
    # P0: 基础特征（所有数据集必有，优先计算）
    # ============================================

    @staticmethod
    def p0_basic_measurements(df: pd.DataFrame) -> pd.DataFrame:
        """体测基础特征"""
        out = pd.DataFrame(index=df.index)

        if "height" in df.columns:
            out["height_cm"] = df["height"] * 2.54
        if "weight" in df.columns and "height" in df.columns:
            out["bmi"] = df["weight"] / ((df["height"] / 39.37) ** 2)
        if "wingspan" in df.columns and "height" in df.columns:
            out["wingspan_minus_height"] = df["wingspan"] - df["height"]
        if "standing_reach" in df.columns and "height" in df.columns:
            out["reach_advantage"] = df["standing_reach"] - df["height"]

        return out

    @staticmethod
    def p0_age_features(df: pd.DataFrame) -> pd.DataFrame:
        """年龄基础特征"""
        out = pd.DataFrame(index=df.index)

        if "age" in df.columns:
            out["age"] = df["age"]
            out["age_squared"] = df["age"] ** 2
            out["is_young"] = (df["age"] <= 20).astype(int)
            out["is_old"] = (df["age"] >= 23).astype(int)

        if "years_in_college" in df.columns:
            out["is_freshman"] = (df["years_in_college"] == 1).astype(int)
            out["is_sophomore"] = (df["years_in_college"] == 2).astype(int)
            out["is_upperclassman"] = (df["years_in_college"] >= 3).astype(int)

        return out

    # ============================================
    # P1: 效率特征（有box score数据时计算）
    # ============================================

    @staticmethod
    def p1_efficiency_features(df: pd.DataFrame) -> pd.DataFrame:
        """效率指标特征"""
        out = pd.DataFrame(index=df.index)

        # 真实命中率
        if all(c in df.columns for c in ["pts", "fga", "fta"]):
            denom = 2 * (df["fga"] + 0.44 * df["fta"])
            out["ts_pct"] = np.where(denom > 0, df["pts"] / denom, 0)

        # 有效命中率
        if all(c in df.columns for c in ["fgm", "fg3m", "fga"]):
            denom = df["fga"].clip(1)
            out["efg_pct"] = (df["fgm"] + 0.5 * df["fg3m"]) / denom

        # 失误比
        if all(c in df.columns for c in ["ast", "tov"]):
            out["ast_tov_ratio"] = np.where(
                df["tov"] > 0, df["ast"] / df["tov"], df["ast"]
            )

        # 抢断+盖帽防守指标
        if all(c in df.columns for c in ["stl", "blk"]):
            out["defensive_impact"] = df["stl"] * 2 + df["blk"] * 2

        # 每40分钟标准化
        if "mp" in df.columns:
            for col in ["pts", "reb", "ast", "stl", "blk"]:
                if col in df.columns:
                    out[f"{col}_per_40"] = np.where(
                        df["mp"] > 0, df[col] / df["mp"] * 40, 0
                    )

        return out

    @staticmethod
    def p1_scoring_features(df: pd.DataFrame) -> pd.DataFrame:
        """得分相关特征"""
        out = pd.DataFrame(index=df.index)

        # 三分产量
        if all(c in df.columns for c in ["fg3a", "fga"]):
            out["three_point_rate"] = np.where(
                df["fga"] > 0, df["fg3a"] / df["fga"], 0
            )

        # 罚球率（侵略性指标）
        if all(c in df.columns for c in ["fta", "fga"]):
            out["fta_rate"] = np.where(
                df["fga"] > 0, df["fta"] / df["fga"], 0
            )

        # 投篮分布
        if all(c in df.columns for c in ["fg2a", "fg3a", "fga"]):
            out["two_point_rate"] = np.where(
                df["fga"] > 0, df["fg2a"] / df["fga"], 0
            )

        return out

    # ============================================
    # P2: 进阶特征（有详细数据时计算）
    # ============================================

    @staticmethod
    def p2_contextual_features(df: pd.DataFrame) -> pd.DataFrame:
        """背景/上下文特征"""
        out = pd.DataFrame(index=df.index)

        # 联盟强度
        if "conference" in df.columns:
            power_5 = ["ACC", "Big 12", "Big East", "Big Ten",
                       "Pac-12", "SEC", "Pac 12", "Big Ten Conference"]
            out["is_power_5"] = df["conference"].isin(power_5).astype(int)

        # 位置编码
        if "position" in df.columns:
            positions = ["PG", "SG", "SF", "PF", "C"]
            for pos in positions:
                out[f"pos_{pos}"] = (df["position"] == pos).astype(int)

        # 位置身高偏差（相对于平均身高）
        if all(c in df.columns for c in ["position", "height"]):
            pos_mean_height = df.groupby("position")["height"].transform("mean")
            out["height_vs_position"] = df["height"] - pos_mean_height

        return out

    # ============================================
    # 组合管道
    # ============================================

    def create_features(self, df: pd.DataFrame, tiers: str = "all") -> pd.DataFrame:
        """生成全部特征

        Args:
            df: 原始数据 DataFrame
            tiers: "all" | "p0" | "p0_p1" — 控制特征深度

        Returns:
            特征 DataFrame
        """
        features = []

        # P0 始终计算
        features.append(self.p0_basic_measurements(df))
        features.append(self.p0_age_features(df))
        features.append(self._binary_school_target(df))

        if tiers in ("p0_p1", "all"):
            features.append(self.p1_efficiency_features(df))
            features.append(self.p1_scoring_features(df))

        if tiers == "all":
            features.append(self.p2_contextual_features(df))

        return pd.concat(features, axis=1)

    def _binary_school_target(self, df: pd.DataFrame) -> pd.DataFrame:
        """学校声望（可选扩展）"""
        out = pd.DataFrame(index=df.index)
        # 简单版本：仅标注是否来自顶级篮球学校
        if "college" in df.columns:
            elite = ["Duke", "Kentucky", "North Carolina", "Kansas",
                     "UCLA", "Arizona", "Gonzaga", "Villanova", "UConn"]
            out["is_elite_school"] = df["college"].isin(elite).astype(int)
        return out

    @staticmethod
    def get_level_report() -> Dict[str, List[str]]:
        """返回按优先级分组的特征列表"""
        return {
            "P0 (必选)": [
                "height_cm", "bmi", "wingspan_minus_height",
                "age", "age_squared", "is_young", "is_freshman",
            ],
            "P1 (推荐)": [
                "ts_pct", "efg_pct", "ast_tov_ratio", "defensive_impact",
                "pts_per_40", "reb_per_40", "three_point_rate",
            ],
            "P2 (锦上添花)": [
                "is_power_5", "pos_*", "height_vs_position", "is_elite_school",
            ],
        }


# 快捷函数
def add_features(df: pd.DataFrame, tiers: str = "all") -> pd.DataFrame:
    """给 DataFrame 添加特征列，直接返回增强后的表"""
    fe = FeatureEngineer()
    features = fe.create_features(df, tiers=tiers)
    return pd.concat([df, features], axis=1)

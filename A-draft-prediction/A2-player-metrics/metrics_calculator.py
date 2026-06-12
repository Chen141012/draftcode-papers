"""NBA Player Metrics Calculator

球员评估指标计算模块 — 基于基础统计数据计算各类效率指标。
比赛日直接 import 到 data_processor 或独立使用。

Usage:
    from metrics_calculator import MetricsCalculator
    calc = MetricsCalculator()
    result = calc.compute_all(pts=20, fga=15, fta=5, ...)
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional


class MetricsCalculator:
    """球员评估指标计算器"""

    # ============================================
    # 第一类：效率指标
    # ============================================

    @staticmethod
    def true_shooting(pts: float, fga: float, fta: float) -> float:
        """真实命中率 TS% — 最准确的得分效率指标"""
        denom = 2 * (fga + 0.44 * fta)
        return pts / denom if denom > 0 else 0.0

    @staticmethod
    def effective_fg(fgm: float, fg3m: float, fga: float) -> float:
        """有效命中率 eFG% — 调整三分权重的命中率"""
        denom = fga if fga > 0 else 1
        return (fgm + 0.5 * fg3m) / denom

    @staticmethod
    def game_score(pts: float, reb: float, ast: float, stl: float,
                   blk: float, fgm: float, fga: float, ftm: float,
                   fta: float, tov: float, pf: float = 0) -> float:
        """单场比赛效率评分（Hollinger's Game Score）"""
        return (pts + 0.4 * fgm - 0.7 * fga - 0.4 * (fta - ftm)
                + 0.7 * reb + 0.3 * ast + stl + 0.7 * blk
                - 0.4 * tov - pf)

    @staticmethod
    def per_simple(pts: float, reb: float, ast: float, stl: float,
                   blk: float, tov: float, fga: float, fta: float,
                   missed_fg: float, missed_ft: float, mp: float = 1) -> float:
        """简版 PER（每分钟标准化）— 完整PER需要联赛平均调整"""
        positive = pts + reb + ast + stl + blk
        negative = (fga - missed_fg) + (fta - missed_ft) + tov
        return (positive - negative * 0.5) / max(mp, 1)

    # ============================================
    # 第二类：率指标（标准化后）
    # ============================================

    @staticmethod
    def assist_ratio(ast: float, fgm: float, fga: float, ft_attempts: float = 0) -> float:
        """助攻率 — 助攻占队友进球比例"""
        denom = fga + 0.44 * ft_attempts
        return ast / denom if denom > 0 else 0.0

    @staticmethod
    def turnover_ratio(tov: float, fga: float, fta: float) -> float:
        """失误率 — 每次出手的失误比例"""
        denom = fga + 0.44 * fta
        return tov / denom if denom > 0 else 0.0

    @staticmethod
    def usage_rate(fga: float, fta: float, tov: float,
                   mp: float, team_possessions: float = 100) -> float:
        """使用率 — 球员在场时终结回合的比例"""
        numerator = fga + 0.44 * fta + tov
        return (numerator / mp) * team_possessions if mp > 0 else 0.0

    # ============================================
    # 第三类：综合指标（用于选秀评估）
    # ============================================

    @staticmethod
    def scoring_efficiency_index(pts: float, fga: float, fta: float,
                                  fgm: float, fg3m: float) -> float:
        """得分效率指数 — 结合真实命中率和得分产量"""
        ts = MetricsCalculator.true_shooting(pts, fga, fta)
        return ts * pts

    @staticmethod
    def prospect_score(pts: float, reb: float, ast: float, stl: float,
                        blk: float, tov: float, fg3_pct: float,
                        height: float, age: float) -> float:
        """选秀潜力评分（简易版）— 值越高前景越好

        权重设计：
        - 三分效率：30%（现代NBA最看重）
        - 得分产量：20%
        - 体型：15%
        - 年龄优势：15%（越年轻分越高）
        - 防守贡献：10%
        - 组织能力：10%
        """
        score = (
            fg3_pct * 100 * 0.3            # 三分效率
            + pts * 0.5 * 0.2               # 得分产量
            + (height - 72) * 2 * 0.15      # 体型优势(超过6尺)
            + max(0, 22 - age) * 0.15       # 年龄优势(越年轻越好)
            + (stl + blk) * 2 * 0.10        # 防守贡献
            + ast * 0.5 * 0.10              # 组织能力
            - tov * 0.5                     # 失误扣分
        )
        return round(max(0, score), 1)

    # ============================================
    # 批量计算（DataFrame）
    # ============================================

    def compute_all(self, pts: float = 0, fga: float = 0, fta: float = 0,
                    fgm: float = 0, fg3m: float = 0, fg3a: float = 0,
                    ftm: float = 0, reb: float = 0, ast: float = 0,
                    stl: float = 0, blk: float = 0, tov: float = 0,
                    pf: float = 0, height: float = 78, age: float = 21,
                    mp: float = 30) -> Dict[str, float]:
        """单球员计算全部指标"""
        fgm_est = fgm if fgm > 0 else pts * 0.4  # 如果没有直接提供，估算
        return {
            "ts_pct": round(self.true_shooting(pts, fga, fta), 3),
            "efg_pct": round(self.effective_fg(fgm_est, fg3m, fga), 3),
            "game_score": round(self.game_score(pts, reb, ast, stl, blk,
                                                 fgm_est, fga, ftm, fta, tov, pf), 1),
            "per_simple": round(self.per_simple(pts, reb, ast, stl, blk,
                                                 tov, fga, fta,
                                                 fga - fgm_est, fta - ftm, mp), 1),
            "scoring_efficiency": round(self.scoring_efficiency_index(
                pts, fga, fta, fgm_est, fg3m), 1),
            "prospect_score": self.prospect_score(
                pts, reb, ast, stl, blk, tov,
                fg3m / fg3a if fg3a > 0 else 0,
                height, age),
        }

    def compute_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """批量计算DataFrame中所有球员的指标

        期望列: pts, fga, fta, fgm, fg3m, fg3a, ftm, reb, ast, stl, blk, tov, pf, height, age, mp
        """
        results = []
        for _, row in df.iterrows():
            try:
                r = self.compute_all(
                    pts=row.get("pts", 0), fga=row.get("fga", 0),
                    fta=row.get("fta", 0), fgm=row.get("fgm", 0),
                    fg3m=row.get("fg3m", 0), fg3a=row.get("fg3a", 0),
                    ftm=row.get("ftm", 0), reb=row.get("reb", 0),
                    ast=row.get("ast", 0), stl=row.get("stl", 0),
                    blk=row.get("blk", 0), tov=row.get("tov", 0),
                    pf=row.get("pf", 0), height=row.get("height", 78),
                    age=row.get("age", 21), mp=row.get("mp", 30),
                )
                results.append(r)
            except Exception:
                results.append({k: None for k in [
                    "ts_pct", "efg_pct", "game_score", "per_simple",
                    "scoring_efficiency", "prospect_score"
                ]})
        return pd.DataFrame(results, index=df.index)


# 快捷函数
def add_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """给 DataFrame 添加球员指标列，直接返回增强后的表"""
    calc = MetricsCalculator()
    metrics = calc.compute_dataframe(df)
    return pd.concat([df, metrics], axis=1)

"""NBA Draft Prediction Pipeline

XGBoost 选秀预测训练 + 推理模块。
与 data_processor.py 配合使用（data_processor → pipeline）。

Usage:
    from draft_pipeline import DraftPredictor, run_draft_pipeline
    model, metrics = run_draft_pipeline("data.csv")
    model.save("draft_model.json")
"""

import pandas as pd
import numpy as np
import json
import os
from typing import Dict, Optional, Tuple

import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from data_processor import DraftDataProcessor


class DraftPredictor:
    """选秀顺位预测器 — XGBoost 回归"""

    def __init__(self):
        self.model: Optional[xgb.XGBRegressor] = None
        self.feature_importance: Optional[pd.DataFrame] = None

    def build_model(self, **kwargs) -> xgb.XGBRegressor:
        """创建 XGBoost 模型，支持覆盖默认参数"""
        defaults = dict(
            n_estimators=500,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.7,
            min_child_weight=3,
            reg_alpha=1.0,
            reg_lambda=1.0,
            random_state=42,
            early_stopping_rounds=30,
            eval_metric="mae",
        )
        defaults.update(kwargs)
        self.model = xgb.XGBRegressor(**defaults)
        return self.model

    def train(self, X_train: pd.DataFrame, y_train: np.ndarray,
              X_val: Optional[pd.DataFrame] = None,
              y_val: Optional[np.ndarray] = None) -> Dict:
        """训练模型"""
        eval_set = [(X_train, y_train)]
        if X_val is not None and y_val is not None:
            eval_set.append((X_val, y_val))

        self.model.fit(X_train, y_train, eval_set=eval_set, verbose=False)

        # 特征重要性
        names = getattr(self.model, "feature_names_in_",
                        [f"f{i}" for i in range(len(self.model.feature_importances_))])
        self.feature_importance = pd.DataFrame({
            "feature": names,
            "importance": self.model.feature_importances_
        }).sort_values("importance", ascending=False)

        return {"best_iteration": getattr(self.model, "best_iteration", None)}

    def evaluate(self, X_test: pd.DataFrame, y_test: np.ndarray) -> Dict:
        """评估模型"""
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        return {
            "mae": round(float(mae), 2),
            "r2": round(float(r2_score(y_test, y_pred)), 4),
            "samples": len(y_test),
        }

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """预测顺位"""
        return self.model.predict(X)

    def predict_teams(self, X: pd.DataFrame, player_names: np.ndarray,
                      team_map: Dict[str, List[int]]) -> Dict[str, list]:
        """预测各队选秀结果"""
        picks = self.model.predict(X)
        results = {}
        for team, indices in team_map.items():
            team_picks = sorted(zip(player_names[indices], picks[indices]),
                                key=lambda x: x[1])
            results[team] = [
                {"player": p, "predicted_pick": int(round(pick))}
                for p, pick in team_picks[:3]
            ]
        return results

    def save(self, path: str):
        """保存模型"""
        self.model.save_model(path)
        print(f"  [DraftPredictor] 模型已保存: {path}")

    def load(self, path: str):
        """加载已训练的模型"""
        self.model = xgb.XGBRegressor()
        self.model.load_model(path)
        print(f"  [DraftPredictor] 模型已加载: {path}")


def run_draft_pipeline(data_path: str, output_dir: str = "./output") -> Tuple[DraftPredictor, Dict]:
    """一键运行选秀预测全流程"""
    os.makedirs(output_dir, exist_ok=True)
    print(f"[Pipeline] 数据: {data_path}")

    # Step 1: 数据处理
    processor = DraftDataProcessor()
    df = processor.load(data_path)
    X, y = processor.preprocess(df)
    print(f"[Pipeline] 特征矩阵: {X.shape}")

    # Step 2: 训练/测试划分
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"[Pipeline] 训练: {len(X_train)} 测试: {len(X_test)}")

    # Step 3: 训练
    predictor = DraftPredictor()
    predictor.build_model()
    train_info = predictor.train(X_train, y_train, X_test, y_test)

    # Step 4: 评估
    metrics = predictor.evaluate(X_test, y_test)
    print(f"[Pipeline] MAE={metrics['mae']} R²={metrics['r2']}")

    # Step 5: 保存
    predictor.save(os.path.join(output_dir, "draft_model.json"))
    with open(os.path.join(output_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f)
    predictor.feature_importance.to_csv(
        os.path.join(output_dir, "feature_importance.csv"), index=False
    )

    return predictor, metrics


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "nba_draft_data.csv"
    model, metrics = run_draft_pipeline(path)
    print(f"\n✅ 管道完成。MAE: {metrics['mae']}")

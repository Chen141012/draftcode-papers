# 选秀预测模型训练模板

> 比赛日数据解锁后直接用的 ML 训练管道模板。
> 基于 XGBoost + scikit-learn，涵盖数据加载→训练→评估→预测全流程。

## 来源参考

- Deepnote: Predicting 2023 NBA Draft — https://deepnote.com/@austin-jeong/Predicting-2023-NBA-Draft
- TDS: NBA Draft Analysis Using ML — https://towardsdatascience.com/nba-draft-analysis-using-machine-learning-to-project-nba-success-a1c6bf576d19
- XGBoost sklearn 接口 — https://xgboost.readthedocs.io/en/latest/python/sklearn_estimator.html

## 完整训练管道

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb
import json

# ============================================
# 1. 数据加载
# ============================================
def load_draft_data(csv_path: str) -> pd.DataFrame:
    """加载选秀数据，识别特征列和目标列"""
    df = pd.read_csv(csv_path)
    print(f"加载数据: {df.shape[0]} 行, {df.shape[1]} 列")
    print(f"列名: {list(df.columns)}")
    return df

# ============================================
# 2. 预处理
# ============================================
def preprocess_data(df: pd.DataFrame, target_col: str = "pick_number",
                    drop_cols: list = None) -> tuple:
    """
    基础预处理：处理缺失值、分离特征和目标
    drop_cols: 要排除的列（如 'player_name', 'team' 等非特征列）
    """
    df = df.copy()
    
    if drop_cols is None:
        drop_cols = ["player_name", "team", "college"]
    
    # 只保留实际存在的列
    drop_cols = [c for c in drop_cols if c in df.columns]
    if target_col in df.columns and target_col not in drop_cols:
        drop_cols = drop_cols + [target_col]
    
    # 分离特征和目标
    y = df[target_col].values if target_col in df.columns else None
    X = df.drop(columns=drop_cols, errors="ignore")
    
    # 只保留数值列
    numeric_cols = X.select_dtypes(include=[np.number]).columns
    X = X[numeric_cols]
    
    # 填充缺失值
    X = X.fillna(X.median())
    
    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns)
    
    print(f"特征数: {X_scaled.shape[1]}")
    print(f"特征: {list(X.columns)}")
    return X_scaled, y, scaler

# ============================================
# 3. 模型训练 (XGBoost)
# ============================================
def train_xgboost(X_train, y_train, X_val=None, y_val=None):
    """
    训练 XGBoost 回归模型
    目标：预测选秀顺位（1-60）
    """
    model = xgb.XGBRegressor(
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
        eval_metric="mae"
    )
    
    eval_set = [(X_train, y_train)]
    if X_val is not None and y_val is not None:
        eval_set.append((X_val, y_val))
    
    model.fit(
        X_train, y_train,
        eval_set=eval_set,
        verbose=False
    )
    
    return model

# ============================================
# 4. 评估
# ============================================
def evaluate_model(model, X_test, y_test):
    """模型评估"""
    y_pred = model.predict(X_test)
    
    metrics = {
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "r2": float(r2_score(y_test, y_pred)),
        "avg_error_picks": float(np.mean(np.abs(y_pred - y_test)))
    }
    
    print(f"MAE (平均误差顺位): {metrics['mae']:.2f}")
    print(f"R²: {metrics['r2']:.3f}")
    print(f"平均偏差顺位: {metrics['avg_error_picks']:.2f}")
    
    # 特征重要性
    importance = pd.DataFrame({
        "feature": model.feature_names_in_ if hasattr(model, "feature_names_in_") else range(len(model.feature_importances_)),
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)
    
    print("\nTop 10 最重要特征:")
    print(importance.head(10).to_string(index=False))
    
    return metrics, importance

# ============================================
# 5. 完整管道
# ============================================
def run_draft_pipeline(csv_path: str, target_col: str = "pick_number"):
    """一键运行完整选秀预测管道"""
    
    # 加载
    df = load_draft_data(csv_path)
    
    # 预处理
    X, y, scaler = preprocess_data(df, target_col)
    
    # 划分
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 训练
    model = train_xgboost(X_train, y_train, X_test, y_test)
    
    # 评估
    metrics, importance = evaluate_model(model, X_test, y_test)
    
    return model, scaler, metrics, importance

# ============================================
# 6. 预测新球员
# ============================================
def predict_prospects(model, scaler, new_player_data: pd.DataFrame):
    """
    预测新球员的选秀顺位
    
    Args:
        model: 训练好的模型
        scaler: 训练时用的 StandardScaler
        new_player_data: 新球员的特征 DataFrame
    """
    X_new = scaler.transform(new_player_data)
    predictions = model.predict(X_new)
    
    results = pd.DataFrame({
        "predicted_pick": np.round(predictions).astype(int),
        "confidence_score": 1.0 / (1.0 + np.abs(predictions - np.round(predictions)))
    })
    
    return results.sort_values("predicted_pick")

# ============================================
# 7. 各队选秀预测（30队）
# ============================================
def predict_all_teams(model, scaler, team_players_dict: dict):
    """
    预测30支球队的首轮选秀
    
    Args:
        model: 训练好的模型
        scaler: StandardScaler
        team_players_dict: {team_name: DataFrame_of_player_features}
    
    Returns:
        {team: [(player, pick), ...]} 按顺位排序
    """
    all_results = {}
    for team, players_df in team_players_dict.items():
        preds = predict_prospects(model, scaler, players_df)
        players_df["predicted_pick"] = preds["predicted_pick"].values
        all_results[team] = players_df.sort_values("predicted_pick")[
            ["player_name", "predicted_pick"]
        ].head(1).to_dict("records")
    return all_results

# ============================================
# 使用示例（比赛日）
# ============================================
if __name__ == "__main__":
    # 比赛日 09:00 数据解锁后：
    # model, scaler, metrics, feat_imp = run_draft_pipeline("nba_draft_2026.csv")
    # 
    # # 输出评估结果到 JSON
    # with open("model_metrics.json", "w") as f:
    #     json.dump(metrics, f)
    # 
    # # 保存模型
    # model.save_model("draft_predictor.json")
    # 
    # # 预测新球员
    # new_prospects = pd.read_csv("prospects_2026.csv")
    # results = predict_prospects(model, scaler, new_prospects)
    # results.to_csv("predicted_draft_order.csv", index=False)
    # 
    # print("✅ 预测完成，结果已保存")
    pass
```

## 模型选型建议

| 模型 | 优点 | 适合场景 |
|------|------|---------|
| XGBoost | 稳定可靠，调参友好，有早停防止过拟合 | 🥇 **首选，比赛日默认用这个** |
| LightGBM | 训练更快，自带类别特征处理 | 数据量大时（10w+行）的备选 |
| Random Forest | 不需要调参，开箱即用 | 快速基线模型，几分钟出结果 |
| Gradient Boosting | sklearn内置，零依赖 | 如果不让装 xgboost/lgbm 的兜底方案 |

## 比赛日 Quickstart

```bash
# 1. 装依赖
pip install xgboost scikit-learn pandas numpy

# 2. 跑管道
python3 -c "
from draft_pipeline import run_draft_pipeline
model, scaler, metrics, imp = run_draft_pipeline('nba_draft_data.csv')
print('模型已训练，MAE:', metrics['mae'])
"
```

> 核心逻辑就一个：`XGBoost` 读数据 → 训练 → 预测30队选秀结果。24小时内数据清洗花的时间会比训练多得多。

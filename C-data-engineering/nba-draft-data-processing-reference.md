# NBA 选秀数据处理参考

> 比赛核心数据：26 年 NBA 选秀历史数据。比赛日 06.16 培训解锁数据格式。
> 此处先准备好数据处理框架，数据下来后直接套用。

## 关键参考

- **NBA Draft ML 分析教程 (TDS)**: https://towardsdatascience.com/nba-draft-analysis-using-machine-learning-to-project-nba-success-a1c6bf576d19
- **Kaggle NBA 特征选择**: https://www.kaggle.com/code/noobiedatascientist/feature-selection-in-the-nba
- **Sports Analytics ETL 示例**: Python + Pandas + SQLAlchemy，清洗 NBA/MLB 数据

## 数据预处理框架

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

class DraftDataProcessor:
    """选秀数据处理器 — 比赛日直接复用"""
    
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
    
    def load_data(self, filepath):
        """加载比赛数据"""
        return pd.read_csv(filepath)
    
    def preprocess(self, df):
        """完整预处理流程"""
        df = self._clean_basics(df)
        df = self._encode_categorical(df)
        df = self._create_features(df)
        df = self._normalize(df)
        return df
    
    def _clean_basics(self, df):
        """基础清洗"""
        df = df.copy()
        # 缺失值处理
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].median())
        # 字符串列
        str_cols = df.select_dtypes(include=['object']).columns
        for col in str_cols:
            df[col] = df[col].fillna('Unknown')
        return df
    
    def _encode_categorical(self, df):
        """分类变量编码"""
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
            else:
                df[col] = self.label_encoders[col].transform(df[col].astype(str))
        return df
    
    def _create_features(self, df):
        """特征工程 — 根据实际字段调整"""
        # 年龄相关
        if 'age' in df.columns:
            df['age_squared'] = df['age'] ** 2
            df['age_experience'] = df['age'] - 19  # 相对于标准选秀年龄
        
        # 效率指标
        if all(col in df.columns for col in ['pts', 'reb', 'ast']):
            df['efficiency'] = df['pts'] + 1.2 * df['reb'] + 1.5 * df['ast']
        
        return df
    
    def _normalize(self, df):
        """归一化（仅数值特征）"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        # 排除 ID 列
        exclude = [c for c in df.columns if 'id' in c.lower()]
        to_scale = [c for c in numeric_cols if c not in exclude]
        
        df_scaled = df.copy()
        df_scaled[to_scale] = self.scaler.fit_transform(df[to_scale])
        return df_scaled

# 使用方式
# processor = DraftDataProcessor()
# data = processor.load_data("nba_draft_2026.csv")
# processed = processor.preprocess(data)
```

## 预测模型示例

```python
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error

class DraftPredictor:
    """选秀顺位预测器"""
    
    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
    
    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
        
    def predict(self, X):
        return self.model.predict(X)
    
    def predict_with_confidence(self, X):
        """带置信度的预测"""
        preds = []
        for estimator in self.model.estimators_:
            preds.append(estimator.predict(X))
        preds = np.array(preds)
        
        mean_pred = preds.mean(axis=0)
        std_pred = preds.std(axis=0)
        
        return mean_pred, std_pred
```

## 数据流设计（比赛日）

```
原始数据 (CSV from S3)
    │
    ▼
DataProcessor.preprocess()
    │
    ├── 清洗（缺失值、异常值、格式统一）
    ├── 编码（分类变量 → 数值）
    ├── 特征工程（领域特定特征）
    └── 归一化
    │
    ▼
特征矩阵
    │
    ▼
DraftPredictor.train() 或 predict()
    │
    ▼
30支球队完整结果
    │
    ▼
Web Agent 可视化展示
```

## 注意事项

1. **06.16 培训后才解锁数据格式** — 上面的处理器是通用框架，届时微调
2. **模型方案也在培训后才清楚** — 先准备好 pipeline，等数据来了直接跑
3. **比赛评分 40% 命中率** — 模型选型很重要，但当前阶段先把管道搭好

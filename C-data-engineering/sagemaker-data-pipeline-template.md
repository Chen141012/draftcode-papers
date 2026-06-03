# SageMaker 数据流水线模板

> 比赛日数据工程的核心"厨具"：数据清洗 → 特征工程 → 模型训练全流程。
> 基于 AWS SageMaker Pipelines 搭建，数据一下来就能跑。

## 来源

- **官方模板 (GitHub)**: https://github.com/aws-samples/amazon-sagemaker-automated-feature-transformation
- **SageMaker Data Wrangler**: https://aws.amazon.com/sagemaker/ai/data-wrangler
- **Processing Jobs 模板**: https://medium.com/@muppedaanvesh/simple-data-processing-with-amazon-sagemaker-processing-jobs-c5a2b2f59caf

## 1. SageMaker Pipeline 全流程模板

```python
import sagemaker
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
from sagemaker.processing import FrameworkProcessor
from sagemaker.sklearn.processing import SKLearnProcessor

# 1. 数据清洗
data_clean_processor = SKLearnProcessor(
    framework_version="1.2-1",
    role=sagemaker.get_execution_role(),
    instance_type="ml.m5.large",
    instance_count=1,
)

step_clean = ProcessingStep(
    name="CleanDraftData",
    processor=data_clean_processor,
    code="scripts/clean_data.py",
    inputs=[ProcessingInput(source="s3://bucket/raw/", destination="/opt/ml/processing/input")],
    outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination="s3://bucket/cleaned/")],
)

# 2. 特征工程
step_features = ProcessingStep(
    name="FeatureEngineering",
    processor=data_clean_processor,
    code="scripts/feature_engineering.py",
    inputs=[ProcessingInput(source=step_clean.properties.ProcessingOutputConfig.Outputs["output"].S3Output.S3Uri,
                           destination="/opt/ml/processing/input")],
    outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination="s3://bucket/features/")],
)

# 3. Pipeline 定义
pipeline = Pipeline(
    name="NBA-Draft-Data-Pipeline",
    steps=[step_clean, step_features],
)
```

## 2. 数据清洗脚本模板 (clean_data.py)

```python
import pandas as pd
import numpy as np
import json
import os

def clean_draft_data(input_path, output_path):
    # 读取原始数据
    df = pd.read_csv(os.path.join(input_path, "draft_data.csv"))
    
    # 基础清洗
    # 1. 处理缺失值
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna('Unknown')
    
    # 2. 异常值检测
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
        df[col] = df[col].clip(lower, upper)
    
    # 3. 生成数据质量报告
    quality_report = {
        "total_rows": len(df),
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_stats": df.describe().to_dict()
    }
    
    with open(os.path.join(output_path, "quality_report.json"), "w") as f:
        json.dump(quality_report, f, default=str)
    
    df.to_csv(os.path.join(output_path, "cleaned_draft_data.csv"), index=False)

if __name__ == "__main__":
    clean_draft_data("/opt/ml/processing/input", "/opt/ml/processing/output")
```

## 3. 特征工程脚本模板 (feature_engineering.py)

```python
import pandas as pd
import numpy as np
import os

def engineer_features(input_path, output_path):
    df = pd.read_csv(os.path.join(input_path, "cleaned_draft_data.csv"))
    
    features = pd.DataFrame()
    features["player_id"] = df["player_id"]
    
    # 核心特征组
    # 1. 球员基础数据特征
    if "height" in df.columns:
        features["height_cm"] = df["height"] * 2.54  # 英寸转厘米
    
    if "weight" in df.columns:
        features["weight_kg"] = df["weight"] * 0.453592
    
    if "age" in df.columns:
        features["age_at_draft"] = df["age"]
        features["age_squared"] = df["age"] ** 2
    
    # 2. 大学表现特征
    college_stat_cols = ["pts", "reb", "ast", "stl", "blk", "fg_pct", "three_pct", "ft_pct"]
    for col in college_stat_cols:
        if col in df.columns:
            features[f"college_{col}"] = df[col]
    
    # 3. 组合特征
    if all(c in df.columns for c in ["pts", "reb", "ast"]):
        features["usage_score"] = df["pts"] + 1.2 * df["reb"] + 1.5 * df["ast"]
    
    # 4. 分类变量编码
    categorical_cols = ["position", "conference", "school"]
    for col in categorical_cols:
        if col in df.columns:
            features = pd.concat([
                features,
                pd.get_dummies(df[col], prefix=col)
            ], axis=1)
    
    # 保存特征
    features.to_csv(os.path.join(output_path, "features.csv"), index=False)
    
    # 特征清单报告
    feature_list = [c for c in features.columns if c != "player_id"]
    with open(os.path.join(output_path, "feature_list.txt"), "w") as f:
        f.write("\n".join(feature_list))

if __name__ == "__main__":
    engineer_features("/opt/ml/processing/input", "/opt/ml/processing/output")
```

## 4. 比赛日数据工程流程

```
06.23 09:00 数据解锁
  ↓
Step 1: 数据加载（S3 → SageMaker）
  ↓
Step 2: 数据清洗（质量报告 + 异常处理）
  ↓
Step 3: 特征工程（基础特征 + 领域特定特征）
  ↓
Step 4: 模型训练（LightGBM / XGBoost / 集成）
  ↓
Step 5: 预测输出（30 支球队首轮选秀结果）
  ↓
Step 6: 可视化（Web Agent 展示预测结果）
```

## 5. 关键工具

| 工具 | 用途 | 适合 |
|------|------|------|
| SageMaker Data Wrangler | 可视化数据准备，300+内置变换 | 快速探索数据 |
| SageMaker Processing Jobs | 可复现的批量数据处理 | 正式数据清洗 |
| SageMaker Feature Store | 特征存储和共享 | 多模型复用特征 |
| SageMaker Pipelines | 全流程自动化 | 端到端ML流水线 |
| SageMaker Autopilot | 自动ML（训练+调参） | 快速基线模型 |

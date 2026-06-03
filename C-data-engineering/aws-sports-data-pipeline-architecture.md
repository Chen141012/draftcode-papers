# Building a Data Pipeline for Tracking Sporting Events Using AWS Services

> **来源**: AWS Architecture Blog
> **链接**: https://aws.amazon.com/blogs/architecture/building-a-data-pipeline-for-tracking-sporting-events-using-aws-services/
> **作者**: Ashwini Rudra, Nick McCabe, Vivek Kumar (AWS)

## 为什么选这篇

IO 数据采集→流式处理→特征工程→模型训练→实时预测的全链路架构参考。比赛用 26 年 NBA 选秀数据，虽然不需要实时 IoT 采集，但**数据处理到模型预测的 AWS 架构设计**可以直接套用。

## 核心架构

### 数据流水线（三段）

```
1. 赛场端采集（IoT传感器 / RFID）
   ↓ Kinesis Data Streams
2. AWS 处理层
   ├── Kinesis Data Firehose → S3（原始数据存储）
   ├── Kinesis Data Analytics（流式分析）
   ├── AWS Lambda（数据转换）
   └── SageMaker Data Wrangler（特征工程）
   ↓
3. 模型训练与预测
   ├── SageMaker（模型训练）
   ├── API Gateway + Lambda（推理接口）
   └── SageMaker Endpoint（实时预测）
```

### 特征工程流程（SageMaker Data Wrangler）

```
原始数据 → S3
    ↓
SageMaker Data Wrangler（可视化界面）
    ├── 数据变换
    ├── 删除无关列
    ├── 缺失值填充
    ├── Label Encoding
    └── Quick Model（快速验证特征预测力）
    ↓
特征矩阵 → SageMaker 训练
```

## 比赛中的复用方式

虽然比赛数据不是实时 IoT，但架构中的 **S3 → Data Wrangler → SageMaker → API Gateway** 链路可以直接迁移：

```
比赛日 09:00 数据解锁
    ↓
数据存入 S3
    ↓
SageMaker Data Wrangler 清洗+特征工程
    ↓
SageMaker 训练预测模型
    ↓
API Gateway + Lambda → Agent 调用推理接口
    ↓
Web Agent 前端展示30队选秀结果
```

## 关键链接

- AWS Sports: https://aws.amazon.com/sports/
- SageMaker Data Wrangler: https://aws.amazon.com/sagemaker/data-wrangler/
- SageMaker Feature Engineering: https://aws.amazon.com/blogs/machine-learning/automate-feature-engineering-pipelines-with-amazon-sagemaker/

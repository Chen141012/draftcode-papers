# 选秀预测特征工程参考

> 基于学术论文和实际研究的特征工程指南。
> 比赛日数据到达后，这套特征框架可以直接复用。

## 1. 特征分类框架

```
球员数据
├── 体测特征（身高/体重/臂展/站立摸高/体脂）
├── 大学表现特征（场均数据/效率指标）
├── 背景特征（年龄/年级/联盟/学校声望）
└── 复合特征（组合/比率/标准化指标）
```

## 2. 体测特征

### 核心体测指标

| 特征 | 类型 | 说明 |
|------|------|------|
| height_no_shoes | 连续 | 裸足身高（英寸），比穿鞋身高更有预测力 |
| weight | 连续 | 体重（磅） |
| wingspan | 连续 | 臂展（英寸）— **最被低估的预测指标** |
| standing_reach | 连续 | 站立摸高（英寸） |
| body_fat_pct | 连续 | 体脂率 |
| vertical_leap_max | 连续 | 最大弹跳（英寸） |
| agility_lane | 连续 | 敏捷性测试（秒） |
| bench_press | 离散 | 84kg卧推次数 |

### 体测组合特征

```python
# 关键比率特征
df['height_to_wingspan_ratio'] = df['height'] / df['wingspan']
# 臂展-身高差越大 → 防守潜力越高

df['weight_to_height_ratio'] = df['weight'] / df['height']
# 相同身高下体重越大 → 对抗能力越强

df['standing_reach_diff'] = df['standing_reach'] - df['height']
# 站立摸高与身高差 → 打同位置的优势
```

## 3. 大学表现特征

### 基础统计特征

| 类别 | 特征 | 说明 |
|------|------|------|
| 得分 | PPG, TS%, eFG% | TS% 比 PPG 更有预测力 |
| 篮板 | RPG, ORB%, DRB% | 篮板率比总数更稳定 |
| 组织 | APG, AST/TO Ratio, AST% | 助攻失误比强于助攻数 |
| 投射 | 3PM, 3P%, FT%, 3PA Rate | 三分能力是**最强预测指标之一** |
| 防守 | SPG, BPG, STL%, BLK% | 抢断率对后卫预测力强，盖帽率对锋线强 |
| 效率 | PER, BPM, WS/40 | 综合效率指标 |

### 大学数据关键发现

基于 TDS 文章和 SMU 学术论文的研究：

1. **选秀顺位本身是最强预测因子** — "a player's draft pick and their college statistics are the best predictors"
2. **三分命中率 > 得分** — TS% 比 PPG 更能预测 NBA 成功
3. **大一生 vs 大四生** — 大一参选球员的 NBA 成功率更高（天赋筛选效应），但需要控制年龄
4. **Power 5 联盟溢价** — 来自 ACC/SEC/B1G 等强联盟的球员，数据价值更高

## 4. 背景特征

```python
features['age_at_draft'] = draft_year - birth_year
# 如果生日在9月后（学年截止），减1

features['is_freshman'] = (years_in_college == 1).astype(int)
features['is_international'] = (country != 'USA').astype(int)

# 联盟强度编码
power_5_conferences = ['ACC', 'Big 12', 'Big East', 'Big Ten', 'Pac-12', 'SEC']
features['is_power_5'] = df['conference'].isin(power_5_conferences).astype(int)

# 学校声望（历史产出NBA球员数量）
features['school_nba_alumni_count'] = ...  # 从历史数据统计
```

## 5. 复合特征（比赛日直接复用）

```python
def create_advanced_features(df):
    """生成选秀预测高级特征"""
    features = pd.DataFrame(index=df.index)
    
    # 1. 效率类
    features['ts_pct'] = df['pts'] / (2 * (df['fga'] + 0.44 * df['fta']))
    features['efg_pct'] = (df['fgm'] + 0.5 * df['fg3m']) / df['fga']
    features['per'] = df['pts'] + df['reb'] + df['ast'] + df['stl'] + df['blk'] - df['missed_fg'] - df['missed_ft'] - df['tov']
    
    # 2. 标准化率指标
    if 'mp' in df.columns:  # 如果有上场时间
        features['pts_per_40'] = df['pts'] / df['mp'] * 40
        features['reb_per_40'] = df['reb'] / df['mp'] * 40
        features['ast_per_40'] = df['ast'] / df['mp'] * 40
    
    # 3. 组合指标
    features['usage_rating'] = df['pts'] + 1.2 * df['reb'] + 1.5 * df['ast']
    features['shooting_efficiency'] = df['fg3m'] * 3 + df['fg2m'] * 2 + df['ftm']
    
    # 4. 体型指数
    if 'height' in df.columns and 'weight' in df.columns:
        features['bmi'] = df['weight'] / (df['height'] / 39.37) ** 2
    
    # 5. 经验调整
    if 'age' in df.columns:
        features['young_talent'] = ((df['age'] <= 20) & df['pts'] > 15).astype(int)
    
    return features
```

## 6. 特征选择优先级（比赛日参考）

| 优先级 | 特征组 | 包含 | 说明 |
|--------|--------|------|------|
| 🔴 P0 | 基础体测 | 身高/体重/臂展 | 所有数据集都有 |
| 🔴 P0 | 大学核心数据 | PPG/3P%/RPG/APG | 必有 |
| 🟡 P1 | 效率指标 | PER/TS%/eFG% | 如果bbref风格数据 |
| 🟡 P1 | 背景 | 年龄/联盟/年级 | 必有 |
| 🟢 P2 | 进阶率指标 | REB%/AST%/STL% | 如果有详细数据 |
| 🟢 P2 | 复合特征 | 组合指数 | 按需计算 |

> **原则**：先跑 P0，时间有余再上 P1/P2。特征越多不一定预测越准。

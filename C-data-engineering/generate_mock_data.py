"""NBA Draft Mock Data Generator

6/16 培训前测试 pipeline 的模拟数据生成器。
生成格式接近真实选秀数据的 CSV，包含体测/大学统计/顺位。

Usage:
    python generate_mock_data.py                     # 默认 1000 行
    python generate_mock_data.py --rows 5000         # 自定义行数
    python generate_mock_data --format             # 查看列格式说明
"""

import argparse
import numpy as np
import pandas as pd
from pathlib import Path

# 种子保证可复现
RNG = np.random.default_rng(2026)

TEAMS = [
    "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets",
    "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets",
    "Detroit Pistons", "Golden State Warriors", "Houston Rockets", "Indiana Pacers",
    "LA Clippers", "Los Angeles Lakers", "Memphis Grizzlies", "Miami Heat",
    "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans",
    "New York Knicks", "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers",
    "Phoenix Suns", "Portland Trail Blazers", "Sacramento Kings",
    "San Antonio Spurs", "Toronto Raptors", "Utah Jazz", "Washington Wizards",
]

POSITIONS = ["PG", "SG", "SF", "PF", "C"]

CONFERENCES = [
    "ACC", "Big 12", "Big East", "Big Ten", "Pac-12", "SEC",
    "A-10", "AAC", "MWC", "WCC", "Ivy", "Other"
]

SCHOOLS = [
    "Duke", "Kentucky", "North Carolina", "Kansas", "UCLA", "Arizona",
    "Gonzaga", "Villanova", "Michigan St", "Indiana", "Arkansas", "Baylor",
    "Houston", "Tennessee", "Alabama", "Auburn", "Florida", "Illinois",
    "Purdue", "Texas", "USC", "Connecticut", "Louisville", "Syracuse",
    "Michigan", "Ohio St", "Oregon", "Memphis", "Xavier", "Creighton",
]


def generate_mock_data(n_rows: int = 1000) -> pd.DataFrame:
    """生成模拟选秀数据"""
    data = {
        # === 标识 ===
        "player_id": [f"P{i:04d}" for i in range(n_rows)],
        "player_name": [f"Player_{i}" for i in range(n_rows)],
        "position": RNG.choice(POSITIONS, n_rows),
        "college": RNG.choice(SCHOOLS, n_rows),
        "conference": RNG.choice(CONFERENCES, n_rows),

        # === 体测 ===
        "height": np.round(RNG.normal(79, 4, n_rows), 1),       # 英寸，~6'7
        "weight": np.round(RNG.normal(215, 30, n_rows)),         # 磅
        "wingspan": np.round(RNG.normal(82, 5, n_rows), 1),      # 英寸
        "vertical": np.round(RNG.normal(32, 5, n_rows), 1),      # 英寸

        # === 大学数据 ===
        "age": np.round(RNG.normal(20.5, 1.5, n_rows), 1),
        "years_in_college": RNG.integers(1, 5, n_rows),
        "gp": RNG.integers(20, 40, n_rows),                      # 出场数

        # 基础统计（场均）
        "pts": np.round(np.maximum(0, RNG.normal(14, 6, n_rows)), 1),
        "reb": np.round(np.maximum(0, RNG.normal(6, 3, n_rows)), 1),
        "ast": np.round(np.maximum(0, RNG.normal(3, 2, n_rows)), 1),
        "stl": np.round(np.maximum(0, RNG.normal(1.2, 0.6, n_rows)), 1),
        "blk": np.round(np.maximum(0, RNG.normal(0.8, 0.6, n_rows)), 1),
        "tov": np.round(np.maximum(0, RNG.normal(2, 1, n_rows)), 1),

        # 命中率
        "fg_pct": np.round(np.clip(RNG.normal(0.44, 0.06, n_rows), 0.25, 0.65), 3),
        "fg3_pct": np.round(np.clip(RNG.normal(0.34, 0.06, n_rows), 0.15, 0.55), 3),
        "ft_pct": np.round(np.clip(RNG.normal(0.74, 0.08, n_rows), 0.40, 0.95), 3),

        # 出手数
        "fga": np.round(np.maximum(0, RNG.normal(10, 4, n_rows)), 1),
        "fg3a": np.round(np.maximum(0, RNG.normal(4, 2.5, n_rows)), 1),
        "fta": np.round(np.maximum(0, RNG.normal(4, 2, n_rows)), 1),
    }

    df = pd.DataFrame(data)

    # === 目标变量：选秀顺位（1-60） ===
    # 特征越强 → 顺位越靠前（数值越小）
    score = (
        df["pts"] * 0.3
        + df["reb"] * 0.2
        + df["ast"] * 0.2
        + df["stl"] * 2 * 0.1
        + df["blk"] * 2 * 0.1
        - df["tov"] * 0.1
        + df["fg3_pct"] * 20 * 0.3
        - (df["age"] - 19) * 2
        + (df["height"] - 75) * 0.5
        + RNG.normal(0, 5, n_rows)  # 噪声
    )

    # 标准化到 1-60
    score_rank = score.rank(pct=True)
    df["pick_number"] = np.round(60 - score_rank * 59 + 1).astype(int)

    # 分配到球队（顺位越低越早被选，但不是简单映射）
    df["drafting_team"] = df["pick_number"].apply(
        lambda p: TEAMS[min(p - 1, len(TEAMS) - 1)]
    )

    return df


def print_format_doc():
    """输出列格式说明"""
    print("""
=== 生成数据列说明 ===

 player_id        | 球员ID             | str
 player_name      | 球员名             | str
 position         | 位置(PG/SG/SF/PF/C)| str
 college          | 大学               | str
 conference       | 联盟               | str
 height           | 身高(英寸)         | float
 weight           | 体重(磅)           | int
 wingspan         | 臂展(英寸)         | float
 vertical         | 弹跳(英寸)         | float
 age              | 年龄               | float
 years_in_college | 大学年级(1-4)      | int
 gp               | 出场数             | int
 pts              | 场均得分           | float
 reb              | 场均篮板           | float
 ast              | 场均助攻           | float
 stl              | 场均抢断           | float
 blk              | 场均盖帽           | float
 tov              | 场均失误           | float
 fg_pct           | 投篮命中率         | float
 fg3_pct          | 三分命中率         | float
 ft_pct           | 罚球命中率         | float
 fga              | 场均出手           | float
 fg3a             | 场均三分出手       | float
 fta              | 场均罚球           | float
 pick_number      | 选秀顺位(1-60)     | int   ← 目标变量
 drafting_team    | 选中球队           | str

6/16 培训后调整：替换为真实数据格式和分布参数。
""")


def main():
    parser = argparse.ArgumentParser(description="生成模拟NBA选秀数据")
    parser.add_argument("--rows", type=int, default=1000, help="行数 (默认 1000)")
    parser.add_argument("--output", type=str, default="mock_draft_data.csv", help="输出路径")
    parser.add_argument("--format", action="store_true", help="显示列格式说明")
    args = parser.parse_args()

    if args.format:
        print_format_doc()
        return

    print(f"生成 {args.rows} 行模拟选秀数据...")
    df = generate_mock_data(args.rows)
    df.to_csv(args.output, index=False)
    print(f"已保存: {args.output} ({args.rows} 行, {len(df.columns)} 列)")
    print(f"特征列: {[c for c in df.columns if c != 'pick_number']}")
    print(f"目标列: pick_number (范围 {df['pick_number'].min()}-{df['pick_number'].max()})")
    print(f"\n一行命令跑 pipeline:")
    print(f"  python3 -c \"from data_processor import DraftDataProcessor;")
    print(f"  from draft_pipeline import run_draft_pipeline;")
    print(f"  model, m = run_draft_pipeline('{args.output}')\"")


if __name__ == "__main__":
    main()

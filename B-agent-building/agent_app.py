"""NBA Draft Prediction Agent

Amazon Bedrock Agent 应用骨架。
使用 Claude Sonnet + Tool Use 提供选秀分析能力。
比赛日集成 data_processor + draft_pipeline 的预测结果。

Usage:
    python agent_app.py --query "预测马刺队#4顺位"
    python agent_app.py --interactive
"""

import json
import os
import argparse
from typing import Optional

import boto3
from botocore.exceptions import ClientError


# ============================================
# 配置
# ============================================
DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-6"
REGION = os.getenv("AWS_REGION", "us-east-1")


class DraftAgent:
    """选秀预测 Agent — 基于 Bedrock Converse API + Tool Use"""

    def __init__(self, model_id: str = DEFAULT_MODEL):
        self.model_id = model_id
        self.client = boto3.client("bedrock-runtime", region_name=REGION)
        self.system_prompt = self._build_system_prompt()
        self.tools = self._define_tools()
        self.conversation_history = []

    def _build_system_prompt(self) -> list:
        return [{"text": """你是一个 NBA 选秀预测分析 Agent。

## 能力
1. 基于历史数据预测选秀顺位
2. 分析球员数据并对比
3. 输出可视化数据表格

## 规则
- 所有预测必须标注置信度
- 使用工具获取数据，不凭空猜测
- 输出格式优先使用 Markdown 表格
- 不确定时输出 Top 3 可能性""" }]

    def _define_tools(self) -> dict:
        return {
            "tools": [
                {
                    "toolSpec": {
                        "name": "predict_draft",
                        "description": "预测指定球队在指定顺位的选秀选择",
                        "inputSchema": {
                            "json": {
                                "type": "object",
                                "properties": {
                                    "team": {"type": "string", "description": "球队名"},
                                    "pick": {"type": "integer", "description": "顺位"},
                                },
                                "required": ["team", "pick"]
                            }
                        }
                    }
                },
                {
                    "toolSpec": {
                        "name": "analyze_player",
                        "description": "分析球员数据和选秀前景",
                        "inputSchema": {
                            "json": {
                                "type": "object",
                                "properties": {
                                    "player_name": {"type": "string"},
                                },
                                "required": ["player_name"]
                            }
                        }
                    }
                },
                {
                    "toolSpec": {
                        "name": "get_team_draft_history",
                        "description": "获取球队历史选秀模式",
                        "inputSchema": {
                            "json": {
                                "type": "object",
                                "properties": {
                                    "team": {"type": "string"},
                                },
                                "required": ["team"]
                            }
                        }
                    }
                },
                {
                    "toolSpec": {
                        "name": "get_predictions_table",
                        "description": "获取所有30支球队的预测选秀结果",
                        "inputSchema": {
                            "json": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                    }
                }
            ]
        }

    # ============================================
    # Tool 实现（TODO 6/16: 接入实际数据和模型）
    # ============================================
    def _tool_predict_draft(self, team: str, pick: int) -> dict:
        """TODO: 接入训练好的 draft_pipeline 预测结果"""
        # 临时返回占位数据
        return {
            "status": "success",
            "prediction": {
                "team": team,
                "pick": pick,
                "recommended_player": "TBD (待模型训练)",
                "confidence": 0.0,
                "alternative_picks": ["TBD", "TBD"]
            }
        }

    def _tool_analyze_player(self, player_name: str) -> dict:
        return {"status": "success", "player": player_name, "analysis": "待数据解锁后更新"}

    def _tool_team_history(self, team: str) -> dict:
        return {"status": "success", "team": team, "history": "待数据解锁后更新"}

    def _tool_predictions_table(self) -> dict:
        return {"status": "success", "message": "30队预测表待模型训练后生成"}

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        handlers = {
            "predict_draft": lambda: self._tool_predict_draft(
                tool_input.get("team", ""), tool_input.get("pick", 0)),
            "analyze_player": lambda: self._tool_analyze_player(
                tool_input.get("player_name", "")),
            "get_team_draft_history": lambda: self._tool_team_history(
                tool_input.get("team", "")),
            "get_predictions_table": lambda: self._tool_predictions_table(),
        }
        handler = handlers.get(tool_name)
        if not handler:
            return json.dumps({"error": f"未知工具: {tool_name}"})
        return json.dumps(handler())

    def chat(self, user_input: str, verbose: bool = False) -> str:
        """单轮对话"""
        messages = self.conversation_history + [
            {"role": "user", "content": [{"text": user_input}]}
        ]

        try:
            response = self.client.converse(
                modelId=self.model_id,
                system=self.system_prompt,
                messages=messages,
                **self.tools,
                inferenceConfig={"maxTokens": 4096, "temperature": 0.3}
            )
        except ClientError as e:
            return f"[错误] Bedrock 调用失败: {e}"

        msg = response["output"]["message"]

        # 处理 Tool Use
        content_blocks = msg.get("content", [])
        tool_results = []
        for block in content_blocks:
            if "toolUse" in block:
                tool = block["toolUse"]
                result = self._execute_tool(tool["name"], tool["input"])
                tool_results.append({
                    "toolUseId": tool["toolUseId"],
                    "content": [{"json": {"result": result}}]
                })
                if verbose:
                    print(f"  [Agent] 调用工具: {tool['name']}({tool['input']})")

        if tool_results:
            messages.append(msg)
            messages.append({
                "role": "user",
                "content": [{"toolResult": tr} for tr in tool_results]
            })
            response = self.client.converse(
                modelId=self.model_id,
                system=self.system_prompt,
                messages=messages,
                **self.tools,
                inferenceConfig={"maxTokens": 4096, "temperature": 0.3}
            )
            msg = response["output"]["message"]

        # 提取文本回复
        text = ""
        for block in msg.get("content", []):
            if "text" in block:
                text += block["text"]

        self.conversation_history = messages + [msg]
        return text or "[Agent 返回空响应]"


def main():
    parser = argparse.ArgumentParser(description="DraftCode 选秀预测 Agent")
    parser.add_argument("--query", "-q", type=str, help="单次查询")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互模式")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="模型 ID")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示工具调用")
    args = parser.parse_args()

    agent = DraftAgent(model_id=args.model)

    if args.query:
        print(agent.chat(args.query, verbose=args.verbose))
    elif args.interactive:
        print("🤖 选秀预测 Agent（输入 exit 退出）")
        while True:
            try:
                q = input("\n> ").strip()
                if q.lower() in ("exit", "quit"):
                    break
                print(agent.chat(q, verbose=args.verbose))
            except KeyboardInterrupt:
                break
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

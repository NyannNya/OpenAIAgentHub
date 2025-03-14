import asyncio
import argparse
import sys

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from agents import Runner, trace
from src.agent_center import dispatcher_agent

async def main():
    with trace(workflow_name="conversation", group_id="group_migo"):
        try:
            question = "我想要學習英文翻譯，請問你能告訴我如何翻譯「你好」這個詞嗎？"
            print(f"User: {question}")
            result = await Runner.run(dispatcher_agent, question)
            print(result.final_output)

            question = "我想了解數據分析演進史"
            print(f"User: {question}")
            result = await Runner.run(dispatcher_agent, question)
            print(result.final_output)

        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
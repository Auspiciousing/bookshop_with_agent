import asyncio
import os
import sys

from dotenv import load_dotenv

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

_root = os.path.dirname(os.path.abspath(__file__))
_src_path = os.path.join(_root, "src")
_workspace_root = os.path.dirname(_root)
for _path in (_src_path, _workspace_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from react_agent import graph
from react_agent.context import Context
from react_agent.utils import get_message_text


def _get_query(preset_query: str | None) -> str:
    # 如果传了命令行参数，先用一次；否则进入交互式输入。
    if preset_query is not None:
        return preset_query
    return input("User> ").strip()


def _print_tool_event(name: str, payload: object, label: str) -> None:
    print(f"[{label}] {name}: {payload}")


async def main() -> None:
    # 从 .env 读取环境变量（API key、模型配置等）。
    load_dotenv()
    # 维护一份对话历史，实现多轮对话。
    messages: list[BaseMessage] = []

    preset_query = " ".join(sys.argv[1:]).strip() or None

    while True:
        query = _get_query(preset_query)
        preset_query = None
        if not query:
            print("No input provided.")
            continue

        if query.lower() in {"exit", "quit"}:
            print("Bye.")
            return

        messages.append(HumanMessage(content=query))
        
        # 用历史消息和运行时上下文调用 LangGraph 代理。
        # result = await graph.ainvoke(
        #     {"messages": messages},
        #     context=Context(),
        # )
        # assistant_msg = result["messages"][-1].content
        # print(f"Assistant> {assistant_msg}")

        # 收集流式增量，最终拼成完整回复。
        assistant_text_parts: list[str] = []
        try:
            async for event in graph.astream_events(
                {"messages": messages},
                context=Context(),
                version="v1",
            ):
                # 只输出工具调用与模型回答。
                # if event.get("event") == "on_tool_start":
                #     tool_name = event.get("name") or "unknown_tool"
                #     tool_input = event.get("data", {}).get("input")
                #     _print_tool_event(tool_name, tool_input, "ToolStart")

                # 只处理模型的 token 流事件。
                if event.get("event") == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk is None:
                        continue
                    delta = get_message_text(chunk)
                    if delta:
                        # 第一次输出时打印前缀，之后只追加内容。
                        if not assistant_text_parts:
                            print("Assistant: ", end="", flush=True)
                        print(delta, end="", flush=True)
                        assistant_text_parts.append(delta)
                elif event.get("event") == "on_chat_model_end":
                    # 结束时补一个换行，避免下一行贴住。
                    if assistant_text_parts:
                        print("")
        except Exception as exc:
            print(f"Assistant> 请求失败：{exc}")

        # 把助手回复追加到历史里，下一轮继续。
        if assistant_text_parts:
            messages.append(AIMessage(content="".join(assistant_text_parts)))


if __name__ == "__main__":
    asyncio.run(main())

"""定义一个自定义的推理-行动（ReAct）代理。

可与支持工具调用的聊天模型配合使用。
"""

from datetime import UTC, datetime
from typing import Dict, List, Literal, cast

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime

from react_agent.context import Context
from react_agent.state import InputState, State
from react_agent.tools import TOOLS
from react_agent.utils import load_chat_model

# 定义调用模型的函数


async def call_model(
    state: State, runtime: Runtime[Context]
) -> Dict[str, List[AIMessage]]:
    """调用驱动代理的 LLM。

    该函数负责准备提示词、初始化模型并处理响应。

    Args:
        state (State): 当前对话状态。
        runtime (Runtime[Context]): 运行时上下文配置。

    Returns:
        dict: 包含模型回复消息的字典。
    """
    # 初始化模型并绑定工具。可在此修改模型或添加更多工具。
    model = load_chat_model(runtime.context.model).bind_tools(TOOLS)

    # 格式化系统提示词。修改此处可改变代理行为。
    system_message = runtime.context.system_prompt.format(
        system_time=datetime.now(tz=UTC).isoformat()
    )

    # 获取模型响应
    response = cast( # type: ignore[redundant-cast]
        AIMessage,
        await model.ainvoke(
            [{"role": "system", "content": system_message}, *state.messages]
        ),
    )

    # 如果已经是最后一步但模型还想调用工具，则给出兜底回复
    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, I could not find an answer to your question in the specified number of steps.",
                )
            ]
        }

    # 将模型回复作为列表返回，以便追加到已有消息中
    return {"messages": [response]}


# 定义新的图

builder = StateGraph(State, input_schema=InputState, context_schema=Context)

# 定义会循环执行的两个节点
builder.add_node(call_model)#模型推理
builder.add_node("tools", ToolNode(TOOLS))#工具执行

# 设置入口为 `call_model`
# 这意味着该节点是第一个被调用的
builder.add_edge("__start__", "call_model")


def route_model_output(state: State) -> Literal["__end__", "tools"]:
    """根据模型输出决定下一步节点。

    该函数检查模型最后一条消息是否包含工具调用。

    Args:
        state (State): 当前对话状态。

    Returns:
        str: 下一步要调用的节点名称（"__end__" 或 "tools"）。
    """
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(
            f"Expected AIMessage in output edges, but got {type(last_message).__name__}"
        )
    # 没有工具调用则结束
    if not last_message.tool_calls:
        return "__end__"
    # 否则执行请求的工具动作
    return "tools"


# 添加条件边，用于决定 `call_model` 之后的下一步
builder.add_conditional_edges(
    "call_model",
    # call_model 执行完成后，依据 route_model_output 的结果调度下一节点
    route_model_output,
)

# 添加从 `tools` 到 `call_model` 的普通边
# 这形成一个循环：使用工具后始终回到模型
builder.add_edge("tools", "call_model")

# 将 builder 编译为可执行的图
graph = builder.compile(name="ReAct Agent")

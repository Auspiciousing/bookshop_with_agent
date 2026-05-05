"""定义代理的状态结构。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep
from typing_extensions import Annotated


@dataclass
class InputState:
    """定义代理的输入状态，表示对外部更窄的接口。

    该类用于定义初始状态以及输入数据的结构。
    """

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(
        default_factory=list
    )
    """
    跟踪代理主要执行状态的消息列表。

    通常会累积成如下模式：
    1. HumanMessage - 用户输入
    2. AIMessage（包含 .tool_calls）- 代理选择要使用的工具来收集信息
    3. ToolMessage - 工具执行后的响应（或错误）
    4. AIMessage（不包含 .tool_calls）- 代理给用户的非结构化回复
    5. HumanMessage - 用户进入下一轮对话

    步骤 2-5 会根据需要重复。

    `add_messages` 标注会把新消息与已有消息合并，
    通过消息 ID 更新，确保是“只追加”的状态（除非提供了相同 ID 的消息）。
    """


@dataclass
class State(InputState):
    """表示代理的完整状态，在 InputState 基础上扩展更多属性。

    该类可用于存储代理生命周期中需要的任何信息。
    """

    is_last_step: IsLastStep = field(default=False)
    """
    表示当前步骤是否是图在抛出错误前的最后一步。

    这是一个“托管”变量，由状态机而不是用户代码控制。
    当步数达到 recursion_limit - 1 时会被置为 True。
    """

    # 需要时可在此添加更多属性。
    # 常见示例包括：
    # retrieved_documents: List[Document] = field(default_factory=list)
    # extracted_entities: Dict[str, Any] = field(default_factory=dict)
    # api_connections: Dict[str, Any] = field(default_factory=dict)

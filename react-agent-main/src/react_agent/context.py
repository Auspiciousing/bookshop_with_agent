"""定义代理的可配置参数。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, fields
from typing import Annotated

from . import prompts


@dataclass(kw_only=True)
class Context:
    """代理的运行时上下文。"""

    system_prompt: str = field(
        default=prompts.SYSTEM_PROMPT,
        metadata={
            "description": "代理交互时使用的系统提示词。"
            "该提示词用于设定上下文与行为。"
        },
    )

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="anthropic/claude-sonnet-4-5-20250929",
        metadata={
            "description": "代理主交互使用的语言模型名称。"
            "格式应为：provider/model-name。"
        },
    )

    max_search_results: int = field(
        default=10,
        metadata={
            "description": "每次搜索请求返回的最大结果数。"
        },
    )

    def __post_init__(self) -> None:
        """为未显式传参的属性读取环境变量。"""
        for f in fields(self):
            if not f.init:
                continue

            if getattr(self, f.name) == f.default:
                setattr(self, f.name, os.environ.get(f.name.upper(), f.default))

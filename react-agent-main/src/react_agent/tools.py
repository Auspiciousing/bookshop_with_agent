"""本模块提供用于网页抓取与搜索功能的示例工具。

其中包含一个基础的 Tavily 搜索函数（示例）。

这些工具仅用于入门示例。生产环境中建议实现更稳健、更专业的工具。
"""

# 标准库类型工具：用于类型标注与类型转换。
import asyncio
import json
import os
import subprocess
from functools import lru_cache
from typing import Any, Callable, List, Optional, cast

import aiohttp

# Tavily 搜索工具（LangChain 集成）。
from langchain_tavily import TavilySearch
# 从 LangGraph 运行时获取上下文。
from langgraph.runtime import get_runtime

# 引入自定义运行时上下文（包含模型与配置）。
from react_agent.context import Context
from react_agent.utils import get_message_text, load_chat_model

# SQLAlchemy（用于图书信息查询）。
from dotenv import load_dotenv
from sqlalchemy import Float, Integer, String, case, create_engine, desc, or_, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy ORM 基类。"""


class Book(Base):
    """图书信息表模型。"""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[Optional[str]] = mapped_column(String(255))
    price: Mapped[Optional[float]] = mapped_column(Float)
    description: Mapped[Optional[str]] = mapped_column(String(2000))
    seller: Mapped[Optional[str]] = mapped_column(String(255))
    stock: Mapped[Optional[int]] = mapped_column(Integer)


@lru_cache(maxsize=1)
def _get_engine():
    """创建并缓存数据库连接引擎。"""
    load_dotenv(override=False)
    database_url = os.getenv("BOOKS_DB_URL", "sqlite:///./books.db")
    engine = create_engine(database_url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return engine


@lru_cache(maxsize=1)
def _get_keyword_model():
    """创建并缓存关键词抽取模型。"""
    load_dotenv(override=False)
    runtime = get_runtime(Context)
    model_name = os.getenv("BOOK_SEARCH_MODEL", runtime.context.model)
    return load_chat_model(model_name)


async def _extract_query_fields(query: str) -> dict[str, Any]:
    """使用 LLM 抽取结构化查询字段。"""
    model = _get_keyword_model()
    system_prompt = (
        "你是查询解析器。请从用户查询中抽取结构化字段，并仅返回 JSON。"
        "JSON 字段包含：keywords(字符串数组)、book_title、author、seller、stock"
        "min_price、max_price。未知填 null。不要输出多余文本。"
        "注意：价格/库存/卖家相关的词不要放入 keywords，应优先映射到"
        "min_price/max_price 或 seller/stock。"
    )

    async def _call_model(extra_note: Optional[str] = None) -> str:
        user_content = query
        if extra_note:
            user_content = f"{query}\n\n注意：{extra_note}"
        response = await model.ainvoke(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ]
        )
        return get_message_text(response)

    def _parse_json(content: str) -> Optional[dict[str, Any]]:
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict):
            return None
        keywords = data.get("keywords")
        if not isinstance(keywords, list):
            data["keywords"] = [query]
        return data

    max_retries = int(os.getenv("BOOK_SEARCH_RETRIES", "2"))
    for attempt in range(max_retries + 1):
        note = None
        if attempt > 0:
            note = "上一次未返回有效 JSON，请仅输出 JSON 对象"
        content = await _call_model(note)
        data = _parse_json(content)
        if data is not None:
            return data

    return {"keywords": [query]}


async def search(query: str) -> Optional[dict[str, Any]]:
    """搜索通用网页结果。

    该函数使用 Tavily 搜索引擎进行查询，旨在提供全面、准确、可信的结果，
    对回答时效性问题尤其有用。
    """
    _original = aiohttp.ClientSession

    class PatchedClientSession(aiohttp.ClientSession):
        def __init__(self, *args, **kwargs):
            kwargs["trust_env"] = True
            super().__init__(*args, **kwargs)

    aiohttp.ClientSession = PatchedClientSession


    print(f"深度思考中：正在调用搜索工具，query={query!r}")
    # 读取运行时上下文（用于获取配置）。
    runtime = get_runtime(Context)
    # 根据上下文配置初始化搜索工具（控制返回条数）。
    wrapped = TavilySearch(max_results=runtime.context.max_search_results)
    # 执行异步搜索并返回结果。
    try:
        return cast(dict[str, Any], await wrapped.ainvoke({"query": query}))
    except Exception as exc:
        print(f"深度思考中：搜索工具报错 -> {exc}")
        raise

async def open_software(name: str) -> str:
    """打开常见桌面软件（Windows）。

    该函数使用预设的绝对路径直接启动软件。
    """
    print(f"深度思考中：正在尝试打开软件 '{name}'...")
    # 固定路径映射（按需增删）。
    commands_by_name = {
        "netease_music": [r"E:\CloudMusic\cloudmusic.exe"],
        "qq": [r"D:\qq\QQ.exe"],
        "wechat": [r"D:\WeChat\Weixin\Weixin.exe", "--scene=taskbarpins"],
        "steam": [r"E:\steam\steam.exe"],
        "mihoyo_launcher": [r"E:\miHoYo Launcher\launcher.exe"],
    }

    # 规范化名称，允许中文别名。
    key = name.strip().lower()
    aliases = {
        "微信": "wechat",
        "qq": "qq",
        "腾讯qq": "qq",
        "steam": "steam",
        "网易云音乐": "netease_music",
        "网易云": "netease_music",
        "米哈游启动器": "mihoyo_launcher",
        "米哈游": "mihoyo_launcher",
        "mihoyo": "mihoyo_launcher",
    }
    key = aliases.get(key, key)
    # 直接按名称执行固定路径。
    if key in commands_by_name:
        command = commands_by_name[key]
        exe_path = command[0]
        if not os.path.exists(exe_path):
            return f"未找到软件：{name}（路径不存在：{exe_path}）"
        subprocess.Popen(command, close_fds=True)
        return f"已打开软件：{name}"

    # 如果传入的是完整路径，也可直接打开。
    if os.path.exists(name):
        subprocess.Popen([name], close_fds=True)
        return f"已打开软件：{name}"

    return f"未配置该软件：{name}。请在映射中添加路径。"

async def book_search(query: str) -> Optional[dict[str, Any]]:
    """搜索图书信息。

    该函数从数据库中查询，返回图书的基本信息。
    """
    print(f"深度思考中：正在调用图书搜索工具，query={query!r}")
    if not query.strip():
        return {"query": query, "results": []}

    fields = await _extract_query_fields(query)
    keywords = [kw for kw in fields.get("keywords", []) if isinstance(kw, str) and kw]
    author = fields.get("author") if isinstance(fields.get("author"), str) else None
    seller = fields.get("seller") if isinstance(fields.get("seller"), str) else None
    min_price = fields.get("min_price") if isinstance(fields.get("min_price"), (int, float)) else None
    max_price = fields.get("max_price") if isinstance(fields.get("max_price"), (int, float)) else None

    engine = _get_engine()

    def _query_books() -> list[dict[str, Any]]:
        with Session(engine) as session:
            conditions = []
            score_expr = None
            if keywords:
                score_terms = []
                for kw in keywords:
                    per_kw_score = (
                        case((Book.title.ilike(f"%{kw}%"), 1), else_=0)
                        + case((Book.author.ilike(f"%{kw}%"), 1), else_=0)
                        + case((Book.description.ilike(f"%{kw}%"), 1), else_=0)
                        + case((Book.seller.ilike(f"%{kw}%"), 1), else_=0)
                    )
                    score_terms.append(per_kw_score)
                    conditions.append(
                        or_(
                            Book.title.ilike(f"%{kw}%"),
                            Book.author.ilike(f"%{kw}%"),
                            Book.description.ilike(f"%{kw}%"),
                            Book.seller.ilike(f"%{kw}%"),
                        )
                    )
                if score_terms:
                    score_expr = sum(score_terms) / len(score_terms)
            if author:
                conditions.append(Book.author.ilike(f"%{author}%"))
            if seller:
                conditions.append(Book.seller.ilike(f"%{seller}%"))
            if min_price is not None:
                conditions.append(Book.price >= float(min_price))
            if max_price is not None:
                conditions.append(Book.price <= float(max_price))

            if not conditions:
                return []

            stmt = select(Book).where(or_(*conditions))
            if score_expr is not None:
                stmt = stmt.order_by(desc(score_expr))
            stmt = stmt.limit(10)
            rows = session.execute(stmt).scalars().all()
            return [
                {
                    "title": row.title,
                    "author": row.author,
                    "price": row.price,
                    "description": row.description,
                    "seller": row.seller,
                    "stock": row.stock,
                }
                for row in rows
            ]

    results = await asyncio.to_thread(_query_books)
    return {"query": query, "results": results}

# 将工具注册到列表中，供图绑定与工具节点调用。
TOOLS: List[Callable[..., Any]] = [search, open_software, book_search]

"""本模块提供用于网页抓取与搜索功能的示例工具。

其中包含一个基础的 Tavily 搜索函数（示例）。

这些工具仅用于入门示例。生产环境中建议实现更稳健、更专业的工具。
"""

# 标准库类型工具：用于类型标注与类型转换。
import asyncio
import io
import json
import os
import subprocess
from contextlib import redirect_stderr, redirect_stdout
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, cast

import aiohttp
# aiohttp 仅用于搜索时的会话打补丁，FormData 不再需要

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


# class Base(DeclarativeBase):
#     """SQLAlchemy ORM 基类。"""


# class Book(Base):
#     """映射 tryflask 中的 `books` 表结构。"""

#     __tablename__ = "books"

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     title: Mapped[str] = mapped_column(String(200), nullable=False)
#     author: Mapped[Optional[str]] = mapped_column(String(100))
#     publisher: Mapped[Optional[str]] = mapped_column(String(100))
#     description: Mapped[Optional[str]] = mapped_column(String(2000))
#     price: Mapped[Optional[float]] = mapped_column(Float)
#     stock: Mapped[Optional[int]] = mapped_column(Integer)
#     seller_id: Mapped[Optional[int]] = mapped_column(Integer)
#     picture_url: Mapped[Optional[str]] = mapped_column(String(500))


# 优先尝试直接使用 tryflask 中定义的模型（在 Flask app 上下文中查询），
# 如果导入或初始化失败则回退到本模块自己的 DB engine 查询。
TRYFLASK_MODELS_AVAILABLE = False
TF_db = None
TFBook = None
TFUser = None
TF_IMPORT_ERROR = None
try:
    import sys

    _root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    _tryflask_root = os.path.join(_root, 'tryflask')
    for _path in (_root, _tryflask_root):
        if _path not in sys.path:
            sys.path.insert(0, _path)

    import importlib

    # 优先使用 tryflask 目录下的 app 包，避免命中 site-packages 的 app
    _app_mod = sys.modules.get("app")
    if _app_mod is not None:
        _app_file = getattr(_app_mod, "__file__", "") or ""
        if _app_file and _tryflask_root not in os.path.abspath(_app_file):
            del sys.modules["app"]

    # 避免混用 app / tryflask.app 导致模型重复定义
    for _mod_name in list(sys.modules.keys()):
        if _mod_name.startswith("tryflask.app"):
            del sys.modules[_mod_name]

    _app_module = importlib.import_module("app")
    create_app = getattr(_app_module, "create_app")
    TF_db = importlib.import_module("app.plugins").db
    _models = importlib.import_module("app.models")
    TFBook = getattr(_models, "Book")
    TFUser = getattr(_models, "User")
    

    # 初始化 Flask app 并推入上下文，确保 TF_db 可用
    _app = create_app()
    _app.app_context().push()
    TRYFLASK_MODELS_AVAILABLE = True
except Exception as exc:
    TRYFLASK_MODELS_AVAILABLE = False
    TF_IMPORT_ERROR = f"tryflask import or init failed: {exc}"


@lru_cache(maxsize=1)
def _get_engine():
    """创建并缓存数据库连接引擎。"""
    load_dotenv(override=False)
    database_url = os.getenv(
        "TRYFLASK_DB_URL",
        os.getenv("BOOKS_DB_URL", "mysql+pymysql://root2:123456@localhost/secondhand_books"),
    )
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


# （不再包含通用 HTTP 后端代理：目前仅通过数据库与 tryflask 联动）


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

    # 关闭结构化抽取过程的多余输出（仅保留本函数的主提示行）
    _silent_buf = io.StringIO()
    with redirect_stdout(_silent_buf), redirect_stderr(_silent_buf):
        fields = await _extract_query_fields(query)
    keywords = [kw for kw in fields.get("keywords", []) if isinstance(kw, str) and kw]
    author = fields.get("author") if isinstance(fields.get("author"), str) else None
    min_price = fields.get("min_price") if isinstance(fields.get("min_price"), (int, float)) else None
    max_price = fields.get("max_price") if isinstance(fields.get("max_price"), (int, float)) else None
    seller = fields.get("seller") if isinstance(fields.get("seller"), str) else None
    stock = fields.get("stock") if isinstance(fields.get("stock"), int) else None

    # 若可用，优先使用 tryflask 的 Flask-SQLAlchemy 模型（在 app 上下文中）
    if TRYFLASK_MODELS_AVAILABLE and TFBook is not None and TFUser is not None and TF_db is not None:
        def _query_books_models() -> list[dict[str, Any]]:
            session = TF_db.session
            conditions = []
            score_expr = None
            if keywords:
                score_terms = []
                for kw in keywords:
                    per_kw_score = (
                        case((TFBook.title.ilike(f"%{kw}%"), 1), else_=0)
                        + case((TFBook.author.ilike(f"%{kw}%"), 1), else_=0)
                        + case((TFBook.description.ilike(f"%{kw}%"), 1), else_=0)
                    )
                    score_terms.append(per_kw_score)
                    conditions.append(
                        or_(
                            TFBook.title.ilike(f"%{kw}%"),
                            TFBook.author.ilike(f"%{kw}%"),
                            TFBook.description.ilike(f"%{kw}%"),
                        )
                    )
                if score_terms:
                    score_expr = sum(score_terms) / len(score_terms)
            if author:
                conditions.append(TFBook.author.ilike(f"%{author}%"))
            if min_price is not None:
                conditions.append(TFBook.price >= float(min_price))
            if max_price is not None:
                conditions.append(TFBook.price <= float(max_price))
            if seller:
                conditions.append(TFUser.username.ilike(f"%{seller}%"))
            if stock is not None:
                conditions.append(TFBook.stock >= stock)

            if not conditions:
                return []

            # 联表查询 seller（User），通过 TFBook.seller_id == TFUser.id
            query_stmt = session.query(TFBook, TFUser).outerjoin(TFUser, TFBook.seller_id == TFUser.id).filter(or_(*conditions))
            if score_expr is not None:
                query_stmt = query_stmt.order_by(desc(score_expr))
            rows = query_stmt.limit(10).all()
            results = []
            for book, user in rows:
                results.append({
                    "title": book.title,
                    "author": book.author,
                    "price": book.price,
                    "description": book.description,
                    "seller_id": book.seller_id,
                    "seller_username": getattr(user, 'username', None) if user is not None else None,
                    "seller_nickname": getattr(user, 'nickname', None) if user is not None else None,
                    "seller_avatar": getattr(user, 'avatar_url', None) if user is not None else None,
                    "publisher": getattr(book, 'publisher', None),
                    "picture_url": getattr(book, 'picture_url', None),
                    "stock": book.stock,
                })
            return results

        results = await asyncio.to_thread(_query_books_models)
        return {"query": query, "results": results}

    # 强制仅使用 tryflask ORM，不再回退到本地 engine。
    return {
        "query": query,
        "results": [],
        "error": "tryflask ORM 不可用，请确认 PYTHONPATH 与数据库配置",
    }


# 将工具注册到列表中，供图绑定与工具节点调用。
TOOLS: List[Callable[..., Any]] = [search, open_software, book_search]

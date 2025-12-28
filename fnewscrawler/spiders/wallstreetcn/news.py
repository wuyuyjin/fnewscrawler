"""
华尔街见闻新闻API接口爬取
通过直接调用API获取数据，避免使用浏览器
"""

import re
import asyncio
import httpx
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlencode

from fnewscrawler.utils.logger import LOGGER


# 类别映射
CATEGORY_MAP = {
    "要闻": "global",
    "A股": "a-stock",
    "美股": "us-stock",
    "港股": "hk-stock",
    "商品": "commodity"
}

# API类别映射
API_CATEGORY_MAP = {
    "global": "global-channel",
    "a-stock": "a-stock-channel",
    "us-stock": "us-stock-channel",
    "hk-stock": "hk-stock-channel",
    "commodity": "commodity-channel"
}

# API基础URL
API_BASE_URL = "https://api-one-wscn.awtmt.com/apiv1/content/lives"


def get_default_headers() -> Dict[str, str]:
    """获取默认的请求头"""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "x-client-type": "pc",
        "Referer": "https://wallstreetcn.com/"
    }


def extract_text_from_html(html_content: str) -> str:
    """从HTML内容中提取纯文本"""
    # 简单的HTML标签清理
    # 移除<p>标签
    text = re.sub(r'</?p>', '', html_content)
    # 移除其他HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 清理多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    # 处理特殊字符
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')

    return text


def format_timestamp(timestamp: int) -> str:
    """格式化时间戳为可读时间（包含年月日时分）"""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return str(timestamp)


async def fetch_news_from_api(category: str, limit: int = 20, cursor: Optional[str] = None) -> Dict:
    """
    从API获取新闻数据

    Args:
        category: 新闻类别
        limit: 获取数量
        cursor: 分页游标

    Returns:
        API响应数据
    """
    channel = API_CATEGORY_MAP.get(category)
    if not channel:
        raise ValueError(f"不支持的类别: {category}")

    params = {
        "channel": channel,
        "client": "pc",
        "limit": str(limit),
        "first_page": "true" if cursor is None else "false",
        "accept": "live,vip-live"
    }

    if cursor:
        params["cursor"] = cursor

    url = f"{API_BASE_URL}?{urlencode(params)}"
    headers = get_default_headers()

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            if data.get("code") != 20000:
                raise Exception(f"API返回错误: {data.get('message', 'Unknown error')}")

            return data

        except httpx.HTTPError as e:
            LOGGER.error(f"HTTP请求失败: {e}")
            raise
        except Exception as e:
            LOGGER.error(f"获取API数据失败: {e}")
            raise


def parse_api_response(data: Dict, category: str) -> List[Dict[str, str]]:
    """
    解析API响应数据

    Args:
        data: API响应数据
        category: 新闻类别

    Returns:
        解析后的新闻列表
    """
    items = data.get("data", {}).get("items", [])

    news_list = []
    for item in items:
        try:
            # 提取新闻内容
            content_html = item.get("content", "")
            content_text = extract_text_from_html(content_html)

            # 解析时间戳
            display_time = item.get("display_time", 0)
            time_str = format_timestamp(display_time) if display_time else ""

            # 检查重要性
            score = item.get("score", 1)
            importance = "important" if score >= 2 else "normal"

            # 获取渠道信息
            channels = item.get("channels", [])
            channel_name = "global"  # 默认为要闻
            for ch in channels:
                if ch in API_CATEGORY_MAP.values():
                    channel_name = ch.replace("-channel", "")
                    break

            news_info = {
                "id": item.get("id", ""),
                "time": time_str,
                "content": content_text,
                "content_html": content_html,
                "importance": importance,
                "category": category,
                "author": item.get("author", {}).get("display_name", ""),
                "title": item.get("title", ""),
                "uri": item.get("uri", ""),
                "comment_count": item.get("comment_count", 0),
                "display_time": display_time,
                "channels": channels
            }

            news_list.append(news_info)

        except Exception as e:
            LOGGER.error(f"解析新闻项失败: {e}")
            continue

    return news_list


async def wallstreetcn_crawl_news(category: str = "global", limit: int = 50) -> List[Dict[str, str]]:
    """
    爬取华尔街见闻快讯新闻（API方式）

    Args:
        category: 新闻类别，支持 global(要闻)、a-stock(A股)、us-stock(美股)、hk-stock(港股)、commodity(商品)
        limit: 最大爬取数量，默认50条

    Returns:
        List[Dict]: 新闻列表，每个元素包含id、time、content、importance、category等字段
    """
    # 验证类别参数
    if category not in API_CATEGORY_MAP:
        LOGGER.error(f"不支持的类别: {category}，支持的类别: {list(API_CATEGORY_MAP.keys())}")
        return []

    try:
        # 获取API数据
        response_data = await fetch_news_from_api(category, min(limit, 100))

        # 解析响应
        news_list = parse_api_response(response_data, category)

        # 限制返回数量
        if limit > 0 and len(news_list) > limit:
            news_list = news_list[:limit]

        LOGGER.info(f"华尔街见闻({category})：成功获取{len(news_list)}条新闻")
        return news_list

    except Exception as e:
        LOGGER.error(f"华尔街见闻：获取 {category} 类别新闻失败: {e}")
        return []


async def wallstreetcn_crawl_all_categories(limit: int = 50) -> Dict[str, List[Dict[str, str]]]:
    """
    爬取所有类别的新闻（API方式）

    Args:
        limit: 每个类别的最大爬取数量，默认50条

    Returns:
        Dict[str, List[Dict]]: 各类别新闻列表的字典
    """
    results = {}
    categories = ["global", "a-stock", "us-stock", "hk-stock", "commodity"]

    # 并发爬取所有类别
    tasks = [wallstreetcn_crawl_news(cat, limit) for cat in categories]
    news_lists = await asyncio.gather(*tasks)

    for cat, news_list in zip(categories, news_lists):
        results[cat] = news_list

    return results


async def get_important_news(category: str = "global", limit: int = 20) -> List[Dict[str, str]]:
    """
    获取重要新闻（API方式）

    Args:
        category: 新闻类别
        limit: 最大数量

    Returns:
        List[Dict]: 重要新闻列表
    """
    all_news = await wallstreetcn_crawl_news(category, limit * 2)  # 获取更多以筛选重要新闻

    # 过滤重要新闻
    important_news = [
        news for news in all_news
        if news.get('importance') == 'important'
    ]

    return important_news[:limit] if limit > 0 else important_news

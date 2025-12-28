"""
华尔街见闻新闻 MCP 工具
"""

from typing import Dict, Any

from fnewscrawler.mcp import mcp_server
from fnewscrawler.spiders.wallstreetcn.news import (
    wallstreetcn_crawl_news,
    wallstreetcn_crawl_all_categories,
    get_important_news
)


@mcp_server.tool(title="获取华尔街见闻快讯新闻", enabled=False)
async def get_wallstreetcn_news(
        category: str = "global",
        limit: int = 50
) -> Dict[str, Any]:
    """
    获取华尔街见闻快讯新闻

    Args:
        category: 新闻类别，支持以下选项：
                 - global: 要闻
                 - a-stock: A股
                 - us-stock: 美股
                 - hk-stock: 港股
                 - commodity: 商品
        limit: 返回新闻数量限制，默认50条，设为0表示不限制

    Returns:
        Dict: 包含success、data、message等字段的响应
              data字段为新闻列表，每条新闻包含time、content、importance、category字段
    """
    try:
        news_list = await wallstreetcn_crawl_news(category, limit)

        return {
            "success": True,
            "data": news_list,
            "message": f"成功获取{len(news_list)}条{category}类别新闻",
            "category": category,
            "total": len(news_list)
        }
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "message": f"获取新闻失败: {str(e)}",
            "category": category,
            "total": 0
        }


@mcp_server.tool(enabled=False,title="获取华尔街见闻所有类别的快讯新闻")
async def get_wallstreetcn_all_news(
        limit: int = 20
) -> Dict[str, Any]:
    """
    获取华尔街见闻所有类别的快讯新闻

    Args:
        limit: 每个类别返回新闻数量限制，默认50条，设为0表示不限制

    Returns:
        Dict: 包含success、data、message等字段的响应
              data字段为各类别新闻的字典，key为类别名称，value为新闻列表
    """
    try:
        all_news = await wallstreetcn_crawl_all_categories(limit)

        total_count = sum(len(news) for news in all_news.values())

        return {
            "success": True,
            "data": all_news,
            "message": f"成功获取所有类别新闻，总计{total_count}条",
            "categories": list(all_news.keys()),
            "total": total_count
        }
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "message": f"获取所有类别新闻失败: {str(e)}",
            "categories": [],
            "total": 0
        }


@mcp_server.tool(enabled=False, title="获取华尔街见闻重要新闻（标记为重要的快讯）")
async def get_wallstreetcn_important_news(
        category: str = "global",
        limit: int = 20
) -> Dict[str, Any]:
    """
    获取华尔街见闻重要新闻（标记为重要的快讯）

    Args:
        category: 新闻类别，支持以下选项：
                 - global: 要闻
                 - a-stock: A股
                 - us-stock: 美股
                 - hk-stock: 港股
                 - commodity: 商品
        limit: 返回新闻数量限制，默认20条，设为0表示不限制

    Returns:
        Dict: 包含success、data、message等字段的响应
              data字段为重要新闻列表
    """
    try:
        important_news = await get_important_news(category, limit)

        return {
            "success": True,
            "data": important_news,
            "message": f"成功获取{len(important_news)}条{category}类别重要新闻",
            "category": category,
            "total": len(important_news)
        }
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "message": f"获取重要新闻失败: {str(e)}",
            "category": category,
            "total": 0
        }

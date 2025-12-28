"""
华尔街见闻新闻爬取测试
"""

import asyncio
import json
from datetime import datetime
from fnewscrawler.spiders.wallstreetcn.news import (
    wallstreetcn_crawl_news,
    wallstreetcn_crawl_all_categories,
    get_important_news,
    CATEGORY_MAP
)


async def test_crawl_global_news():
    """测试爬取要闻新闻"""
    print("=" * 60)
    print("测试爬取要闻新闻（global）")
    print("=" * 60)

    try:
        news_list = await wallstreetcn_crawl_news("global", limit=5)
        print(f"成功获取 {len(news_list)} 条要闻\n")

        for i, news in enumerate(news_list, 1):
            print(f"{i}. 【时间】: {news.get('time', 'N/A')}")
            print(f"   【重要性】: {news.get('importance', 'N/A')}")
            print(f"   【内容】: {news.get('content', 'N/A')}")
            print("-" * 40)

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_crawl_a_stock_news():
    """测试爬取A股新闻"""
    print("\n" + "=" * 60)
    print("测试爬取A股新闻（a-stock）")
    print("=" * 60)

    try:
        news_list = await wallstreetcn_crawl_news("a-stock", limit=3)
        print(f"成功获取 {len(news_list)} 条A股新闻\n")

        for i, news in enumerate(news_list, 1):
            print(f"{i}. 【时间】: {news.get('time', 'N/A')}")
            print(f"   【重要性】: {news.get('importance', 'N/A')}")
            print(f"   【内容】: {news.get('content', 'N/A')}")
            print("-" * 40)

    except Exception as e:
        print(f"测试失败: {e}")


async def test_crawl_all_categories():
    """测试爬取所有类别新闻"""
    print("\n" + "=" * 60)
    print("测试爬取所有类别新闻（每类取2条）")
    print("=" * 60)

    try:
        all_news = await wallstreetcn_crawl_all_categories(limit=2)
        total_count = 0

        for category, news_list in all_news.items():
            category_name = {v: k for k, v in CATEGORY_MAP.items()}.get(category, category)
            print(f"\n【{category_name}】: {len(news_list)} 条")
            total_count += len(news_list)

            if news_list:
                latest = news_list[0]
                print(f"  最新: {latest.get('content', 'N/A')[:80]}...")

        print(f"\n总计获取 {total_count} 条新闻")

    except Exception as e:
        print(f"测试失败: {e}")


async def test_get_important_news():
    """测试获取重要新闻"""
    print("\n" + "=" * 60)
    print("测试获取重要新闻")
    print("=" * 60)

    try:
        important_news = await get_important_news("global", limit=3)
        print(f"成功获取 {len(important_news)} 条重要新闻\n")

        for i, news in enumerate(important_news, 1):
            print(f"{i}. 【时间】: {news.get('time', 'N/A')}")
            print(f"   【内容】: {news.get('content', 'N/A')}")
            print("-" * 40)

    except Exception as e:
        print(f"测试失败: {e}")


async def test_crawl_multiple_categories():
    """测试爬取多个类别"""
    print("\n" + "=" * 60)
    print("测试爬取多个类别（美股、港股、商品）")
    print("=" * 60)

    categories = ["us-stock", "hk-stock", "commodity"]

    for category in categories:
        try:
            print(f"\n正在爬取 {category}...")
            news_list = await wallstreetcn_crawl_news(category, limit=2)
            print(f"成功获取 {len(news_list)} 条新闻")

            if news_list:
                print(f"示例: {news_list[0].get('content', 'N/A')[:60]}...")

        except Exception as e:
            print(f"爬取 {category} 失败: {e}")



async def save_news_to_file(news_list, filename):
    """保存新闻到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        print(f"新闻已保存到 {filename}")
    except Exception as e:
        print(f"保存文件失败: {e}")


async def main():
    """主测试函数"""
    print("\n开始华尔街见闻新闻爬取测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 运行各项测试
    await test_crawl_global_news()
    await test_crawl_a_stock_news()
    await test_crawl_all_categories()
    await test_get_important_news()
    await test_crawl_multiple_categories()

    # 获取一些要闻保存到文件
    print("\n" + "=" * 60)
    print("保存要闻到文件")
    print("=" * 60)

    try:
        global_news = await wallstreetcn_crawl_news("global", limit=10)
        if global_news:
            filename = f"wallstreetcn_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            await save_news_to_file(global_news, filename)
    except Exception as e:
        print(f"保存新闻失败: {e}")

    print("\n测试完成！")


if __name__ == "__main__":
    asyncio.run(main())
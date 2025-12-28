#!/bin/bash
# Keep Render service alive
# 使用 cron 或 GitHub Actions 定期调用

URL="https://fnewscrawler.onrender.com/api/monitor/overview"

while true; do
    echo "$(date): Pinging $URL"
    curl -s "$URL" > /dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Service is alive"
    else
        echo "❌ Service is down"
    fi
    
    # 每10分钟 ping 一次
    sleep 600
done


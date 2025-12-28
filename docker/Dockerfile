FROM noimankdocker/fnewscrawler:dev

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 使用uv安装项目依赖
RUN uv sync --frozen --no-dev

# 安装Playwright浏览器
RUN uv run playwright install chromium && \
    uv run playwright install-deps chromium || true

# 设置环境变量
ENV PYTHONPATH=/app
ENV WEB_HOST=0.0.0.0
ENV WEB_PORT=8480
ENV REDIS_HOST=localhost
ENV REDIS_PORT=6379
ENV PW_USE_HEADLESS=true
ENV LOG_FILE_PATH=/app/FNewsCrawler.log

EXPOSE 8480

# 启动脚本
COPY docker/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8480/api/monitor/overview || exit 1

# 启动命令
ENTRYPOINT ["/app/start.sh"]
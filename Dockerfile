# 使用官方 Python 3.11 轻量镜像
FROM python:3.11-slim

# 环境变量：避免输出缓冲，pip 不缓存，Render 默认 PORT=8080
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080 \
    PYTHONPATH="/app/backend/app:${PYTHONPATH}"

# 安装系统依赖：libpq5 用于 psycopg2 连接 Postgres/Neon
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

# 设置容器工作目录
WORKDIR /app

# 先复制 requirements.txt 并安装（利用缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再复制代码（后端 + 前端）
COPY backend ./backend
COPY frontend ./frontend

# 可选健康检查（本地调试有用，Render 也会识别）
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -fsS "http://127.0.0.1:${PORT}/" || curl -fsS "http://127.0.0.1:${PORT}/docs" || exit 1

# 暴露端口（本地用，Render 会自动映射）
EXPOSE ${PORT}

# 启动应用：gunicorn + uvicorn worker
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "backend.app.main:app", "--bind", "0.0.0.0:8080", "--timeout", "120"]

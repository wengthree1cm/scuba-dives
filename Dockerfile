# 使用官方 Python 3.11 轻量镜像
FROM python:3.11-slim

# 避免输出被缓冲，pip 不用缓存
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

# 设置容器里的工作目录
WORKDIR /app

# 先复制依赖文件并安装（利用缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再复制项目代码
COPY . .

# 容器启动时运行 gunicorn + uvicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "backend.app.main:app", "--bind", "0.0.0.0:8080", "--timeout", "120"]

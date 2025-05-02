FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
# 先安装特定版本的numpy，避免与pandas的兼容性问题
RUN pip install --no-cache-dir numpy==1.22.4
# 然后安装其他依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p uploads instance
RUN chmod 755 uploads instance

# 暴露端口
EXPOSE 5050

# 设置环境变量
ENV FLASK_DEBUG=False
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5050
ENV PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5050/ || exit 1

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5050", "app:create_app()"]

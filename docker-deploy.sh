#!/bin/bash

# Docker部署脚本 - 在服务器上部署词汇卡片应用

# 确保脚本在出错时停止
set -e

echo "开始Docker部署词汇卡片应用..."

# 1. 更新系统
echo "更新系统..."
sudo apt-get update
sudo apt-get upgrade -y

# 2. 安装Docker和Docker Compose
echo "安装Docker和Docker Compose..."
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo apt-get install -y docker-compose

# 3. 创建SSL证书目录
echo "创建SSL证书目录..."
sudo mkdir -p nginx/ssl

# 4. 生成自签名SSL证书（如果没有正式证书）
echo "生成自签名SSL证书（仅用于测试）..."
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/CN=vocabulary.fueny.cn" \
  -addext "subjectAltName=DNS:vocabulary.fueny.cn"

# 5. 设置环境变量
echo "设置环境变量..."
if [ ! -f .env ]; then
    echo "创建.env文件..."
    # 生成随机密钥
    SECRET_KEY=$(openssl rand -hex 24)
    # 创建.env文件
    echo "SECRET_KEY=$SECRET_KEY" > .env
    echo "已创建.env文件并设置随机密钥"
fi

# 6. 构建和启动Docker容器
echo "构建和启动Docker容器..."
sudo docker-compose up -d --build

# 7. 显示容器状态
echo "显示容器状态..."
sudo docker-compose ps

echo "Docker部署完成！应用现在应该可以通过配置的域名访问。"
echo "如需使用正式SSL证书，请将证书文件放置在 nginx/ssl/ 目录下，并重启容器。"

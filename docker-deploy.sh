#!/bin/bash

# Docker部署脚本 - 在服务器上部署词汇卡片应用
# 此脚本会自动安装Docker、配置环境并部署应用

# 确保脚本在出错时停止
set -e

echo "开始Docker部署词汇卡片应用..."

# 1. 更新系统
echo "更新系统..."

# 检测操作系统
if [ ! -f /etc/os-release ]; then
    echo "无法检测操作系统，尝试通用更新方式..."
    sudo apt-get update || sudo yum update -y
else
    OS_NAME=$(grep -oP '(?<=^ID=).+' /etc/os-release | tr -d '"')

    if [[ "$OS_NAME" == "ubuntu" ]] || [[ "$OS_NAME" == "debian" ]]; then
        # Ubuntu/Debian更新方式
        sudo apt-get update
        sudo apt-get upgrade -y
    elif [[ "$OS_NAME" == "amzn" ]]; then
        # Amazon Linux更新方式
        sudo yum update -y
    else
        echo "未知操作系统，尝试通用更新方式..."
        sudo apt-get update || sudo yum update -y
    fi
fi

# 2. 安装Docker和Docker Compose
echo "安装Docker和Docker Compose..."

# 检测操作系统
OS_NAME=$(grep -oP '(?<=^ID=).+' /etc/os-release | tr -d '"')
OS_VERSION=$(grep -oP '(?<=^VERSION_ID=).+' /etc/os-release | tr -d '"')
echo "检测到操作系统: $OS_NAME $OS_VERSION"

if ! command -v docker &> /dev/null; then
    echo "Docker未安装，正在安装..."

    # 安装通用依赖
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common || true

    # 根据不同操作系统安装Docker
    if [[ "$OS_NAME" == "ubuntu" ]] || [[ "$OS_NAME" == "debian" ]]; then
        # Ubuntu/Debian安装方式
        curl -fsSL https://download.docker.com/linux/$OS_NAME/gpg | sudo apt-key add - || true
        sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/$OS_NAME $(lsb_release -cs) stable" || true
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    elif [[ "$OS_NAME" == "amzn" ]]; then
        # Amazon Linux安装方式
        sudo amazon-linux-extras install docker -y || true
        sudo yum install -y docker
        sudo systemctl enable docker
        sudo systemctl start docker
    else
        echo "未知操作系统，尝试通用安装方式..."
        sudo apt-get install -y docker.io || sudo yum install -y docker
    fi
else
    echo "Docker已安装，跳过安装步骤"
fi

# 确保当前用户可以运行docker命令
sudo usermod -aG docker $USER || true

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose未安装，正在安装..."

    if [[ "$OS_NAME" == "ubuntu" ]] || [[ "$OS_NAME" == "debian" ]]; then
        # Ubuntu/Debian安装方式
        sudo apt-get install -y docker-compose-plugin docker-compose || true
    elif [[ "$OS_NAME" == "amzn" ]]; then
        # Amazon Linux安装方式
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    else
        # 通用安装方式
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
else
    echo "Docker Compose已安装，跳过安装步骤"
fi

# 3. 创建必要的目录
echo "创建必要的目录..."
mkdir -p nginx/conf.d
mkdir -p nginx/ssl
mkdir -p uploads
mkdir -p instance
mkdir -p static
mkdir -p logs

# 4. 设置目录权限
echo "设置目录权限..."
chmod -R 755 uploads instance static logs

# 5. 设置环境变量
echo "设置环境变量..."
if [ ! -f .env ]; then
    echo "创建.env文件..."
    # 生成随机密钥
    SECRET_KEY=$(openssl rand -hex 24)
    # 创建.env文件
    cat > .env << EOF
# 安全配置
SECRET_KEY=$SECRET_KEY

# 应用配置
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5050

# 域名配置（可选）
DOMAIN_NAME=localhost
EOF
    echo "已创建.env文件并设置随机密钥"
fi

# 6. 生成自签名SSL证书（可选）
echo "检查SSL证书..."
if [ ! -f nginx/ssl/fullchain.pem ] || [ ! -f nginx/ssl/privkey.pem ]; then
    echo "未找到SSL证书，生成自签名证书..."

    # 从.env文件获取域名，如果存在
    DOMAIN_NAME="vocabulary.fueny.cn"
    if [ -f .env ]; then
        source .env
    fi

    # 生成自签名证书
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout nginx/ssl/privkey.pem \
      -out nginx/ssl/fullchain.pem \
      -subj "/CN=$DOMAIN_NAME" \
      -addext "subjectAltName=DNS:$DOMAIN_NAME"

    echo "已生成自签名SSL证书（仅用于测试）"
    echo "如需在生产环境使用，请替换为正式的SSL证书"
else
    echo "SSL证书已存在，跳过生成步骤"
fi

# 7. 构建和启动Docker容器
echo "构建和启动Docker容器..."
sudo docker-compose up -d --build

# 等待容器启动
echo "等待容器启动..."
sleep 15

# 8. 检查容器状态
echo "检查容器状态..."
CONTAINER_STATUS=$(sudo docker ps -a --filter "name=vocabulary-app" --format "{{.Status}}")
if [[ $CONTAINER_STATUS == *"Up"* ]]; then
    echo "应用容器已成功启动！"
else
    echo "警告：应用容器可能未正常启动，请检查日志："
    sudo docker logs vocabulary-app
    echo ""
    echo "常见问题："
    echo "1. 依赖版本不兼容：确保numpy和pandas版本兼容"
    echo "2. 端口冲突：确保80和443端口未被其他应用占用"
    echo "3. 权限问题：确保uploads和instance目录有正确的权限"
    echo ""
    echo "如需修复依赖问题，请编辑Dockerfile和requirements.txt文件，调整numpy和pandas版本"
fi

# 9. 显示容器状态
echo "显示容器状态..."
sudo docker-compose ps

# 10. 显示访问信息
echo ""
echo "Docker部署完成！应用现在应该可以通过以下方式访问："
echo "- 通过HTTP访问: http://服务器IP:8080"
echo "- 通过域名访问: http://$DOMAIN_NAME:8080"
echo "- 通过HTTPS访问: https://$DOMAIN_NAME:8443"
echo ""
echo "注意：这是基本Docker部署方式，使用非标准端口。"
echo "如果您希望通过标准端口（无需指定端口号）访问应用，请使用反向代理部署方式："
echo ""
echo "  chmod +x setup-reverse-proxy.sh"
echo "  ./setup-reverse-proxy.sh"
echo ""
echo "反向代理部署方式适用于在同一服务器上运行多个应用，或者您希望通过标准端口访问应用。"
echo "详细说明请参考README.md文件中的\"反向代理部署\"部分。"
echo ""
echo "如需查看应用日志，请运行: sudo docker logs vocabulary-app"
echo "如需查看Nginx日志，请运行: sudo docker logs vocabulary-nginx"

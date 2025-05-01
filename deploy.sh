#!/bin/bash

# 部署脚本 - 在AWS EC2 Ubuntu服务器上部署词汇卡片应用

# 确保脚本在出错时停止
set -e

echo "开始部署词汇卡片应用..."

# 1. 更新系统
echo "更新系统..."
sudo apt-get update
sudo apt-get upgrade -y

# 2. 安装依赖
echo "安装依赖..."
sudo apt-get install -y python3 python3-pip python3-venv nginx

# 3. 项目目录已通过git clone创建
echo "项目目录已通过git clone创建，无需再创建..."

# 4. 项目文件已通过git clone获取，无需复制
echo "项目文件已通过git clone获取，无需复制..."

# 5. 创建并激活虚拟环境
echo "设置Python虚拟环境..."
# 当前目录已经是项目目录，无需cd
python3 -m venv venv
source venv/bin/activate

# 6. 安装Python依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 7. 设置服务
echo "设置systemd服务..."
# 文件已经预先配置好路径，无需替换
sudo cp REW.service /etc/systemd/system/REW.service
sudo systemctl daemon-reload
sudo systemctl enable REW
sudo systemctl start REW

# 8. 配置Nginx
echo "配置Nginx..."
# 文件已经预先配置好路径，无需替换
sudo cp REW_nginx.conf /etc/nginx/sites-available/REW
sudo ln -sf /etc/nginx/sites-available/REW /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 9. 创建必要的目录并设置权限
echo "设置目录权限..."
mkdir -p uploads
mkdir -p instance
chmod 755 uploads
chmod 755 instance

echo "部署完成！应用现在应该可以通过配置的域名访问。"

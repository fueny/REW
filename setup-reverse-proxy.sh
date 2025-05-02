#!/bin/bash

# 反向代理设置脚本 - 在服务器上设置Nginx反向代理
# 此脚本会安装Nginx、配置反向代理并获取SSL证书

# 确保脚本在出错时停止
set -e

echo "开始设置Nginx反向代理..."

# 1. 安装Nginx
echo "安装Nginx..."
sudo apt-get update
sudo apt-get install -y nginx

# 2. 创建配置目录
echo "创建配置目录..."
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled
sudo mkdir -p /var/www/html

# 3. 复制配置文件
echo "复制配置文件..."
sudo cp nginx/external/vocabulary.fueny.cn.conf /etc/nginx/sites-available/

# 4. 创建符号链接
echo "创建符号链接..."
sudo ln -sf /etc/nginx/sites-available/vocabulary.fueny.cn.conf /etc/nginx/sites-enabled/

# 5. 测试Nginx配置
echo "测试Nginx配置..."
sudo nginx -t

# 6. 重启Nginx
echo "重启Nginx..."
sudo systemctl restart nginx

# 7. 安装Certbot（用于获取SSL证书）
echo "安装Certbot..."
sudo apt-get install -y certbot python3-certbot-nginx

# 8. 获取SSL证书
echo "获取SSL证书..."
sudo certbot --nginx -d vocabulary.fueny.cn

# 9. 显示完成信息
echo ""
echo "反向代理设置完成！"
echo "现在您可以通过以下方式访问应用："
echo "- HTTP: http://vocabulary.fueny.cn (会自动重定向到HTTPS)"
echo "- HTTPS: https://vocabulary.fueny.cn"
echo ""
echo "注意：如果您的服务器上有防火墙，请确保开放80和443端口："
echo "sudo ufw allow 80/tcp"
echo "sudo ufw allow 443/tcp"
echo ""
echo "如需查看Nginx日志，请运行："
echo "sudo tail -f /var/log/nginx/access.log"
echo "sudo tail -f /var/log/nginx/error.log"

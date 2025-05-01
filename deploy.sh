#!/bin/bash

# 部署脚本 - 在AWS EC2 Ubuntu服务器上部署词汇卡片应用

# 确保脚本在出错时停止
set -e

echo "开始部署词汇卡片应用..."

# 备份当前版本（如果存在）
if [ -d "/home/ubuntu/REW_backup" ]; then
    echo "删除旧的备份..."
    sudo rm -rf /home/ubuntu/REW_backup
fi

if [ -d "/home/ubuntu/REW" ] && [ "$(pwd)" != "/home/ubuntu/REW" ]; then
    echo "备份当前版本..."
    sudo cp -r /home/ubuntu/REW /home/ubuntu/REW_backup
fi

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

# 7. 设置环境变量
echo "设置环境变量..."
if [ ! -f .env ]; then
    echo "创建.env文件..."
    if [ -f .env.example ]; then
        cp .env.example .env
        # 生成随机密钥
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(24))")
        # 替换密钥
        sed -i "s/your_secret_key_here/$SECRET_KEY/g" .env
        echo "已创建.env文件并设置随机密钥"
    else
        echo "警告：.env.example文件不存在，无法创建.env文件"
    fi
fi

# 7. 设置服务
echo "设置systemd服务..."
# 文件已经预先配置好路径，无需替换
sudo cp REW.service /etc/systemd/system/REW.service
sudo systemctl daemon-reload
sudo systemctl enable REW
sudo systemctl start REW

# 8. 安装Certbot并获取SSL证书
echo "安装Certbot并获取SSL证书..."
sudo apt-get install -y certbot python3-certbot-nginx

# 从.env文件获取域名，如果存在
DOMAIN_NAME="vocabulary.fueny.cn"
if [ -f .env ]; then
    source .env
fi

# 获取SSL证书
echo "为域名 $DOMAIN_NAME 获取SSL证书..."
sudo certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email admin@$DOMAIN_NAME

# 9. 配置Nginx
echo "配置Nginx..."
# 文件已经预先配置好路径，无需替换
sudo cp REW_nginx.conf /etc/nginx/sites-available/REW
sudo ln -sf /etc/nginx/sites-available/REW /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 10. 创建必要的目录并设置权限
echo "设置目录权限..."
mkdir -p uploads
mkdir -p instance
chmod 755 uploads
chmod 755 instance

# 11. 设置定时备份
echo "设置数据库定时备份..."
# 创建备份目录
sudo mkdir -p /home/ubuntu/REW_backups
# 设置备份脚本权限
chmod +x backup_db.sh
# 添加到crontab，每天凌晨3点执行备份
(crontab -l 2>/dev/null; echo "0 3 * * * /home/ubuntu/REW/backup_db.sh") | crontab -

echo "部署完成！应用现在应该可以通过配置的域名访问。"

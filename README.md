# 词汇卡片 Web 应用

这是一个基于 Flask 的 Web 应用程序，用于从 Excel 文件 (`vocabulary.xlsx`) 加载词汇数据并以交互式卡片的形式展示，支持导航和词汇块显示。本项目使用Docker进行部署，简化了环境配置和依赖管理。

## 功能

*   从 `vocabulary.xlsx` 读取包含 `编号`, `单词`, `音标`, `释义`, `拆分`, `综合法`, `联想法` 七个字段的数据。
*   在网页上以卡片形式展示词汇。
*   提供 "上一张" 和 "下一张" 按钮进行导航。
*   提供按钮切换 "释义", "拆分", "综合法", "联想法" 等详细信息的可见性。
*   词汇块功能：将词汇按100个一组显示，点击块可查看对应范围内的单词列表。
*   允许用户点击词汇列表中的单词跳转到对应的卡片。
*   **新功能**：允许用户上传自定义的 Excel 文件，支持中英文文件名。
*   **新功能**：保存学习进度，用户可以从上次学习的位置继续。
*   **新功能**：显示当前使用的词汇表文件名，并支持随时切换文件。

## 手动部署指南

本项目使用Docker进行部署，以下是手动部署的步骤。

### 准备工作

1. **准备服务器**:
   * 确保服务器已安装Docker和Docker Compose
   * 如果未安装，可以使用以下命令安装：
     ```bash
     # 安装Docker
     sudo apt update
     sudo apt install -y docker.io
     sudo systemctl enable docker
     sudo systemctl start docker

     # 安装Docker Compose
     sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
     sudo chmod +x /usr/local/bin/docker-compose
     sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
     ```

2. **准备词汇文件**:
   * 准备一个名为 `vocabulary.xlsx` 的Excel文件。
   * 确保该文件包含以下七个列标题：`编号`, `单词`, `音标`, `释义`, `拆分`, `综合法`, `联想法`。
   * 将 `vocabulary.xlsx` 文件放置在项目根目录中。
   * 如果您没有自己的文件，可以使用项目根目录中提供的示例文件。

### 部署方式选择

本项目提供两种部署方式：

1. **独立部署**：适用于在新服务器上部署单个应用
2. **与其他应用共存部署**：适用于在已有其他应用（如memos）的服务器上部署

### 独立部署

1. **创建必要的目录**:
   ```bash
   mkdir -p uploads
   mkdir -p instance
   mkdir -p static
   mkdir -p logs

   # 设置目录权限
   chmod -R 755 uploads instance static logs

   # 创建nginx配置目录
   mkdir -p nginx/conf.d
   ```

2. **创建Nginx配置文件**:
   ```bash
   # 创建nginx配置文件
   cat > nginx/conf.d/app.conf << EOF
   # HTTP服务器
   server {
       listen 80;
       server_name vocabulary.fueny.cn;  # 请替换为您的域名

       # 设置较大的客户端请求体大小限制，以支持文件上传
       client_max_body_size 20M;

       # 静态文件直接由nginx提供服务
       location /static/ {
           alias /app/static/;
           expires 30d;
       }

       # 上传文件目录（只读访问）
       location /uploads/ {
           alias /app/uploads/;
           expires 30d;
           add_header Cache-Control "public, max-age=2592000";
       }

       # 所有其他请求转发到Flask应用
       location / {
           proxy_pass http://web:5050;
           proxy_set_header Host \$host;
           proxy_set_header X-Real-IP \$remote_addr;
           proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto \$scheme;

           # 增加超时时间，避免大文件上传超时
           proxy_connect_timeout 300s;
           proxy_send_timeout 300s;
           proxy_read_timeout 300s;
       }
   }
   EOF
   ```

3. **创建环境变量文件**:
   ```bash
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
   DOMAIN_NAME=vocabulary.fueny.cn
   EOF
   ```

4. **修改docker-compose.yml文件**:

   根据您的Docker Compose版本，可能需要修改版本号。如果您使用的是较旧版本的Docker Compose，请将版本号从`3.8`改为`3.3`或`2.2`。

   ```bash
   # 查看Docker Compose版本
   docker-compose --version

   # 如果版本低于1.25.0，请修改docker-compose.yml文件
   # 将第一行的 version: '3.8' 改为 version: '3.3' 或 version: '2.2'
   ```

5. **构建和启动Docker容器**:
   ```bash
   # 构建和启动容器
   docker-compose up -d --build

   # 检查容器状态
   docker-compose ps
   ```

6. **访问应用**:
   * 打开您的Web浏览器。
   * 访问 `http://localhost:8080` 或 `http://服务器IP:8080`。
   * 如果您配置了域名，也可以通过域名访问：`http://vocabulary.fueny.cn:8080`。

### 与其他应用共存部署（使用外部Nginx反向代理）

如果您的服务器上已经有其他应用（如memos）和Nginx运行，您可以使用以下步骤部署REW项目：

1. **按照独立部署的步骤1-4部署Docker容器**

2. **找出外部Nginx配置目录**:
   ```bash
   # 如果Nginx运行在Docker容器中，查找配置目录的挂载点
   docker inspect nginx | grep -A 10 Mounts

   # 例如，配置目录可能挂载在 /opt/dockers/nginx/conf 或类似位置
   ```

3. **创建Nginx反向代理配置**:
   ```bash
   # 假设Nginx配置目录在 /opt/dockers/nginx/conf
   cat > /opt/dockers/nginx/conf/vocabulary.conf << EOF
   server {
       listen 80;
       server_name vocabulary.fueny.cn;
       location / {
           proxy_pass http://vocabulary-app:5050;
           proxy_set_header Host \$host;
           proxy_set_header X-Real-IP \$remote_addr;
           proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto \$scheme;

           # 增加上传文件大小限制
           client_max_body_size 20M;
       }
   }
   EOF
   ```

4. **将Nginx容器连接到REW项目网络**:
   ```bash
   # 查看REW项目的网络
   docker network ls | grep vocabulary

   # 将Nginx容器连接到REW项目网络
   docker network connect rew_vocabulary-network nginx
   ```

5. **重新加载Nginx配置**:
   ```bash
   # 重新加载Nginx配置
   docker exec nginx nginx -s reload
   ```

6. **访问应用**:
   * 打开您的Web浏览器。
   * 通过域名访问：`http://vocabulary.fueny.cn`。

7. **如果无法通过容器名访问，使用IP地址**:

   如果Nginx容器无法通过容器名（vocabulary-app）访问REW应用，可以使用IP地址：

   ```bash
   # 获取vocabulary-app容器的IP地址
   VOCABULARY_IP=$(docker inspect vocabulary-app --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')
   echo $VOCABULARY_IP

   # 修改Nginx配置使用IP地址
   cat > /opt/dockers/nginx/conf/vocabulary.conf << EOF
   server {
       listen 80;
       server_name vocabulary.fueny.cn;
       location / {
           proxy_pass http://$VOCABULARY_IP:5050;
           proxy_set_header Host \$host;
           proxy_set_header X-Real-IP \$remote_addr;
           proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto \$scheme;

           # 增加上传文件大小限制
           client_max_body_size 20M;
       }
   }
   EOF

   # 重新加载Nginx配置
   docker exec nginx nginx -s reload
   ```

## 文件结构

```
REW/
├── app.py                  # 应用入口
├── controllers/            # 控制器
│   ├── vocabulary_controller.py  # 词汇控制器
│   └── auth_controller.py  # 用户认证控制器
├── models/                 # 数据模型
│   ├── vocabulary_model.py # 词汇模型
│   └── database.py         # 数据库操作类
├── static/                 # 静态资源
│   ├── css/                # CSS样式
│   │   └── styles.css
│   └── js/                 # JavaScript文件
│       ├── api.js          # API客户端
│       ├── archive.js      # 存档功能
│       ├── card.js         # 卡片显示功能
│       ├── core.js         # 核心功能和初始化
│       ├── file.js         # 文件管理功能
│       ├── wordblock.js    # 词汇块功能
│       ├── progress.js     # 学习进度功能
│       ├── storage.js      # 本地存储功能
│       └── utils.js        # 通用工具函数
├── templates/              # HTML模板
│   ├── index.html          # 主页面
│   ├── login.html          # 登录页面
│   └── register.html       # 注册页面
├── uploads/                # 上传的文件（持久化卷）
├── instance/               # 实例文件夹（数据库，持久化卷）
├── utils/                  # 工具类
│   ├── config.py           # 配置类
│   └── logging_config.py   # 日志配置
├── nginx/                  # Nginx配置
│   ├── conf.d/             # Nginx配置文件
│   │   └── app.conf        # 应用的Nginx配置
│   └── ssl/                # SSL证书目录（可选）
│       ├── fullchain.pem   # SSL证书链
│       └── privkey.pem     # SSL私钥
├── logs/                   # 日志目录
├── Dockerfile              # Docker镜像构建文件
├── docker-compose.yml      # Docker Compose配置
├── docker-deploy.sh        # Docker部署脚本
├── .dockerignore           # Docker忽略文件
├── .env                    # 环境变量文件
├── .env.example            # 环境变量示例文件
├── vocabulary.xlsx         # 默认词汇表
├── requirements.txt        # 依赖列表
├── README.md               # 项目说明文档
├── .gitignore              # Git忽略文件
└── .gitattributes          # Git属性文件
```

## 注意事项

### 使用说明
* 如果 `vocabulary.xlsx` 文件未找到或格式不正确，应用会显示错误信息或加载默认的错误提示卡片。
* 上传的文件会保存在 `uploads` 目录中，文件名会自动添加唯一标识符以避免冲突。
* 学习进度保存在浏览器的 localStorage 中，与特定的词汇表文件关联。
* 如果更换浏览器或清除浏览器数据，保存的学习进度将会丢失。
* 词汇块功能将词汇按100个一组显示，点击块可查看对应范围内的单词列表，点击单词可跳转到对应卡片。

### Docker部署说明
* 本项目只支持Docker部署，这样可以避免依赖问题并简化部署过程。
* Docker部署会自动设置Nginx、应用服务和必要的目录结构。
* 数据持久化通过Docker卷实现，确保容器重启或重建后数据不会丢失。
* 默认配置的持久化目录：
  * `./uploads`: 存储用户上传的词汇表文件
  * `./instance`: 存储SQLite数据库文件
  * `./logs`: 存储应用日志

### SSL配置（HTTPS）

#### 独立部署的HTTPS配置

如果您使用独立部署方式，并希望启用HTTPS，可以按照以下步骤操作：

1. **获取SSL证书**：
   * 您可以使用Let's Encrypt获取免费的SSL证书
   * 或者使用自签名证书（仅用于测试）

2. **使用Let's Encrypt获取证书**：
   ```bash
   # 安装certbot
   sudo apt install -y certbot

   # 获取证书
   sudo certbot certonly --standalone -d vocabulary.fueny.cn
   ```

3. **创建SSL目录并配置Nginx**：
   ```bash
   # 创建SSL目录
   mkdir -p nginx/ssl

   # 复制证书文件
   sudo cp /etc/letsencrypt/live/vocabulary.fueny.cn/fullchain.pem nginx/ssl/
   sudo cp /etc/letsencrypt/live/vocabulary.fueny.cn/privkey.pem nginx/ssl/

   # 设置权限
   sudo chmod 755 nginx/ssl
   sudo chmod 644 nginx/ssl/*.pem

   # 创建HTTPS配置
   cat > nginx/conf.d/app.conf << EOF
   # HTTP服务器 - 重定向到HTTPS
   server {
       listen 80;
       server_name vocabulary.fueny.cn;  # 请替换为您的域名

       # 将所有HTTP请求重定向到HTTPS
       location / {
           return 301 https://\$host\$request_uri;
       }
   }

   # HTTPS服务器
   server {
       listen 443 ssl;
       server_name vocabulary.fueny.cn;  # 请替换为您的域名

       # SSL证书配置
       ssl_certificate /etc/nginx/ssl/fullchain.pem;
       ssl_certificate_key /etc/nginx/ssl/privkey.pem;

       # SSL配置
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_prefer_server_ciphers on;
       ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;

       # 设置较大的客户端请求体大小限制，以支持文件上传
       client_max_body_size 20M;

       # 静态文件直接由nginx提供服务
       location /static/ {
           alias /app/static/;
           expires 30d;
       }

       # 上传文件目录（只读访问）
       location /uploads/ {
           alias /app/uploads/;
           expires 30d;
           add_header Cache-Control "public, max-age=2592000";
       }

       # 所有其他请求转发到Flask应用
       location / {
           proxy_pass http://web:5050;
           proxy_set_header Host \$host;
           proxy_set_header X-Real-IP \$remote_addr;
           proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto \$scheme;

           # 增加超时时间，避免大文件上传超时
           proxy_connect_timeout 300s;
           proxy_send_timeout 300s;
           proxy_read_timeout 300s;
       }
   }
   EOF
   ```

4. **重启容器**：
   ```bash
   docker-compose restart nginx
   ```

#### 与其他应用共存部署的HTTPS配置

如果您使用与其他应用共存的部署方式，并希望启用HTTPS，可以按照以下步骤操作：

1. **获取SSL证书**：
   ```bash
   # 安装certbot
   sudo apt install -y certbot

   # 创建验证目录
   sudo mkdir -p /var/www/html/.well-known/acme-challenge
   sudo chmod -R 755 /var/www/html

   # 修改Nginx配置，添加验证路径
   cat > /opt/dockers/nginx/conf/vocabulary.conf << EOF
   server {
       listen 80;
       server_name vocabulary.fueny.cn;

       # 添加Let's Encrypt验证路径
       location /.well-known/acme-challenge/ {
           root /var/www/html;
       }

       location / {
           proxy_pass http://vocabulary-app:5050;
           proxy_set_header Host \$host;
           proxy_set_header X-Real-IP \$remote_addr;
           proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto \$scheme;

           # 增加上传文件大小限制
           client_max_body_size 20M;
       }
   }
   EOF

   # 重新加载Nginx配置
   docker exec nginx nginx -s reload

   # 获取证书
   sudo certbot certonly --webroot -w /var/www/html -d vocabulary.fueny.cn
   ```

2. **配置HTTPS**：
   ```bash
   # 修改Nginx配置
   cat > /opt/dockers/nginx/conf/vocabulary.conf << EOF
   server {
       listen 80;
       server_name vocabulary.fueny.cn;

       # 重定向到HTTPS
       location / {
           return 301 https://\$host\$request_uri;
       }

       # Let's Encrypt验证
       location /.well-known/acme-challenge/ {
           root /var/www/html;
       }
   }

   server {
       listen 443 ssl;
       server_name vocabulary.fueny.cn;

       # SSL证书配置
       ssl_certificate /etc/letsencrypt/live/vocabulary.fueny.cn/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/vocabulary.fueny.cn/privkey.pem;

       # SSL配置
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_prefer_server_ciphers on;
       ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;

       location / {
           proxy_pass http://vocabulary-app:5050;
           proxy_set_header Host \$host;
           proxy_set_header X-Real-IP \$remote_addr;
           proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto \$scheme;

           # 增加上传文件大小限制
           client_max_body_size 20M;
       }
   }
   EOF

   # 重新加载Nginx配置
   docker exec nginx nginx -s reload
   ```

3. **设置证书自动更新**：
   ```bash
   # 编辑crontab
   crontab -e

   # 添加以下行，每天凌晨3点尝试更新证书
   0 3 * * * certbot renew --quiet && docker exec nginx nginx -s reload
   ```

更多详细信息，请参考[HTTPS配置指南.md](HTTPS配置指南.md)文件。

### 依赖版本兼容性
* **特别注意**：本项目使用了pandas和numpy库，这些库之间的版本兼容性非常重要。
* 我们已经在Dockerfile中固定了numpy版本为1.22.4，在requirements.txt中固定了pandas版本为1.4.2，这两个版本是兼容的。
* 如果您需要更新这些库的版本，请确保它们之间相互兼容，否则可能会出现`numpy.dtype size changed`错误。
* 如果您在部署过程中遇到依赖问题，请检查容器日志（`docker logs vocabulary-app`）以获取详细错误信息。

### 常见问题排查
* 如果容器无法启动，请检查日志：`docker logs vocabulary-app`
* 如果Nginx无法启动，请检查日志：`docker logs vocabulary-nginx`
* 如果端口冲突，请修改docker-compose.yml文件中的端口映射
* 如果需要更多故障排除信息，请参考项目中的TROUBLESHOOTING.md文件

## 高级部署问题与解决方案

在部署过程中，您可能会遇到一些复杂的问题。以下是一些常见问题及其解决方案：

### 1. Docker Compose版本兼容性问题

**问题**：使用旧版本的Docker Compose时，可能会出现以下错误：
```
ERROR: Version in "./docker-compose.yml" is unsupported.
```

**解决方案**：
1. 降低docker-compose.yml文件中的版本号：
   ```yaml
   # 将
   version: '3.8'
   # 改为
   version: '3.3'
   # 或
   version: '2.2'
   ```
2. 或者升级Docker Compose：
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
   ```

### 2. 环境变量插值问题

**问题**：旧版本的Docker Compose可能不支持环境变量的默认值语法：
```
ERROR: Invalid interpolation format for "web" option in service "services": "SECRET_KEY=${SECRET_KEY:-default_dev_key}"
```

**解决方案**：
1. 简化环境变量设置：
   ```yaml
   environment:
     - FLASK_DEBUG=False
     - SECRET_KEY=${SECRET_KEY}
   ```
2. 确保在运行docker-compose命令前设置了环境变量：
   ```bash
   export SECRET_KEY=$(openssl rand -hex 24)
   ```

### 3. 网络配置问题

**问题**：旧版本的Docker Compose可能不支持networks配置：
```
Unsupported config option for networks: 'vocabulary-network'
```

**解决方案**：
1. 使用旧版本兼容的docker-compose.yml文件：
   ```yaml
   web:
     build: .
     container_name: vocabulary-app
     restart: always
     volumes:
       - ./uploads:/app/uploads
       - ./instance:/app/instance
     environment:
       - FLASK_DEBUG=False
       - SECRET_KEY=your_secret_key_here

   nginx:
     image: nginx:1.22
     container_name: vocabulary-nginx
     restart: always
     ports:
       - "127.0.0.1:8080:80"
       - "127.0.0.1:8443:443"
     volumes:
       - ./nginx/conf.d:/etc/nginx/conf.d:ro
       - ./static:/app/static:ro
       - ./uploads:/app/uploads:ro
       - ./nginx/ssl:/etc/nginx/ssl:ro
     links:
       - web
   ```

### 4. Nginx SSL证书问题

**问题**：Nginx容器无法启动，日志显示：
```
cannot load certificate "/etc/nginx/ssl/fullchain.pem": BIO_new_file() failed
```

**解决方案**：
1. 创建自签名SSL证书：
   ```bash
   mkdir -p nginx/ssl
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout nginx/ssl/privkey.pem \
     -out nginx/ssl/fullchain.pem \
     -subj "/CN=vocabulary.fueny.cn"
   ```
2. 或者修改Nginx配置，禁用HTTPS：
   ```bash
   # 备份原始配置
   cp nginx/conf.d/app.conf nginx/conf.d/app.conf.bak

   # 创建只使用HTTP的配置
   cat > nginx/conf.d/app.conf << EOF
   server {
       listen 80;
       server_name vocabulary.fueny.cn;

       # 设置较大的客户端请求体大小限制，以支持文件上传
       client_max_body_size 20M;

       # 静态文件直接由nginx提供服务
       location /static/ {
           alias /app/static/;
           expires 30d;
       }

       # 上传文件目录（只读访问）
       location /uploads/ {
           alias /app/uploads/;
           expires 30d;
           add_header Cache-Control "public, max-age=2592000";
       }

       # 所有其他请求转发到Flask应用
       location / {
           proxy_pass http://web:5050;
           proxy_set_header Host \$host;
           proxy_set_header X-Real-IP \$remote_addr;
           proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto \$scheme;

           # 增加超时时间，避免大文件上传超时
           proxy_connect_timeout 300s;
           proxy_send_timeout 300s;
           proxy_read_timeout 300s;
       }
   }
   EOF
   ```

### 5. 在已有Nginx服务器上配置反向代理

**问题**：如何在已有Nginx服务器上配置反向代理，将vocabulary.fueny.cn域名指向REW应用？

**解决方案**：
1. 检查Nginx配置目录：
   ```bash
   # 查看Nginx配置文件位置
   nginx -t
   ```

2. 找出配置文件的挂载点（如果使用Docker）：
   ```bash
   docker inspect nginx | grep -A 10 Mounts
   ```

3. 创建配置文件并放在正确的目录中：
   ```bash
   # 假设配置目录挂载在/opt/dockers/memos/nginx/conf
   cat > /opt/dockers/memos/nginx/conf/vocabulary.conf << EOF
   server {
       listen 80;
       server_name vocabulary.fueny.cn;
       location / {
           proxy_pass http://vocabulary-app:5050;
           proxy_set_header Host \$host;
           proxy_set_header X-Real-IP \$remote_addr;
           proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto \$scheme;
       }
   }
   EOF
   ```

4. 重新加载Nginx配置：
   ```bash
   docker exec nginx nginx -s reload
   ```

### 6. 登录问题

**问题**：登录后无法进入主页。

**解决方案**：
1. 检查SECRET_KEY环境变量是否正确设置：
   ```bash
   docker inspect vocabulary-app --format '{{.Config.Env}}'
   ```

2. 如果SECRET_KEY为空，修改.env文件并重启容器：
   ```bash
   # 生成随机密钥
   SECRET_KEY=$(openssl rand -hex 24)

   # 编辑.env文件
   cat > .env << EOF
   # 安全配置
   SECRET_KEY=$SECRET_KEY

   # 应用配置
   FLASK_DEBUG=False
   FLASK_HOST=0.0.0.0
   FLASK_PORT=5050

   # 域名配置
   DOMAIN_NAME=vocabulary.fueny.cn
   EOF

   # 重启容器
   docker-compose down
   docker-compose up -d
   ```

### 7. 配置HTTPS

如果您需要为vocabulary.fueny.cn配置HTTPS，请参考[HTTPS配置指南.md](HTTPS配置指南.md)文件。

## 服务器部署建议

### 选择部署方式

本项目提供两种部署方式，请根据您的需求选择：

1. **基本Docker部署**：适用于单一应用部署，或者您不介意使用非标准端口访问应用。
2. **反向代理部署**：适用于在同一服务器上运行多个应用，或者您希望通过标准端口（无需指定端口号）访问应用。

### 准备服务器

无论选择哪种部署方式，都需要先准备服务器：

1. **准备服务器**
   - 启动一个Ubuntu服务器实例或Amazon EC2实例
   - 确保安全组/防火墙允许HTTP(80)和HTTPS(443)端口访问
   - 连接到实例（使用SSH）

   **AWS EC2特别说明**：
   - 启动EC2实例时，建议选择Amazon Linux 2或Ubuntu
   - 实例类型建议至少为t2.micro（1GB内存）
   - 确保EC2安全组允许入站HTTP(80)和HTTPS(443)流量
   - 如果您使用弹性IP，请将其关联到您的EC2实例

2. **获取项目代码**
   - 在服务器上安装Git（如果尚未安装）
   ```bash
   sudo apt update
   sudo apt install -y git
   ```
   - 克隆项目仓库
   ```bash
   git clone https://github.com/your-username/REW.git
   cd REW
   ```

### 管理Docker容器

部署完成后，您可以使用以下命令管理Docker容器：

- 查看容器状态：`sudo docker-compose ps`
- 启动容器：`sudo docker-compose up -d`
- 停止容器：`sudo docker-compose down`
- 重启容器：`sudo docker-compose restart`
- 查看应用日志：`sudo docker logs vocabulary-app`
- 查看Nginx日志：`sudo docker logs vocabulary-nginx`
- 查看所有容器日志：`sudo docker-compose logs -f`

### 更新应用

如果您需要更新应用，可以按照以下步骤操作：

1. 拉取最新代码
   ```bash
   git pull
   ```

2. 重新构建并启动容器
   ```bash
   sudo docker-compose up -d --build
   ```

### 备份数据

建议定期备份以下目录，以防数据丢失：

- `./uploads`：用户上传的词汇表文件
- `./instance`：SQLite数据库文件

您可以使用以下命令创建备份：

```bash
# 创建备份目录
mkdir -p backups

# 备份数据
tar -czf backups/data-backup-$(date +%Y%m%d).tar.gz uploads instance

# 列出备份文件
ls -la backups/
```

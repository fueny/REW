# 故障排除指南

本文档提供了部署和运行词汇卡片应用时可能遇到的常见问题及其解决方案。

## 目录

1. [依赖问题](#依赖问题)
2. [容器启动失败](#容器启动失败)
3. [网络访问问题](#网络访问问题)
4. [数据持久化问题](#数据持久化问题)
5. [性能问题](#性能问题)

## 依赖问题

### numpy和pandas版本不兼容

**症状**：应用容器不断重启，日志中出现类似以下错误：
```
ValueError: numpy.dtype size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject
```

**解决方案**：
1. 确保使用兼容的numpy和pandas版本：
   - 在Dockerfile中固定numpy版本：`RUN pip install --no-cache-dir numpy==1.22.4`
   - 在requirements.txt中固定pandas版本：`pandas==1.4.2`

2. 如果问题仍然存在，尝试清理并重建容器：
   ```bash
   sudo docker-compose down
   sudo docker system prune -f
   sudo docker-compose up -d --build
   ```

### 其他依赖问题

**症状**：应用启动失败，日志中出现导入错误或模块未找到错误。

**解决方案**：
1. 检查requirements.txt文件，确保所有依赖都列出并且版本兼容
2. 在Dockerfile中添加必要的系统依赖
3. 尝试在本地环境中测试依赖安装

## 容器启动失败

### 端口冲突

**症状**：容器无法启动，日志中出现类似以下错误：
```
ERROR: for nginx Cannot start service nginx: failed to bind port 80
```
或
```
ERROR: for nginx Cannot start service nginx: failed to bind port 443
```

**解决方案**：

#### 方案1：修改端口映射

1. 检查端口是否被占用：
   ```bash
   sudo netstat -tulpn | grep -E '80|443'
   ```

2. 修改docker-compose.yml文件，使用不同的端口：
   ```yaml
   ports:
     - "8080:80"  # 将80改为8080
     - "8443:443"  # 将443改为8443
   ```

3. 如果修改了HTTPS端口，还需要更新Nginx配置中的重定向规则：
   ```
   # 在nginx/conf.d/app.conf文件中
   location / {
       return 301 https://$host:8443$request_uri;  # 添加端口号
   }
   ```

4. 重启容器：
   ```bash
   docker-compose down
   docker-compose up -d
   ```

#### 方案2：使用Nginx反向代理

如果您希望通过标准端口（无需指定端口号）访问应用，但端口已被其他应用占用，可以设置一个额外的Nginx反向代理：

1. 安装Nginx：
   ```bash
   sudo apt update
   sudo apt install -y nginx
   ```

2. 创建配置文件：
   ```bash
   sudo nano /etc/nginx/sites-available/vocabulary.fueny.cn
   ```

3. 添加以下配置：
   ```nginx
   server {
       listen 80;
       server_name vocabulary.fueny.cn;

       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }

   server {
       listen 443 ssl;
       server_name vocabulary.fueny.cn;

       ssl_certificate /etc/letsencrypt/live/vocabulary.fueny.cn/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/vocabulary.fueny.cn/privkey.pem;

       location / {
           proxy_pass https://localhost:8443;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

4. 启用配置：
   ```bash
   sudo ln -s /etc/nginx/sites-available/vocabulary.fueny.cn /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. 获取SSL证书（如果需要）：
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d vocabulary.fueny.cn
   ```

#### 方案3：使用不同的子域名

如果您有多个应用需要通过标准端口访问，可以为每个应用使用不同的子域名：

1. 为每个应用创建DNS记录，指向您的服务器IP
2. 在每个应用的Nginx配置中使用不同的server_name
3. 使用Let's Encrypt为每个子域名获取证书

### 权限问题

**症状**：容器启动但应用无法写入文件，日志中出现权限错误。

**解决方案**：
1. 确保volumes目录有正确的权限：
   ```bash
   sudo chmod -R 755 uploads instance
   ```

2. 在Dockerfile中设置正确的用户权限

## 网络访问问题

### 无法从公网访问应用

**症状**：容器正常运行，但无法从公网访问应用。

**解决方案**：
1. 检查安全组设置，确保允许HTTP(80)和HTTPS(443)端口的入站流量
2. 检查服务器防火墙设置：
   ```bash
   sudo ufw status
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```
3. 确认域名解析正确（如果使用域名）：
   ```bash
   nslookup your-domain.com
   ```
4. 测试本地访问：
   ```bash
   curl http://localhost
   ```

### Nginx配置问题

**症状**：Nginx容器运行正常，但请求未正确代理到应用容器。

**解决方案**：
1. 检查Nginx配置：
   ```bash
   sudo docker exec -it vocabulary-nginx cat /etc/nginx/conf.d/app.conf
   ```
2. 确保proxy_pass指向正确的应用容器和端口：
   ```
   proxy_pass http://web:5050;
   ```
3. 检查容器网络连接：
   ```bash
   sudo docker network inspect bridge
   ```

## 数据持久化问题

### 数据丢失

**症状**：容器重启后数据丢失。

**解决方案**：
1. 确保正确配置了卷映射：
   ```yaml
   volumes:
     - ./uploads:/app/uploads
     - ./instance:/app/instance
   ```
2. 检查主机目录是否存在并有正确的权限
3. 备份重要数据

## 性能问题

### 应用响应缓慢

**症状**：应用加载缓慢或响应时间长。

**解决方案**：
1. 增加gunicorn工作进程数：
   ```
   CMD ["gunicorn", "-w", "8", "-b", "0.0.0.0:5050", "app:create_app()"]
   ```
2. 优化数据库查询
3. 添加缓存机制
4. 考虑使用更强大的服务器

### 内存使用过高

**症状**：容器使用过多内存，可能导致服务器内存不足。

**解决方案**：
1. 在docker-compose.yml中限制容器内存使用：
   ```yaml
   mem_limit: 512m
   ```
2. 优化应用代码，减少内存使用
3. 增加服务器内存

## 获取帮助

如果您遇到本文档未涵盖的问题，请：
1. 检查应用日志：`sudo docker logs vocabulary-app`
2. 检查Nginx日志：`sudo docker logs vocabulary-nginx`
3. 在GitHub仓库中提交issue

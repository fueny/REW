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

## 部署方式

本项目提供两种部署方式：基本Docker部署和反向代理部署。反向代理部署适用于在同一服务器上运行多个应用的情况。

### 基本Docker部署

1. **准备词汇文件**:
   * 准备一个名为 `vocabulary.xlsx` 的Excel文件。
   * 确保该文件包含以下七个列标题：`编号`, `单词`, `音标`, `释义`, `拆分`, `综合法`, `联想法`。
   * 将 `vocabulary.xlsx` 文件放置在项目根目录中。
   * 如果您没有自己的文件，可以使用项目根目录中提供的示例文件。

2. **使用部署脚本**:
   * 给部署脚本添加执行权限：
     ```bash
     chmod +x docker-deploy.sh
     ```
   * 运行部署脚本：
     ```bash
     ./docker-deploy.sh
     ```
   * 脚本会自动安装Docker（如果尚未安装）、创建必要的目录、生成SSL证书（自签名）并启动容器。

3. **访问应用**:
   * 打开您的Web浏览器。
   * 访问 `http://localhost:8080` 或 `http://服务器IP:8080`。
   * 如果您配置了域名，也可以通过域名访问：`http://vocabulary.fueny.cn:8080`。
   * 如果启用了HTTPS，可以通过 `https://vocabulary.fueny.cn:8443` 访问。

### 反向代理部署（推荐）

如果您的服务器上运行多个应用，推荐使用反向代理部署方式，这样可以通过标准端口（80/443）访问应用，无需指定端口号。

1. **准备词汇文件并部署Docker容器**:
   * 按照基本部署的步骤1-2操作，部署Docker容器。
   * 这将启动应用，但只在本地端口（127.0.0.1:8080和127.0.0.1:8443）上可用。

2. **设置反向代理**:
   * 给反向代理设置脚本添加执行权限：
     ```bash
     chmod +x setup-reverse-proxy.sh
     ```
   * 运行反向代理设置脚本：
     ```bash
     ./setup-reverse-proxy.sh
     ```
   * 脚本会安装Nginx、配置反向代理并获取SSL证书。

3. **访问应用**:
   * 打开您的Web浏览器。
   * 通过域名直接访问：`https://vocabulary.fueny.cn`（不需要端口号）。
   * HTTP请求会自动重定向到HTTPS。

   > **注意**：反向代理部署方式允许您在同一服务器上运行多个应用，每个应用使用不同的域名或子域名，而不会出现端口冲突。

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
* 默认情况下，部署脚本会生成自签名SSL证书，仅用于测试。
* 如果您需要使用正式的SSL证书，请将证书文件放置在 `nginx/ssl/` 目录下：
  * `fullchain.pem`: SSL证书链
  * `privkey.pem`: SSL私钥
* 要启用HTTPS，请编辑 `nginx/conf.d/app.conf` 文件，取消HTTPS服务器部分的注释，然后重启Nginx容器。

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

## 服务器部署指南

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

2. **克隆GitHub仓库**
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

### 基本Docker部署

如果您选择基本Docker部署，请按照以下步骤操作：

1. **运行部署脚本**
   - 给部署脚本添加执行权限并运行
   ```bash
   chmod +x docker-deploy.sh
   ./docker-deploy.sh
   ```

   部署脚本会自动执行以下操作：
   - 更新系统
   - 安装Docker和Docker Compose（如果尚未安装）
   - 创建必要的目录
   - 生成自签名SSL证书（仅用于测试）
   - 构建和启动Docker容器

2. **访问应用**
   - 通过HTTP访问：`http://您的服务器IP:8080`
   - 通过HTTPS访问：`https://您的服务器IP:8443`
   - 如果您配置了域名，也可以通过域名访问：`http://vocabulary.fueny.cn:8080`或`https://vocabulary.fueny.cn:8443`

### 反向代理部署（推荐）

如果您选择反向代理部署，请按照以下步骤操作：

1. **运行Docker部署脚本**
   - 给部署脚本添加执行权限并运行
   ```bash
   chmod +x docker-deploy.sh
   ./docker-deploy.sh
   ```

2. **设置反向代理**
   - 给反向代理设置脚本添加执行权限并运行
   ```bash
   chmod +x setup-reverse-proxy.sh
   ./setup-reverse-proxy.sh
   ```

   反向代理设置脚本会自动执行以下操作：
   - 安装Nginx
   - 配置反向代理
   - 使用Let's Encrypt获取SSL证书
   - 设置HTTP到HTTPS的自动重定向

3. **访问应用**
   - 通过域名直接访问：`https://vocabulary.fueny.cn`（不需要端口号）
   - HTTP请求会自动重定向到HTTPS

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

# 词汇卡片 Web 应用

这是一个基于 Flask 的 Web 应用程序，用于从 Excel 文件 (`vocabulary.xlsx`) 加载词汇数据并以交互式卡片的形式展示，支持导航和浏览历史记录。

## 功能

*   从 `vocabulary.xlsx` 读取包含 `编号`, `单词`, `音标`, `释义`, `拆分`, `综合法`, `联想法` 七个字段的数据。
*   在网页上以卡片形式展示词汇。
*   提供 "上一张" 和 "下一张" 按钮进行导航。
*   提供按钮切换 "释义", "拆分", "综合法", "联想法" 等详细信息的可见性。
*   记录用户浏览过的卡片历史，避免重复显示相同的卡片。
*   允许用户点击历史记录条目跳转到对应的卡片。
*   **新功能**：允许用户上传自定义的 Excel 文件，支持中英文文件名。
*   **新功能**：保存学习进度，用户可以从上次学习的位置继续。
*   **新功能**：显示当前使用的词汇表文件名，并支持随时切换文件。

## 设置与运行

1.  **环境准备**:
    *   确保您已安装 Python 3 和 pip。

2.  **解压文件**:
    *   将提供的 `vocabulary_app.zip` 文件解压到您选择的目录。

3.  **准备词汇文件**:
    *   准备一个名为 `vocabulary.xlsx` 的 Excel 文件。
    *   确保该文件包含以下七个列标题：`编号`, `单词`, `音标`, `释义`, `拆分`, `综合法`, `联想法`。
    *   将 `vocabulary.xlsx` 文件放置在解压后的项目根目录中（即与 `vocabulary_app` 文件夹同级）。应用程序会优先查找此位置，如果找不到，会尝试在 `vocabulary_app` 文件夹内查找。
    *   如果您没有自己的文件，可以使用项目根目录中提供的 `vocabulary.xlsx` 示例文件。

4.  **安装依赖**:
    *   打开终端或命令提示符。
    *   导航到解压后的 `vocabulary_app` 目录。
    *   运行以下命令安装所需的 Python 包：
        ```bash
        pip install -r requirements.txt
        ```

5.  **运行应用**:
    *   在 `vocabulary_app` 目录下，运行以下命令启动 Flask 开发服务器：
        ```bash
        python3 app.py
        ```

6.  **访问应用**:
    *   打开您的 Web 浏览器。
    *   访问 `http://127.0.0.1:5000` 或 `http://localhost:5000`。
    *   您应该能看到词汇卡片应用界面。

## 文件结构

### 应用代码结构

```
vocabulary_app/
├── app.py                  # 应用入口
├── controllers/            # 控制器
│   ├── vocabulary_controller.py
│   └── auth_controller.py  # 用户认证控制器
├── models/                 # 数据模型
│   ├── vocabulary_model.py
│   └── database.py         # 数据库操作类
├── static/                 # 静态资源
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── api.js          # API客户端
│       ├── archive.js      # 学习历史功能
│       ├── card.js         # 卡片显示功能
│       ├── core.js         # 核心功能和初始化
│       ├── file.js         # 文件管理功能
│       ├── history.js      # 历史记录功能
│       ├── progress.js     # 学习进度功能
│       ├── storage.js      # 本地存储功能
│       └── utils.js        # 通用工具函数
├── templates/              # HTML模板
│   ├── index.html          # 主页面
│   ├── login.html          # 登录页面
│   └── register.html       # 注册页面
├── uploads/                # 上传的文件
├── instance/               # 实例文件夹（数据库）
├── utils/                  # 工具类
│   ├── config.py           # 配置类
│   └── logging_config.py   # 日志配置
├── vocabulary.xlsx         # 默认词汇表
├── requirements.txt        # 依赖列表
├── .gitignore              # Git忽略文件
└── .gitattributes          # Git属性文件
```

### Docker部署文件结构

```
REW/
├── app.py                  # 应用入口
├── controllers/            # 控制器
├── models/                 # 数据模型
├── static/                 # 静态资源
├── templates/              # HTML模板
├── uploads/                # 上传的文件（持久化卷）
├── instance/               # 实例文件夹（持久化卷）
├── utils/                  # 工具类
├── nginx/                  # Nginx配置
│   ├── conf.d/             # Nginx配置文件
│   │   └── app.conf        # 应用的Nginx配置
│   └── ssl/                # SSL证书目录
│       ├── fullchain.pem   # SSL证书链
│       └── privkey.pem     # SSL私钥
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

## 注意

### 开发环境
*   当前的 Flask 开发服务器仅用于开发，不建议在生产环境直接使用。
*   如果 `vocabulary.xlsx` 文件未找到或格式不正确，应用会显示错误信息或加载默认的错误提示卡片。
*   上传的文件会保存在 `uploads` 目录中，文件名会自动添加唯一标识符以避免冲突。
*   学习进度保存在浏览器的 localStorage 中，与特定的词汇表文件关联。
*   如果更换浏览器或清除浏览器数据，保存的学习进度将会丢失。

### 生产部署
*   推荐使用Docker进行部署，这样可以避免依赖问题并简化部署过程。
*   Docker部署会自动设置Nginx、SSL证书和应用服务，无需手动配置。
*   数据持久化通过Docker卷实现，确保容器重启或重建后数据不会丢失。
*   如果您需要使用正式的SSL证书，请将证书文件放置在 `nginx/ssl/` 目录下。
*   默认情况下，Docker部署使用自签名SSL证书，仅用于测试。在生产环境中，建议使用正式的SSL证书。
*   Docker部署会自动生成安全密钥，无需手动配置。
*   `uploads` 目录会在需要时自动创建，无需手动创建。

## 服务器部署

### Docker部署指南（推荐）

本项目现在支持使用Docker进行部署，这是推荐的部署方式，可以避免依赖问题并简化部署过程。

1. **准备服务器**
   - 启动一个Ubuntu服务器实例
   - 确保安全组允许HTTP(80)和HTTPS(443)端口访问
   - 连接到实例（使用SSH）

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

3. **运行Docker部署脚本**
   - 给部署脚本添加执行权限并运行
   ```bash
   chmod +x docker-deploy.sh
   ./docker-deploy.sh
   ```

   Docker部署脚本会自动执行以下操作：
   - 更新系统
   - 安装Docker和Docker Compose
   - 创建SSL证书目录
   - 生成自签名SSL证书（用于测试）
   - 设置环境变量
   - 构建和启动Docker容器

   **注意**：Docker配置已经预先设置为使用以下配置：
   - 应用端口：`5050`
   - 域名：`vocabulary.fueny.cn`

   如果您的实际情况不同，请在部署前修改相应文件。

4. **使用正式SSL证书**
   - 如果您有正式的SSL证书，请将证书文件放置在 `nginx/ssl/` 目录下：
     - 将完整证书链放在 `nginx/ssl/fullchain.pem`
     - 将私钥放在 `nginx/ssl/privkey.pem`
   - 然后重启容器：
   ```bash
   sudo docker-compose restart nginx
   ```

5. **管理Docker容器**
   - 查看容器状态：`sudo docker-compose ps`
   - 启动容器：`sudo docker-compose up -d`
   - 停止容器：`sudo docker-compose down`
   - 重启容器：`sudo docker-compose restart`
   - 查看日志：`sudo docker-compose logs -f`

6. **数据持久化**
   - 应用数据存储在以下目录中，这些目录已经通过卷映射到容器外部：
     - 上传的文件：`./uploads`
     - 数据库文件：`./instance`
   - 这些目录中的数据在容器重启或重建后仍然保留

### 手动Docker部署

如果您想手动控制Docker部署过程，可以按照以下步骤操作：

1. **安装Docker和Docker Compose**
   ```bash
   sudo apt update
   sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
   sudo apt install -y docker-compose
   ```

2. **准备SSL证书**
   - 创建证书目录：
   ```bash
   mkdir -p nginx/ssl
   ```

   - 生成自签名证书（仅用于测试）：
   ```bash
   sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout nginx/ssl/privkey.pem \
     -out nginx/ssl/fullchain.pem \
     -subj "/CN=vocabulary.fueny.cn" \
     -addext "subjectAltName=DNS:vocabulary.fueny.cn"
   ```

3. **创建环境变量文件**
   ```bash
   # 生成随机密钥
   SECRET_KEY=$(openssl rand -hex 24)
   # 创建.env文件
   echo "SECRET_KEY=$SECRET_KEY" > .env
   ```

4. **构建和启动容器**
   ```bash
   sudo docker-compose up -d --build
   ```

5. **验证部署**
   ```bash
   sudo docker-compose ps
   ```

### 传统部署指南（不推荐）

如果您无法使用Docker，也可以使用传统方式部署：

1. **准备EC2实例**
   - 启动一个Ubuntu服务器实例
   - 确保安全组允许HTTP(80)和HTTPS(443)端口访问
   - 连接到实例（使用SSH）

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

3. **运行部署脚本**
   - 给部署脚本添加执行权限并运行
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

   部署脚本会自动执行以下操作：
   - 更新系统
   - 安装必要的依赖
   - 设置Python虚拟环境
   - 安装Python依赖
   - 配置Nginx
   - 设置systemd服务
   - 创建必要的目录并设置权限

4. **配置SSL证书（可选）**
   - 使用Certbot为您的域名添加SSL证书
   ```bash
   sudo certbot --nginx -d vocabulary.fueny.cn
   ```

5. **管理应用**
   - 启动应用：`sudo systemctl start REW`
   - 停止应用：`sudo systemctl stop REW`
   - 重启应用：`sudo systemctl restart REW`
   - 查看状态：`sudo systemctl status REW`
   - 查看日志：`sudo journalctl -u REW`

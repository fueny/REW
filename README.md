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
│   └── config.py           # 配置类
├── vocabulary.xlsx         # 默认词汇表
├── requirements.txt        # 依赖列表
├── .gitignore              # Git忽略文件
└── .gitattributes          # Git属性文件
```

## 注意

*   当前的 Flask 服务器是用于开发的，不建议在生产环境直接使用。
*   如果 `vocabulary.xlsx` 文件未找到或格式不正确，应用会显示错误信息或加载默认的错误提示卡片。
*   上传的文件会保存在 `uploads` 目录中，文件名会自动添加唯一标识符以避免冲突。
*   学习进度保存在浏览器的 localStorage 中，与特定的词汇表文件关联。
*   如果更换浏览器或清除浏览器数据，保存的学习进度将会丢失。

## 服务器部署

### AWS EC2 Ubuntu部署指南

本项目包含了部署到AWS EC2 Ubuntu服务器的必要文件和脚本。按照以下步骤进行部署：

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

   **注意**：部署脚本和配置文件已经预先配置为使用以下设置：
   - 项目路径：`/home/ubuntu/REW`
   - 应用端口：`5050`
   - 域名：`vocabulary.fueny.cn`

   如果您的实际情况不同，请在部署前修改相应文件。

4. **配置SSL证书（可选）**
   - 使用Certbot为您的域名添加SSL证书
   ```bash
   sudo certbot --nginx -d vocabulary.fueny.cn
   ```
   - Certbot会自动修改Nginx配置并重启Nginx

5. **管理应用**
   - 启动应用：`sudo systemctl start REW`
   - 停止应用：`sudo systemctl stop REW`
   - 重启应用：`sudo systemctl restart REW`
   - 查看状态：`sudo systemctl status REW`
   - 查看日志：`sudo journalctl -u REW`

### 手动部署步骤

如果您不想使用自动部署脚本，也可以按照以下步骤手动部署：

1. 在服务器上安装Python和pip
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv nginx
   ```

2. 克隆GitHub仓库并进入项目目录
   ```bash
   git clone https://github.com/your-username/REW.git
   cd REW
   ```

3. 创建并激活虚拟环境
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

5. 使用生产级Web服务器（如Gunicorn）运行应用
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 127.0.0.1:5050 "app:create_app()"
   ```

6. 配置Nginx作为反向代理
   ```bash
   # 创建Nginx配置文件
   sudo nano /etc/nginx/sites-available/REW

   # 文件内容
   server {
       listen 80;
       server_name vocabulary.fueny.cn;

       location / {
           proxy_pass http://127.0.0.1:5050;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       # 静态文件处理
       location /static {
           alias /home/ubuntu/REW/static;
           expires 30d;
       }
   }

   # 启用配置
   sudo ln -s /etc/nginx/sites-available/REW /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

7. 设置自动启动
   ```bash
   # 创建systemd服务文件
   sudo nano /etc/systemd/system/REW.service

   # 文件内容
   [Unit]
   Description=Vocabulary App
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/REW
   ExecStart=/home/ubuntu/REW/venv/bin/gunicorn -w 4 -b 127.0.0.1:5050 "app:create_app()"
   Restart=always
   Environment="FLASK_DEBUG=False"

   [Install]
   WantedBy=multi-user.target

   # 启用服务
   sudo systemctl enable REW
   sudo systemctl start REW
   ```

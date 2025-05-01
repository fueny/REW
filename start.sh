#!/bin/bash

# 激活虚拟环境
source venv/bin/activate

# 启动Gunicorn服务器
gunicorn -w 4 -b 127.0.0.1:5050 "app:create_app()"

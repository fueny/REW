#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta
from flask import Flask, session, request
from utils.config import Config
from models.database import Database
from controllers.vocabulary_controller import VocabularyController
from controllers.auth_controller import AuthController, login_required

# 创建全局数据库实例
db = Database()

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__, instance_relative_config=True)

    # 初始化应用配置
    Config.init_app(app)

    # 设置会话密钥
    app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

    # 初始化数据库
    db.init_app(app)

    # 注册关闭时的清理函数
    @app.teardown_appcontext
    def close_db(exception):
        db.close_connection()

    # 初始化控制器
    auth_controller = AuthController(app, db)

    # 将用户ID添加到模板全局变量
    @app.context_processor
    def inject_user():
        return {
            'user_id': session.get('user_id', None),
            'username': session.get('username', None)
        }

    # 添加会话刷新中间件
    @app.before_request
    def refresh_session():
        # 只处理已登录用户的会话
        if 'user_id' in session:
            # 检查会话是否需要刷新（如果剩余时间不足总时间的一半）
            # 注意：Flask不直接提供会话过期时间的访问，所以我们使用一个辅助字段
            if 'last_refresh' not in session:
                session['last_refresh'] = datetime.now().timestamp()
            else:
                # 计算上次刷新到现在的时间
                last_refresh = datetime.fromtimestamp(session['last_refresh'])
                time_since_refresh = datetime.now() - last_refresh

                # 如果超过3.5天（7天的一半），刷新会话
                if time_since_refresh > timedelta(days=3.5):
                    # 更新刷新时间
                    session['last_refresh'] = datetime.now().timestamp()
                    # 通过修改会话来刷新它
                    session.modified = True

    # 初始化词汇控制器（在认证控制器之后）
    vocabulary_controller = VocabularyController(app, db)

    return app

if __name__ == "__main__":
    app = create_app()
    # 获取环境变量或使用默认值
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))

    # 启动应用
    app.run(debug=debug_mode, host=host, port=port)

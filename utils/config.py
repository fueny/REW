#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


class Config:
    """应用配置类，管理应用的配置参数"""

    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 基本配置
        app.config['UPLOAD_FOLDER'] = os.path.normpath('uploads')
        app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

        # 数据库配置
        app.config['DATABASE_PATH'] = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'vocabulary.db'))

        # 确保上传文件夹和数据库目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(os.path.dirname(app.config['DATABASE_PATH']), exist_ok=True)

        # 打印路径信息，便于调试
        print(f"上传文件夹路径: {os.path.abspath(app.config['UPLOAD_FOLDER'])}")
        print(f"数据库路径: {app.config['DATABASE_PATH']}")

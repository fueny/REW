#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash

class AuthController:
    """用户认证控制器"""

    def __init__(self, app, db):
        self.app = app
        self.db = db
        self.setup_routes()

    def setup_routes(self):
        """设置路由"""
        # 登录页面
        self.app.add_url_rule('/login', 'login_page', self.login_page, methods=['GET'])
        # 登录处理
        self.app.add_url_rule('/login', 'login', self.login, methods=['POST'])
        # 注册页面
        self.app.add_url_rule('/register', 'register_page', self.register_page, methods=['GET'])
        # 注册处理
        self.app.add_url_rule('/register', 'register', self.register, methods=['POST'])
        # 登出
        self.app.add_url_rule('/logout', 'logout', self.logout)

    def login_page(self):
        """登录页面"""
        # 如果已经登录，重定向到首页
        if 'user_id' in session:
            return redirect(url_for('index'))
        return render_template('login.html')

    def login(self):
        """处理登录请求"""
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return redirect(url_for('login_page'))

        # 获取用户信息
        user = self.db.get_user_by_username(username)
        if not user:
            flash('用户名或密码错误', 'error')
            return redirect(url_for('login_page'))

        # 验证密码
        hashed_password = self._hash_password(password)
        if user['password'] != hashed_password:
            flash('用户名或密码错误', 'error')
            return redirect(url_for('login_page'))

        # 更新最后登录时间
        self.db.update_last_login(user['id'])

        # 设置会话
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['last_refresh'] = datetime.now().timestamp()  # 添加刷新时间戳
        session.permanent = True  # 使会话持久化
        self.app.permanent_session_lifetime = timedelta(days=7)  # 设置会话有效期为7天

        flash('登录成功', 'success')
        return redirect(url_for('index'))

    def register_page(self):
        """注册页面"""
        # 如果已经登录，重定向到首页
        if 'user_id' in session:
            return redirect(url_for('index'))
        return render_template('register.html')

    def register(self):
        """处理注册请求"""
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email', None)

        # 验证输入
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return redirect(url_for('register_page'))

        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return redirect(url_for('register_page'))

        # 检查用户名是否已存在
        existing_user = self.db.get_user_by_username(username)
        if existing_user:
            flash('用户名已存在', 'error')
            return redirect(url_for('register_page'))

        # 创建用户
        hashed_password = self._hash_password(password)
        user_id = self.db.create_user(username, hashed_password, email)

        if not user_id:
            flash('注册失败，请稍后重试', 'error')
            return redirect(url_for('register_page'))

        # 设置会话
        session['user_id'] = user_id
        session['username'] = username
        session['last_refresh'] = datetime.now().timestamp()  # 添加刷新时间戳
        session.permanent = True  # 使会话持久化
        self.app.permanent_session_lifetime = timedelta(days=7)  # 设置会话有效期为7天

        flash('注册成功', 'success')
        return redirect(url_for('index'))

    def logout(self):
        """处理登出请求"""
        session.pop('user_id', None)
        session.pop('username', None)
        flash('已成功登出', 'success')
        return redirect(url_for('login_page'))

    def _hash_password(self, password):
        """密码哈希"""
        # 简单的密码哈希，实际应用中应使用更安全的方法如bcrypt
        return hashlib.sha256(password.encode()).hexdigest()

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
from datetime import datetime

class Database:
    """数据库操作类，负责SQLite数据库的初始化和操作"""

    def __init__(self, app=None):
        self.app = app
        self.db_path = 'vocabulary.db'

        if app:
            self.init_app(app)

    def init_app(self, app):
        """初始化应用配置"""
        self.app = app
        self.db_path = app.config.get('DATABASE_PATH', 'vocabulary.db')

        # 确保数据库目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # 检查数据库是否需要迁移
        self.check_and_migrate_db()

        # 初始化数据库
        with self.get_connection() as conn:
            self.init_db(conn)

    def get_connection(self):
        """获取数据库连接 - 每次调用返回新的连接，确保线程安全"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
        return conn

    def close_connection(self):
        """关闭数据库连接 - 现在是空操作，因为我们不再保存连接"""
        pass

    def init_db(self, conn=None):
        """初始化数据库表结构"""
        if conn is None:
            conn = self.get_connection()
        cursor = conn.cursor()

        # 创建用户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')

        # 创建文件表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            display_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, path)
        )
        ''')

        # 创建历史记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_id INTEGER NOT NULL,
            card_index INTEGER NOT NULL,
            date TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
        )
        ''')

        # 创建存档表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS archives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_id INTEGER NOT NULL,
            card_index INTEGER NOT NULL,
            details_visible INTEGER DEFAULT 0,
            name TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
        )
        ''')

        # 创建用户设置表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            key TEXT NOT NULL,
            value TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, key)
        )
        ''')

        conn.commit()

    def get_file_by_path(self, file_path, user_id=None):
        """根据文件路径获取文件信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if user_id:
                cursor.execute('SELECT * FROM files WHERE path = ? AND user_id = ?', (file_path, user_id))
            else:
                cursor.execute('SELECT * FROM files WHERE path = ? AND user_id IS NULL', (file_path,))

            file = cursor.fetchone()

            if file:
                # 更新最后访问时间
                cursor.execute('UPDATE files SET last_accessed = ? WHERE id = ?',
                              (datetime.now().isoformat(), file['id']))
                conn.commit()

                return dict(file)

            return None

    def add_file(self, name, path, display_name, user_id=None):
        """添加文件记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            try:
                if user_id:
                    cursor.execute(
                        'INSERT INTO files (name, path, display_name, user_id) VALUES (?, ?, ?, ?)',
                        (name, path, display_name, user_id)
                    )
                else:
                    cursor.execute(
                        'INSERT INTO files (name, path, display_name) VALUES (?, ?, ?)',
                        (name, path, display_name)
                    )
                conn.commit()

                # 获取新添加的文件ID
                if user_id:
                    cursor.execute('SELECT id FROM files WHERE path = ? AND user_id = ?', (path, user_id))
                else:
                    cursor.execute('SELECT id FROM files WHERE path = ? AND user_id IS NULL', (path,))

                file_id = cursor.fetchone()['id']

                return file_id
            except sqlite3.IntegrityError:
                # 如果文件已存在，更新信息并返回ID
                if user_id:
                    cursor.execute(
                        'UPDATE files SET name = ?, display_name = ?, last_accessed = ? WHERE path = ? AND user_id = ?',
                        (name, display_name, datetime.now().isoformat(), path, user_id)
                    )
                else:
                    cursor.execute(
                        'UPDATE files SET name = ?, display_name = ?, last_accessed = ? WHERE path = ? AND user_id IS NULL',
                        (name, display_name, datetime.now().isoformat(), path)
                    )
                conn.commit()

                if user_id:
                    cursor.execute('SELECT id FROM files WHERE path = ? AND user_id = ?', (path, user_id))
                else:
                    cursor.execute('SELECT id FROM files WHERE path = ? AND user_id IS NULL', (path,))

                file_id = cursor.fetchone()['id']

                return file_id

    def get_all_files(self, user_id=None):
        """获取所有文件记录，确保文件不重复"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 先检查是否有重复的默认文件
            if user_id:
                cursor.execute('SELECT * FROM files WHERE (name = "vocabulary.xlsx" OR path = "vocabulary.xlsx") AND user_id = ? ORDER BY last_accessed DESC', (user_id,))
            else:
                cursor.execute('SELECT * FROM files WHERE (name = "vocabulary.xlsx" OR path = "vocabulary.xlsx") AND user_id IS NULL ORDER BY last_accessed DESC')

            default_files = cursor.fetchall()

            # 如果有多个默认文件，删除多余的
            if len(default_files) > 1:
                # 保留最近访问的一个
                keep_id = default_files[0]['id']
                print(f"保留默认文件: ID={keep_id}")

                # 删除其他的
                for file in default_files[1:]:
                    print(f"删除重复的默认文件: ID={file['id']}")
                    cursor.execute('DELETE FROM files WHERE id = ?', (file['id'],))

                conn.commit()

            # 检查其他文件是否有重复
            if user_id:
                cursor.execute('SELECT path, COUNT(*) as count, MAX(last_accessed) as latest FROM files WHERE path != "vocabulary.xlsx" AND user_id = ? GROUP BY path HAVING count > 1', (user_id,))
            else:
                cursor.execute('SELECT path, COUNT(*) as count, MAX(last_accessed) as latest FROM files WHERE path != "vocabulary.xlsx" AND user_id IS NULL GROUP BY path HAVING count > 1')

            duplicate_paths = cursor.fetchall()

            # 处理重复文件
            for dup in duplicate_paths:
                path = dup['path']
                print(f"发现重复文件路径: {path}, 数量: {dup['count']}")

                # 获取该路径的所有文件记录
                if user_id:
                    cursor.execute('SELECT * FROM files WHERE path = ? AND user_id = ? ORDER BY last_accessed DESC', (path, user_id))
                else:
                    cursor.execute('SELECT * FROM files WHERE path = ? AND user_id IS NULL ORDER BY last_accessed DESC')

                dup_files = cursor.fetchall()

                # 保留最近访问的一个
                keep_id = dup_files[0]['id']
                print(f"保留文件: ID={keep_id}, 路径={path}")

                # 删除其他的
                for file in dup_files[1:]:
                    print(f"删除重复文件: ID={file['id']}, 路径={path}")
                    cursor.execute('DELETE FROM files WHERE id = ?', (file['id'],))

            # 如果有删除操作，提交事务
            if duplicate_paths:
                conn.commit()

            # 获取所有文件
            if user_id:
                cursor.execute('SELECT * FROM files WHERE user_id = ? ORDER BY last_accessed DESC', (user_id,))
            else:
                cursor.execute('SELECT * FROM files WHERE user_id IS NULL ORDER BY last_accessed DESC')

            files = cursor.fetchall()

            # 确保默认文件没有删除按钮
            result = []
            for file in files:
                file_dict = dict(file)
                # 检查是否是默认文件（通过名称或路径）
                if file_dict['name'] == 'vocabulary.xlsx' or file_dict['path'] == 'vocabulary.xlsx':
                    file_dict['is_default'] = True
                else:
                    file_dict['is_default'] = False
                result.append(file_dict)

            return result

    def delete_file(self, file_id, user_id=None):
        """删除文件记录及相关数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 获取文件信息
            if user_id:
                cursor.execute('SELECT * FROM files WHERE id = ? AND user_id = ?', (file_id, user_id))
            else:
                cursor.execute('SELECT * FROM files WHERE id = ? AND user_id IS NULL', (file_id,))

            file = cursor.fetchone()

            if not file:
                return False, "文件不存在"

            # 检查是否是默认文件
            if file['path'] == 'vocabulary.xlsx':
                return False, "不能删除默认文件"

            try:
                # 开始事务
                cursor.execute('BEGIN TRANSACTION')

                # 删除相关的历史记录
                if user_id:
                    cursor.execute('DELETE FROM history WHERE file_id = ? AND user_id = ?', (file_id, user_id))
                else:
                    cursor.execute('DELETE FROM history WHERE file_id = ? AND user_id IS NULL', (file_id,))

                # 删除相关的存档
                if user_id:
                    cursor.execute('DELETE FROM archives WHERE file_id = ? AND user_id = ?', (file_id, user_id))
                else:
                    cursor.execute('DELETE FROM archives WHERE file_id = ? AND user_id IS NULL', (file_id,))

                # 删除文件记录
                if user_id:
                    cursor.execute('DELETE FROM files WHERE id = ? AND user_id = ?', (file_id, user_id))
                else:
                    cursor.execute('DELETE FROM files WHERE id = ? AND user_id IS NULL', (file_id,))

                # 提交事务
                conn.commit()

                return True, "文件删除成功"
            except Exception as e:
                # 回滚事务
                conn.rollback()
                return False, f"删除文件失败: {str(e)}"

    def add_history(self, file_id, card_index, user_id=None, force_new_date=False):
        """添加历史记录

        按照以下规则工作：
        1. 以北京时间晚上12点为分界线，每天有独立的历史记录
        2. 每个单词只能出现在一天的历史记录中，不会重复出现在其他天
        3. 历史记录按照单词的序号排序（而不是浏览时间）
        4. 一旦单词进入某天的历史记录，即使在其他天再次浏览，也不会改变其所属的历史日期
        5. 新的一天应该从上一天最后浏览的单词序号之后开始记录

        参数:
            file_id: 文件ID
            card_index: 卡片索引
            user_id: 用户ID
            force_new_date: 是否强制使用新日期（用于测试）
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 获取当前北京时间（格式：YYYY-MM-DD）
            # 注意：这里使用UTC+8时区，即北京时间
            beijing_time = datetime.now() + timedelta(hours=8)

            # 如果强制使用新日期，则使用当前日期+1天
            if force_new_date:
                beijing_time = beijing_time + timedelta(days=1)

            today = beijing_time.strftime('%Y-%m-%d')

            # 1. 首先检查这个卡片是否已经在任何日期的历史记录中
            if user_id:
                cursor.execute(
                    'SELECT id, date FROM history WHERE file_id = ? AND card_index = ? AND user_id = ? LIMIT 1',
                    (file_id, card_index, user_id)
                )
            else:
                cursor.execute(
                    'SELECT id, date FROM history WHERE file_id = ? AND card_index = ? AND user_id IS NULL LIMIT 1',
                    (file_id, card_index)
                )

            existing_in_any_date = cursor.fetchone()

            if existing_in_any_date:
                # 如果这个卡片已经在某个日期的历史记录中，只更新时间戳
                cursor.execute(
                    'UPDATE history SET timestamp = ? WHERE id = ?',
                    (datetime.now().isoformat(), existing_in_any_date['id'])
                )
                conn.commit()
                return True

            # 2. 如果卡片不在任何历史记录中，检查今天是否有历史记录
            if user_id:
                cursor.execute(
                    'SELECT EXISTS(SELECT 1 FROM history WHERE file_id = ? AND date = ? AND user_id = ? LIMIT 1) as has_records',
                    (file_id, today, user_id)
                )
            else:
                cursor.execute(
                    'SELECT EXISTS(SELECT 1 FROM history WHERE file_id = ? AND date = ? AND user_id IS NULL LIMIT 1) as has_records',
                    (file_id, today)
                )

            has_today_records = cursor.fetchone()['has_records']

            # 3. 如果今天没有历史记录，需要找到上一天的最大卡片索引
            if not has_today_records:
                # 获取所有历史记录日期，按日期降序排序
                if user_id:
                    cursor.execute(
                        'SELECT DISTINCT date FROM history WHERE file_id = ? AND user_id = ? ORDER BY date DESC',
                        (file_id, user_id)
                    )
                else:
                    cursor.execute(
                        'SELECT DISTINCT date FROM history WHERE file_id = ? AND user_id IS NULL ORDER BY date DESC',
                        (file_id,)
                    )

                dates = [row['date'] for row in cursor.fetchall()]

                # 如果有历史日期，找到最近一天的最大卡片索引
                max_card_index = -1
                if dates:
                    last_date = dates[0]

                    if user_id:
                        cursor.execute(
                            'SELECT MAX(card_index) as max_index FROM history WHERE file_id = ? AND date = ? AND user_id = ?',
                            (file_id, last_date, user_id)
                        )
                    else:
                        cursor.execute(
                            'SELECT MAX(card_index) as max_index FROM history WHERE file_id = ? AND date = ? AND user_id IS NULL',
                            (file_id, last_date)
                        )

                    result = cursor.fetchone()
                    if result and result['max_index'] is not None:
                        max_card_index = result['max_index']

                # 如果当前卡片索引小于等于上一天的最大索引，不添加到历史记录
                if card_index <= max_card_index:
                    conn.commit()
                    return True

            # 4. 添加新记录
            if user_id:
                cursor.execute(
                    'INSERT INTO history (file_id, card_index, date, user_id, timestamp) VALUES (?, ?, ?, ?, ?)',
                    (file_id, card_index, today, user_id, datetime.now().isoformat())
                )
            else:
                cursor.execute(
                    'INSERT INTO history (file_id, card_index, date, timestamp) VALUES (?, ?, ?, ?)',
                    (file_id, card_index, today, datetime.now().isoformat())
                )

            conn.commit()
            return True

    def get_history_by_date(self, file_id, date=None, user_id=None):
        """获取指定日期的历史记录，按照卡片索引排序"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if date is None:
                # 如果未指定日期，获取所有日期
                if user_id:
                    cursor.execute(
                        'SELECT DISTINCT date FROM history WHERE file_id = ? AND user_id = ? ORDER BY date DESC',
                        (file_id, user_id)
                    )
                else:
                    cursor.execute(
                        'SELECT DISTINCT date FROM history WHERE file_id = ? AND user_id IS NULL ORDER BY date DESC',
                        (file_id,)
                    )

                dates = [row['date'] for row in cursor.fetchall()]

                result = {}
                for d in dates:
                    # 获取该日期的所有卡片索引，按照卡片索引排序（从小到大）
                    if user_id:
                        cursor.execute(
                            '''
                            SELECT DISTINCT card_index
                            FROM history
                            WHERE file_id = ? AND date = ? AND user_id = ?
                            ORDER BY card_index ASC
                            ''',
                            (file_id, d, user_id)
                        )
                    else:
                        cursor.execute(
                            '''
                            SELECT DISTINCT card_index
                            FROM history
                            WHERE file_id = ? AND date = ? AND user_id IS NULL
                            ORDER BY card_index ASC
                            ''',
                            (file_id, d)
                        )

                    result[d] = [row['card_index'] for row in cursor.fetchall()]

                return result
            else:
                # 获取指定日期的历史记录，按照卡片索引排序（从小到大）
                if user_id:
                    cursor.execute(
                        '''
                        SELECT DISTINCT card_index
                        FROM history
                        WHERE file_id = ? AND date = ? AND user_id = ?
                        ORDER BY card_index ASC
                        ''',
                        (file_id, date, user_id)
                    )
                else:
                    cursor.execute(
                        '''
                        SELECT DISTINCT card_index
                        FROM history
                        WHERE file_id = ? AND date = ? AND user_id IS NULL
                        ORDER BY card_index ASC
                        ''',
                        (file_id, date)
                    )

                return [row['card_index'] for row in cursor.fetchall()]

    def clear_history(self, file_id=None, user_id=None):
        """清除历史记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if file_id and user_id:
                cursor.execute('DELETE FROM history WHERE file_id = ? AND user_id = ?', (file_id, user_id))
            elif file_id:
                cursor.execute('DELETE FROM history WHERE file_id = ?', (file_id,))
            elif user_id:
                cursor.execute('DELETE FROM history WHERE user_id = ?', (user_id,))
            else:
                cursor.execute('DELETE FROM history')

            conn.commit()
            return True

    def create_archive(self, file_id, card_index, details_visible, name=None, user_id=None):
        """创建存档"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if name is None:
                # 如果未提供名称，使用时间戳作为默认名称
                name = f"存档 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            if user_id:
                cursor.execute(
                    'INSERT INTO archives (file_id, card_index, details_visible, name, user_id) VALUES (?, ?, ?, ?, ?)',
                    (file_id, card_index, 1 if details_visible else 0, name, user_id)
                )
            else:
                cursor.execute(
                    'INSERT INTO archives (file_id, card_index, details_visible, name) VALUES (?, ?, ?, ?)',
                    (file_id, card_index, 1 if details_visible else 0, name)
                )

            conn.commit()

            # 返回新创建的存档ID
            return cursor.lastrowid

    def get_archives(self, file_id=None, user_id=None):
        """获取存档列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if file_id and user_id:
                cursor.execute('''
                    SELECT a.*, f.name as file_name, f.path as file_path, f.display_name
                    FROM archives a
                    JOIN files f ON a.file_id = f.id
                    WHERE a.file_id = ? AND a.user_id = ?
                    ORDER BY a.timestamp DESC
                ''', (file_id, user_id))
            elif file_id:
                cursor.execute('''
                    SELECT a.*, f.name as file_name, f.path as file_path, f.display_name
                    FROM archives a
                    JOIN files f ON a.file_id = f.id
                    WHERE a.file_id = ? AND a.user_id IS NULL
                    ORDER BY a.timestamp DESC
                ''', (file_id,))
            elif user_id:
                cursor.execute('''
                    SELECT a.*, f.name as file_name, f.path as file_path, f.display_name
                    FROM archives a
                    JOIN files f ON a.file_id = f.id
                    WHERE a.user_id = ?
                    ORDER BY a.timestamp DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT a.*, f.name as file_name, f.path as file_path, f.display_name
                    FROM archives a
                    JOIN files f ON a.file_id = f.id
                    WHERE a.user_id IS NULL
                    ORDER BY a.timestamp DESC
                ''')

            archives = cursor.fetchall()
            return [dict(archive) for archive in archives]

    def get_archive(self, archive_id, user_id=None):
        """获取指定存档"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if user_id:
                cursor.execute('''
                    SELECT a.*, f.name as file_name, f.path as file_path, f.display_name
                    FROM archives a
                    JOIN files f ON a.file_id = f.id
                    WHERE a.id = ? AND a.user_id = ?
                ''', (archive_id, user_id))
            else:
                cursor.execute('''
                    SELECT a.*, f.name as file_name, f.path as file_path, f.display_name
                    FROM archives a
                    JOIN files f ON a.file_id = f.id
                    WHERE a.id = ? AND a.user_id IS NULL
                ''', (archive_id,))

            archive = cursor.fetchone()
            return dict(archive) if archive else None

    def delete_archive(self, archive_id, user_id=None):
        """删除存档"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if user_id:
                cursor.execute('DELETE FROM archives WHERE id = ? AND user_id = ?', (archive_id, user_id))
            else:
                cursor.execute('DELETE FROM archives WHERE id = ? AND user_id IS NULL', (archive_id,))

            conn.commit()

            return cursor.rowcount > 0

    def set_setting(self, key, value, user_id=None):
        """设置配置项"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            try:
                if user_id:
                    cursor.execute(
                        'INSERT INTO settings (key, value, user_id) VALUES (?, ?, ?)',
                        (key, value, user_id)
                    )
                else:
                    cursor.execute(
                        'INSERT INTO settings (key, value) VALUES (?, ?)',
                        (key, value)
                    )
            except sqlite3.IntegrityError:
                if user_id:
                    cursor.execute(
                        'UPDATE settings SET value = ?, timestamp = ? WHERE key = ? AND user_id = ?',
                        (value, datetime.now().isoformat(), key, user_id)
                    )
                else:
                    cursor.execute(
                        'UPDATE settings SET value = ?, timestamp = ? WHERE key = ? AND user_id IS NULL',
                        (value, datetime.now().isoformat(), key)
                    )

            conn.commit()
            return True

    def get_setting(self, key, default=None, user_id=None):
        """获取配置项"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if user_id:
                cursor.execute('SELECT value FROM settings WHERE key = ? AND user_id = ?', (key, user_id))
            else:
                cursor.execute('SELECT value FROM settings WHERE key = ? AND user_id IS NULL', (key,))

            setting = cursor.fetchone()

            return setting['value'] if setting else default

    def get_last_file(self, user_id=None):
        """获取最后使用的文件"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if user_id:
                cursor.execute('SELECT * FROM files WHERE user_id = ? ORDER BY last_accessed DESC LIMIT 1', (user_id,))
            else:
                cursor.execute('SELECT * FROM files ORDER BY last_accessed DESC LIMIT 1')

            file = cursor.fetchone()

            return dict(file) if file else None

    # 用户相关方法
    def create_user(self, username, password, email=None):
        """创建新用户"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                    (username, password, email)
                )
                conn.commit()

                # 获取新用户ID
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                user_id = cursor.fetchone()['id']

                return user_id
            except sqlite3.IntegrityError:
                # 用户名已存在
                return None

    def get_user_by_username(self, username):
        """根据用户名获取用户信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

            return dict(user) if user else None

    def get_user_by_id(self, user_id):
        """根据ID获取用户信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()

            return dict(user) if user else None

    def update_last_login(self, user_id):
        """更新用户最后登录时间"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                'UPDATE users SET last_login = ? WHERE id = ?',
                (datetime.now().isoformat(), user_id)
            )
            conn.commit()

            return True

    def check_and_migrate_db(self):
        """检查数据库是否需要迁移，并执行必要的迁移"""
        # 检查数据库文件是否存在
        if not os.path.exists(self.db_path):
            # 如果不存在，不需要迁移
            return

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 检查表结构
            try:
                # 检查 files 表是否有 user_id 列
                cursor.execute("PRAGMA table_info(files)")
                columns = cursor.fetchall()
                column_names = [column['name'] for column in columns]

                # 如果没有 user_id 列，需要迁移
                if 'user_id' not in column_names:
                    print("检测到数据库需要迁移：添加 user_id 列")
                    self._migrate_add_user_id_columns(conn)

                # 检查 history 表是否有 user_id 列
                cursor.execute("PRAGMA table_info(history)")
                columns = cursor.fetchall()
                column_names = [column['name'] for column in columns]

                # 如果没有 user_id 列，需要迁移
                if 'user_id' not in column_names:
                    print("检测到数据库需要迁移：添加 user_id 列到 history 表")
                    self._migrate_add_user_id_to_history(conn)

                # 检查 archives 表是否有 user_id 列
                cursor.execute("PRAGMA table_info(archives)")
                columns = cursor.fetchall()
                column_names = [column['name'] for column in columns]

                # 如果没有 user_id 列，需要迁移
                if 'user_id' not in column_names:
                    print("检测到数据库需要迁移：添加 user_id 列到 archives 表")
                    self._migrate_add_user_id_to_archives(conn)

                # 检查 settings 表是否有 user_id 列
                cursor.execute("PRAGMA table_info(settings)")
                columns = cursor.fetchall()
                column_names = [column['name'] for column in columns]

                # 如果没有 user_id 列，需要迁移
                if 'user_id' not in column_names:
                    print("检测到数据库需要迁移：添加 user_id 列到 settings 表")
                    self._migrate_add_user_id_to_settings(conn)

            except sqlite3.OperationalError as e:
                # 如果表不存在，不需要迁移
                print(f"迁移检查时出现错误：{str(e)}")
                pass

    def _migrate_add_user_id_columns(self, conn):
        """迁移：添加 user_id 列到 files 表"""
        cursor = conn.cursor()

        try:
            # 开始事务
            cursor.execute('BEGIN TRANSACTION')

            # 创建新表
            cursor.execute('''
            CREATE TABLE files_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                display_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(user_id, path)
            )
            ''')

            # 复制数据
            cursor.execute('''
            INSERT INTO files_new (id, name, path, display_name, created_at, last_accessed)
            SELECT id, name, path, display_name, created_at, last_accessed FROM files
            ''')

            # 删除旧表
            cursor.execute('DROP TABLE files')

            # 重命名新表
            cursor.execute('ALTER TABLE files_new RENAME TO files')

            # 提交事务
            conn.commit()

            print("成功迁移 files 表")

        except Exception as e:
            # 回滚事务
            conn.rollback()
            print(f"迁移 files 表失败：{str(e)}")

    def _migrate_add_user_id_to_history(self, conn):
        """迁移：添加 user_id 列到 history 表"""
        cursor = conn.cursor()

        try:
            # 开始事务
            cursor.execute('BEGIN TRANSACTION')

            # 创建新表
            cursor.execute('''
            CREATE TABLE history_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                file_id INTEGER NOT NULL,
                card_index INTEGER NOT NULL,
                date TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
            )
            ''')

            # 复制数据
            cursor.execute('''
            INSERT INTO history_new (id, file_id, card_index, date, timestamp)
            SELECT id, file_id, card_index, date, timestamp FROM history
            ''')

            # 删除旧表
            cursor.execute('DROP TABLE history')

            # 重命名新表
            cursor.execute('ALTER TABLE history_new RENAME TO history')

            # 提交事务
            conn.commit()

            print("成功迁移 history 表")

        except Exception as e:
            # 回滚事务
            conn.rollback()
            print(f"迁移 history 表失败：{str(e)}")

    def _migrate_add_user_id_to_archives(self, conn):
        """迁移：添加 user_id 列到 archives 表"""
        cursor = conn.cursor()

        try:
            # 开始事务
            cursor.execute('BEGIN TRANSACTION')

            # 创建新表
            cursor.execute('''
            CREATE TABLE archives_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                file_id INTEGER NOT NULL,
                card_index INTEGER NOT NULL,
                details_visible INTEGER DEFAULT 0,
                name TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
            )
            ''')

            # 复制数据
            cursor.execute('''
            INSERT INTO archives_new (id, file_id, card_index, details_visible, name, timestamp)
            SELECT id, file_id, card_index, details_visible, name, timestamp FROM archives
            ''')

            # 删除旧表
            cursor.execute('DROP TABLE archives')

            # 重命名新表
            cursor.execute('ALTER TABLE archives_new RENAME TO archives')

            # 提交事务
            conn.commit()

            print("成功迁移 archives 表")

        except Exception as e:
            # 回滚事务
            conn.rollback()
            print(f"迁移 archives 表失败：{str(e)}")

    def _migrate_add_user_id_to_settings(self, conn):
        """迁移：添加 user_id 列到 settings 表"""
        cursor = conn.cursor()

        try:
            # 开始事务
            cursor.execute('BEGIN TRANSACTION')

            # 创建新表
            cursor.execute('''
            CREATE TABLE settings_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                key TEXT NOT NULL,
                value TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(user_id, key)
            )
            ''')

            # 复制数据
            cursor.execute('''
            INSERT INTO settings_new (id, key, value, timestamp)
            SELECT id, key, value, timestamp FROM settings
            ''')

            # 删除旧表
            cursor.execute('DROP TABLE settings')

            # 重命名新表
            cursor.execute('ALTER TABLE settings_new RENAME TO settings')

            # 提交事务
            conn.commit()

            print("成功迁移 settings 表")

        except Exception as e:
            # 回滚事务
            conn.rollback()
            print(f"迁移 settings 表失败：{str(e)}")

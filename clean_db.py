#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import os

def clean_database():
    """清理数据库中的重复文件记录"""
    # 连接数据库
    db_path = os.path.join('instance', 'vocabulary.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # 1. 备份最近访问的默认文件记录信息
        cursor.execute('SELECT * FROM files WHERE name = "vocabulary.xlsx" ORDER BY last_accessed DESC')
        default_files = cursor.fetchall()

        print(f"找到 {len(default_files)} 个默认文件记录")

        # 保存最近访问的默认文件信息
        latest_default_file = None
        if default_files:
            latest_default_file = dict(default_files[0])
            print(f"最近访问的默认文件: ID={latest_default_file['id']}, 路径={latest_default_file['path']}")

        # 2. 删除所有默认文件记录
        cursor.execute('DELETE FROM files WHERE name = "vocabulary.xlsx"')
        print(f"删除了 {cursor.rowcount} 个默认文件记录")

        # 3. 添加一个干净的默认文件记录
        if latest_default_file:
            user_id = latest_default_file['user_id']
            display_name = "默认词汇表 (vocabulary.xlsx)"

            cursor.execute(
                'INSERT INTO files (user_id, name, path, display_name) VALUES (?, ?, ?, ?)',
                (user_id, "vocabulary.xlsx", "vocabulary.xlsx", display_name)
            )
            print(f"添加了新的默认文件记录，用户ID={user_id}")
        else:
            # 如果没有默认文件记录，添加一个新的
            cursor.execute(
                'INSERT INTO files (name, path, display_name) VALUES (?, ?, ?)',
                ("vocabulary.xlsx", "vocabulary.xlsx", "默认词汇表 (vocabulary.xlsx)")
            )
            print("添加了新的默认文件记录，无用户ID")

        # 4. 清理重复的上传文件记录
        # 查找所有重复的文件路径（除了默认文件）
        cursor.execute('''
            SELECT path, COUNT(*) as count, MAX(last_accessed) as latest
            FROM files
            WHERE path != "vocabulary.xlsx"
            GROUP BY path
            HAVING count > 1
        ''')
        duplicate_paths = cursor.fetchall()

        # 处理重复文件
        for dup in duplicate_paths:
            path = dup['path']
            print(f"发现重复文件路径: {path}, 数量: {dup['count']}")

            # 获取该路径的所有文件记录
            cursor.execute('SELECT * FROM files WHERE path = ? ORDER BY last_accessed DESC', (path,))
            dup_files = cursor.fetchall()

            # 保留最近访问的一个
            keep_id = dup_files[0]['id']
            print(f"保留文件: ID={keep_id}, 路径={path}")

            # 删除其他的
            for file in dup_files[1:]:
                print(f"删除重复文件: ID={file['id']}, 路径={path}")
                cursor.execute('DELETE FROM files WHERE id = ?', (file['id'],))

        # 5. 标准化所有上传文件的路径
        cursor.execute('SELECT * FROM files WHERE path != "vocabulary.xlsx"')
        upload_files = cursor.fetchall()

        for file in upload_files:
            path = file['path']
            new_path = path

            # 处理容器内路径
            if path.startswith('/app/'):
                new_path = path[4:]  # 去掉'/app'前缀
            elif path.startswith('/uploads/'):
                new_path = path[1:]  # 去掉开头的'/'

            # 处理Windows路径分隔符
            if '\\' in new_path:
                new_path = new_path.replace('\\', '/')

            if new_path != path:
                print(f"标准化路径: {path} -> {new_path}")
                cursor.execute('UPDATE files SET path = ? WHERE id = ?', (new_path, file['id']))

        # 6. 提交更改
        conn.commit()
        print("数据库清理完成")

    except Exception as e:
        print(f"清理数据库时出错: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clean_database()

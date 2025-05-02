#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import uuid
import shutil
from werkzeug.utils import secure_filename
from flask import current_app, flash, url_for

# 创建上传集合
ALLOWED_EXTENSIONS = ('xlsx', 'xls')

def init_app(app):
    """初始化文件上传配置"""
    # 确保上传文件夹存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 设置最大文件大小限制
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

def save_uploaded_file(file):
    """保存上传的文件并返回文件信息"""
    if not file:
        return {
            "success": False,
            "error": "没有选择文件"
        }

    try:
        # 检查文件扩展名
        if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
            return {
                "success": False,
                "error": f"不支持的文件类型，请上传 {', '.join(ALLOWED_EXTENSIONS)} 文件"
            }

        # 生成唯一文件名
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"

        # 保存文件
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # 验证文件是否成功保存
        if not os.path.exists(file_path):
            raise Exception(f"文件保存失败：{file_path} 不存在")

        # 设置文件权限
        try:
            os.chmod(file_path, 0o644)
        except Exception as e:
            print(f"警告：无法设置文件权限: {str(e)}")

        print(f"文件成功保存到: {file_path}")

        return {
            "success": True,
            "file_path": file_path,
            "original_filename": original_filename,
            "unique_filename": unique_filename
        }
    except Exception as e:
        print(f"保存上传文件时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {
            "success": False,
            "error": f"保存文件时出错: {str(e)}"
        }

def get_file_list():
    """获取所有可用的Excel文件列表"""
    files = []
    upload_folder = current_app.config['UPLOAD_FOLDER']

    # 添加默认文件
    default_file_path = "vocabulary.xlsx"
    if os.path.exists(default_file_path):
        files.append({
            "name": "vocabulary.xlsx",
            "display_name": "默认词汇表 (vocabulary.xlsx)",
            "path": default_file_path,
            "is_default": True
        })

    # 添加上传的文件
    if os.path.exists(upload_folder):
        for filename in os.listdir(upload_folder):
            if filename.endswith(('.xlsx', '.xls')):
                file_path = os.path.join(upload_folder, filename)

                # 从文件名中提取原始文件名（去掉UUID前缀）
                original_name = "_".join(filename.split("_")[1:]) if "_" in filename else filename

                files.append({
                    "name": filename,
                    "display_name": f"上传的文件: {original_name}",
                    "path": file_path,
                    "is_default": False
                })

    return files

def delete_file(file_path):
    """删除指定的文件"""
    try:
        # 不允许删除默认文件
        if file_path == "vocabulary.xlsx" or os.path.basename(file_path) == "vocabulary.xlsx":
            return False, "不能删除默认文件"

        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False, f"文件不存在: {file_path}"

        # 删除文件
        os.remove(file_path)

        # 验证文件是否已删除
        if os.path.exists(file_path):
            return False, f"文件删除失败: {file_path}"

        return True, "文件删除成功"
    except Exception as e:
        print(f"删除文件时出错: {str(e)}")
        return False, f"删除文件时出错: {str(e)}"

def find_file(file_path):
    """查找文件的实际路径"""
    # 如果是默认文件，直接返回
    if file_path == "vocabulary.xlsx" and os.path.exists("vocabulary.xlsx"):
        return "vocabulary.xlsx"

    # 如果文件存在，直接返回
    if os.path.exists(file_path):
        return file_path

    # 尝试在上传文件夹中查找
    upload_folder = current_app.config['UPLOAD_FOLDER']
    basename = os.path.basename(file_path)
    possible_path = os.path.join(upload_folder, basename)

    if os.path.exists(possible_path):
        return possible_path

    # 尝试其他可能的路径
    possible_paths = [
        file_path,
        os.path.abspath(file_path),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), file_path),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', file_path),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # 如果找不到文件，返回None
    return None

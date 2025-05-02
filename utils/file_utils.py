#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import uuid
from werkzeug.utils import secure_filename


class FileUtils:
    """文件处理工具类，负责文件上传和管理"""

    @staticmethod
    def allowed_file(filename, allowed_extensions):
        """检查文件扩展名是否允许"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @staticmethod
    def save_uploaded_file(file, upload_folder, allowed_extensions):
        """保存上传的文件并返回文件路径"""
        if file and FileUtils.allowed_file(file.filename, allowed_extensions):
            try:
                # 生成唯一文件名以避免冲突
                original_filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{original_filename}"

                # 确保上传文件夹存在并有正确的权限
                os.makedirs(upload_folder, exist_ok=True)

                # 设置文件夹权限（确保可写）
                try:
                    os.chmod(upload_folder, 0o755)
                except Exception as e:
                    print(f"警告：无法设置上传文件夹权限: {str(e)}")

                # 构建文件路径
                file_path = os.path.join(upload_folder, unique_filename)

                # 保存文件
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
                return {
                    "success": False,
                    "error": f"保存文件时出错: {str(e)}"
                }

        return {
            "success": False,
            "error": "不支持的文件类型或无效的文件"
        }

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
            # 生成唯一文件名以避免冲突
            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            file_path = os.path.join(upload_folder, unique_filename)
            
            # 确保上传文件夹存在
            os.makedirs(upload_folder, exist_ok=True)
            
            # 保存文件
            file.save(file_path)
            
            return {
                "success": True,
                "file_path": file_path,
                "original_filename": original_filename,
                "unique_filename": unique_filename
            }
        
        return {
            "success": False,
            "error": "不支持的文件类型或无效的文件"
        }

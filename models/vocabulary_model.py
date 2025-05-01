#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas as pd


class VocabularyModel:
    """词汇数据模型类，负责加载和管理词汇数据"""

    def __init__(self):
        # 定义期望的列
        self.expected_columns = ["编号", "单词", "音标", "释义", "拆分", "综合法", "联想法"]
        # 存储卡片数据
        self.card_data = []
        # 当前文件信息
        self.current_file = {
            "name": "vocabulary.xlsx",  # 当前加载的文件名
            "display_name": "默认词汇表 (vocabulary.xlsx)",  # 显示名称
            "path": "vocabulary.xlsx"  # 文件路径
        }

    def load_vocabulary_data(self, file_path="vocabulary.xlsx", display_name=None, app_config=None):
        """从指定的Excel文件加载词汇数据"""
        try:
            # 规范化路径分隔符，确保在不同操作系统上一致
            file_path = os.path.normpath(file_path)

            # 检查文件是否存在于应用目录
            app_dir_path = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), file_path))
            # 然后检查父目录
            parent_dir_path = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', file_path))

            # 检查文件是否存在
            if os.path.isabs(file_path) and os.path.exists(file_path):
                # 如果是绝对路径且文件存在
                pass  # file_path已经正确
            elif os.path.exists(file_path):
                # 如果文件存在于当前工作目录
                file_path = os.path.abspath(file_path)
            elif os.path.exists(app_dir_path):
                file_path = app_dir_path
            elif os.path.exists(parent_dir_path):
                file_path = parent_dir_path
            else:
                print(f"Error: File not found at {file_path}, {app_dir_path}, or {parent_dir_path}")
                return False

            print(f"Attempting to load data from: {file_path}")
            # 使用pandas读取Excel文件
            df = pd.read_excel(file_path)

            # 验证列
            actual_columns = df.columns.tolist()
            if not all(col in actual_columns for col in self.expected_columns):
                missing_cols = [col for col in self.expected_columns if col not in actual_columns]
                print(f"Error: Missing expected columns in {file_path}: {missing_cols}")
                return False

            # 只选择期望的列并处理潜在的NaN值
            df = df[self.expected_columns].fillna("")

            # 将DataFrame转换为字典列表
            self.card_data = df.to_dict("records")

            # 更新当前文件信息
            file_name = os.path.basename(file_path)
            self.current_file["name"] = file_name
            self.current_file["path"] = file_path

            # 如果提供了显示名称，使用它；否则使用文件名
            if display_name:
                self.current_file["display_name"] = display_name
            else:
                # 如果是上传的文件，显示"上传的文件：原始文件名"
                if app_config and file_path.startswith(app_config['UPLOAD_FOLDER']):
                    # 从文件名中提取原始文件名（去掉UUID前缀）
                    original_name = "_".join(file_name.split("_")[1:]) if "_" in file_name else file_name
                    self.current_file["display_name"] = f"上传的文件: {original_name}"
                else:
                    self.current_file["display_name"] = f"默认词汇表 ({file_name})"

            print(f"Successfully loaded {len(self.card_data)} cards from {file_path}")
            return True

        except Exception as e:
            print(f"Error loading data from {file_path}: {e}")
            return False

    def get_card_data(self):
        """获取卡片数据"""
        return self.card_data

    def get_current_file(self):
        """获取当前文件信息"""
        return self.current_file

    def get_file_list(self, app_config):
        """获取所有可用的词汇文件列表"""
        files = []

        # 添加默认文件
        if os.path.exists("vocabulary.xlsx"):
            files.append({
                "name": "vocabulary.xlsx",
                "display_name": "默认词汇表 (vocabulary.xlsx)",
                "path": "vocabulary.xlsx"
            })

        # 添加上传的文件
        if os.path.exists(app_config['UPLOAD_FOLDER']):
            for filename in os.listdir(app_config['UPLOAD_FOLDER']):
                if self._allowed_file(filename, app_config):
                    file_path = os.path.join(app_config['UPLOAD_FOLDER'], filename)
                    # 从文件名中提取原始文件名（去掉UUID前缀）
                    original_name = "_".join(filename.split("_")[1:]) if "_" in filename else filename
                    files.append({
                        "name": filename,
                        "display_name": f"上传的文件: {original_name}",
                        "path": file_path
                    })

        return files

    def _allowed_file(self, filename, app_config):
        """检查文件扩展名是否允许"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app_config['ALLOWED_EXTENSIONS']

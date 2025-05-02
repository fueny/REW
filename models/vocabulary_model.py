#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas as pd
# 不再需要导入file_manager


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
            "path": "vocabulary.xlsx",  # 文件路径
            "is_default": True  # 是否是默认文件
        }

    def load_vocabulary_data(self, file_path="vocabulary.xlsx", display_name=None, app_config=None):
        """从指定的Excel文件加载词汇数据"""
        try:
            print(f"尝试加载文件: {file_path}")

            # 查找文件的实际路径
            if app_config:
                # 使用辅助方法查找文件
                actual_path = self._find_file(file_path, app_config)
            else:
                # 如果没有app_config，直接使用file_path
                actual_path = file_path if os.path.exists(file_path) else None

            if not actual_path:
                print(f"错误: 找不到文件 {file_path}")
                return False

            print(f"找到文件: {actual_path}")

            # 使用pandas读取Excel文件
            df = pd.read_excel(actual_path)

            # 验证列
            actual_columns = df.columns.tolist()
            if not all(col in actual_columns for col in self.expected_columns):
                missing_cols = [col for col in self.expected_columns if col not in actual_columns]
                print(f"错误: 文件 {actual_path} 缺少必要的列: {missing_cols}")
                return False

            # 只选择期望的列并处理潜在的NaN值
            df = df[self.expected_columns].fillna("")

            # 将DataFrame转换为字典列表
            self.card_data = df.to_dict("records")

            # 更新当前文件信息
            file_name = os.path.basename(actual_path)
            self.current_file["name"] = file_name
            self.current_file["path"] = actual_path

            # 判断是否是默认文件
            is_default = (file_name == "vocabulary.xlsx" or actual_path == "vocabulary.xlsx")
            self.current_file["is_default"] = is_default

            # 如果提供了显示名称，使用它；否则使用文件名
            if display_name:
                self.current_file["display_name"] = display_name
            else:
                if is_default:
                    self.current_file["display_name"] = f"默认词汇表 ({file_name})"
                else:
                    # 从文件名中提取原始文件名（去掉UUID前缀）
                    original_name = "_".join(file_name.split("_")[1:]) if "_" in file_name else file_name
                    self.current_file["display_name"] = f"上传的文件: {original_name}"

            print(f"成功加载 {len(self.card_data)} 个卡片，来自文件 {actual_path}")
            return True

        except Exception as e:
            print(f"加载文件 {file_path} 时出错: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False

    def get_card_data(self):
        """获取卡片数据"""
        return self.card_data

    def get_current_file(self):
        """获取当前文件信息"""
        return self.current_file

    def _find_file(self, file_path, app_config):
        """查找文件的实际路径"""
        # 如果是默认文件，直接返回
        if file_path == "vocabulary.xlsx" and os.path.exists("vocabulary.xlsx"):
            return "vocabulary.xlsx"

        # 如果文件存在，直接返回
        if os.path.exists(file_path):
            return file_path

        # 尝试在上传文件夹中查找
        upload_folder = app_config.get('UPLOAD_FOLDER')
        if upload_folder:
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

    def get_file_list(self, app_config=None):
        """获取所有可用的词汇文件列表"""
        try:
            # 直接使用文件系统获取文件列表
            files = []

            # 添加默认文件
            if os.path.exists("vocabulary.xlsx"):
                files.append({
                    "name": "vocabulary.xlsx",
                    "display_name": "默认词汇表 (vocabulary.xlsx)",
                    "path": "vocabulary.xlsx",
                    "is_default": True
                })

            # 添加上传的文件
            if app_config and 'UPLOAD_FOLDER' in app_config and os.path.exists(app_config['UPLOAD_FOLDER']):
                for filename in os.listdir(app_config['UPLOAD_FOLDER']):
                    if filename.lower().endswith(('.xlsx', '.xls')):
                        file_path = os.path.join(app_config['UPLOAD_FOLDER'], filename)

                        # 从文件名中提取原始文件名（去掉UUID前缀）
                        original_name = "_".join(filename.split("_")[1:]) if "_" in filename else filename

                        files.append({
                            "name": filename,
                            "display_name": f"上传的文件: {original_name}",
                            "path": file_path,
                            "is_default": False
                        })

            return files
        except Exception as e:
            print(f"获取文件列表时出错: {str(e)}")
            import traceback
            print(traceback.format_exc())
            # 如果出错，返回一个只包含当前文件的列表
            return [self.current_file]

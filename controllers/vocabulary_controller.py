#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, request, redirect, url_for, flash, jsonify, session
from models.vocabulary_model import VocabularyModel
from utils.file_utils import FileUtils
from controllers.auth_controller import login_required
import os


class VocabularyController:
    """词汇应用控制器，处理路由和业务逻辑"""

    def __init__(self, app, db):
        self.app = app
        self.db = db
        self.model = VocabularyModel()

        # 初始化时加载默认词汇数据
        if not self.model.load_vocabulary_data("vocabulary.xlsx", app_config=app.config):
            print("Failed to load vocabulary data. Application might not function correctly.")
            # 提供一些默认数据，以便UI测试
            self.model.card_data = [
                {"编号": "N/A", "单词": "Error", "音标": "", "释义": "Failed to load data.", "拆分": "", "综合法": "", "联想法": ""}
            ]

        # 注册路由
        self._register_routes()

    def _add_current_file_to_db(self, user_id=None):
        """将当前文件添加到数据库"""
        current_file = self.model.get_current_file()
        self.db.add_file(
            current_file["name"],
            current_file["path"],
            current_file["display_name"],
            user_id
        )

    def _register_routes(self):
        """注册应用路由"""
        # 基本路由
        self.app.add_url_rule('/', 'index', login_required(self.index), methods=['GET'])
        self.app.add_url_rule('/upload', 'upload_file', login_required(self.upload_file), methods=['POST'])
        self.app.add_url_rule('/switch/<path:file_path>', 'switch_file', login_required(self.switch_file))
        self.app.add_url_rule('/list_files', 'list_files', login_required(self.list_files))
        self.app.add_url_rule('/api/files/<int:file_id>', 'delete_file', login_required(self.delete_file), methods=['DELETE'])

        # 历史记录API
        self.app.add_url_rule('/api/history', 'get_history', login_required(self.get_history), methods=['GET'])
        self.app.add_url_rule('/api/history', 'add_history', login_required(self.add_history), methods=['POST'])
        self.app.add_url_rule('/api/history', 'clear_history', login_required(self.clear_history), methods=['DELETE'])

        # 存档API
        self.app.add_url_rule('/api/archives', 'get_archives', login_required(self.get_archives), methods=['GET'])
        self.app.add_url_rule('/api/archives', 'create_archive', login_required(self.create_archive), methods=['POST'])
        self.app.add_url_rule('/api/archives/<int:archive_id>', 'get_archive', login_required(self.get_archive), methods=['GET'])
        self.app.add_url_rule('/api/archives/<int:archive_id>', 'delete_archive', login_required(self.delete_archive), methods=['DELETE'])

    def index(self):
        """渲染主页面，显示词汇卡片"""
        # 获取当前用户ID（在请求上下文中）
        user_id = session.get('user_id')

        # 确保当前文件已添加到数据库
        self._add_current_file_to_db(user_id)

        return render_template(
            "index.html",
            cards=self.model.get_card_data(),
            current_file=self.model.get_current_file()
        )

    def upload_file(self):
        """处理文件上传"""
        if 'file' not in request.files:
            flash('没有选择文件', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('没有选择文件', 'error')
            return redirect(request.url)

        # 获取当前用户ID
        user_id = session.get('user_id')

        # 保存上传的文件
        result = FileUtils.save_uploaded_file(
            file,
            self.app.config['UPLOAD_FOLDER'],
            self.app.config['ALLOWED_EXTENSIONS']
        )

        if result['success']:
            # 尝试加载新上传的文件，使用原始文件名作为显示名
            display_name = f"上传的文件: {result['original_filename']}"
            if self.model.load_vocabulary_data(result['file_path'], display_name, self.app.config):
                # 将文件添加到数据库
                current_file = self.model.get_current_file()
                self.db.add_file(
                    current_file["name"],
                    current_file["path"],
                    current_file["display_name"],
                    user_id
                )

                flash('文件上传成功，数据已加载', 'success')
                # 添加上传成功标记到URL，用于前端检测
                return redirect(url_for('index', upload_success=1))
            else:
                flash('文件格式不正确，请确保包含所需的列', 'error')
        else:
            flash('不支持的文件类型，请上传 .xlsx 或 .xls 文件', 'error')

        return redirect(url_for('index'))

    def switch_file(self, file_path):
        """切换到指定的词汇文件"""
        # 安全检查：确保文件路径是允许的
        if not (file_path == "vocabulary.xlsx" or file_path.startswith(self.app.config['UPLOAD_FOLDER'])):
            flash('不允许访问该文件', 'error')
            return redirect(url_for('index'))

        # 获取当前用户ID
        user_id = session.get('user_id')

        # 尝试加载指定的文件
        if self.model.load_vocabulary_data(file_path, app_config=self.app.config):
            # 将文件添加到数据库
            current_file = self.model.get_current_file()
            self.db.add_file(
                current_file["name"],
                current_file["path"],
                current_file["display_name"],
                user_id
            )

            flash(f'已切换到文件: {self.model.current_file["display_name"]}', 'success')
        else:
            flash('无法加载指定的文件', 'error')

        return redirect(url_for('index'))

    def list_files(self):
        """列出所有可用的词汇文件"""
        # 获取当前用户ID
        user_id = session.get('user_id')

        # 从数据库获取文件列表
        db_files = self.db.get_all_files(user_id)

        # 如果数据库中没有文件，则从文件系统获取
        if not db_files:
            files = self.model.get_file_list(self.app.config)
            # 将文件添加到数据库
            for file in files:
                self.db.add_file(file["name"], file["path"], file["display_name"], user_id)
            # 重新获取文件列表（现在包含ID）
            db_files = self.db.get_all_files(user_id)

        return jsonify({
            "files": db_files,
            "current": self.model.get_current_file()
        })

    # --- 历史记录API ---

    def get_history(self):
        """获取历史记录"""
        # 获取当前用户ID
        user_id = session.get('user_id')

        # 获取当前文件ID
        current_file = self.model.get_current_file()
        file_db = self.db.get_file_by_path(current_file["path"], user_id)

        if not file_db:
            return jsonify({"error": "当前文件未在数据库中注册"}), 404

        # 获取历史记录
        history = self.db.get_history_by_date(file_db["id"], user_id=user_id)

        return jsonify({
            "history": history,
            "file": {
                "id": file_db["id"],
                "name": file_db["name"],
                "display_name": file_db["display_name"]
            }
        })

    def add_history(self):
        """添加历史记录"""
        data = request.json

        if not data or "card_index" not in data:
            return jsonify({"error": "缺少必要参数"}), 400

        # 获取当前用户ID
        user_id = session.get('user_id')

        # 获取当前文件ID
        current_file = self.model.get_current_file()
        file_db = self.db.get_file_by_path(current_file["path"], user_id)

        if not file_db:
            return jsonify({"error": "当前文件未在数据库中注册"}), 404

        # 添加历史记录
        self.db.add_history(file_db["id"], data["card_index"], user_id)

        return jsonify({"success": True})

    def clear_history(self):
        """清除历史记录"""
        # 获取当前用户ID
        user_id = session.get('user_id')

        # 获取当前文件ID
        current_file = self.model.get_current_file()
        file_db = self.db.get_file_by_path(current_file["path"], user_id)

        if not file_db:
            return jsonify({"error": "当前文件未在数据库中注册"}), 404

        # 清除历史记录
        self.db.clear_history(file_db["id"], user_id)

        return jsonify({"success": True})

    # --- 存档API ---

    def get_archives(self):
        """获取存档列表"""
        # 获取当前用户ID
        user_id = session.get('user_id')

        # 获取当前文件ID
        current_file = self.model.get_current_file()
        file_db = self.db.get_file_by_path(current_file["path"], user_id)

        if not file_db:
            return jsonify({"error": "当前文件未在数据库中注册"}), 404

        # 获取存档列表
        archives = self.db.get_archives(file_db["id"], user_id)

        return jsonify({
            "archives": archives,
            "file": {
                "id": file_db["id"],
                "name": file_db["name"],
                "display_name": file_db["display_name"]
            }
        })

    def create_archive(self):
        """创建存档"""
        data = request.json

        if not data or "card_index" not in data:
            return jsonify({"error": "缺少必要参数"}), 400

        # 获取当前用户ID
        user_id = session.get('user_id')

        # 获取当前文件ID
        current_file = self.model.get_current_file()
        file_db = self.db.get_file_by_path(current_file["path"], user_id)

        if not file_db:
            return jsonify({"error": "当前文件未在数据库中注册"}), 404

        # 创建存档
        details_visible = data.get("details_visible", False)
        name = data.get("name", None)

        archive_id = self.db.create_archive(
            file_db["id"],
            data["card_index"],
            details_visible,
            name,
            user_id
        )

        return jsonify({
            "success": True,
            "archive_id": archive_id
        })

    def get_archive(self, archive_id):
        """获取指定存档"""
        # 获取当前用户ID
        user_id = session.get('user_id')

        archive = self.db.get_archive(archive_id, user_id)

        if not archive:
            return jsonify({"error": "存档不存在"}), 404

        return jsonify({"archive": archive})

    def delete_archive(self, archive_id):
        """删除存档"""
        # 获取当前用户ID
        user_id = session.get('user_id')

        result = self.db.delete_archive(archive_id, user_id)

        if not result:
            return jsonify({"error": "存档不存在或删除失败"}), 404

        return jsonify({"success": True})

    def delete_file(self, file_id):
        """删除文件"""
        # 获取当前用户ID
        user_id = session.get('user_id')

        # 获取当前文件
        current_file = self.model.get_current_file()

        # 获取文件信息（在删除前获取）
        file_path = None
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if user_id:
                cursor.execute('SELECT path FROM files WHERE id = ? AND user_id = ?', (file_id, user_id))
            else:
                cursor.execute('SELECT path FROM files WHERE id = ? AND user_id IS NULL', (file_id,))

            file_record = cursor.fetchone()

            if file_record:
                file_path = file_record['path']

        # 如果是当前正在使用的文件，则不允许删除
        if file_path and file_path == current_file['path']:
            return jsonify({"error": "不能删除当前正在使用的文件"}), 400

        # 从数据库中删除文件记录
        success, message = self.db.delete_file(file_id, user_id)

        if not success:
            return jsonify({"error": message}), 400

        # 尝试删除物理文件（如果存在且不是默认文件）
        if file_path and file_path != 'vocabulary.xlsx':
            # 如果是相对路径，转换为绝对路径
            if not os.path.isabs(file_path):
                # 规范化路径分隔符
                file_path = os.path.normpath(file_path)
                physical_file_path = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), file_path))
            else:
                physical_file_path = file_path

            try:
                if os.path.exists(physical_file_path):
                    os.remove(physical_file_path)
                    print(f"成功删除物理文件: {physical_file_path}")
                else:
                    print(f"物理文件不存在: {physical_file_path}")
            except Exception as e:
                # 即使物理文件删除失败，也继续返回成功
                print(f"警告：无法删除物理文件 {physical_file_path}: {str(e)}")

        return jsonify({"success": True, "message": message})

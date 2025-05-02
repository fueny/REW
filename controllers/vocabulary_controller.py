#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, request, redirect, url_for, flash, jsonify, session
from models.vocabulary_model import VocabularyModel
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
        self.app.add_url_rule('/switch_file', 'switch_file', login_required(self.switch_file), methods=['POST'])
        self.app.add_url_rule('/switch_file_direct', 'switch_file_direct', login_required(self.switch_file_direct), methods=['POST'])
        self.app.add_url_rule('/switch/<path:file_path>', 'switch_file_path', login_required(self.switch_file_path), methods=['GET'])
        self.app.add_url_rule('/list_files', 'list_files', login_required(self.list_files))
        self.app.add_url_rule('/api/files/<int:file_id>', 'delete_file', login_required(self.delete_file), methods=['DELETE'])

        # 历史记录API已禁用

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
        try:
            if 'file' not in request.files:
                flash('没有选择文件', 'error')
                return redirect(request.url)

            file = request.files['file']

            if file.filename == '':
                flash('没有选择文件', 'error')
                return redirect(request.url)

            # 获取当前用户ID
            user_id = session.get('user_id')

            # 检查文件类型
            if not file.filename.lower().endswith(('.xlsx', '.xls')):
                flash('不支持的文件类型，请上传 .xlsx 或 .xls 文件', 'error')
                return redirect(url_for('index'))

            # 打印上传信息
            print(f"正在上传文件: {file.filename}")

            # 保存上传的文件
            result = self._save_uploaded_file(file)

            if result['success']:
                print(f"文件上传成功: {result['file_path']}")

                # 尝试加载新上传的文件，使用原始文件名作为显示名
                display_name = f"上传的文件: {result['original_filename']}"

                # 检查文件是否存在
                if not os.path.exists(result['file_path']):
                    print(f"错误：上传的文件不存在: {result['file_path']}")
                    flash('文件上传失败：文件不存在', 'error')
                    return redirect(url_for('index'))

                # 检查文件大小
                file_size = os.path.getsize(result['file_path'])
                if file_size == 0:
                    print(f"错误：上传的文件为空: {result['file_path']}")
                    flash('文件上传失败：文件为空', 'error')
                    return redirect(url_for('index'))

                print(f"尝试加载文件: {result['file_path']}, 大小: {file_size} 字节")

                if self.model.load_vocabulary_data(result['file_path'], display_name, self.app.config):
                    print(f"文件加载成功: {result['file_path']}")

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
                    print(f"文件格式不正确: {result['file_path']}")
                    flash('文件格式不正确，请确保包含所需的列', 'error')
            else:
                print(f"文件上传失败: {result.get('error', '未知错误')}")
                flash(f"文件上传失败: {result.get('error', '未知错误')}", 'error')

            return redirect(url_for('index'))

        except Exception as e:
            print(f"上传文件时发生错误: {str(e)}")
            import traceback
            print(traceback.format_exc())
            flash(f'上传文件时发生错误: {str(e)}', 'error')
            return redirect(url_for('index'))

    def switch_file(self):
        """切换到指定的词汇文件 (API方式)"""
        try:
            print(f"收到切换文件请求，方法: {request.method}")
            print(f"请求头: {dict(request.headers)}")
            print(f"请求内容类型: {request.content_type}")
            print(f"请求URL: {request.url}")
            print(f"请求路径: {request.path}")
            print(f"请求参数: {request.args}")
            print(f"请求表单: {request.form}")
            print(f"请求数据: {request.data}")

            # 从POST请求中获取文件路径
            try:
                if request.is_json:
                    data = request.json
                    print(f"JSON请求数据: {data}")
                elif request.form:
                    data = {'file_path': request.form.get('file_path')}
                    print(f"表单请求数据: {data}")
                else:
                    # 尝试从请求体解析JSON
                    try:
                        import json
                        data = json.loads(request.data.decode('utf-8'))
                        print(f"从请求体解析的JSON数据: {data}")
                    except:
                        # 如果所有方法都失败，尝试从URL参数获取
                        data = {'file_path': request.args.get('file_path')}
                        print(f"从URL参数获取数据: {data}")
            except Exception as e:
                print(f"解析请求数据失败: {str(e)}")
                import traceback
                print(traceback.format_exc())
                data = {}

            if not data or 'file_path' not in data or not data['file_path']:
                error_msg = "缺少文件路径参数"
                print(error_msg)
                return jsonify({"success": False, "error": error_msg}), 400

            file_path = data['file_path']
            print(f"尝试切换到文件: {file_path}")

            # 获取当前用户ID
            user_id = session.get('user_id')
            print(f"当前用户ID: {user_id}")

            # 使用模型查找文件
            actual_path = self.model._find_file(file_path, self.app.config)
            print(f"查找文件结果: {actual_path}")

            if not actual_path:
                print(f"找不到文件: {file_path}")
                return jsonify({
                    "success": False,
                    "error": "找不到指定的文件"
                }), 404

            print(f"找到文件: {actual_path}")

            # 尝试加载指定的文件
            load_result = self.model.load_vocabulary_data(actual_path, app_config=self.app.config)
            print(f"加载文件结果: {load_result}")

            if load_result:
                # 将文件添加到数据库
                current_file = self.model.get_current_file()
                print(f"当前文件信息: {current_file}")

                # 添加到数据库
                db_result = self.db.add_file(
                    current_file["name"],
                    current_file["path"],
                    current_file["display_name"],
                    user_id
                )
                print(f"添加到数据库结果: {db_result}")

                print(f"成功切换到文件: {current_file['path']}")
                flash(f'已切换到文件: {current_file["display_name"]}', 'success')

                # 返回成功响应
                return jsonify({
                    "success": True,
                    "message": f"已切换到文件: {current_file['display_name']}",
                    "file": current_file
                })
            else:
                print(f"无法加载文件: {actual_path}")
                return jsonify({
                    "success": False,
                    "error": "无法加载指定的文件"
                }), 500

        except Exception as e:
            import traceback
            print(f"切换文件时出错: {str(e)}")
            print(traceback.format_exc())  # 打印完整的堆栈跟踪
            return jsonify({
                "success": False,
                "error": f"切换文件时出错: {str(e)}"
            }), 500

    def switch_file_direct(self):
        """切换到指定的词汇文件 (表单提交方式)"""
        try:
            # 从表单中获取文件路径
            file_path = request.form.get('file_path')
            if not file_path:
                flash('缺少文件路径参数', 'error')
                return redirect(url_for('index'))

            print(f"尝试切换到文件 (表单方式): {file_path}")

            # 获取当前用户ID
            user_id = session.get('user_id')

            # 使用模型查找文件
            actual_path = self.model._find_file(file_path, self.app.config)

            if not actual_path:
                print(f"找不到文件: {file_path}")
                flash('找不到指定的文件', 'error')
                return redirect(url_for('index'))

            print(f"找到文件: {actual_path}")

            # 尝试加载指定的文件
            if self.model.load_vocabulary_data(actual_path, app_config=self.app.config):
                # 将文件添加到数据库
                current_file = self.model.get_current_file()

                # 添加到数据库
                self.db.add_file(
                    current_file["name"],
                    current_file["path"],
                    current_file["display_name"],
                    user_id
                )

                print(f"成功切换到文件: {current_file['path']}")
                flash(f'已切换到文件: {current_file["display_name"]}', 'success')
            else:
                print(f"无法加载文件: {actual_path}")
                flash('无法加载指定的文件', 'error')

            return redirect(url_for('index'))

        except Exception as e:
            import traceback
            print(f"切换文件时出错: {str(e)}")
            print(traceback.format_exc())  # 打印完整的堆栈跟踪
            flash(f'切换文件时出错: {str(e)}', 'error')
            return redirect(url_for('index'))

    def switch_file_path(self, file_path):
        """处理/switch/[文件路径]格式的请求"""
        try:
            print(f"收到/switch/路径的请求，文件路径: {file_path}")

            # 获取当前用户ID
            user_id = session.get('user_id')

            # 使用模型查找文件
            actual_path = self.model._find_file(file_path, self.app.config)

            if not actual_path:
                print(f"找不到文件: {file_path}")
                flash('找不到指定的文件', 'error')
                return redirect(url_for('index'))

            print(f"找到文件: {actual_path}")

            # 尝试加载指定的文件
            if self.model.load_vocabulary_data(actual_path, app_config=self.app.config):
                # 将文件添加到数据库
                current_file = self.model.get_current_file()

                # 添加到数据库
                self.db.add_file(
                    current_file["name"],
                    current_file["path"],
                    current_file["display_name"],
                    user_id
                )

                print(f"成功切换到文件: {current_file['path']}")
                flash(f'已切换到文件: {current_file["display_name"]}', 'success')
            else:
                print(f"无法加载文件: {actual_path}")
                flash('无法加载指定的文件', 'error')

            return redirect(url_for('index'))

        except Exception as e:
            import traceback
            print(f"切换文件时出错: {str(e)}")
            print(traceback.format_exc())  # 打印完整的堆栈跟踪
            flash(f'切换文件时出错: {str(e)}', 'error')
            return redirect(url_for('index'))

    def list_files(self):
        """列出所有可用的词汇文件"""
        try:
            # 获取当前用户ID
            user_id = session.get('user_id')

            # 使用模型获取文件列表
            files = self.model.get_file_list(self.app.config)

            # 将文件添加到数据库（如果不存在）
            for file in files:
                # 检查文件是否已存在于数据库中
                existing_file = self.db.get_file_by_path(file["path"], user_id)

                # 如果文件不存在，则添加
                if not existing_file:
                    self.db.add_file(
                        file["name"],
                        file["path"],
                        file["display_name"],
                        user_id
                    )
                # 如果文件存在但显示名称不同，则更新显示名称
                elif existing_file["display_name"] != file["display_name"]:
                    self.db.add_file(  # add_file 函数会处理更新逻辑
                        file["name"],
                        file["path"],
                        file["display_name"],
                        user_id
                    )

            # 从数据库获取文件列表（包含ID）
            # 这个函数会处理重复文件的清理
            db_files = self.db.get_all_files(user_id)

            return jsonify({
                "files": db_files,
                "current": self.model.get_current_file()
            })
        except Exception as e:
            import traceback
            print(f"获取文件列表时出错: {str(e)}")
            print(traceback.format_exc())

            # 如果出错，返回一个只包含当前文件的列表
            return jsonify({
                "files": [self.model.get_current_file()],
                "current": self.model.get_current_file()
            })

    # --- 历史记录API已禁用 ---

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

    def _save_uploaded_file(self, file):
        """保存上传的文件并返回文件信息"""
        if not file:
            return {
                "success": False,
                "error": "没有选择文件"
            }

        try:
            # 检查文件扩展名
            if not file.filename.lower().endswith(('.xlsx', '.xls')):
                return {
                    "success": False,
                    "error": "不支持的文件类型，请上传 .xlsx 或 .xls 文件"
                }

            # 生成唯一文件名
            import uuid
            from werkzeug.utils import secure_filename

            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"

            # 保存文件
            upload_folder = self.app.config['UPLOAD_FOLDER']
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

    def _delete_file(self, file_path):
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
            import traceback
            print(traceback.format_exc())
            return False, f"删除文件时出错: {str(e)}"

    def delete_file(self, file_id):
        """删除文件"""
        try:
            print(f"尝试删除文件ID: {file_id}")

            # 获取当前用户ID
            user_id = session.get('user_id')

            # 获取当前文件
            current_file = self.model.get_current_file()
            print(f"当前文件: {current_file['path']}")

            # 获取文件信息（在删除前获取）
            file_path = None
            file_name = None
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                if user_id:
                    cursor.execute('SELECT * FROM files WHERE id = ? AND user_id = ?', (file_id, user_id))
                else:
                    cursor.execute('SELECT * FROM files WHERE id = ? AND user_id IS NULL', (file_id,))

                file_record = cursor.fetchone()

                if file_record:
                    file_path = file_record['path']
                    file_name = file_record['name']
                    print(f"要删除的文件: ID={file_id}, 路径={file_path}, 名称={file_name}")

            if not file_path:
                print(f"文件不存在: ID={file_id}")
                return jsonify({"error": "文件不存在"}), 404

            # 如果是默认文件，不允许删除
            if file_name == 'vocabulary.xlsx' or file_path == 'vocabulary.xlsx':
                print(f"不能删除默认文件: {file_path}")
                return jsonify({"error": "不能删除默认文件"}), 400

            # 如果是当前正在使用的文件，则不允许删除
            if file_path == current_file['path'] or file_name == current_file['name']:
                print(f"不能删除当前正在使用的文件: {file_path}")
                return jsonify({"error": "不能删除当前正在使用的文件"}), 400

            # 从数据库中删除文件记录
            success, message = self.db.delete_file(file_id, user_id)

            if not success:
                print(f"删除文件记录失败: {message}")
                return jsonify({"error": message}), 400

            print(f"成功从数据库中删除文件记录: ID={file_id}")

            # 删除物理文件
            delete_success, delete_message = self._delete_file(file_path)

            if delete_success:
                print(f"成功删除物理文件: {file_path}")
            else:
                print(f"警告：删除物理文件失败: {delete_message}")

            return jsonify({"success": True, "message": "文件删除成功"})

        except Exception as e:
            import traceback
            print(f"删除文件时出错: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": f"删除文件时出错: {str(e)}"}), 500

// file.js - 文件管理功能

// 加载可用的文件列表
function loadFileList() {
    const fileList = document.getElementById('file-list');

    // 显示加载中
    fileList.innerHTML = '<div class="loading">加载中...</div>';

    // 发送请求获取文件列表
    fetch('/list_files', {
        method: 'GET',
        headers: {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        },
        credentials: 'same-origin'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`获取文件列表失败: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            // 清空列表
            fileList.innerHTML = '';

            // 添加文件项
            if (data.files && data.files.length > 0) {
                data.files.forEach(file => {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';

                    // 检查是否是当前文件
                    const isCurrentFile = (
                        file.name === currentFile.name ||
                        file.path === currentFile.path ||
                        (file.path && currentFile.path && file.path.replace(/\\/g, '/') === currentFile.path.replace(/\\/g, '/'))
                    );

                    if (isCurrentFile) {
                        fileItem.classList.add('active');
                    }

                    // 创建文件名容器
                    const fileNameContainer = document.createElement('div');
                    fileNameContainer.className = 'file-name';
                    fileNameContainer.textContent = file.display_name;
                    fileItem.appendChild(fileNameContainer);

                    // 添加文件路径数据属性
                    fileItem.dataset.path = file.path;
                    fileItem.dataset.id = file.id;

                    // 创建操作按钮容器
                    const actionContainer = document.createElement('div');
                    actionContainer.className = 'file-actions';

                    // 如果不是默认文件，添加删除按钮
                    if (!file.is_default) {
                        const deleteBtn = document.createElement('button');
                        deleteBtn.className = 'file-delete-btn';
                        deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i>';
                        deleteBtn.title = '删除文件';

                        // 添加删除按钮点击事件
                        deleteBtn.addEventListener('click', async (e) => {
                            e.stopPropagation(); // 阻止事件冒泡

                            // 显示确认对话框
                            showConfirmDialog(
                                '删除文件',
                                `确定要删除文件 "${file.display_name}" 吗？此操作不可撤销，相关的历史记录和存档也将被删除。`,
                                async () => {
                                    // 显示删除中提示
                                    showMessage('正在删除文件，请稍候...', 'info');

                                    // 调用API删除文件
                                    const response = await deleteFile(file.id);

                                    if (response.success) {
                                        showMessage('文件删除成功', 'success');
                                        // 重新加载文件列表
                                        loadFileList();
                                    } else {
                                        showMessage(response.error || '删除文件失败', 'error');
                                    }
                                }
                            );
                        });

                        actionContainer.appendChild(deleteBtn);
                    }

                    // 将操作按钮容器添加到文件项
                    fileItem.appendChild(actionContainer);

                    // 点击切换文件
                    fileNameContainer.addEventListener('click', () => {
                        // 调试信息
                        console.log('文件点击事件触发，文件路径:', file.path);

                        // 如果点击的是当前文件，则不做任何操作
                        if (isCurrentFile) {
                            document.getElementById('file-list-container').classList.add('hidden');
                            return;
                        }

                        // 使用switchToFile函数切换文件
                        switchToFile(file.path);
                    });

                    fileList.appendChild(fileItem);
                });
            } else {
                fileList.innerHTML = '<div class="loading">没有可用的文件</div>';
            }
        })
        .catch(error => {
            console.error('获取文件列表失败:', error);
            fileList.innerHTML = '<div class="loading">获取文件列表失败: ' + error.message + '</div>';
        });
}

// 切换文件列表的显示/隐藏
function toggleFileList() {
    const fileListContainer = document.getElementById('file-list-container');

    // 切换文件列表的显示/隐藏
    if (fileListContainer.classList.contains('hidden')) {
        loadFileList();
        fileListContainer.classList.remove('hidden');
    } else {
        fileListContainer.classList.add('hidden');
    }
}

// 上传文件
function uploadFile() {
    const fileInput = document.getElementById('file');

    // 检查是否选择了文件
    if (!fileInput.files || fileInput.files.length === 0) {
        showMessage('请选择要上传的文件', 'error');
        return;
    }

    // 检查文件类型
    const file = fileInput.files[0];
    const fileExt = file.name.split('.').pop().toLowerCase();
    if (fileExt !== 'xlsx' && fileExt !== 'xls') {
        showMessage('请上传Excel文件 (.xlsx 或 .xls)', 'error');
        return;
    }

    // 显示上传中提示
    showMessage('正在上传文件，请稍候...', 'info');

    // 设置一个标记，表示正在上传文件
    sessionStorage.setItem('file_uploading', 'true');

    // 提交表单
    const form = document.getElementById('upload-form');
    form.submit();
}

// 切换到指定文件
function switchToFile(filePath) {
    try {
        // 检查是否与当前文件相同
        if (filePath === currentFile.path) {
            console.log('已经是当前文件，无需切换');
            showMessage('已经是当前文件', 'info');
            // 清除切换状态
            sessionStorage.removeItem('switching_file');
            return true;
        }

        // 显示加载中提示
        showMessage('正在切换文件，请稍候...', 'info');
        console.log(`尝试切换到文件: ${filePath}`);

        // 获取现有的切换信息
        let switchInfo = {
            path: filePath,
            timestamp: new Date().getTime(),
            attempts: 0
        };

        // 检查是否已有切换记录
        const existingData = sessionStorage.getItem('switching_file');
        if (existingData) {
            try {
                const existingInfo = JSON.parse(existingData);
                // 如果是同一个文件，保留尝试次数
                if (existingInfo.path === filePath) {
                    switchInfo.attempts = existingInfo.attempts || 0;
                }
            } catch (e) {
                console.error('解析现有切换数据失败:', e);
            }
        }

        // 记录切换文件的状态，以便在页面刷新后恢复
        sessionStorage.setItem('switching_file', JSON.stringify(switchInfo));

        // 使用表单提交方式切换文件
        const switchForm = document.getElementById('switch-file-form');
        const filePathInput = document.getElementById('switch-file-path');

        // 设置文件路径
        filePathInput.value = filePath;

        // 打印表单信息
        console.log('switchToFile函数 - 表单信息:', {
            'form_action': switchForm.action,
            'form_method': switchForm.method,
            'file_path_value': filePathInput.value,
            'attempts': switchInfo.attempts
        });

        // 提交表单
        switchForm.submit();

        return true;
    } catch (error) {
        console.error('切换文件失败:', error);
        showMessage('切换文件失败: ' + error.message, 'error');

        // 清除切换状态，避免无限循环
        sessionStorage.removeItem('switching_file');

        return false;
    }
}



// progress.js - 学习进度管理

// 自动保存当前学习进度
function autoSaveProgress() {
    // 使用localStorage保存进度
    localStorage.setItem('currentCardIndex', currentCardIndex);
    return true;
}

// 自动加载上次学习进度
async function autoLoadProgress() {
    try {
        // 从localStorage获取上次的进度
        const savedIndex = localStorage.getItem('currentCardIndex');

        if (savedIndex !== null) {
            // 跳转到保存的卡片
            jumpToCard(parseInt(savedIndex, 10));
            return true;
        }

        // 如果没有保存的进度，显示第一张卡片
        jumpToCard(0);
        return false;
    } catch (error) {
        console.error('自动加载进度失败:', error);
        // 出错时显示第一张卡片
        jumpToCard(0);
        return false;
    }
}

// 手动加载上次使用的文件（通过按钮触发）
async function manualLoadLastFile() {
    try {
        // 获取文件列表
        const response = await fetch('/list_files');
        const data = await response.json();

        if (!data.files || data.files.length === 0) {
            showMessage('没有找到可用的文件', 'info');
            return false;
        }

        // 找到最近使用的文件（第一个文件，因为后端已经按最近访问时间排序）
        const lastFile = data.files[0];

        // 如果当前文件与上次使用的文件相同，直接返回
        if (lastFile.name === currentFile.name && lastFile.path === currentFile.path) {
            showMessage('当前已经是上次使用的文件', 'warning');
            return false;
        }

        // 显示确认对话框
        return new Promise(resolve => {
            showConfirmDialog(
                '加载上次文件',
                `是否要加载上次使用的文件 "${lastFile.display_name}"？`,
                async () => {
                    try {
                        // 显示加载中提示
                        showMessage('正在切换文件，请稍候...', 'info');
                        console.log(`尝试切换到文件: ${lastFile.path}`);

                        // 记录切换文件的状态，以便在页面刷新后恢复
                        sessionStorage.setItem('switching_file', JSON.stringify({
                            path: lastFile.path,
                            timestamp: new Date().getTime()
                        }));

                        // 使用API方式切换文件
                        const result = await switchToFile(lastFile.path);

                        resolve(true);
                    } catch (error) {
                        console.error('切换文件失败:', error);
                        showMessage('切换文件失败: ' + error.message, 'error');

                        // 清除切换状态，避免无限循环
                        sessionStorage.removeItem('switching_file');

                        resolve(false);
                    }
                },
                () => {
                    resolve(false);
                }
            );
        });
    } catch (error) {
        console.error('加载上次文件失败:', error);
        showMessage('加载上次文件失败: ' + error.message, 'error');
        return false;
    }
}

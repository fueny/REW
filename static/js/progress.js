// progress.js - 学习进度管理

// 自动保存当前学习进度
function autoSaveProgress() {
    // 将当前卡片索引添加到历史记录
    addCardToHistory(currentCardIndex);
    return true;
}

// 自动加载上次学习进度
async function autoLoadProgress() {
    try {
        // 从API获取历史记录
        const response = await fetchHistory();
        const history = response.history || {};

        // 如果有历史记录，找到最近的一条
        if (Object.keys(history).length > 0) {
            // 获取最新的日期
            const dates = Object.keys(history).sort().reverse();
            const latestDate = dates[0];

            // 获取该日期下最新的记录（最后一条）
            const latestRecords = history[latestDate];
            if (latestRecords && latestRecords.length > 0) {
                const latestCardIndex = latestRecords[latestRecords.length - 1];

                // 跳转到最近浏览的卡片
                jumpToCard(latestCardIndex);
                return true;
            }
        }

        // 如果没有历史记录，显示第一张卡片
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
                    // 切换到上次使用的文件
                    const result = await switchToFile(lastFile.path);
                    resolve(result);
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

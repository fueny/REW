// archive.js - 学习历史功能

// 显示学习历史
async function displayLearningHistory() {
    try {
        // 从API获取历史记录
        const response = await fetchHistory();
        const history = response.history || {};

        // 更新学习历史显示
        updateLearningHistoryDisplay(history);
        return true;
    } catch (error) {
        console.error('获取学习历史失败:', error);
        showMessage('获取学习历史失败: ' + error.message, 'error');
        return false;
    }
}

// 跳转到历史记录中的特定卡片
async function jumpToHistoryCard(cardIndex) {
    try {
        // 跳转到指定卡片
        jumpToCard(cardIndex);

        // 更新历史记录显示
        await loadAndUpdateHistoryDisplay();

        return true;
    } catch (error) {
        console.error('跳转到历史卡片失败:', error);
        showMessage('跳转到历史卡片失败: ' + error.message, 'error');
        return false;
    }
}

// 加载并更新学习历史显示
async function loadAndUpdateArchivesDisplay() {
    // 从API获取历史记录
    const response = await fetchHistory();
    const history = response.history || {};

    // 更新显示
    updateLearningHistoryDisplay(history);
}

// 更新学习历史显示
function updateLearningHistoryDisplay(history = {}) {
    const archivesContainer = document.getElementById('archives-container');

    // 清空容器
    archivesContainer.innerHTML = '';

    // 如果没有历史记录，显示提示
    if (Object.keys(history).length === 0) {
        const emptyMessage = document.createElement('div');
        emptyMessage.className = 'archives-empty';
        emptyMessage.textContent = '暂无学习历史';
        archivesContainer.appendChild(emptyMessage);
        return;
    }

    // 按日期排序（从新到旧）
    const dates = Object.keys(history).sort().reverse();

    // 为每个日期创建一个历史记录组
    dates.forEach(date => {
        // 创建日期标题
        const dateHeader = document.createElement('div');
        dateHeader.className = 'history-date-header';

        // 格式化日期
        const formattedDate = formatDateFromISOString(date);
        dateHeader.textContent = formattedDate;

        // 创建该日期的历史记录容器
        const dateHistoryContainer = document.createElement('div');
        dateHistoryContainer.className = 'history-date-content';

        // 获取该日期的历史记录
        const dateHistory = history[date];

        // 添加该日期的所有历史记录
        dateHistory.forEach(cardIndex => {
            if (cardIndex >= 0 && cardIndex < cardsData.length) {
                const card = cardsData[cardIndex];
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';

                // 如果是当前卡片，添加active类
                if (cardIndex === currentCardIndex) {
                    historyItem.classList.add('active');
                }

                // 设置历史记录项的内容
                historyItem.textContent = `${cardIndex + 1}. ${card["单词"]}`;

                // 添加点击事件，点击时跳转到对应的卡片
                historyItem.addEventListener('click', () => {
                    jumpToHistoryCard(cardIndex);
                });

                // 将历史记录项添加到容器
                dateHistoryContainer.appendChild(historyItem);
            }
        });

        // 将日期标题和历史记录容器添加到主容器
        archivesContainer.appendChild(dateHeader);
        archivesContainer.appendChild(dateHistoryContainer);
    });
}

// 格式化ISO日期字符串
function formatDateFromISOString(isoString) {
    const date = new Date(isoString);
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${year}.${month}.${day}`;
}

// 初始化学习历史功能
async function initArchives() {
    // 从API加载历史记录
    await loadAndUpdateArchivesDisplay();
}

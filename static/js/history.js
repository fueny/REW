// history.js - 历史记录功能

// 添加卡片到历史记录
async function addCardToHistory(index) {
    // 调用API添加历史记录
    await addToHistory(index);

    // 更新显示
    await loadAndUpdateHistoryDisplay();
}

// 加载并更新历史记录显示
async function loadAndUpdateHistoryDisplay() {
    // 从API获取历史记录
    const response = await fetchHistory();
    viewHistory = response.history || {};

    // 更新显示
    updateHistoryDisplay();
}

// 更新历史记录显示
function updateHistoryDisplay() {
    const historyContainer = document.getElementById('history-container');

    // 清空容器
    historyContainer.innerHTML = '';

    // 如果没有历史记录，显示提示
    if (Object.keys(viewHistory).length === 0) {
        const emptyMessage = document.createElement('div');
        emptyMessage.className = 'history-empty';
        emptyMessage.textContent = '暂无浏览历史';
        historyContainer.appendChild(emptyMessage);
        return;
    }

    // 按日期排序（从新到旧）
    const sortedDates = Object.keys(viewHistory).sort().reverse();

    // 为每个日期创建一个可折叠部分
    sortedDates.forEach(date => {
        // 创建日期容器
        const dateContainer = document.createElement('div');
        dateContainer.className = 'history-date-container';

        // 创建日期标题（可点击折叠/展开）
        const dateHeader = document.createElement('div');
        dateHeader.className = 'history-date-header';

        // 格式化日期显示（YYYY-MM-DD 转为 YYYY.MM.DD）
        const formattedDate = date.replace(/-/g, '.');

        // 添加折叠/展开图标
        const expandIcon = document.createElement('i');
        expandIcon.className = 'fas fa-chevron-down';
        dateHeader.appendChild(expandIcon);

        // 添加日期文本
        const dateText = document.createElement('span');
        dateText.textContent = formattedDate;

        // 添加日期图标
        const dateIcon = document.createElement('i');
        dateIcon.className = 'fas fa-calendar-day';
        dateIcon.style.marginRight = '8px';

        // 将图标和文本添加到日期标题
        dateText.prepend(dateIcon);
        dateHeader.appendChild(dateText);

        // 创建该日期的历史记录容器（默认展开）
        const dateHistoryContainer = document.createElement('div');
        dateHistoryContainer.className = 'history-date-content';

        // 添加该日期的所有历史记录
        viewHistory[date].forEach((cardIndex) => {
            if (cardIndex >= 0 && cardIndex < cardsData.length) {
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';

                // 如果是当前卡片，添加active类
                if (cardIndex === currentCardIndex) {
                    historyItem.classList.add('active');
                }

                // 设置历史记录项的内容
                const card = cardsData[cardIndex];

                // 创建单词编号
                const wordNumber = document.createElement('span');
                wordNumber.className = 'word-number';
                wordNumber.textContent = `${cardIndex + 1}.`;
                wordNumber.style.marginRight = '8px';
                wordNumber.style.color = '#666';
                wordNumber.style.fontWeight = '500';
                wordNumber.style.flexShrink = '0'; // 防止编号被压缩
                wordNumber.style.minWidth = '25px'; // 设置最小宽度

                // 创建单词文本
                const wordText = document.createElement('span');
                wordText.className = 'word-text';
                wordText.textContent = card["单词"];
                wordText.style.fontWeight = '600';
                wordText.style.wordBreak = 'break-word'; // 确保长单词可以换行
                wordText.style.overflow = 'hidden'; // 防止溢出
                wordText.style.textOverflow = 'ellipsis'; // 超出部分显示省略号
                wordText.style.maxWidth = '180px'; // 设置最大宽度

                // 创建跳转图标
                const jumpIcon = document.createElement('i');
                jumpIcon.className = 'fas fa-arrow-right';
                jumpIcon.style.marginLeft = '5px';
                jumpIcon.style.opacity = '0';
                jumpIcon.style.transition = 'opacity 0.3s ease';
                jumpIcon.style.flexShrink = '0'; // 防止图标被压缩

                // 鼠标悬停时显示跳转图标
                historyItem.addEventListener('mouseenter', () => {
                    jumpIcon.style.opacity = '1';
                });

                historyItem.addEventListener('mouseleave', () => {
                    jumpIcon.style.opacity = '0';
                });

                // 添加所有元素到历史记录项
                historyItem.appendChild(wordNumber);
                historyItem.appendChild(wordText);
                historyItem.appendChild(jumpIcon);

                // 设置历史记录项的样式
                historyItem.style.display = 'flex';
                historyItem.style.alignItems = 'center';
                historyItem.style.justifyContent = 'flex-start'; // 改为左对齐
                historyItem.style.flexWrap = 'wrap'; // 允许内容换行
                historyItem.style.gap = '5px'; // 设置元素间距

                // 添加点击事件，点击时跳转到对应的卡片
                historyItem.addEventListener('click', () => {
                    jumpToCard(cardIndex);
                });

                // 将历史记录项添加到容器
                dateHistoryContainer.appendChild(historyItem);
            }
        });

        // 添加点击事件，点击日期标题时折叠/展开内容
        dateHeader.addEventListener('click', () => {
            // 切换内容的显示/隐藏
            dateHistoryContainer.classList.toggle('collapsed');
            // 切换图标方向
            expandIcon.classList.toggle('fa-chevron-down');
            expandIcon.classList.toggle('fa-chevron-right');
        });

        // 将日期标题和历史记录容器添加到日期容器
        dateContainer.appendChild(dateHeader);
        dateContainer.appendChild(dateHistoryContainer);

        // 将日期容器添加到主容器
        historyContainer.appendChild(dateContainer);
    });
}

// 清除历史记录
async function clearHistoryRecords() {
    // 调用API清除历史记录
    const response = await clearHistory();

    if (response.success) {
        // 清空本地历史记录
        viewHistory = {};
        updateHistoryDisplay();
        showMessage('历史记录已清除', 'success');
    }
}

// 初始化历史记录
async function initHistory() {
    // 从API加载历史记录
    await loadAndUpdateHistoryDisplay();
}

// wordblock.js - 词汇块功能

// 初始化词汇块
async function initWordBlocks() {
    // 生成词汇块
    generateWordBlocks();

    // 初始化词汇弹出窗口关闭按钮事件
    initVocabularyModalEvents();
}

// 生成词汇块
function generateWordBlocks() {
    const wordblockContainer = document.getElementById('wordblock-container');

    // 清空容器
    wordblockContainer.innerHTML = '';

    // 如果没有卡片数据，显示提示
    if (!cardsData || cardsData.length === 0) {
        const emptyMessage = document.createElement('div');
        emptyMessage.className = 'wordblock-empty';
        emptyMessage.textContent = '暂无词汇数据';
        wordblockContainer.appendChild(emptyMessage);
        return;
    }

    // 计算需要多少个词汇块
    const totalCards = cardsData.length;
    const blocksCount = Math.ceil(totalCards / 100);

    // 创建词汇块容器
    const blocksContainer = document.createElement('div');
    blocksContainer.className = 'word-blocks-container';

    // 生成每个词汇块
    for (let i = 0; i < blocksCount; i++) {
        const startIndex = i * 100;
        const endIndex = Math.min((i + 1) * 100 - 1, totalCards - 1);

        // 创建词汇块
        const block = document.createElement('div');
        block.className = 'word-block';

        // 设置词汇块文本
        block.textContent = `${startIndex + 1}-${endIndex + 1}`;

        // 添加点击事件，显示词汇弹出窗口
        block.addEventListener('click', (event) => {
            event.preventDefault(); // 防止默认行为
            showVocabularyModal(startIndex, endIndex);
        });

        // 添加触摸事件，增强移动端体验
        block.addEventListener('touchstart', () => {
            block.style.opacity = '0.8'; // 触摸时的视觉反馈
        });

        block.addEventListener('touchend', () => {
            block.style.opacity = '1'; // 恢复正常状态
        });

        // 将词汇块添加到容器
        blocksContainer.appendChild(block);
    }

    // 将词汇块容器添加到词汇块容器
    wordblockContainer.appendChild(blocksContainer);
}

// 显示词汇弹出窗口
function showVocabularyModal(startIndex, endIndex) {
    // 获取弹出窗口元素
    const modal = document.getElementById('vocabulary-modal');
    const modalTitle = document.getElementById('vocabulary-modal-title');
    const listContainer = document.getElementById('vocabulary-list-container');

    // 设置标题
    modalTitle.textContent = `词汇列表 (${startIndex + 1}-${endIndex + 1})`;

    // 清空列表容器
    listContainer.innerHTML = '';

    // 生成词汇列表
    for (let i = startIndex; i <= endIndex && i < cardsData.length; i++) {
        const card = cardsData[i];

        // 创建词汇项
        const item = document.createElement('div');
        item.className = 'vocabulary-item';

        // 创建序号元素
        const number = document.createElement('span');
        number.className = 'vocabulary-number';
        number.textContent = `${i + 1}.`;

        // 创建单词元素
        const word = document.createElement('span');
        word.className = 'vocabulary-word';
        word.textContent = card["单词"];

        // 创建音标元素
        const phonetic = document.createElement('span');
        phonetic.className = 'vocabulary-phonetic';
        phonetic.textContent = card["音标"] ? `[${card["音标"]}]` : '';

        // 将元素添加到词汇项
        item.appendChild(number);
        item.appendChild(word);
        item.appendChild(phonetic);

        // 添加点击事件，点击时跳转到对应的卡片
        item.addEventListener('click', (event) => {
            event.preventDefault(); // 防止默认行为
            // 关闭弹出窗口
            modal.classList.remove('active');
            // 跳转到对应卡片
            jumpToCard(i);
        });

        // 添加触摸事件，增强移动端体验
        item.addEventListener('touchstart', () => {
            item.style.backgroundColor = '#e9ecef'; // 触摸时的视觉反馈
        });

        item.addEventListener('touchend', () => {
            item.style.backgroundColor = '#f8f9fa'; // 恢复正常状态
        });

        // 将词汇项添加到列表容器
        listContainer.appendChild(item);
    }

    // 显示弹出窗口
    modal.classList.add('active');
}

// 初始化词汇弹出窗口事件
function initVocabularyModalEvents() {
    // 获取弹出窗口元素
    const modal = document.getElementById('vocabulary-modal');
    const closeBtn = document.querySelector('.vocabulary-modal-close');

    // 添加关闭按钮事件
    closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    // 点击弹出窗口背景关闭
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.classList.remove('active');
        }
    });
}
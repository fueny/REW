// card.js - 卡片显示和导航功能

// 显示指定索引的卡片
function displayCard(index) {
    // 获取DOM元素
    const cardNumberEl = document.getElementById('card-number');
    const cardWordEl = document.getElementById('card-word');
    const cardPhoneticEl = document.getElementById('card-phonetic');
    const cardMeaningEl = document.getElementById('card-meaning');
    const cardSplitEl = document.getElementById('card-split');
    const cardSynthesisEl = document.getElementById('card-synthesis');
    const cardAssociationEl = document.getElementById('card-association');
    const cardDetailsEl = document.getElementById('card-details');
    const toggleDetailsBtn = document.getElementById('toggle-details-btn');
    const currentPositionEl = document.getElementById('current-position');
    const totalCardsEl = document.getElementById('total-cards');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');

    if (totalCards === 0) {
        // 处理没有卡片的情况
        cardNumberEl.textContent = "N/A";
        cardWordEl.textContent = "无卡片";
        cardPhoneticEl.textContent = "";
        cardMeaningEl.textContent = "请检查 vocabulary.xlsx 文件是否存在且格式正确。";
        cardSplitEl.textContent = "";
        cardSynthesisEl.textContent = "";
        cardAssociationEl.textContent = "";
        currentPositionEl.textContent = "0";
        totalCardsEl.textContent = "0";
        // 禁用按钮
        prevBtn.disabled = true;
        nextBtn.disabled = true;
        toggleDetailsBtn.disabled = true;
        return;
    }

    // 确保索引有效
    index = (index + totalCards) % totalCards;
    const card = cardsData[index];

    // 更新基本信息
    cardNumberEl.textContent = card["编号"] || (index + 1); // 如果没有编号，使用索引+1
    cardWordEl.textContent = card["单词"];
    cardPhoneticEl.textContent = card["音标"];

    // 更新详细信息
    cardMeaningEl.textContent = card["释义"];
    cardSplitEl.textContent = card["拆分"];
    cardSynthesisEl.textContent = card["综合法"];
    cardAssociationEl.textContent = card["联想法"];

    // 根据全局状态设置详细信息的显示/隐藏
    if (detailsVisible) {
        cardDetailsEl.classList.remove("hidden");
        cardDetailsEl.classList.add("visible");
        toggleDetailsBtn.textContent = "隐藏详细信息";
        toggleDetailsBtn.classList.add("details-visible");
    } else {
        cardDetailsEl.classList.remove("visible");
        cardDetailsEl.classList.add("hidden");
        toggleDetailsBtn.textContent = "显示详细信息";
        toggleDetailsBtn.classList.remove("details-visible");
    }

    // 更新位置信息
    currentPositionEl.textContent = index + 1;
    totalCardsEl.textContent = totalCards;

    // 启用按钮
    prevBtn.disabled = false;
    nextBtn.disabled = false;
    toggleDetailsBtn.disabled = false;
}

// 切换详细信息的显示/隐藏
function toggleDetails() {
    const cardDetailsEl = document.getElementById('card-details');
    const toggleDetailsBtn = document.getElementById('toggle-details-btn');

    detailsVisible = !detailsVisible;

    if (detailsVisible) {
        // 先移除隐藏类，然后添加可见类（触发动画）
        cardDetailsEl.classList.remove("hidden");
        // 使用setTimeout确保DOM更新后再添加visible类，以触发过渡动画
        setTimeout(() => {
            cardDetailsEl.classList.add("visible");
        }, 10);
        toggleDetailsBtn.textContent = "隐藏详细信息";
        toggleDetailsBtn.classList.add("details-visible");

        // 添加动画效果到详情项
        const detailItems = cardDetailsEl.querySelectorAll('.detail-item');
        detailItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            setTimeout(() => {
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
                item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            }, 100 + index * 100); // 错开动画时间
        });
    } else {
        cardDetailsEl.classList.remove("visible");
        // 等待过渡动画完成后再添加hidden类
        setTimeout(() => {
            cardDetailsEl.classList.add("hidden");
        }, 300); // 与CSS中的过渡时间匹配
        toggleDetailsBtn.textContent = "显示详细信息";
        toggleDetailsBtn.classList.remove("details-visible");
    }
}

// 移动到上一张卡片
function prevCard() {
    currentCardIndex = (currentCardIndex - 1 + totalCards) % totalCards;
    displayCard(currentCardIndex);
    addCardToHistory(currentCardIndex);
}

// 移动到下一张卡片
function nextCard() {
    currentCardIndex = (currentCardIndex + 1) % totalCards;
    displayCard(currentCardIndex);
    addCardToHistory(currentCardIndex);
}

// 跳转到指定索引的卡片
function jumpToCard(index) {
    currentCardIndex = index;
    displayCard(currentCardIndex);
    addCardToHistory(currentCardIndex);
}

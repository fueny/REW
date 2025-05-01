// ui.js - UI相关功能

// 显示消息提示
function showMessage(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');

    // 创建提示元素
    const alertElement = document.createElement('div');
    alertElement.className = `alert ${type}`; // 使用正确的类名格式
    alertElement.textContent = message;

    // 添加关闭按钮
    const closeButton = document.createElement('span');
    closeButton.className = 'alert-close';
    closeButton.innerHTML = '&times;';
    closeButton.addEventListener('click', () => {
        alertContainer.removeChild(alertElement);
    });

    alertElement.appendChild(closeButton);

    // 添加到容器
    alertContainer.appendChild(alertElement);

    // 自动关闭（5秒后）
    setTimeout(() => {
        if (alertElement.parentNode === alertContainer) {
            alertContainer.removeChild(alertElement);
        }
    }, 5000);
}

// 显示确认对话框
function showConfirmDialog(title, message, onConfirm, onCancel) {
    const modal = document.getElementById('custom-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const confirmBtn = document.getElementById('modal-confirm-btn');
    const cancelBtn = document.getElementById('modal-cancel-btn');

    // 设置对话框内容
    modalTitle.textContent = title;
    modalMessage.textContent = message;

    // 显示对话框
    modal.style.display = 'flex';

    // 设置确认按钮事件
    const confirmHandler = () => {
        closeModal();
        if (onConfirm) onConfirm();
    };

    // 设置取消按钮事件
    const cancelHandler = () => {
        closeModal();
        if (onCancel) onCancel();
    };

    // 移除旧的事件监听器
    confirmBtn.replaceWith(confirmBtn.cloneNode(true));
    cancelBtn.replaceWith(cancelBtn.cloneNode(true));

    // 获取新的按钮引用
    const newConfirmBtn = document.getElementById('modal-confirm-btn');
    const newCancelBtn = document.getElementById('modal-cancel-btn');

    // 添加新的事件监听器
    newConfirmBtn.addEventListener('click', confirmHandler);
    newCancelBtn.addEventListener('click', cancelHandler);

    // 添加关闭按钮事件
    const closeBtn = document.querySelector('.modal-close');
    closeBtn.addEventListener('click', cancelHandler);

    // 点击模态框背景关闭
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            cancelHandler();
        }
    });
}

// 关闭模态对话框
function closeModal() {
    const modal = document.getElementById('custom-modal');
    modal.style.display = 'none';
}

// 切换移动端菜单
function toggleMobileMenu() {
    const leftSidebar = document.querySelector('.left-sidebar');

    // 切换左侧边栏的显示/隐藏
    leftSidebar.classList.toggle('mobile-visible');

    // 如果右侧边栏是可见的，隐藏它
    const rightSidebar = document.querySelector('.right-sidebar');
    if (rightSidebar.classList.contains('mobile-visible')) {
        rightSidebar.classList.remove('mobile-visible');
    }
}

// 切换移动端历史记录
function toggleMobileHistory() {
    const rightSidebar = document.querySelector('.right-sidebar');

    // 切换右侧边栏的显示/隐藏
    rightSidebar.classList.toggle('mobile-visible');

    // 如果左侧边栏是可见的，隐藏它
    const leftSidebar = document.querySelector('.left-sidebar');
    if (leftSidebar.classList.contains('mobile-visible')) {
        leftSidebar.classList.remove('mobile-visible');
    }
}

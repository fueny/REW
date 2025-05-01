// core.js - 核心功能和初始化

// 全局变量
let currentCardIndex = 0;
let totalCards = 0;
let detailsVisible = false; // 详细信息显示状态
let viewHistory = {}; // 历史记录对象: { "2025-04-29": [indices] }

// 初始化函数
async function initApp() {
    // 设置卡片总数
    totalCards = cardsData.length;

    // 初始化事件监听器
    initEventListeners();

    if (totalCards > 0) {
        // 自动加载上次的学习进度
        await autoLoadProgress();

        // 初始化历史记录
        await initHistory();

        // 初始化学习历史显示
        await initArchives();
    } else {
        // 处理没有加载卡片数据的情况
        displayCard(0); // 显示在displayCard中设置的错误信息
    }

    // 显示当前文件信息
    document.querySelector('.current-file-name').textContent = currentFile.display_name;

    // 检查是否有切换文件的会话存储
    handleFileSwitchingState();
}

// 初始化事件监听器
function initEventListeners() {
    // 卡片导航按钮
    document.getElementById('prev-btn').addEventListener('click', () => {
        currentCardIndex = (currentCardIndex - 1 + totalCards) % totalCards; // 循环到最后一张
        displayCard(currentCardIndex);
        autoSaveProgress(); // 自动保存进度
    });

    document.getElementById('next-btn').addEventListener('click', () => {
        currentCardIndex = (currentCardIndex + 1) % totalCards; // 循环到第一张
        displayCard(currentCardIndex);
        autoSaveProgress(); // 自动保存进度
    });

    // 显示/隐藏详细信息按钮
    document.getElementById('toggle-details-btn').addEventListener('click', () => {
        toggleDetails();
    });

    // 切换文件按钮
    document.getElementById('switch-file-btn').addEventListener('click', () => {
        toggleFileList();
    });

    // 加载上次文件按钮
    document.getElementById('load-last-file-btn').addEventListener('click', async () => {
        // 手动调用加载上次文件函数
        await manualLoadLastFile();
    });

    // 上传按钮
    document.getElementById('upload-btn').addEventListener('click', () => {
        uploadFile();
    });

    // 自动保存进度
    // 注意：我们不再需要手动保存和加载进度的按钮事件监听器
    // 进度会在浏览卡片时自动保存

    // 移动端菜单按钮
    document.getElementById('mobile-menu-btn').addEventListener('click', () => {
        toggleMobileMenu();
    });

    // 移动端历史按钮
    document.getElementById('mobile-history-btn').addEventListener('click', () => {
        toggleMobileHistory();
    });

    // 模态框关闭按钮
    document.querySelector('.modal-close').addEventListener('click', () => {
        closeModal();
    });

    // 点击文档其他地方时隐藏文件列表
    document.addEventListener('click', (event) => {
        // 如果点击的不是文件列表相关元素，则隐藏文件列表
        if (!event.target.closest('#file-list-container') &&
            !event.target.closest('#switch-file-btn') &&
            !document.getElementById('file-list-container').classList.contains('hidden')) {
            document.getElementById('file-list-container').classList.add('hidden');
        }
    });

    // 检测页面是否是从上传文件后重定向回来的
    window.addEventListener('pageshow', function(event) {
        // 如果是从缓存加载的页面（如浏览器后退），不执行操作
        if (event.persisted) {
            return;
        }

        // 检查URL参数是否包含上传成功的标记
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('upload_success')) {
            // 清除URL参数
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    });
}

// 处理文件切换状态
function handleFileSwitchingState() {
    const switchingFileData = sessionStorage.getItem('switching_file');
    if (switchingFileData) {
        try {
            const fileInfo = JSON.parse(switchingFileData);
            // 清除会话存储
            sessionStorage.removeItem('switching_file');

            // 检查当前文件是否与切换的文件匹配
            if (fileInfo.path !== currentFile.path) {
                // 如果不匹配，可能是切换失败，尝试再次切换
                showMessage('正在重新尝试切换文件...', 'info');
                setTimeout(() => {
                    switchToFile(fileInfo.path);
                }, 500);
            } else {
                // 文件匹配，自动加载该文件的最新进度
                autoLoadProgress().then(loaded => {
                    if (loaded) {
                        showMessage('已自动恢复学习进度', 'success');
                    }
                });
            }
        } catch (error) {
            console.error('解析切换文件数据失败:', error);
        }
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', initApp);

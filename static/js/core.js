// core.js - 核心功能和初始化

// 全局变量
let currentCardIndex = 0;
let totalCards = 0;
let detailsVisible = false; // 详细信息显示状态

// 初始化函数
async function initApp() {
    // 设置卡片总数
    totalCards = cardsData.length;

    // 初始化事件监听器
    initEventListeners();

    if (totalCards > 0) {
        // 自动加载上次的学习进度
        await autoLoadProgress();

        // 初始化词汇块
        await initWordBlocks();
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

    // 移动端词汇块按钮
    document.getElementById('mobile-history-btn').addEventListener('click', () => {
        toggleMobileWordBlocks();
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
            // 显示成功消息
            showMessage('文件上传成功，数据已加载', 'success');

            // 清除URL参数
            window.history.replaceState({}, document.title, window.location.pathname);

            // 检查是否是从上传文件页面返回的
            if (sessionStorage.getItem('file_uploading') === 'true') {
                // 清除标记
                sessionStorage.removeItem('file_uploading');

                // 自动打开文件列表
                document.getElementById('file-list-container').classList.remove('hidden');

                // 刷新文件列表
                loadFileList();

                // 添加一个延迟，确保文件列表已经加载完成
                setTimeout(() => {
                    // 再次刷新文件列表，确保新上传的文件显示出来
                    loadFileList();
                }, 500);
            }
        }
    });
}

// 处理文件切换状态
function handleFileSwitchingState() {
    const switchingFileData = sessionStorage.getItem('switching_file');
    if (switchingFileData) {
        try {
            const fileInfo = JSON.parse(switchingFileData);

            // 检查时间戳，如果超过10秒，则认为是过期的切换请求
            const currentTime = new Date().getTime();
            const timeDiff = currentTime - fileInfo.timestamp;

            // 如果时间差超过10秒，则清除会话存储并不再尝试切换
            if (timeDiff > 10000) {
                console.log('文件切换请求已过期，不再尝试切换');
                sessionStorage.removeItem('switching_file');
                return;
            }

            // 检查是否已经尝试切换次数过多
            const switchAttempts = fileInfo.attempts || 0;
            if (switchAttempts >= 2) {
                console.log('文件切换尝试次数过多，不再尝试切换');
                sessionStorage.removeItem('switching_file');
                showMessage('切换文件失败，请手动选择文件', 'error');
                return;
            }

            // 清除会话存储
            sessionStorage.removeItem('switching_file');

            // 检查当前文件是否与切换的文件匹配
            if (fileInfo.path !== currentFile.path) {
                // 如果不匹配，可能是切换失败，尝试再次切换
                showMessage('正在重新尝试切换文件...', 'info');

                // 使用表单提交方式切换文件，但增加尝试次数
                setTimeout(() => {
                    try {
                        // 更新尝试次数
                        fileInfo.attempts = switchAttempts + 1;
                        fileInfo.timestamp = new Date().getTime();

                        // 保存更新后的信息
                        sessionStorage.setItem('switching_file', JSON.stringify(fileInfo));

                        switchToFile(fileInfo.path);
                    } catch (error) {
                        console.error('重新切换文件失败:', error);
                        showMessage('重新切换文件失败: ' + error.message, 'error');
                        // 清除切换状态，避免无限循环
                        sessionStorage.removeItem('switching_file');
                    }
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
            // 出错时清除会话存储
            sessionStorage.removeItem('switching_file');
        }
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', initApp);

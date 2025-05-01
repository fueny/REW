// api.js - API客户端

// 文件API
async function deleteFile(fileId) {
    try {
        const response = await fetch(`/api/files/${fileId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`删除文件失败: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('删除文件失败:', error);
        showMessage('删除文件失败: ' + error.message, 'error');
        return { success: false };
    }
}

// 历史记录API
async function fetchHistory() {
    try {
        const response = await fetch('/api/history');
        if (!response.ok) {
            throw new Error(`获取历史记录失败: ${response.status} ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('获取历史记录失败:', error);
        showMessage('获取历史记录失败: ' + error.message, 'error');
        return { history: {} };
    }
}

async function addToHistory(cardIndex) {
    try {
        const response = await fetch('/api/history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ card_index: cardIndex })
        });

        if (!response.ok) {
            throw new Error(`添加历史记录失败: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('添加历史记录失败:', error);
        return { success: false };
    }
}

async function clearHistory() {
    try {
        const response = await fetch('/api/history', {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`清除历史记录失败: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('清除历史记录失败:', error);
        showMessage('清除历史记录失败: ' + error.message, 'error');
        return { success: false };
    }
}

// 存档API
async function fetchArchives() {
    try {
        const response = await fetch('/api/archives');
        if (!response.ok) {
            throw new Error(`获取存档列表失败: ${response.status} ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('获取存档列表失败:', error);
        showMessage('获取存档列表失败: ' + error.message, 'error');
        return { archives: [] };
    }
}

async function createArchive(cardIndex, detailsVisible, name = null) {
    try {
        const data = {
            card_index: cardIndex,
            details_visible: detailsVisible
        };

        if (name) {
            data.name = name;
        }

        const response = await fetch('/api/archives', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`创建存档失败: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('创建存档失败:', error);
        showMessage('创建存档失败: ' + error.message, 'error');
        return { success: false };
    }
}

async function fetchArchive(archiveId) {
    try {
        const response = await fetch(`/api/archives/${archiveId}`);
        if (!response.ok) {
            throw new Error(`获取存档失败: ${response.status} ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('获取存档失败:', error);
        showMessage('获取存档失败: ' + error.message, 'error');
        return { archive: null };
    }
}

async function deleteArchive(archiveId) {
    try {
        const response = await fetch(`/api/archives/${archiveId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`删除存档失败: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('删除存档失败:', error);
        showMessage('删除存档失败: ' + error.message, 'error');
        return { success: false };
    }
}

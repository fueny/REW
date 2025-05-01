// storage.js - 会话存储工具

// 生成文件唯一键
function generateFileKey(fileInfo) {
    // 使用文件路径作为唯一标识
    return btoa(fileInfo.path).replace(/[^a-zA-Z0-9]/g, '_');
}

// 获取会话存储项
function getSessionItem(key, defaultValue = null) {
    try {
        const value = sessionStorage.getItem(key);
        return value ? JSON.parse(value) : defaultValue;
    } catch (error) {
        console.error(`获取会话存储项 ${key} 失败:`, error);
        return defaultValue;
    }
}

// 设置会话存储项
function setSessionItem(key, value) {
    try {
        sessionStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (error) {
        console.error(`设置会话存储项 ${key} 失败:`, error);
        return false;
    }
}

// 删除会话存储项
function removeSessionItem(key) {
    try {
        sessionStorage.removeItem(key);
        return true;
    } catch (error) {
        console.error(`删除会话存储项 ${key} 失败:`, error);
        return false;
    }
}

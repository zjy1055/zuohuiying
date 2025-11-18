// 公共JS文件 - 处理登录状态和API调用

// API基础URL
const API_BASE_URL = 'http://localhost:8000';

// 获取本地存储的token
function getToken() {
    return localStorage.getItem('token');
}

// 获取用户角色
function getUserRole() {
    return localStorage.getItem('userRole');
}

// 保存登录信息
function saveLoginInfo(token, role) {
    localStorage.setItem('token', token);
    localStorage.setItem('userRole', role);
}

// 清除登录信息
function clearLoginInfo() {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userInfo');
}

// 获取用户名
function getUsername() {
    const userInfo = localStorage.getItem('userInfo');
    if (userInfo) {
        try {
            const parsedInfo = JSON.parse(userInfo);
            return parsedInfo.username || parsedInfo.name || null;
        } catch (e) {
            console.error('解析用户信息失败:', e);
        }
    }
    return null;
}

// 检查是否已登录
function isLoggedIn() {
    return !!getToken();
}

// 验证登录状态，如果未登录则跳转
function checkLogin() {
    if (!isLoggedIn()) {
        window.location.href = '../index.html';
        return false;
    }
    return true;
}

// 验证角色权限
function checkRole(expectedRole) {
    const role = getUserRole();
    if (role !== expectedRole) {
        alert('没有权限访问此页面');
        window.location.href = '../index.html';
        return false;
    }
    return true;
}

// 声明全局apiClient变量
let apiClient;

// 初始化apiClient函数
function initApiClient() {
    if (typeof axios === 'undefined') {
        console.error('axios未加载，无法初始化apiClient');
        return;
    }
    
    // 创建带token的axios实例
    apiClient = axios.create({
        baseURL: API_BASE_URL,
        headers: {
            'Content-Type': 'application/json'
        }
    });

    // 请求拦截器 - 添加token
    apiClient.interceptors.request.use(config => {
        const token = getToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    });

    // 响应拦截器 - 处理错误
    apiClient.interceptors.response.use(
        response => response,
        error => {
            if (error.response && error.response.status === 401) {
                // Token过期或无效
                alert('登录已过期，请重新登录');
                clearLoginInfo();
                window.location.href = '../index.html';
            } else if (error.response && error.response.data) {
                alert(error.response.data.message || '请求失败');
            } else {
                alert('网络错误，请稍后重试');
            }
            return Promise.reject(error);
        }
    );
    
    console.log('apiClient初始化成功');
}

// 处理URL参数
function getUrlParams() {
    const params = {};
    const queryString = window.location.search.substring(1);
    const pairs = queryString.split('&');
    
    for (let i = 0; i < pairs.length; i++) {
        const pair = pairs[i].split('=');
        params[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1] || '');
    }
    
    return params;
}

// 退出登录
function logout() {
    clearLoginInfo();
    window.location.href = '../index.html';
}

// 页面加载时处理URL参数
window.addEventListener('DOMContentLoaded', () => {
    // 初始化apiClient
    initApiClient();
    // 处理登录按钮
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
    
    // 自动设置登录页的角色选择
    const roleParam = getUrlParams().role;
    if (roleParam && document.getElementById('role')) {
        document.getElementById('role').value = roleParam;
    }
});
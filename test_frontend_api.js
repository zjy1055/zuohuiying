// 这是一个模拟前端API调用的Node.js脚本
// 运行: node test_frontend_api.js

const axios = require('axios');

// 模拟localStorage
const localStorage = {
  _data: {},
  getItem(key) {
    return this._data[key] || null;
  },
  setItem(key, value) {
    this._data[key] = value;
  },
  removeItem(key) {
    delete this._data[key];
  }
};

// 模拟前端apiClient
class ApiClient {
  constructor() {
    this.client = axios.create({
      baseURL: 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // 请求拦截器 - 添加token
    this.client.interceptors.request.use(config => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      console.log('请求配置:', { url: config.url, headers: config.headers });
      return config;
    });

    // 响应拦截器
    this.client.interceptors.response.use(
      response => response,
      error => {
        console.error('响应错误:', error.response ? error.response.status : error.message);
        if (error.response && error.response.data) {
          console.error('错误详情:', error.response.data);
        }
        return Promise.reject(error);
      }
    );
  }

  async post(url, data) {
    return this.client.post(url, data);
  }

  async get(url) {
    return this.client.get(url);
  }
}

// 模拟登录函数
async function login(username, password, role) {
  try {
    const loginClient = axios.create({
      baseURL: 'http://localhost:8000'
    });
    
    // 使用表单数据登录
    const response = await loginClient.post('/auth/login', {
      username,
      password,
      scope: role
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    
    if (response.status === 200) {
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('userRole', role);
      localStorage.setItem('userInfo', JSON.stringify({ username }));
      console.log('登录成功！Token已保存到localStorage');
      return access_token;
    }
  } catch (error) {
    console.error('登录失败:', error.message);
    if (error.response) {
      console.error('登录响应状态:', error.response.status);
      console.error('登录响应数据:', error.response.data);
    }
  }
}

// 测试前端流程
async function testFrontendFlow() {
  console.log('开始模拟前端API调用流程...');
  
  // 1. 登录
  console.log('\n1. 测试登录...');
  await login('test_student', '123456', 'student');
  
  // 2. 初始化apiClient
  console.log('\n2. 初始化apiClient...');
  const apiClient = new ApiClient();
  
  // 3. 测试文书预约
  console.log('\n3. 测试文书预约API调用...');
  try {
    const response = await apiClient.post('/student/document/reserve', {
      teacher_id: 2,
      document_count: 1,
      document_type: 'personal_statement'
    });
    
    console.log('预约成功！状态码:', response.status);
    console.log('预约响应:', response.data);
  } catch (error) {
    console.error('预约失败:', error.message);
  }
  
  // 4. 测试GET请求
  console.log('\n4. 测试文书列表GET请求...');
  try {
    const response = await apiClient.get('/student/document/list');
    console.log('获取列表成功！状态码:', response.status);
    console.log('列表数据:', response.data);
  } catch (error) {
    console.error('获取列表失败:', error.message);
  }
}

// 执行测试
testFrontendFlow().then(() => {
  console.log('\n测试完成！');
}).catch(err => {
  console.error('测试出错:', err);
});
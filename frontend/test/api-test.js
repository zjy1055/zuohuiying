// API测试脚本 - 用于验证前端与后端的交互功能

// API基础URL
const API_BASE_URL = 'http://localhost:8000';

// 测试用例
const testCases = [
    {
        id: 1,
        name: '测试登录功能',
        description: '验证用户登录API是否正常工作',
        endpoint: '/auth/login',
        method: 'POST',
        data: {
            username: 'test_teacher',
            password: 'test123',
            role: 'teacher'
        },
        expectedStatusCode: 200,
        expectedDataContains: ['token', 'user_id', 'username']
    },
    {
        id: 2,
        name: '测试获取教师个人信息',
        description: '验证获取教师个人信息API是否正常工作',
        endpoint: '/teacher/profile',
        method: 'GET',
        requiresAuth: true,
        role: 'teacher',
        expectedStatusCode: 200,
        expectedDataContains: ['username', 'name', 'email', 'phone']
    },
    {
        id: 3,
        name: '测试获取学校列表',
        description: '验证获取学校列表API是否正常工作',
        endpoint: '/teacher/school/list?page=1&page_size=10',
        method: 'GET',
        requiresAuth: true,
        role: 'teacher',
        expectedStatusCode: 200,
        expectedDataContains: ['schools', 'total_pages', 'current_page']
    },
    {
        id: 4,
        name: '测试获取学生统计数据',
        description: '验证获取学生统计数据API是否正常工作',
        endpoint: '/teacher/statistics/student',
        method: 'GET',
        requiresAuth: true,
        role: 'teacher',
        expectedStatusCode: 200,
        expectedDataContains: ['total_students', 'gender_ratio', 'avg_scores']
    }
];

// 测试结果
let testResults = [];
let authToken = null;
let currentRole = null;

// 执行所有测试
async function runAllTests() {
    console.log('开始执行API测试...');
    console.log('=============================================');
    
    // 按顺序执行测试用例
    for (const test of testCases) {
        console.log(`\n测试用例 ${test.id}: ${test.name}`);
        console.log(`描述: ${test.description}`);
        
        try {
            // 检查是否需要认证
            if (test.requiresAuth) {
                if (!authToken) {
                    // 尝试使用测试账号登录
                    await loginForTest(test.role || 'teacher');
                } else if (currentRole !== test.role) {
                    // 如果需要切换角色，重新登录
                    await loginForTest(test.role);
                }
            }
            
            // 执行测试
            const result = await executeTest(test);
            testResults.push(result);
            
            // 输出测试结果
            if (result.passed) {
                console.log('✓ 测试通过');
            } else {
                console.log('✗ 测试失败');
                console.log(`  错误信息: ${result.errorMessage}`);
            }
        } catch (error) {
            console.log('✗ 测试执行异常');
            console.log(`  异常信息: ${error.message}`);
            testResults.push({
                id: test.id,
                name: test.name,
                passed: false,
                errorMessage: error.message
            });
        }
        
        console.log('---------------------------------------------');
    }
    
    // 输出总体测试结果
    console.log('\n测试总结:');
    console.log('=============================================');
    
    const passedTests = testResults.filter(r => r.passed).length;
    const totalTests = testResults.length;
    const passRate = (passedTests / totalTests * 100).toFixed(2);
    
    console.log(`通过测试: ${passedTests}/${totalTests} (${passRate}%)`);
    
    if (passedTests < totalTests) {
        console.log('\n失败的测试:');
        testResults.forEach(result => {
            if (!result.passed) {
                console.log(`- ${result.name}: ${result.errorMessage}`);
            }
        });
    }
    
    return {
        passedTests,
        totalTests,
        passRate,
        details: testResults
    };
}

// 执行单个测试
async function executeTest(test) {
    const url = `${API_BASE_URL}${test.endpoint}`;
    const options = {
        method: test.method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    // 如果需要认证，添加认证头
    if (test.requiresAuth && authToken) {
        options.headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    // 添加请求体
    if (test.method === 'POST' || test.method === 'PUT') {
        options.body = JSON.stringify(test.data);
    }
    
    try {
        // 发送请求
        const response = await fetch(url, options);
        const data = await response.json();
        
        // 检查状态码
        if (response.status !== test.expectedStatusCode) {
            return {
                id: test.id,
                name: test.name,
                passed: false,
                errorMessage: `预期状态码 ${test.expectedStatusCode}，实际得到 ${response.status}`,
                actualStatusCode: response.status,
                responseData: data
            };
        }
        
        // 检查返回数据是否包含预期字段
        for (const field of test.expectedDataContains) {
            if (!data.hasOwnProperty(field)) {
                return {
                    id: test.id,
                    name: test.name,
                    passed: false,
                    errorMessage: `返回数据缺少预期字段: ${field}`,
                    actualStatusCode: response.status,
                    responseData: data
                };
            }
        }
        
        // 对于登录测试，保存token
        if (test.id === 1 && data.token) {
            authToken = data.token;
            currentRole = test.data.role;
        }
        
        return {
            id: test.id,
            name: test.name,
            passed: true,
            actualStatusCode: response.status,
            responseData: data
        };
    } catch (error) {
        return {
            id: test.id,
            name: test.name,
            passed: false,
            errorMessage: `请求执行失败: ${error.message}`
        };
    }
}

// 为测试登录
async function loginForTest(role) {
    const loginData = {
        username: role === 'teacher' ? 'test_teacher' : 'test_student',
        password: 'test123',
        role: role
    };
    
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(loginData)
    });
    
    const data = await response.json();
    
    if (response.status === 200 && data.token) {
        authToken = data.token;
        currentRole = role;
        console.log(`已使用${role === 'teacher' ? '教师' : '学生'}账号登录`);
    } else {
        throw new Error(`无法使用${role === 'teacher' ? '教师' : '学生'}账号登录: ${data.message || '未知错误'}`);
    }
}

// 创建简单的HTML测试报告
function createTestReport(results) {
    const reportContainer = document.createElement('div');
    reportContainer.className = 'container mt-5';
    
    let reportHTML = `
        <h1 class="text-center mb-4">API测试报告</h1>
        <div class="card mb-4">
            <div class="card-header bg-primary text-white">
                <h3 class="mb-0">测试结果汇总</h3>
            </div>
            <div class="card-body">
                <div class="row text-center">
                    <div class="col-md-4">
                        <div class="h5">总测试数</div>
                        <div class="display-4 font-weight-bold">${results.totalTests}</div>
                    </div>
                    <div class="col-md-4">
                        <div class="h5">通过测试</div>
                        <div class="display-4 font-weight-bold text-success">${results.passedTests}</div>
                    </div>
                    <div class="col-md-4">
                        <div class="h5">通过率</div>
                        <div class="display-4 font-weight-bold ${results.passRate >= 80 ? 'text-success' : 'text-danger'}">${results.passRate}%</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h3 class="mb-0">测试详情</h3>
            </div>
            <div class="card-body">
                <table class="table table-bordered">
                    <thead class="thead-light">
                        <tr>
                            <th>ID</th>
                            <th>测试名称</th>
                            <th>状态</th>
                            <th>错误信息</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    results.details.forEach(result => {
        reportHTML += `
            <tr class="${result.passed ? 'table-success' : 'table-danger'}">
                <td>${result.id}</td>
                <td>${result.name}</td>
                <td>${result.passed ? '通过' : '失败'}</td>
                <td>${result.errorMessage || '-'}</td>
            </tr>
        `;
    });
    
    reportHTML += `
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    reportContainer.innerHTML = reportHTML;
    return reportContainer;
}

// 在浏览器中运行时显示测试报告
if (typeof window !== 'undefined') {
    // 等待页面加载完成
    document.addEventListener('DOMContentLoaded', async () => {
        // 创建加载指示器
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'container mt-5 text-center';
        loadingDiv.innerHTML = `
            <div class="spinner-border" role="status">
                <span class="sr-only">加载中...</span>
            </div>
            <p class="mt-3">正在执行API测试，请稍候...</p>
        `;
        document.body.appendChild(loadingDiv);
        
        // 运行测试
        const results = await runAllTests();
        
        // 移除加载指示器
        document.body.removeChild(loadingDiv);
        
        // 显示测试报告
        const reportContainer = createTestReport(results);
        document.body.appendChild(reportContainer);
    });
}

// 在Node.js环境中运行时导出函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        runAllTests,
        executeTest,
        testCases
    };
}
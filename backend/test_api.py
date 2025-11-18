import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_STUDENT = {
    "username": "test_student",
    "password": "123456",
    "scope": "student"
}
TEST_TEACHER = {
    "username": "test_teacher",
    "password": "123456",
    "scope": "teacher"
}

# 测试结果记录
results = {
    "tests_run": 0,
    "tests_passed": 0,
    "tests_failed": 0,
    "failed_endpoints": [],
    "start_time": datetime.now().isoformat()
}

def test_endpoint(endpoint, method="GET", headers=None, data=None, expected_status=200, description=""):
    """测试单个API端点"""
    url = f"{BASE_URL}{endpoint}"
    results["tests_run"] += 1
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, data=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"不支持的请求方法: {method}")
            return False
        
        success = response.status_code == expected_status
        if success:
            results["tests_passed"] += 1
            print(f"✅ 成功: {endpoint} - {description} (状态码: {response.status_code})")
        else:
            results["tests_failed"] += 1
            error_info = {
                "endpoint": endpoint,
                "description": description,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "response": response.text[:200] + "..." if len(response.text) > 200 else response.text
            }
            results["failed_endpoints"].append(error_info)
            print(f"❌ 失败: {endpoint} - {description} (预期: {expected_status}, 实际: {response.status_code})")
            print(f"  响应: {error_info['response']}")
        
        return success
    except Exception as e:
        results["tests_failed"] += 1
        error_info = {
            "endpoint": endpoint,
            "description": description,
            "error": str(e)
        }
        results["failed_endpoints"].append(error_info)
        print(f"❌ 错误: {endpoint} - {description} (错误: {str(e)})")
        return False

def get_auth_token(credentials):
    """获取认证令牌"""
    print(f"\n正在获取 {credentials['scope']} 的认证令牌...")
    url = f"{BASE_URL}/auth/login"
    
    # 使用x-www-form-urlencoded格式发送数据
    form_data = {
        "username": credentials["username"],
        "password": credentials["password"],
        "scope": credentials["scope"]
    }
    
    try:
        response = requests.post(url, data=form_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ 成功获取 {credentials['scope']} 令牌")
            return token_data["access_token"]
        else:
            print(f"❌ 认证失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 认证请求错误: {str(e)}")
        return None

def run_tests():
    """运行所有API测试"""
    print("="*80)
    print("开始测试后端API")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试基础URL: {BASE_URL}")
    print("="*80)
    
    # 测试公开端点
    print("\n🔍 测试公开端点:")
    test_endpoint("/", description="根路径")
    test_endpoint("/health", description="健康检查")
    
    # 测试认证功能
    print("\n🔍 测试认证功能:")
    student_token = get_auth_token(TEST_STUDENT)
    teacher_token = get_auth_token(TEST_TEACHER)
    
    # 测试学生API（如果获取到token）
    if student_token:
        print("\n🔍 测试学生API:")
        student_headers = {
            "Authorization": f"Bearer {student_token}"
        }
        
        test_endpoint("/student/profile", headers=student_headers, description="获取学生个人信息")
        test_endpoint("/student/success-cases", headers=student_headers, description="获取成功案例")
        test_endpoint("/student/search-schools", headers=student_headers, description="搜索学校")
        test_endpoint("/student/training/list", headers=student_headers, description="查看培训预约列表")
        test_endpoint("/student/document/list", headers=student_headers, description="查看文书预约列表")
    
    # 测试教师API（如果获取到token）
    if teacher_token:
        print("\n🔍 测试教师API:")
        teacher_headers = {
            "Authorization": f"Bearer {teacher_token}"
        }
        
        test_endpoint("/teacher/profile", headers=teacher_headers, description="获取教师个人信息")
        test_endpoint("/teacher/statistics/student", headers=teacher_headers, description="获取学生统计信息")
        test_endpoint("/teacher/school/list", headers=teacher_headers, description="获取学校列表")
    
    # 测试错误情况
    print("\n🔍 测试错误情况:")
    invalid_headers = {"Authorization": "Bearer invalid_token"}
    test_endpoint("/student/profile", headers=invalid_headers, expected_status=401, description="无效令牌访问")
    
    # 汇总测试结果
    results["end_time"] = datetime.now().isoformat()
    print("\n" + "="*80)
    print(f"测试完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总测试数: {results['tests_run']}")
    print(f"通过测试: {results['tests_passed']}")
    print(f"失败测试: {results['tests_failed']}")
    
    if results['failed_endpoints']:
        print("\n❌ 失败的端点详细信息:")
        for i, error in enumerate(results['failed_endpoints'], 1):
            print(f"\n{i}. 端点: {error['endpoint']}")
            print(f"   描述: {error['description']}")
            if 'expected_status' in error:
                print(f"   预期状态: {error['expected_status']}")
                print(f"   实际状态: {error['actual_status']}")
            if 'response' in error:
                print(f"   响应: {error['response']}")
            if 'error' in error:
                print(f"   错误: {error['error']}")
    
    print("="*80)
    
    # 保存测试结果到文件
    with open("api_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("测试结果已保存到 api_test_results.json")
    
    # 如果有测试失败，返回非零退出码
    return 0 if results['tests_failed'] == 0 else 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
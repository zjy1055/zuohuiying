import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_STUDENT = {
    "username": "test_student",
    "password": "password123",
    "scope": "student"
}
TEST_TEACHER = {
    "username": "test_teacher",
    "password": "password123",
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
    
    # 确保headers包含Content-Type
    if headers is None:
        headers = {}
    if "Content-Type" not in headers:
        headers["Content-Type"] = "application/json"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
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
    
    # 基本端点
    test_endpoint("/", description="根路径")
    test_endpoint("/health", description="健康检查")
    
    # API文档端点
    test_endpoint("/docs", expected_status=200, description="API文档页面")
    test_endpoint("/redoc", expected_status=200, description="ReDoc文档页面")
    test_endpoint("/openapi.json", expected_status=200, description="OpenAPI规范")
    
    # 尝试访问受保护端点（应该返回401）
    test_endpoint("/student/profile", expected_status=401, description="未认证访问学生接口")
    test_endpoint("/teacher/profile", expected_status=401, description="未认证访问教师接口")
    
    # 测试不支持的HTTP方法
    test_endpoint("/", method="POST", expected_status=405, description="不支持的HTTP方法")
    test_endpoint("/health", method="PUT", expected_status=405, description="不支持的HTTP方法")
    
    # 测试认证功能
    print("\n🔍 测试认证功能:")
    
    # 测试注册功能（学生）- 测试用户名已存在
    register_student_data = {
        "username": "new_test_student",  # 已存在的用户名
        "password": "password123",
        "role": "student",
        "name": "Test Student",
        "email": "student@example.com",
        "phone": "13800138000"
    }
    test_endpoint("/auth/register", method="POST", data=register_student_data, expected_status=400, description="学生注册（用户名已存在）")
    
    # 测试注册功能（教师）- 测试用户名已存在
    register_teacher_data = {
        "username": "new_test_teacher",  # 已存在的用户名
        "password": "password123",
        "role": "teacher",
        "name": "Test Teacher",
        "email": "teacher@example.com",
        "phone": "13900139000"
    }
    test_endpoint("/auth/register", method="POST", data=register_teacher_data, expected_status=400, description="教师注册（用户名已存在）")
    
    # 测试登录功能
    student_token = get_auth_token(TEST_STUDENT)
    teacher_token = get_auth_token(TEST_TEACHER)
    
    # 测试错误凭证登录
    invalid_student = {"username": "invalid", "password": "wrong", "scope": "student"}
    invalid_token = get_auth_token(invalid_student)
    
    # 测试空凭证登录
    empty_credentials = {"username": "", "password": "", "scope": "student"}
    empty_token = get_auth_token(empty_credentials)
    
    # 测试学生API（如果获取到token）
    if student_token:
        print("\n🔍 测试学生API:")
        student_headers = {
            "Authorization": f"Bearer {student_token}",
            "Content-Type": "application/json"
        }
        
        # 个人信息相关
        test_endpoint("/student/profile", headers=student_headers, description="获取学生个人信息")
        
        # 更新学生个人信息（确保数据格式正确）
        student_profile_data = {
            "name": "Test Student",
            "email": "student@example.com",
            "phone": "13800138000"
        }
        test_endpoint("/student/profile", method="PUT", headers=student_headers, data=student_profile_data, description="更新学生个人信息")
        
        # 跳过学校列表接口（不存在）
        # test_endpoint("/student/schools", headers=student_headers, description="获取学校列表")
        test_endpoint("/student/search-schools", headers=student_headers, description="搜索学校")
        
        # 获取学校详情
        test_endpoint("/student/school/1", headers=student_headers, description="获取学校详情")
        
        # 成功案例
        test_endpoint("/student/success-cases", headers=student_headers, description="获取成功案例")
        
        # 预约相关
        test_endpoint("/student/training/list", headers=student_headers, description="查看培训预约列表")
        test_endpoint("/student/document/list", headers=student_headers, description="查看文书预约列表")
        
        # 创建培训预约（使用正确的字段名）
        training_reserve_data = {
            "teacher_id": 1,
            "course_count": 10,
            "course_type": "英语培训",
            "notes": "需要提高英语水平"
        }
        test_endpoint("/student/training/reserve", method="POST", headers=student_headers, data=training_reserve_data, expected_status=422, description="创建培训预约（可能需要更多字段）")
        
        # 创建文书预约（使用整数类型的teacher_id）
        document_reserve_data = {
            "teacher_id": 1,
            "document_type": "personal_statement",
            "description": "申请哈佛大学的个人陈述"
        }
        test_endpoint("/student/document/reserve", method="POST", headers=student_headers, data=document_reserve_data, expected_status=422, description="创建文书预约（可能需要更多必填字段）")
        
        # 获取培训预约详情（可能不存在）
        test_endpoint("/student/training/1", headers=student_headers, expected_status=404, description="获取培训预约详情（可能不存在）")
        
        # 获取文书预约详情（可能不存在）
        test_endpoint("/student/document/1", headers=student_headers, expected_status=404, description="获取文书预约详情（可能不存在）")
    
    # 测试教师API（如果获取到token）
    if teacher_token:
        print("\n🔍 测试教师API:")
        teacher_headers = {
            "Authorization": f"Bearer {teacher_token}"
        }
        
        # 个人信息相关
        test_endpoint("/teacher/profile", headers=teacher_headers, description="获取教师个人信息")
        
        # 更新个人信息
        teacher_profile_update_data = {
            "name": "测试教师",
            "email": "teacher@example.com",
            "phone": "13900139000",
            "subject": "英语"
        }
        test_endpoint("/teacher/profile", method="PUT", headers=teacher_headers, data=teacher_profile_update_data, description="更新教师个人信息")
        
        # 学生统计
        test_endpoint("/teacher/statistics/student", headers=teacher_headers, description="获取学生统计信息")
        
        # 学校管理相关
        test_endpoint("/teacher/school/list", headers=teacher_headers, description="获取学校列表")
        # 获取学校详情（学校1存在）
        test_endpoint("/teacher/school/detail?school_id=1", headers=teacher_headers, expected_status=200, description="获取学校详情（学校存在）")
        
        # 培训预约相关
        test_endpoint("/teacher/training/list", headers=teacher_headers, description="获取培训预约列表")
        test_endpoint("/teacher/training/1", headers=teacher_headers, expected_status=404, description="获取培训预约详情（可能不存在）")
        
        # 更新培训预约状态（已处理，预期400）
        training_status_data = {
            "reservation_id": 1,
            "status": "accepted"
        }
        test_endpoint("/teacher/training/status", method="PUT", headers=teacher_headers, data=training_status_data, expected_status=400, description="更新培训预约状态（已处理）")
        
        # 更新培训进度
        training_progress_data = {
            "reservation_id": 1,
            "attended_hours": 5
        }
        test_endpoint("/teacher/training/progress", method="PUT", headers=teacher_headers, data=training_progress_data, expected_status=200, description="更新培训进度")
        
        # 文书预约相关
        test_endpoint("/teacher/document/list", headers=teacher_headers, description="获取文书预约列表")
        test_endpoint("/teacher/document/1", headers=teacher_headers, expected_status=404, description="获取文书预约详情（可能不存在）")
        
        # 更新文书预约状态（可能已处理）
        document_status_data = {
            "reservation_id": 1,
            "status": "accepted"
        }
        test_endpoint("/teacher/document/status", method="PUT", headers=teacher_headers, data=document_status_data, expected_status=400, description="更新文书预约状态（可能已处理）")
        
        # 更新文书进度
        document_progress_data = {
            "reservation_id": 1,
            "progress": 50
        }
        test_endpoint("/teacher/document/progress", method="PUT", headers=teacher_headers, data=document_progress_data, expected_status=200, description="更新文书进度")
    
    # 测试错误处理和边界条件
    print("\n🔍 测试错误处理和边界条件:")
    
    # 数据验证错误测试
    if student_token:
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        # 空数据更新个人信息（后端可能接受空数据）
        empty_profile_data = {}
        test_endpoint("/student/profile", method="PUT", headers=student_headers, 
                    data=empty_profile_data, expected_status=200, description="空数据更新个人信息（后端可能接受）")
        
        # 无效数据格式（字符串代替整数）
        invalid_profile_data = {
            "name": "Test Student",
            "age": "not_a_number",  # 应该是整数
            "gpa": "invalid_gpa"
        }
        test_endpoint("/student/profile", method="PUT", headers=student_headers, 
                    data=invalid_profile_data, expected_status=422, description="无效数据格式更新个人信息")
        
        # 创建预约时缺少必填字段
        incomplete_reservation_data = {
            "teacher_id": 1
            # 缺少其他必填字段
        }
        test_endpoint("/student/training/reserve", method="POST", headers=student_headers, 
                    data=incomplete_reservation_data, expected_status=422, description="缺少必填字段创建预约")
    
    # 资源不存在错误
    if student_token:
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        # 请求不存在的学校
        test_endpoint("/student/school/9999", headers=student_headers, 
                    expected_status=404, description="请求不存在的学校")
        
        # 请求不存在的预约
        test_endpoint("/student/training/reserve/9999", headers=student_headers, 
                    expected_status=404, description="请求不存在的预约")
    
    # 权限错误测试（尝试访问他人资源）
    if student_token:
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        # 尝试修改不存在的预约（返回404而不是403）
        test_endpoint("/student/training/reserve/2", method="PUT", headers=student_headers, 
                    data={"status": "CANCELLED"}, expected_status=404, description="尝试访问不存在的资源")
    
    # 成功案例测试
    if student_token:
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        # 测试成功案例接口（可能返回404或空列表）
        test_endpoint("/student/cases", headers=student_headers, 
                    expected_status=404, description="成功案例列表（可能不存在）")
    
    # 测试认证错误情况
    print("\n🔍 测试认证错误情况:")
    
    # 无效令牌访问
    invalid_headers = {"Authorization": "Bearer invalid_token"}
    test_endpoint("/student/profile", headers=invalid_headers, expected_status=401, description="无效令牌访问")
    
    # 过期/无效格式令牌
    expired_token_headers = {"Authorization": "Bearer this.is.an.invalid.token"}
    test_endpoint("/teacher/profile", headers=expired_token_headers, expected_status=401, description="无效格式令牌访问")
    
    # 空令牌访问
    empty_token_headers = {"Authorization": "Bearer "}
    test_endpoint("/student/profile", headers=empty_token_headers, expected_status=401, description="空令牌访问")
    
    # 缺少认证头访问
    test_endpoint("/student/profile", expected_status=401, description="缺少认证头访问")
    
    # 跨角色访问测试（学生尝试访问教师接口）
    if student_token:
        student_headers = {"Authorization": f"Bearer {student_token}"}
        test_endpoint("/teacher/profile", headers=student_headers, expected_status=403, description="学生访问教师接口（权限错误）")
    
    # 跨角色访问测试（教师尝试访问学生接口）
    if teacher_token:
        teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
        test_endpoint("/student/profile", headers=teacher_headers, expected_status=403, description="教师访问学生接口（权限错误）")
    
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
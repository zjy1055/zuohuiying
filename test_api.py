import requests
import json

# 测试登录获取token
def test_login():
    url = 'http://localhost:8000/auth/login'
    # OAuth2PasswordRequestForm期望表单数据，role通过scope传递
    form_data = {
        'username': 'test_student',
        'password': '123456',
        'scope': 'student'  # 角色信息通过scope参数传递
    }
    print(f'登录请求表单数据: {form_data}')
    response = requests.post(url, data=form_data)
    print(f'登录响应状态码: {response.status_code}')
    print(f'登录响应内容: {response.text}')
    
    if response.status_code == 200:
        result = response.json()
        print(f'登录成功！获取到的信息: {result}')
        return result.get('access_token')
    return None

# 测试不同URL路径变体
def test_url_variations(token):
    if not token:
        print('未获取到token，无法测试URL变体')
        return
    
    # 测试各种可能的URL路径变体
    url_variations = [
        'http://localhost:8000/student/document/reserve',        # 原始路径
        'http://localhost:8000/student/document/reserve/',       # 带斜杠
        'http://127.0.0.1:8000/student/document/reserve',        # 使用127.0.0.1
        'http://127.0.0.1:8000/student/document/reserve/'        # 使用127.0.0.1带斜杠
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'teacher_id': 2,
        'document_count': 1,
        'document_type': 'personal_statement'
    }
    
    print('\n===== 测试URL路径变体 =====')
    for url in url_variations:
        print(f'\n测试URL: {url}')
        try:
            response = requests.post(url, headers=headers, json=data)
            print(f'响应状态码: {response.status_code}')
            print(f'响应内容: {response.text}')
        except Exception as e:
            print(f'请求异常: {str(e)}')

# 测试完整前端流程
def test_frontend_flow():
    print('\n===== 模拟前端完整流程 =====')
    
    # 1. 登录
    print('\n1. 登录获取token...')
    token = test_login()
    if not token:
        print('登录失败，无法继续测试')
        return
    
    # 2. 测试文书预约 - 模拟前端完全相同的数据结构
    print('\n2. 测试文书预约接口...')
    url = 'http://localhost:8000/student/document/reserve'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        # 模拟前端可能的其他头信息
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    # 完全模拟前端发送的数据结构
    front_end_data = {
        'document_type': 'personal_statement',
        'document_count': 1,
        'teacher_id': 2,
        'target_school': '',  # 前端可能发送空字符串
        'notes': ''  # 前端可能发送空字符串
    }
    
    print(f'模拟前端请求头: {headers}')
    print(f'模拟前端请求数据: {front_end_data}')
    
    response = requests.post(url, headers=headers, json=front_end_data)
    print(f'模拟前端请求响应状态码: {response.status_code}')
    print(f'模拟前端请求响应内容: {response.text}')
    
    # 3. 测试获取文书列表接口
    print('\n3. 测试获取文书列表接口...')
    list_url = 'http://localhost:8000/student/document/list'
    list_response = requests.get(list_url, headers=headers)
    print(f'列表请求响应状态码: {list_response.status_code}')
    print(f'列表请求响应内容: {list_response.text}')

# 执行测试
if __name__ == '__main__':
    print('开始详细测试API...')
    token = test_login()
    
    # 测试URL变体
    test_url_variations(token)
    
    # 测试完整前端流程
    test_frontend_flow()
    
    print('\n测试完成！')
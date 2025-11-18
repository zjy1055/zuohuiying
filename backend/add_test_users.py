import sqlite3
import datetime
import os

# 尝试导入passlib，如果没有安装则提供明确的错误信息
try:
    from passlib.context import CryptContext
    # 创建密码上下文，使用sha-256算法（与security.py保持一致）
    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
    
    def hash_password(password):
        """生成密码哈希"""
        return pwd_context.hash(password)
    
    print("使用sha-256进行密码哈希")
    has_password_hash_available = True
except ImportError:
    print("错误: 未安装passlib库，请先安装: pip install passlib bcrypt")
    has_password_hash_available = False
    
    # 如果没有安装passlib，提供更明确的错误处理
    def hash_password(password):
        raise ImportError("需要passlib库来正确哈希密码")

# 检查passlib是否可用
if not has_password_hash_available:
    print("无法创建测试用户，因为缺少必要的密码哈希库")
    exit(1)

# 获取数据库文件路径
db_path = os.path.join(os.path.dirname(__file__), 'study_abroad.db') if __file__ else 'study_abroad.db'

# 连接到SQLite数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("添加测试用户...")
try:
    # 先删除现有的测试用户（使用错误哈希方式创建的）
    print("删除现有测试用户...")
    
    # 删除测试学生用户及其相关数据
    cursor.execute("SELECT id FROM users WHERE username = ?", ('test_student',))
    student_data = cursor.fetchone()
    if student_data:
        student_id = student_data[0]
        cursor.execute("DELETE FROM student_profiles WHERE user_id = ?", (student_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (student_id,))
        print("已删除测试学生用户")
    
    # 删除测试教师用户及其相关数据
    cursor.execute("SELECT id FROM users WHERE username = ?", ('test_teacher',))
    teacher_data = cursor.fetchone()
    if teacher_data:
        teacher_id = teacher_data[0]
        cursor.execute("DELETE FROM teacher_profiles WHERE user_id = ?", (teacher_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (teacher_id,))
        print("已删除测试教师用户")
    
    # 添加学生测试用户
    student_username = 'test_student'
    student_password = hash_password('123456')
    student_role = 'student'
    
    cursor.execute(
        "INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
        (student_username, student_password, student_role, datetime.datetime.now())
    )
    student_id = cursor.lastrowid
    print(f"已创建学生用户: {student_username} (ID: {student_id})")
    
    # 添加学生详细信息
    cursor.execute(
        "INSERT INTO student_profiles (user_id, name, gender, age, toefl, gre, gpa, target_region, email, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (student_id, '测试学生', '男', 22, 95.0, 320.0, 3.5, '美国', 'student@example.com', '13800138000')
    )
    
    # 添加教师测试用户
    teacher_username = 'test_teacher'
    teacher_password = hash_password('123456')
    teacher_role = 'teacher'
    
    cursor.execute(
        "INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
        (teacher_username, teacher_password, teacher_role, datetime.datetime.now())
    )
    teacher_id = cursor.lastrowid
    print(f"已创建教师用户: {teacher_username} (ID: {teacher_id})")
    
    # 添加教师详细信息
    cursor.execute(
        "INSERT INTO teacher_profiles (user_id, name, email, phone, subject) VALUES (?, ?, ?, ?, ?)",
        (teacher_id, '测试教师', 'teacher@example.com', '13900139000', '留学咨询')
    )
    
    # 提交事务
    conn.commit()
    print("测试用户添加成功！")
    print("\n登录信息：")
    print("学生账号: test_student / 123456")
    print("教师账号: test_teacher / 123456")
    
except Exception as e:
    conn.rollback()
    print(f"添加用户时出错：{e}")

finally:
    conn.close()
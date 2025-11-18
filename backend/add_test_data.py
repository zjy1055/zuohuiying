import random
from datetime import datetime, timedelta
from models.database import Base, User, StudentProfile, TeacherProfile, School, SchoolMajor, TrainingReservation, DocumentReservation, SuccessCase
from utils.database import SessionLocal, engine
from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_tables():
    """创建所有数据库表"""
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

def get_password_hash(password):
    """获取密码哈希值"""
    return pwd_context.hash(password)

def add_test_data():
    try:
        # 首先创建数据库表
        create_tables()
        
        print("开始添加测试数据...")
        db = SessionLocal()
        
        try:
            # 1. 添加用户数据（如果不存在）
            add_users(db)
            
            # 2. 添加学校和专业数据
            add_schools_and_majors(db)
            
            # 3. 添加学生和教师个人信息
            add_user_profiles(db)
            
            # 4. 添加成功案例
            add_success_cases(db)
            
            # 5. 添加培训和文书预约
            add_reservations(db)
            
            db.commit()
            print("\n测试数据添加完成！")
            
        except Exception as e:
            print(f"添加测试数据时出错：{e}")
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        print(f"程序执行出错：{e}")

def add_users(db):
    """添加用户数据"""
    print("\n1. 添加用户数据...")
    
    # 检查是否已有用户数据
    existing_users = db.query(User).count()
    if existing_users > 0:
        print(f"   已存在{existing_users}个用户，跳过用户数据添加...")
        return
    
    # 添加学生用户
    student_count = 10
    print(f"   添加{student_count}个学生用户...")
    for i in range(1, student_count + 1):
        student = User(
            username=f"student{i}",
            password=get_password_hash(f"student{i}pass"),
            role="student"
        )
        db.add(student)
    
    # 添加教师用户
    teacher_count = 5
    print(f"   添加{teacher_count}个教师用户...")
    for i in range(1, teacher_count + 1):
        teacher = User(
            username=f"teacher{i}",
            password=get_password_hash(f"teacher{i}pass"),
            role="teacher"
        )
        db.add(teacher)
    
    print("   用户数据添加完成")

def add_schools_and_majors(db):
    """添加学校和专业数据"""
    print("\n2. 添加学校和专业数据...")
    
    # 检查schools表是否已有数据
    if db.query(School).count() > 0:
        print("   schools表已有数据，跳过...")
        return
    
    # 学校数据
    schools_data = [
        {
            "chinese_name": "哈佛大学",
            "english_name": "Harvard University",
            "location": "美国",
            "rank": 1,
            "basic_info": "哈佛大学是一所世界著名的私立研究型大学，位于美国马萨诸塞州剑桥市。",
            "detailed_info": "哈佛大学成立于1636年，是美国历史最悠久的高等教育机构，也是常春藤盟校成员之一。该校在多个学科领域处于世界领先地位。",
            "majors": ["计算机科学", "电子工程", "工商管理", "经济学", "法学"]
        },
        {
            "chinese_name": "斯坦福大学",
            "english_name": "Stanford University",
            "location": "美国",
            "rank": 2,
            "basic_info": "斯坦福大学是一所位于美国加利福尼亚州斯坦福市的私立研究型大学。",
            "detailed_info": "斯坦福大学成立于1885年，是世界顶尖的高等教育机构之一，尤其在计算机科学、工程和商业等领域享有盛誉。",
            "majors": ["计算机科学", "电子工程", "机械工程", "生物学", "化学"]
        },
        {
            "chinese_name": "麻省理工学院",
            "english_name": "Massachusetts Institute of Technology",
            "location": "美国",
            "rank": 3,
            "basic_info": "麻省理工学院是一所世界顶尖的私立研究型大学，专注于科学、技术、工程和数学。",
            "detailed_info": "麻省理工学院成立于1861年，位于马萨诸塞州剑桥市，与哈佛大学相邻。MIT在工程、计算机科学和物理学等领域处于全球领先地位。",
            "majors": ["计算机科学", "电子工程", "物理学", "数学", "化学工程"]
        },
        {
            "chinese_name": "牛津大学",
            "english_name": "University of Oxford",
            "location": "英国",
            "rank": 4,
            "basic_info": "牛津大学是一所位于英国牛津市的世界顶尖公立研究型大学。",
            "detailed_info": "牛津大学是英语世界中最古老的大学，其历史可追溯至11世纪末。牛津大学采用学院制，拥有38个独立学院。",
            "majors": ["法学", "经济学", "英语文学", "历史学", "哲学"]
        },
        {
            "chinese_name": "剑桥大学",
            "english_name": "University of Cambridge",
            "location": "英国",
            "rank": 5,
            "basic_info": "剑桥大学是一所位于英国剑桥市的世界顶尖公立研究型大学。",
            "detailed_info": "剑桥大学成立于1209年，是英语世界中第二古老的大学。剑桥大学同样采用学院制，拥有31个独立学院。",
            "majors": ["物理学", "数学", "化学", "生物学", "计算机科学"]
        },
        {
            "chinese_name": "普林斯顿大学",
            "english_name": "Princeton University",
            "location": "美国",
            "rank": 6,
            "basic_info": "普林斯顿大学是一所位于美国新泽西州普林斯顿市的私立研究型大学。",
            "detailed_info": "普林斯顿大学成立于1746年，是常春藤盟校成员之一，以其出色的本科教育和严谨的学术氛围而闻名。",
            "majors": ["经济学", "计算机科学", "数学", "物理学", "历史学"]
        },
        {
            "chinese_name": "加州大学伯克利分校",
            "english_name": "University of California, Berkeley",
            "location": "美国",
            "rank": 7,
            "basic_info": "加州大学伯克利分校是一所位于美国加利福尼亚州伯克利市的公立研究型大学。",
            "detailed_info": "加州大学伯克利分校成立于1868年，是加州大学系统的创始校区，在工程、计算机科学和自然科学等领域享有盛誉。",
            "majors": ["计算机科学", "电子工程", "经济学", "物理学", "生物学"]
        },
        {
            "chinese_name": "耶鲁大学",
            "english_name": "Yale University",
            "location": "美国",
            "rank": 8,
            "basic_info": "耶鲁大学是一所位于美国康涅狄格州纽黑文市的私立研究型大学。",
            "detailed_info": "耶鲁大学成立于1701年，是常春藤盟校成员之一，以其卓越的法学、医学和人文社科教育而闻名。",
            "majors": ["法学", "医学", "经济学", "历史学", "英语文学"]
        }
    ]
    
    # 添加学校和专业数据
    for school_data in schools_data:
        # 创建学校
        school = School(
            chinese_name=school_data["chinese_name"],
            english_name=school_data["english_name"],
            location=school_data["location"],
            rank=school_data["rank"],
            basic_info=school_data["basic_info"],
            detailed_info=school_data["detailed_info"]
        )
        db.add(school)
        db.flush()  # 获取school.id
        
        # 添加专业
        for major_name in school_data["majors"]:
            major = SchoolMajor(
                school_id=school.id,
                major_name=major_name,
                major_rank=random.randint(1, 50)
            )
            db.add(major)
        
        print(f"   添加学校：{school_data['chinese_name']}，包含{len(school_data['majors'])}个专业")
    
    print("   学校和专业数据添加完成")

def add_user_profiles(db):
    """添加学生和教师个人信息"""
    print("\n3. 添加用户个人信息...")
    
    # 添加学生个人信息
    students = db.query(User).filter(User.role == "student").all()
    print(f"   处理{len(students)}个学生用户...")
    
    for student in students:
        # 检查是否已有个人信息
        if not student.student_profile:
            # 生成学生个人信息
            names = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十", "郑十一", "陈十二"]
            genders = ["男", "女"]
            regions = ["北京", "上海", "广州", "深圳", "南京", "杭州", "成都", "武汉", "西安", "重庆"]
            
            profile = StudentProfile(
                user_id=student.id,
                name=random.choice(names) if student.id <= len(names) else f"学生{student.id}",
                gender=random.choice(genders),
                age=random.randint(18, 25),
                toefl=round(random.uniform(80, 110), 1),
                gre=round(random.uniform(290, 340), 1),
                gpa=round(random.uniform(2.5, 4.0), 2),
                target_region=random.choice(regions),
                email=f"student{student.id}@example.com",
                phone=f"138001380{student.id:02d}"
            )
            db.add(profile)
            print(f"   为学生用户 '{student.username}' 添加个人信息")
    
    # 添加教师个人信息
    teachers = db.query(User).filter(User.role == "teacher").all()
    print(f"   处理{len(teachers)}个教师用户...")
    
    for teacher in teachers:
        # 检查是否已有个人信息
        if not teacher.teacher_profile:
            # 生成教师个人信息
            names = ["王老师", "李老师", "张老师", "刘老师", "陈老师", "杨老师", "赵老师", "黄老师", "周老师", "吴老师"]
            subjects = ["英语", "数学", "物理", "化学", "计算机科学", "生物学", "经济学", "历史学", "法学", "心理学"]
            
            profile = TeacherProfile(
                user_id=teacher.id,
                name=random.choice(names) if teacher.id <= len(names) else f"老师{teacher.id}",
                email=f"teacher{teacher.id}@example.com",
                phone=f"139001390{teacher.id:02d}",
                subject=random.choice(subjects)
            )
            db.add(profile)
            print(f"   为教师用户 '{teacher.username}' 添加个人信息")
    
    print("   用户个人信息添加完成")

def add_success_cases(db):
    """添加成功案例"""
    print("\n4. 添加成功案例...")
    
    # 检查是否已有成功案例
    if db.query(SuccessCase).count() > 0:
        print("   success_cases表已有数据，跳过...")
        return
    
    # 成功案例数据
    cases_data = [
        {
            "title": "哈佛大学生物学博士申请成功案例",
            "content": "张明同学在我们专业团队的指导下，成功申请到哈佛大学分子生物学博士项目。该同学GPA 3.9，托福115分，GRE 330分，发表了2篇SCI论文。我们为其定制了详细的申请计划，从选校定位到文书写作，再到面试准备，提供了全方位的指导。最终在激烈的竞争中脱颖而出，获得了全额奖学金录取。",
            "file_path": None
        },
        {
            "title": "斯坦福大学计算机科学硕士录取",
            "content": "李华同学成功录取斯坦福大学计算机科学硕士项目。该同学来自国内985高校，GPA 3.8，托福110分，GRE 328分。我们帮助其优化简历，突出科研经历和实习项目，并在推荐信方面提供了专业建议。在申请过程中，我们还针对斯坦福的特殊要求进行了针对性准备，最终成功获得录取。",
            "file_path": None
        },
        {
            "title": "牛津大学MBA录取经验分享",
            "content": "王芳同学拥有5年金融行业工作经验，成功申请到牛津大学MBA项目。我们为其量身定制了职业规划文书，突出其在投资银行的项目经验和领导力。在面试环节，我们提供了多轮模拟面试和专业指导，帮助其充分展示自己的商业洞察力和团队协作能力。最终获得了录取和部分奖学金。",
            "file_path": None
        },
        {
            "title": "麻省理工学院电子工程硕士全奖录取",
            "content": "赵强同学本科毕业于清华大学电子工程系，GPA 3.95，托福118分，GRE 335分。在我们的指导下，他完善了研究计划，强调了其在人工智能领域的研究成果。我们还帮助其联系了MIT的潜在导师，增强了申请的竞争力。最终，他成功获得了麻省理工学院电子工程硕士项目的全奖录取。",
            "file_path": None
        },
        {
            "title": "剑桥大学教育学博士录取",
            "content": "陈静同学在国内高校担任讲师3年，成功申请到剑桥大学教育学博士项目。我们帮助其将教学经验与研究兴趣相结合，构建了有深度的研究提案。在语言方面，我们提供了针对性的英语写作培训，提升了其学术写作能力。最终，她成功获得了剑桥大学的录取，并获得了海外研究奖学金。",
            "file_path": None
        },
        {
            "title": "普林斯顿大学经济学博士录取",
            "content": "李明同学本科和硕士均毕业于国内顶尖财经院校，GPA 3.9，托福112分，GRE 330分。我们帮助其撰写了高质量的研究计划，突出了其在计量经济学方面的研究成果。通过模拟面试和专业指导，李明同学在面试中表现出色，最终获得了普林斯顿大学经济学博士项目的录取和全额奖学金。",
            "file_path": None
        },
        {
            "title": "加州大学伯克利分校计算机科学本科转学成功",
            "content": "王浩同学成功从国内985高校转学至加州大学伯克利分校计算机科学专业。我们帮助其准备了全面的申请材料，包括个人陈述、推荐信和课外活动证明。在申请过程中，我们针对伯克利的转学要求提供了专业指导，最终王浩同学成功获得了录取。",
            "file_path": None
        }
    ]
    
    # 添加成功案例
    for case_data in cases_data:
        # 生成随机创建时间（过去一年内）
        now = datetime.now()
        random_days = random.randint(1, 365)
        created_at = now - timedelta(days=random_days)
        
        case = SuccessCase(
            title=case_data["title"],
            content=case_data["content"],
            file_path=case_data["file_path"],
            created_at=created_at
        )
        db.add(case)
        print(f"   添加成功案例：{case_data['title']}")
    
    print("   成功案例数据添加完成")

def add_reservations(db):
    """添加培训和文书预约"""
    print("\n5. 添加培训和文书预约...")
    
    # 获取所有学生和教师用户
    students = db.query(User).filter(User.role == "student").all()
    teachers = db.query(User).filter(User.role == "teacher").all()
    
    if not students or not teachers:
        print("   缺少学生或教师用户，跳过预约数据添加...")
        return
    
    # 添加培训预约
    statuses = ["pending", "accepted", "completed"]
    training_types = ["托福培训", "GRE培训", "雅思培训", "SAT培训", "口语培训", "写作培训"]
    training_count = 15
    
    print(f"   添加{training_count}个培训预约记录...")
    for i in range(training_count):
        student = random.choice(students)
        teacher = random.choice([t for t in teachers if t.id != student.id])  # 确保不是同一个用户
        total_hours = random.randint(10, 50)
        status = random.choice(statuses)
        attended_hours = random.randint(0, total_hours) if status == "completed" else 0
        
        # 生成随机创建时间和更新时间
        now = datetime.now()
        random_days = random.randint(1, 90)
        created_at = now - timedelta(days=random_days)
        updated_at = created_at + timedelta(days=random.randint(1, random_days)) if status != "pending" else None
        
        # 根据状态生成不同的反馈内容
        feedback_options = [
            "学生学习态度认真，进步显著。",
            "需要加强练习，但整体表现良好。",
            "词汇量有所提高，语法还需加强。",
            "口语表达流畅度提升明显。",
            "写作逻辑清晰，论证有力。"
        ]
        feedback = random.choice(feedback_options) if status == "completed" else None
        
        # 随机生成作业内容
        homework_options = [
            "完成托福TPO第30套听力部分。",
            "背诵GRE核心词汇300个。",
            "写一篇关于环保主题的议论文。",
            "准备3分钟英语口语自我介绍。",
            "整理错题本并分析错误原因。"
        ]
        homework = random.choice(homework_options) if status != "pending" else None
        
        training_reservation = TrainingReservation(
            student_id=student.id,
            teacher_id=teacher.id,
            total_hours=total_hours,
            training_type=random.choice(training_types),
            notes=f"学生希望提高{random.choice(['听力', '阅读', '写作', '口语', '整体'])}能力。" if random.random() > 0.3 else None,
            status=status,
            attended_hours=attended_hours,
            feedback=feedback,
            homework=homework,
            updated_at=updated_at,
            created_at=created_at
        )
        db.add(training_reservation)
    
    # 添加文书预约
    document_types = ["个人陈述", "推荐信", "简历", "研究计划", "论文润色", "申请动机信"]
    document_count = 10
    
    print(f"   添加{document_count}个文书预约记录...")
    for i in range(document_count):
        student = random.choice(students)
        teacher = random.choice([t for t in teachers if t.id != student.id])
        doc_count = random.randint(1, 3)
        status = random.choice(statuses)
        progress = 100 if status == "completed" else random.randint(0, 90)
        
        # 生成随机创建时间和更新时间
        now = datetime.now()
        random_days = random.randint(1, 60)
        created_at = now - timedelta(days=random_days)
        updated_at = created_at + timedelta(days=random.randint(1, random_days)) if status != "pending" else None
        
        # 获取学校列表，随机选择目标学校
        schools = db.query(School).all()
        target_school = random.choice(schools).chinese_name if schools else None
        
        # 根据进度生成不同的修订内容
        revised_contents = [
            "已根据要求对文书进行润色，突出了学术背景和研究能力。",
            "调整了文章结构，使逻辑更加清晰流畅。",
            "强化了个人经历与申请专业的关联性。",
            "优化了语言表达，提高了专业术语准确性。",
            "完善了研究计划部分，增加了可行性分析。"
        ]
        revised_content = random.choice(revised_contents) if progress > 50 else None
        
        # 随机生成评语
        comments = f"整体质量良好，建议在{random.choice(['结构', '内容', '语言表达', '专业术语'])}方面进一步完善。" if progress > 30 else None
        
        document_reservation = DocumentReservation(
            student_id=student.id,
            teacher_id=teacher.id,
            document_count=doc_count,
            document_type=random.choice(document_types),
            target_school=target_school,
            notes=f"希望突出{random.choice(['学术背景', '实践经验', '研究兴趣', '个人特质'])}。" if random.random() > 0.3 else None,
            comments=comments,
            status=status,
            progress=progress,
            original_content="学生原始文档内容示例..." if progress > 0 else None,
            revised_content=revised_content,
            file_path=None,
            updated_at=updated_at,
            created_at=created_at
        )
        db.add(document_reservation)
    
    print("   预约数据添加完成")

if __name__ == "__main__":
    add_test_data()
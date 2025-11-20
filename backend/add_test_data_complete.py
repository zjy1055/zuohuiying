# -*- coding: utf-8 -*-
"""
插入完整的测试数据，确保每个表的每个字段都有数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import (
    Base, User, UserRole, StudentProfile, TeacherProfile, 
    School, SchoolMajor, TrainingReservation, DocumentReservation, 
    ReservationStatus, SuccessCase, engine, SessionLocal
)
from sqlalchemy.exc import IntegrityError
from utils.security import get_password_hash

def hash_password(password: str) -> str:
    """使用与security.py中相同的密码哈希方法"""
    return get_password_hash(password)

def init_database():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)
    print("数据库表已创建")

def add_test_data():
    """添加完整的测试数据"""
    db = SessionLocal()
    
    try:
        # 1. 插入用户数据（学生和教师）
        print("\n=== 插入用户数据 ===")
        
        # 先删除相关的依赖记录，避免外键约束错误
        # 获取要删除的用户ID列表
        users_to_delete = db.query(User.id).filter(User.username.in_(["test_student", "student_2", "student_3", "student_4", "student_5", "test_teacher", "teacher_2", "teacher_3", "teacher_4", "admin"])).all()
        user_ids = [user[0] for user in users_to_delete]
        
        if user_ids:
            # 删除预约相关记录
            db.query(DocumentReservation).filter(DocumentReservation.student_id.in_(user_ids)).delete(synchronize_session=False)
            db.query(TrainingReservation).filter(TrainingReservation.student_id.in_(user_ids)).delete(synchronize_session=False)
            
            # 删除依赖关系较强的表数据
            db.query(SuccessCase).delete(synchronize_session=False)
            db.query(SchoolMajor).delete(synchronize_session=False)  # 清理专业排名数据
            db.query(School).delete(synchronize_session=False)  # 清理学校数据
            
            # 删除学生和教师信息
            db.query(StudentProfile).filter(StudentProfile.user_id.in_(user_ids)).delete(synchronize_session=False)
            db.query(TeacherProfile).filter(TeacherProfile.user_id.in_(user_ids)).delete(synchronize_session=False)
            
            # 删除用户
            db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
            db.commit()
            print("已清理现有测试数据")
        
        # 学生用户
        student_user = User(
            username="test_student",
            password=hash_password("password123"),
            role=UserRole.STUDENT
        )
        student_user2 = User(
            username="student_2",
            password=hash_password("password123"),
            role=UserRole.STUDENT
        )
        student_user3 = User(
            username="student_3",
            password=hash_password("password123"),
            role=UserRole.STUDENT
        )
        student_user4 = User(
            username="student_4",
            password=hash_password("password123"),
            role=UserRole.STUDENT
        )
        student_user5 = User(
            username="student_5",
            password=hash_password("password123"),
            role=UserRole.STUDENT
        )
        db.add_all([student_user, student_user2, student_user3, student_user4, student_user5])
        
        # 教师用户
        teacher_user = User(
            username="test_teacher",
            password=hash_password("password123"),
            role=UserRole.TEACHER
        )
        teacher_user2 = User(
            username="teacher_2",
            password=hash_password("password123"),
            role=UserRole.TEACHER
        )
        teacher_user3 = User(
            username="teacher_3",
            password=hash_password("password123"),
            role=UserRole.TEACHER
        )
        teacher_user4 = User(
            username="teacher_4",
            password=hash_password("password123"),
            role=UserRole.TEACHER
        )
        
        # 管理员用户（可选）
        admin_user = User(
            username="admin",
            password=hash_password("admin123"),
            role=UserRole.TEACHER  # 暂时使用教师角色作为管理员
        )
        
        db.add_all([teacher_user, teacher_user2, teacher_user3, teacher_user4, admin_user])
        
        db.commit()
        print(f"已插入 {len([student_user, teacher_user, admin_user])} 个用户")
        
        # 2. 插入学生信息
        print("\n=== 插入学生信息 ===")
        student_profiles = [
            StudentProfile(
                user_id=student_user.id,
                name="张三",
                gender="男",
                age=22,
                toefl=95.5,
                gre=310.0,
                gpa=3.5,
                target_region="美国",
                email="zhangsan@example.com",
                phone="13800138000"
            ),
            StudentProfile(
                user_id=student_user2.id,
                name="李四",
                gender="女",
                age=23,
                toefl=105.0,
                gre=325.0,
                gpa=3.8,
                target_region="英国",
                email="lisi@example.com",
                phone="13800138001"
            ),
            StudentProfile(
                user_id=student_user3.id,
                name="王五",
                gender="男",
                age=21,
                toefl=88.0,
                gre=305.0,
                gpa=3.3,
                target_region="澳大利亚",
                email="wangwu@example.com",
                phone="13800138002"
            ),
            StudentProfile(
                user_id=student_user4.id,
                name="赵六",
                gender="女",
                age=24,
                toefl=110.5,
                gre=330.0,
                gpa=3.9,
                target_region="美国",
                email="zhaoliu@example.com",
                phone="13800138003"
            ),
            StudentProfile(
                user_id=student_user5.id,
                name="钱七",
                gender="男",
                age=22,
                toefl=92.0,
                gre=315.0,
                gpa=3.6,
                target_region="加拿大",
                email="qianqi@example.com",
                phone="13800138004"
            )
        ]
        db.add_all(student_profiles)
        
        db.commit()
        print(f"已插入 {len(student_profiles)} 个学生信息")
        
        # 3. 插入教师信息
        print("\n=== 插入教师信息 ===")
        teacher_profiles = [
            TeacherProfile(
                user_id=teacher_user.id,
                name="李老师",
                email="teacher_li@example.com",
                phone="13900139000",
                subject="英语, GRE, 文书写作"
            ),
            TeacherProfile(
                user_id=teacher_user2.id,
                name="张老师",
                email="teacher_zhang@example.com",
                phone="13900139001",
                subject="GMAT, 商业分析, 面试培训"
            ),
            TeacherProfile(
                user_id=teacher_user3.id,
                name="刘老师",
                email="teacher_liu@example.com",
                phone="13900139002",
                subject="托福, SAT, 高中留学规划"
            ),
            TeacherProfile(
                user_id=teacher_user4.id,
                name="陈老师",
                email="teacher_chen@example.com",
                phone="13900139003",
                subject="学术写作, 研究计划, 博士申请"
            ),
            TeacherProfile(
                user_id=admin_user.id,
                name="王老师",
                email="teacher_wang@example.com",
                phone="13700137000",
                subject="留学规划, 院校申请"
            )
        ]
        db.add_all(teacher_profiles)
        
        db.commit()
        print(f"已插入 {len(teacher_profiles)} 个教师信息")
        
        # 4. 插入学校信息
        print("\n=== 插入学校信息 ===")
        schools = [
            School(
                chinese_name="哈佛大学",
                english_name="Harvard University",
                location="美国马萨诸塞州剑桥市",
                ranking=1,
                introduction="哈佛大学是一所世界著名的私立研究型大学，成立于1636年。",
                details="哈佛大学是常春藤盟校成员之一，拥有世界一流的教学和研究设施。学校提供丰富的本科和研究生课程，在多个领域处于世界领先地位。"
            ),
            School(
                chinese_name="麻省理工学院",
                english_name="Massachusetts Institute of Technology",
                location="美国马萨诸塞州剑桥市",
                ranking=2,
                introduction="麻省理工学院是一所世界顶尖的私立研究型大学，成立于1861年。",
                details="麻省理工学院以工程学和计算机科学而闻名，同时在物理学、经济学等领域也有卓越成就。学校强调实践教学和创新精神。"
            ),
            School(
                chinese_name="斯坦福大学",
                english_name="Stanford University",
                location="美国加利福尼亚州斯坦福市",
                ranking=3,
                introduction="斯坦福大学是一所位于美国加州的私立研究型大学，成立于1891年。",
                details="斯坦福大学位于硅谷中心，与众多科技公司有密切合作。学校在计算机科学、工程学、商业管理等领域享有盛誉。"
            ),
            School(
                chinese_name="牛津大学",
                english_name="University of Oxford",
                location="英国牛津市",
                ranking=4,
                introduction="牛津大学是一所位于英国牛津市的世界顶尖公立研究型大学，成立于1167年。",
                details="牛津大学是英语世界中最古老的大学，也是世界上现存第二古老的高等教育机构。牛津大学拥有38个学院，在人文、社会科学、自然科学等领域都有杰出的研究成果。"
            ),
            School(
                chinese_name="剑桥大学",
                english_name="University of Cambridge",
                location="英国剑桥市",
                ranking=5,
                introduction="剑桥大学是一所位于英国剑桥市的世界顶尖公立研究型大学，成立于1209年。",
                details="剑桥大学是英语世界中第二古老的大学，拥有31个学院。学校在数学、物理、计算机科学等领域享有全球声誉，培养了众多诺贝尔奖获得者。"
            ),
            School(
                chinese_name="加州大学伯克利分校",
                english_name="University of California, Berkeley",
                location="美国加利福尼亚州伯克利市",
                ranking=6,
                introduction="加州大学伯克利分校是一所世界顶尖的公立研究型大学，成立于1868年。",
                details="伯克利是加州大学系统的创始校区，也是美国最负盛名的公立大学之一。学校在工程学、计算机科学、社会科学等领域处于领先地位，拥有众多诺贝尔奖获得者和图灵奖获得者。"
            ),
            School(
                chinese_name="普林斯顿大学",
                english_name="Princeton University",
                location="美国新泽西州普林斯顿市",
                ranking=7,
                introduction="普林斯顿大学是一所世界顶尖的私立研究型大学，成立于1746年。",
                details="普林斯顿大学是常春藤盟校成员之一，以其卓越的学术声誉和严格的入学标准闻名。学校在数学、物理学、经济学等领域处于领先地位。"
            ),
            School(
                chinese_name="耶鲁大学",
                english_name="Yale University",
                location="美国康涅狄格州纽黑文市",
                ranking=8,
                introduction="耶鲁大学是一所世界顶尖的私立研究型大学，成立于1701年。",
                details="耶鲁大学是常春藤盟校成员之一，以其强大的人文社科传统和法学院而闻名。学校拥有世界上最大的大学图书馆系统之一。"
            ),
            School(
                chinese_name="帝国理工学院",
                english_name="Imperial College London",
                location="英国伦敦市",
                ranking=9,
                introduction="帝国理工学院是一所世界顶尖的公立研究型大学，成立于1907年。",
                details="帝国理工学院专注于科学、工程、医学和商业领域，在全球享有极高声誉。学校与众多工业界和研究机构有着密切合作。"
            ),
            School(
                chinese_name="芝加哥大学",
                english_name="University of Chicago",
                location="美国伊利诺伊州芝加哥市",
                ranking=10,
                introduction="芝加哥大学是一所世界顶尖的私立研究型大学，成立于1890年。",
                details="芝加哥大学以其严格的学术氛围和强大的研究传统而闻名，在经济学、物理学、法学等领域尤为突出。学校培养了众多诺贝尔奖获得者。"
            ),
            School(
                chinese_name="新加坡国立大学",
                english_name="National University of Singapore",
                location="新加坡",
                ranking=11,
                introduction="新加坡国立大学是一所世界顶尖的公立研究型大学，成立于1905年。",
                details="新加坡国立大学是新加坡历史最悠久的高等教育机构，在工程、计算机科学、生命科学等领域具有强大实力，是亚洲最顶尖的大学之一。"
            ),
            School(
                chinese_name="北京大学",
                english_name="Peking University",
                location="中国北京市",
                ranking=15,
                introduction="北京大学是中国顶尖的公立研究型大学，成立于1898年。",
                details="北京大学是中国近代第一所国立综合性大学，也是中国最高学府之一。学校在人文社科、自然科学、医学等多个领域具有卓越实力。"
            )
        ]
        db.add_all(schools)
        db.commit()
        print(f"已插入 {len(schools)} 个学校信息")
        
        # 5. 插入学校专业排名信息
        print("\n=== 插入学校专业排名信息 ===")
        majors = [
            # 哈佛大学专业
            SchoolMajor(school_id=schools[0].id, major_name="计算机科学", major_rank=5),
            SchoolMajor(school_id=schools[0].id, major_name="经济学", major_rank=1),
            SchoolMajor(school_id=schools[0].id, major_name="法学", major_rank=1),
            SchoolMajor(school_id=schools[0].id, major_name="医学", major_rank=2),
            SchoolMajor(school_id=schools[0].id, major_name="历史学", major_rank=1),
            SchoolMajor(school_id=schools[0].id, major_name="政治学", major_rank=1),
            
            # 麻省理工学院专业
            SchoolMajor(school_id=schools[1].id, major_name="计算机科学", major_rank=1),
            SchoolMajor(school_id=schools[1].id, major_name="电子工程", major_rank=1),
            SchoolMajor(school_id=schools[1].id, major_name="机械工程", major_rank=2),
            SchoolMajor(school_id=schools[1].id, major_name="物理学", major_rank=3),
            SchoolMajor(school_id=schools[1].id, major_name="数学", major_rank=2),
            SchoolMajor(school_id=schools[1].id, major_name="化学工程", major_rank=1),
            
            # 斯坦福大学专业
            SchoolMajor(school_id=schools[2].id, major_name="计算机科学", major_rank=2),
            SchoolMajor(school_id=schools[2].id, major_name="商业管理", major_rank=1),
            SchoolMajor(school_id=schools[2].id, major_name="心理学", major_rank=3),
            SchoolMajor(school_id=schools[2].id, major_name="电气工程", major_rank=2),
            SchoolMajor(school_id=schools[2].id, major_name="环境科学", major_rank=4),
            SchoolMajor(school_id=schools[2].id, major_name="统计学", major_rank=2),
            
            # 牛津大学专业
            SchoolMajor(school_id=schools[3].id, major_name="哲学", major_rank=1),
            SchoolMajor(school_id=schools[3].id, major_name="历史", major_rank=2),
            SchoolMajor(school_id=schools[3].id, major_name="英语文学", major_rank=1),
            SchoolMajor(school_id=schools[3].id, major_name="医学", major_rank=3),
            SchoolMajor(school_id=schools[3].id, major_name="数学", major_rank=4),
            
            # 剑桥大学专业
            SchoolMajor(school_id=schools[4].id, major_name="数学", major_rank=1),
            SchoolMajor(school_id=schools[4].id, major_name="物理学", major_rank=1),
            SchoolMajor(school_id=schools[4].id, major_name="化学", major_rank=2),
            SchoolMajor(school_id=schools[4].id, major_name="工程学", major_rank=3),
            SchoolMajor(school_id=schools[4].id, major_name="计算机科学", major_rank=6),
            
            # 加州大学伯克利分校专业
            SchoolMajor(school_id=schools[5].id, major_name="计算机科学", major_rank=3),
            SchoolMajor(school_id=schools[5].id, major_name="电子工程", major_rank=3),
            SchoolMajor(school_id=schools[5].id, major_name="经济学", major_rank=2),
            SchoolMajor(school_id=schools[5].id, major_name="环境科学", major_rank=1),
            SchoolMajor(school_id=schools[5].id, major_name="统计学", major_rank=3),
            
            # 普林斯顿大学专业
            SchoolMajor(school_id=schools[6].id, major_name="数学", major_rank=1),
            SchoolMajor(school_id=schools[6].id, major_name="物理学", major_rank=2),
            SchoolMajor(school_id=schools[6].id, major_name="经济学", major_rank=3),
            SchoolMajor(school_id=schools[6].id, major_name="政治学", major_rank=2),
            
            # 耶鲁大学专业
            SchoolMajor(school_id=schools[7].id, major_name="法学", major_rank=2),
            SchoolMajor(school_id=schools[7].id, major_name="历史", major_rank=3),
            SchoolMajor(school_id=schools[7].id, major_name="英语文学", major_rank=2),
            SchoolMajor(school_id=schools[7].id, major_name="经济学", major_rank=4),
            
            # 帝国理工学院专业
            SchoolMajor(school_id=schools[8].id, major_name="工程学", major_rank=2),
            SchoolMajor(school_id=schools[8].id, major_name="计算机科学", major_rank=5),
            SchoolMajor(school_id=schools[8].id, major_name="物理学", major_rank=4),
            SchoolMajor(school_id=schools[8].id, major_name="医学", major_rank=4),
            
            # 芝加哥大学专业
            SchoolMajor(school_id=schools[9].id, major_name="经济学", major_rank=1),
            SchoolMajor(school_id=schools[9].id, major_name="法学", major_rank=3),
            SchoolMajor(school_id=schools[9].id, major_name="统计学", major_rank=1),
            SchoolMajor(school_id=schools[9].id, major_name="历史学", major_rank=2),
            
            # 新加坡国立大学专业
            SchoolMajor(school_id=schools[10].id, major_name="计算机科学", major_rank=8),
            SchoolMajor(school_id=schools[10].id, major_name="电子工程", major_rank=7),
            SchoolMajor(school_id=schools[10].id, major_name="商业管理", major_rank=5),
            SchoolMajor(school_id=schools[10].id, major_name="环境科学", major_rank=9),
            
            # 北京大学专业
            SchoolMajor(school_id=schools[11].id, major_name="计算机科学", major_rank=12),
            SchoolMajor(school_id=schools[11].id, major_name="数学", major_rank=8),
            SchoolMajor(school_id=schools[11].id, major_name="物理学", major_rank=10),
            SchoolMajor(school_id=schools[11].id, major_name="化学", major_rank=9),
            SchoolMajor(school_id=schools[11].id, major_name="历史学", major_rank=5)
        ]
        db.add_all(majors)
        db.commit()
        print(f"已插入 {len(majors)} 个学校专业排名信息")
        
        # 6. 插入语言培训预约
        print("\n=== 插入语言培训预约 ===")
        training_reservations = [
            # 学生1的预约
            TrainingReservation(
                student_id=student_user.id,
                teacher_id=teacher_user.id,
                total_hours=40,
                training_type="GRE综合培训",
                notes="学生希望提高GRE成绩，特别是数学部分",
                status=ReservationStatus.PENDING,
                attended_hours=0,
                feedback="",
                homework="完成GRE数学练习题第1-10套"
            ),
            TrainingReservation(
                student_id=student_user.id,
                teacher_id=admin_user.id,
                total_hours=20,
                training_type="英语口语培训",
                notes="提高日常交流和面试口语能力",
                status=ReservationStatus.ACCEPTED,
                attended_hours=5,
                feedback="学生进步明显，需要加强听力训练",
                homework="每天练习听力1小时，准备下节课的口语话题"
            ),
            # 学生2的预约
            TrainingReservation(
                student_id=student_user2.id,
                teacher_id=teacher_user2.id,
                total_hours=30,
                training_type="GMAT强化班",
                notes="目标分数720+，重点突破逻辑和阅读",
                status=ReservationStatus.COMPLETED,
                attended_hours=30,
                feedback="学生非常努力，最终得分730，成功达到目标",
                homework="已完成所有练习，建议参加模拟面试训练"
            ),
            # 学生3的预约
            TrainingReservation(
                student_id=student_user3.id,
                teacher_id=teacher_user3.id,
                total_hours=25,
                training_type="托福全项培训",
                notes="目前分数88，目标分数95+",
                status=ReservationStatus.ACCEPTED,
                attended_hours=15,
                feedback="听力和阅读进步明显，口语仍需加强",
                homework="完成TPO 30-35的听力和阅读练习"
            ),
            # 学生4的预约
            TrainingReservation(
                student_id=student_user4.id,
                teacher_id=teacher_user.id,
                total_hours=15,
                training_type="留学面试培训",
                notes="准备哈佛大学计算机科学专业面试",
                status=ReservationStatus.ACCEPTED,
                attended_hours=0,
                feedback="",
                homework="准备个人经历介绍和研究兴趣陈述"
            ),
            # 学生5的预约
            TrainingReservation(
                student_id=student_user5.id,
                teacher_id=teacher_user4.id,
                total_hours=35,
                training_type="学术写作训练",
                notes="提高研究计划书写作能力",
                status=ReservationStatus.ACCEPTED,
                attended_hours=10,
                feedback="结构组织不错，但论证深度需要加强",
                homework="重写研究方法部分，增加文献引用"
            )
        ]
        db.add_all(training_reservations)
        db.commit()
        print(f"已插入 {len(training_reservations)} 个语言培训预约")
        
        # 7. 插入文书润色预约
        print("\n=== 插入文书润色预约 ===")
        document_reservations = [
            # 学生1的预约
            DocumentReservation(
                student_id=student_user.id,
                teacher_id=teacher_user.id,
                document_count=3,
                document_type="个人陈述",
                target_school="哈佛大学",
                notes="希望文书能突出个人优势和研究经历",
                comments="整体结构清晰，需要加强研究动机部分",
                status=ReservationStatus.COMPLETED,
                progress=100,
                original_content="我是张三，我想申请哈佛大学的计算机科学专业...",
                revised_content="作为一名对人工智能充满热情的计算机科学爱好者，我张三希望能够在哈佛大学继续深造...",
                file_path="/documents/zhangsan_ps_revised.docx"
            ),
            DocumentReservation(
                student_id=student_user.id,
                teacher_id=admin_user.id,
                document_count=2,
                document_type="推荐信",
                target_school="斯坦福大学",
                notes="需要修改教授提供的推荐信",
                comments="推荐信内容不错，但需要更具体的实例支持",
                status=ReservationStatus.ACCEPTED,
                progress=50,
                original_content="张三同学是我教过的最优秀的学生之一...",
                revised_content="在我教授的算法课程中，张三同学不仅取得了98分的优异成绩，还独立完成了一个创新的算法优化项目...",
                file_path="/documents/zhangsan_lor_in_progress.docx"
            ),
            # 学生2的预约
            DocumentReservation(
                student_id=student_user2.id,
                teacher_id=teacher_user2.id,
                document_count=1,
                document_type="商业计划书",
                target_school="哈佛商学院",
                notes="MBA申请，需要突出领导力和创业经历",
                comments="内容丰富，但需要更清晰地展示商业思维",
                status=ReservationStatus.COMPLETED,
                progress=100,
                original_content="我的创业经历包括创立了一家小型科技公司...",
                revised_content="通过创立科技公司的经历，我培养了战略性思维和团队领导能力，这些经验将使我在哈佛商学院的学习中受益匪浅...",
                file_path="/documents/lisi_business_plan_revised.docx"
            ),
            # 学生3的预约
            DocumentReservation(
                student_id=student_user3.id,
                teacher_id=teacher_user3.id,
                document_count=3,
                document_type="个人陈述",
                target_school="墨尔本大学",
                notes="转专业申请，需要解释专业转换动机",
                comments="专业转换的逻辑性需要加强",
                status=ReservationStatus.ACCEPTED,
                progress=60,
                original_content="我是王五，本科学习机械工程，现在想申请计算机科学...",
                revised_content="我的机械工程背景为我提供了坚实的数学基础，同时我通过自学掌握了编程技能，这种跨学科背景使我在人工智能领域有独特优势...",
                file_path="/documents/wangwu_ps_in_progress.docx"
            ),
            # 学生4的预约
            DocumentReservation(
                student_id=student_user4.id,
                teacher_id=teacher_user4.id,
                document_count=2,
                document_type="研究计划书",
                target_school="斯坦福大学",
                notes="博士申请，研究方向为机器学习在医疗领域的应用",
                comments="研究计划创新性强，但方法论部分需要补充",
                status=ReservationStatus.ACCEPTED,
                progress=30,
                original_content="我的研究计划旨在探索深度学习在医学影像分析中的应用...",
                revised_content="本研究计划提出了一种创新的多模态深度学习框架，用于整合医学影像和电子健康记录数据，以提高疾病诊断的准确性...",
                file_path="/documents/zhaoliu_research_plan.docx"
            ),
            # 学生5的预约
            DocumentReservation(
                student_id=student_user5.id,
                teacher_id=teacher_user.id,
                document_count=1,
                document_type="个人陈述",
                target_school="多伦多大学",
                notes="希望突出跨文化交流经历和语言学习能力",
                comments="个人经历丰富，但需要更紧密地与目标专业联系",
                status=ReservationStatus.PENDING,
                progress=0,
                original_content="我是钱七，有丰富的国际交流经验...",
                revised_content="",
                file_path="/documents/qianqi_ps_pending.docx"
            )
        ]
        db.add_all(document_reservations)
        db.commit()
        print(f"已插入 {len(document_reservations)} 个文书润色预约")
        
        # 8. 插入成功案例
        print("\n=== 插入成功案例 ===")
        success_cases = [
            # 张三同学的案例
            SuccessCase(
                title="张三同学成功申请哈佛大学计算机科学硕士",
                content="张三同学通过我们的培训和指导，成功申请到哈佛大学计算机科学硕士项目。他在GRE考试中取得了335分的优异成绩，并在文书中突出展示了自己在人工智能领域的研究经历和创新思维。",
                file_path="/success_cases/zhangsan_harvard_cs_case.pdf"
            ),
            SuccessCase(
                title="张三同学获得斯坦福大学全奖博士录取",
                content="经过为期一年的准备，张三同学不仅在托福考试中取得了118分的高分，还在我们导师的指导下发表了两篇学术论文，最终成功获得斯坦福大学电子工程博士项目的全额奖学金录取。",
                file_path="/success_cases/zhangsan_stanford_phd_case.pdf"
            ),
            # 李四同学的案例
            SuccessCase(
                title="李四同学成功申请哈佛商学院MBA项目",
                content="李四同学在我们的GMAT强化培训和MBA申请指导下，GMAT取得了730分的优异成绩。通过对其创业经历的专业包装和面试技巧的系统训练，最终成功获得哈佛商学院MBA项目的录取。",
                file_path="/success_cases/lisi_harvard_mba_case.pdf"
            ),
            # 王五同学的案例
            SuccessCase(
                title="王五同学跨专业申请成功录取墨尔本大学计算机科学",
                content="王五同学本科机械工程背景，通过我们的专业课程规划和自学指导，成功弥补了计算机专业背景的不足。在文书中突出了跨学科优势和自学能力，最终被墨尔本大学计算机科学硕士项目录取。",
                file_path="/success_cases/wangwu_melbourne_cs_case.pdf"
            ),
            # 赵六同学的案例
            SuccessCase(
                title="赵六同学获得斯坦福大学机器学习全奖博士",
                content="赵六同学在我们研究方向定位和套磁指导下，精准对接了斯坦福大学教授的研究兴趣。通过优化研究计划书和模拟面试训练，最终获得了斯坦福大学机器学习博士项目的全额奖学金录取。",
                file_path="/success_cases/zhaoliu_stanford_ml_case.pdf"
            ),
            # 钱七同学的案例
            SuccessCase(
                title="钱七同学成功申请多伦多大学语言学硕士",
                content="钱七同学凭借丰富的国际交流经历和语言学习背景，在我们的文书指导下成功突出了跨文化沟通能力和语言学习天赋。虽然GPA不占优势，但通过弥补短板和突出优势，最终被多伦多大学语言学硕士项目录取。",
                file_path="/success_cases/qianqi_toronto_linguistics_case.pdf"
            ),
            # 其他案例
            SuccessCase(
                title="优秀应届生成功录取麻省理工学院金融工程",
                content="该生本科金融专业，GPA 3.9，GRE 330，通过我们的背景提升规划，参与了两个金融科技相关的实习项目，并在文书中有效展示了量化分析能力和编程技能，最终成功被麻省理工学院金融工程硕士项目录取。",
                file_path="/success_cases/mit_financial_engineering_case.pdf"
            ),
            SuccessCase(
                title="工作党转专业录取牛津大学数据科学硕士",
                content="该生有3年市场营销工作经验，通过我们的在线课程推荐和项目指导，完成了多个数据科学相关的实战项目。在文书中成功解释了职业转变动机并展示了自学能力，最终被牛津大学数据科学硕士项目录取。",
                file_path="/success_cases/oxford_data_science_case.pdf"
            )
        ]
        db.add_all(success_cases)
        db.commit()
        print(f"已插入 {len(success_cases)} 个成功案例")
        
        print("\n=== 测试数据插入完成 ===")
        print(f"总计插入: {len([student_user, student_user2, student_user3, student_user4, student_user5, teacher_user, teacher_user2, teacher_user3, teacher_user4, admin_user])} 个用户")
        print(f"总计插入: {len(student_profiles)} 个学生信息")
        print(f"总计插入: {len(teacher_profiles)} 个教师信息")
        print(f"总计插入: {len(schools)} 个学校信息")
        print(f"总计插入: {len(majors)} 个学校专业排名信息")
        print(f"总计插入: {len(training_reservations)} 个语言培训预约")
        print(f"总计插入: {len(document_reservations)} 个文书润色预约")
        print(f"总计插入: {len(success_cases)} 个成功案例")
        
    except IntegrityError as e:
        db.rollback()
        print(f"\n错误: 数据插入失败，可能存在重复数据 - {str(e)}")
    except Exception as e:
        db.rollback()
        print(f"\n错误: 数据插入失败 - {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("开始初始化数据库和插入测试数据...")
    init_database()
    add_test_data()
    print("\n测试数据插入脚本执行完毕！")
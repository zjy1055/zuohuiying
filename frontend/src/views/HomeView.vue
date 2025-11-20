<template>
  <div class="home">

    <!-- 平台功能概览 -->
    <section class="services-section">
      <div class="container">
        <h2 class="section-title">核心服务</h2>
        <div class="services-grid">
          <!-- 智能学校推荐 -->
          <div class="service-card">
            <div class="service-icon">🔍🗺️</div>
            <h3 class="service-title">AI 匹配你的理想院校</h3>
            <p class="service-description">
              基于你的托福/GRE/GPA成绩和目标地区，智能计算录取概率，推荐最适配的院校清单。支持按专业、排名、地理位置筛选，附带详细录取要求和学长经验。
            </p>
            <button class="service-btn">立即注册，获取专属推荐</button>
          </div>

          <!-- 1对1语言培训 -->
          <div class="service-card">
            <div class="service-icon">👨‍🏫🎓</div>
            <h3 class="service-title">定制化语言提分计划</h3>
            <p class="service-description">
              根据你的薄弱项（听力/阅读/写作等）匹配资深教师，灵活预约课时，实时跟踪学习进度。支持托福、GRE等多类考试培训，过往学员平均提分15+。
            </p>
            <button class="service-btn">了解培训详情</button>
          </div>

          <!-- 文书润色服务 -->
          <div class="service-card">
            <div class="service-icon">📄✒️</div>
            <h3 class="service-title">让文书成为申请加分项</h3>
            <p class="service-description">
              资深留学文书导师1对1润色，涵盖个人陈述、推荐信等类型，突出你的学术优势和独特经历，规避申请雷区。支持多次修改，直至符合目标院校要求。
            </p>
            <button class="service-btn">查看文书案例</button>
          </div>
        </div>
      </div>
    </section>

    <!-- 数据看板 -->
    <section class="stats-section">
      <div class="container">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">10000+</div>
            <div class="stat-label">已服务学生</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">98%</div>
            <div class="stat-label">院校推荐匹配度</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">8年</div>
            <div class="stat-label">教师团队平均经验</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 用户评价轮播 -->
    <section class="testimonials-section">
      <div class="container">
        <h2 class="section-title">用户评价</h2>
        <div class="testimonial-carousel">
          <div class="testimonial-item active">
            <div class="testimonial-content">推荐的3所学校都拿到了offer！服务非常专业。</div>
            <div class="testimonial-author">- 张同学，美国top30录取</div>
          </div>
          <div class="testimonial-item">
            <div class="testimonial-content">老师的文书润色让我的申请材料提升了一个档次。</div>
            <div class="testimonial-author">- 李同学，英国G5录取</div>
          </div>
          <div class="testimonial-item">
            <div class="testimonial-content">培训课程很有针对性，托福从80分提到了105分！</div>
            <div class="testimonial-author">- 王同学，澳洲八大录取</div>
          </div>
        </div>
      </div>
    </section>

    
    

  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      currentTestimonial: 0
    }
  },
  mounted() {
    // 启动评价轮播
    this.startTestimonialCarousel()
  },
  beforeUnmount() {
    clearInterval(this.carouselInterval)
  },
  methods: {
    
    startTestimonialCarousel() {
      // 评价轮播
      this.carouselInterval = setInterval(() => {
        const testimonials = document.querySelectorAll('.testimonial-item')
        testimonials[this.currentTestimonial].classList.remove('active')
        this.currentTestimonial = (this.currentTestimonial + 1) % testimonials.length
        testimonials[this.currentTestimonial].classList.add('active')
      }, 3000)
    }
  }
}
</script>

<style scoped>
/* 全局样式重置 */
.home {
  min-height: 100vh;
  font-family: 'Arial', sans-serif;
  color: #333;
  padding-top: 80px; /* 为固定导航栏留出空间 */
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 2rem;
  color: #3498db;
}

.english-name {
  font-size: 0.9rem;
  color: #7f8c8d;
}

/* 导航链接 */
.nav-links {
  display: flex;
  gap: 30px;
}

.nav-item {
  position: relative;
  font-size: 1rem;
  color: #34495e;
  cursor: pointer;
  padding: 8px 0;
  transition: color 0.3s ease;
}

.nav-item:hover {
  color: #3498db;
}

/* 下拉菜单 */
.dropdown {
  position: relative;
}

.dropdown-content {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: white;
  min-width: 200px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px);
  transition: all 0.3s ease;
  z-index: 1001;
  display: flex;
}

.dropdown:hover .dropdown-content {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-section {
  padding: 10px 15px;
  min-width: 120px;
}

.dropdown-section h4 {
  margin: 0 0 10px 0;
  font-size: 0.9rem;
  color: #3498db;
}

.dropdown-section a {
  display: block;
  color: #34495e;
  text-decoration: none;
  padding: 5px 0;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.dropdown-section a:hover {
  color: #3498db;
}

/* 用户操作区 */
.user-actions {
  display: flex;
  gap: 10px;
}

.login-btn, .register-btn {
  padding: 8px 20px;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.login-btn {
  background-color: white;
  color: #34495e;
  border: 1px solid #ddd;
}

.login-btn:hover {
  background-color: #f8f9fa;
  border-color: #3498db;
}

.register-btn {
  background-color: #3498db;
  color: white;
}

.register-btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
}

/* 用户信息 */
.user-info {
  cursor: pointer;
  font-weight: bold;
}

.student-role {
  color: #27ae60;
}

.teacher-role {
  color: #e67e22;
}

/* 移动端用户信息 */
.mobile-user-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mobile-user-info .logout {
  color: #e74c3c;
  cursor: pointer;
}

/* 认证模态框 */
.auth-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.auth-modal-content {
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 12px;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 移动端菜单按钮 */
.mobile-menu-btn {
  display: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #34495e;
}

.mobile-menu {
  position: fixed;
  top: 70px;
  left: 0;
  right: 0;
  background-color: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-100%);
  transition: transform 0.3s ease;
  z-index: 999;
  max-height: 0;
  overflow: hidden;
}

.mobile-menu-open {
  transform: translateY(0);
  max-height: 500px;
}

/* 认证模态框样式 */
.auth-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  padding: 20px;
}

.auth-modal-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 450px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

/* 按钮样式调整 */
.btn-link {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  font-family: inherit;
  font-size: inherit;
  padding: inherit;
  text-decoration: none;
}

.btn-link:hover {
  text-decoration: underline;
}

/* 下拉菜单样式 */
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-menu {
  display: none;
  position: absolute;
  right: 0;
  background-color: white;
  min-width: 160px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  z-index: 1;
  border-radius: 4px;
  padding: 8px 0;
}

.dropdown:hover .dropdown-menu {
  display: block;
}

.dropdown-item {
  color: #333;
  padding: 12px 16px;
  text-decoration: none;
  display: block;
  width: 100%;
  text-align: left;
  border: none;
  background: none;
  cursor: pointer;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .auth-modal-content {
    margin: 10px;
  }
}

.mobile-nav-links {
  padding: 20px;
}

.mobile-nav-item {
  padding: 15px 0;
  border-bottom: 1px solid #eee;
  font-size: 1rem;
  color: #34495e;
  cursor: pointer;
  transition: color 0.3s ease;
}

.mobile-nav-item:hover {
  color: #3498db;
}

.mobile-nav-item:last-child {
  border-bottom: none;
}

/* 服务卡片区域 */
.services-section {
  padding: 100px 0 80px;
  background-color: #f8f9fa;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
}

.service-card {
  background-color: white;
  border-radius: 10px;
  padding: 30px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.service-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.12);
}

.service-icon {
  font-size: 3.5rem;
  margin-bottom: 20px;
}

.service-title {
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: #2c3e50;
}

.service-description {
  color: #7f8c8d;
  line-height: 1.6;
  margin-bottom: 20px;
  min-height: 100px;
}

.service-btn {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 25px;
    border-radius: 4px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .service-btn:hover {
    background-color: #2980b9;
    transform: translateY(-2px);
  }
  
  

/* 数据看板 */
.stats-section {
  padding: 60px 0;
  background-color: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
}

.stat-item {
  text-align: center;
  padding: 30px;
  background-color: #f8f9fa;
  border-radius: 10px;
  transition: transform 0.3s ease;
}

.stat-item:hover {
  transform: scale(1.05);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #3498db;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 1rem;
  color: #7f8c8d;
}

/* 用户评价 */
.testimonials-section {
  padding: 80px 0;
  background-color: #f8f9fa;
}

.testimonial-carousel {
  position: relative;
  max-width: 800px;
  margin: 0 auto;
  height: 200px;
  overflow: hidden;
}

.testimonial-item {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  padding: 30px;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  opacity: 0;
  transform: translateX(100%);
  transition: all 0.5s ease;
}

.testimonial-item.active {
  opacity: 1;
  transform: translateX(0);
}

.testimonial-content {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #34495e;
  margin-bottom: 20px;
  font-style: italic;
}

.testimonial-author {
  font-size: 0.9rem;
  color: #3498db;
  text-align: right;
}





/* 响应式设计 */
@media (max-width: 768px) {
  /* 导航栏 */
  .nav-links,
  .user-actions {
    display: none;
  }
  
  .mobile-menu-btn {
    display: block;
  }
  
  .logo {
    font-size: 2rem;
  }
  
  .chinese-name {
    font-size: 1rem;
  }
  
  .english-name {
    font-size: 0.8rem;
  }
  
  /* 服务卡片 */
  .services-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  /* 数据看板 */
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  /* 评价轮播 */
  .testimonial-carousel {
    height: 250px;
  }
  
  .testimonial-content {
    font-size: 1rem;
  }
  
  
}

@media (max-width: 1024px) and (min-width: 769px) {
  .services-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
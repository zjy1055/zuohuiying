<template>
  <div class="help-center-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>帮助中心</h1>
      <p>为您提供留学申请全方位支持和解答</p>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="search-box">
        <input 
          type="text" 
          placeholder="搜索您的问题..."
          class="search-input"
          v-model="searchQuery"
        />
        <button class="search-btn">🔍</button>
      </div>
    </div>

    <!-- 常见问题分类 -->
    <div class="faq-categories">
      <div 
        v-for="category in categories" 
        :key="category.id"
        class="category-card"
        @click="activeCategory = activeCategory === category.id ? null : category.id"
      >
        <div class="category-header">
          <h3>{{ category.title }}</h3>
          <span class="toggle-icon">{{ activeCategory === category.id ? '−' : '+' }}</span>
        </div>
        <div v-if="activeCategory === category.id" class="category-content">
          <div v-for="faq in category.faqs" :key="faq.id" class="faq-item">
            <div class="faq-question">{{ faq.question }}</div>
            <div class="faq-answer">{{ faq.answer }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 服务流程 -->
    <div class="service-process">
      <h2>留学服务流程</h2>
      <div class="process-steps">
        <div v-for="step in processSteps" :key="step.id" class="process-step">
          <div class="step-number">{{ step.number }}</div>
          <div class="step-content">
            <h4>{{ step.title }}</h4>
            <p>{{ step.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 联系方式 -->
    <div class="contact-section">
      <h2>联系我们</h2>
      <div class="contact-methods">
        <div class="contact-method">
          <div class="contact-icon">📞</div>
          <div class="contact-info">
            <h4>电话咨询</h4>
            <p>400-123-4567</p>
            <p>工作日 9:00-18:00</p>
          </div>
        </div>
        <div class="contact-method">
          <div class="contact-icon">✉️</div>
          <div class="contact-info">
            <h4>邮箱咨询</h4>
            <p>support@studyaid.com</p>
          </div>
        </div>
        <div class="contact-method">
          <div class="contact-icon">💬</div>
          <div class="contact-info">
            <h4>在线客服</h4>
            <p>点击右下角客服按钮</p>
            <p>工作日 9:00-21:00</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 留言反馈 -->
    <div class="feedback-section">
      <h2>留言反馈</h2>
      <form class="feedback-form">
        <div class="form-group">
          <label for="name">姓名</label>
          <input type="text" id="name" placeholder="请输入您的姓名">
        </div>
        <div class="form-group">
          <label for="email">邮箱</label>
          <input type="email" id="email" placeholder="请输入您的邮箱">
        </div>
        <div class="form-group">
          <label for="message">留言内容</label>
          <textarea id="message" rows="5" placeholder="请输入您的问题或建议"></textarea>
        </div>
        <button type="submit" class="submit-btn">提交留言</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HelpCenter',
  data() {
    return {
      searchQuery: '',
      activeCategory: null,
      categories: [
        {
          id: 1,
          title: '申请准备',
          faqs: [
            {
              id: 1,
              question: '申请留学需要准备哪些材料？',
              answer: '申请留学通常需要准备：个人简历、推荐信、个人陈述、成绩单、语言成绩（如托福、雅思）、护照复印件、资金证明等。具体要求因国家和学校而异。'
            },
            {
              id: 2,
              question: '语言成绩有效期是多久？',
              answer: '一般来说，托福成绩有效期为2年，雅思成绩有效期也为2年。建议尽早准备并在有效期内提交申请。'
            },
            {
              id: 3,
              question: 'GPA达到多少才能申请好的大学？',
              answer: '不同国家和学校对GPA要求不同。一般来说，申请美国TOP50大学建议GPA 3.5以上，英国G5大学建议均分85以上。但GPA只是参考因素之一，学校还会综合考虑其他方面。'
            }
          ]
        },
        {
          id: 2,
          title: '选校与专业',
          faqs: [
            {
              id: 4,
              question: '如何选择适合自己的学校和专业？',
              answer: '选校应综合考虑：学校排名、专业实力、地理位置、学费、就业前景等因素。建议先确定专业方向，再根据自身条件选择匹配的学校。'
            },
            {
              id: 5,
              question: '可以同时申请多个学校吗？',
              answer: '可以。通常建议申请5-8所学校，包括冲刺、匹配和保底三个层次，以增加录取概率。'
            }
          ]
        },
        {
          id: 3,
          title: '签证与行前准备',
          faqs: [
            {
              id: 6,
              question: '拿到录取通知书后多久可以开始签证申请？',
              answer: '建议在拿到录取通知书后尽快准备签证材料，一般提前1-2个月申请签证较为合适，以避开签证高峰期。'
            },
            {
              id: 7,
              question: '留学行前需要准备哪些物品？',
              answer: '基本物品包括：护照、录取通知书、机票、住宿确认单、资金证明、转换插头、常用药品、适量衣物等。具体可根据留学国家的气候和个人需求调整。'
            }
          ]
        },
        {
          id: 4,
          title: '费用与奖学金',
          faqs: [
            {
              id: 8,
              question: '留学费用包括哪些部分？',
              answer: '留学费用主要包括：学费、住宿费、生活费、医疗保险费、交通费、签证费、语言考试费等。不同国家和地区的费用差异较大。'
            },
            {
              id: 9,
              question: '如何申请奖学金？',
              answer: '奖学金申请通常需要：优秀的学术成绩、语言成绩、个人陈述、推荐信等。部分奖学金需要单独申请，有些则会自动考虑。建议提前了解目标学校的奖学金政策。'
            }
          ]
        }
      ],
      processSteps: [
        {
          id: 1,
          number: '01',
          title: '免费咨询评估',
          description: '专业顾问为您进行留学规划评估，了解您的背景和需求，制定初步方案。'
        },
        {
          id: 2,
          number: '02',
          title: '签约服务',
          description: '确认合作意向，签订服务合同，支付服务费用，正式开始留学申请服务。'
        },
        {
          id: 3,
          number: '03',
          title: '规划与准备',
          description: '根据您的情况制定详细申请规划，包括选校方案、材料准备计划和时间节点。'
        },
        {
          id: 4,
          number: '04',
          title: '文书撰写',
          description: '专业文书团队协助您完成个人陈述、推荐信等申请材料的撰写和修改。'
        },
        {
          id: 5,
          number: '05',
          title: '院校申请',
          description: '按照学校要求提交申请，跟进申请状态，协助解决申请过程中的问题。'
        },
        {
          id: 6,
          number: '06',
          title: '签证办理',
          description: '提供签证材料准备指导，进行签证面试培训，协助完成签证申请。'
        },
        {
          id: 7,
          number: '07',
          title: '行前准备',
          description: '提供行前指导，包括住宿安排、机票预订、生活常识等信息。'
        },
        {
          id: 8,
          number: '08',
          title: '境外服务',
          description: '提供接机、住宿安置、入学注册等境外服务，帮助您顺利开始留学生活。'
        }
      ]
    }
  }
}
</script>

<style scoped>
.help-center-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Arial', sans-serif;
  color: #333;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 10px;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-header p {
  font-size: 1.1rem;
  color: #7f8c8d;
}

/* 搜索区域 */
.search-section {
  margin-bottom: 40px;
  text-align: center;
}

.search-box {
  display: inline-flex;
  max-width: 600px;
  width: 100%;
}

.search-input {
  flex: 1;
  padding: 12px 20px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-radius: 25px 0 0 25px;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #3498db;
}

.search-btn {
  padding: 12px 24px;
  font-size: 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 0 25px 25px 0;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-btn:hover {
  background-color: #2980b9;
}

/* 常见问题分类 */
.faq-categories {
  margin-bottom: 60px;
}

.category-card {
  margin-bottom: 20px;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background-color: #3498db;
  color: white;
  cursor: pointer;
}

.category-header h3 {
  margin: 0;
  font-size: 1.3rem;
}

.toggle-icon {
  font-size: 1.5rem;
  font-weight: bold;
  transition: transform 0.3s;
}

.category-content {
  padding: 20px;
  background-color: #f9f9f9;
}

.faq-item {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.faq-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.faq-question {
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 1.1rem;
}

.faq-answer {
  color: #7f8c8d;
  line-height: 1.6;
}

/* 服务流程 */
.service-process {
  margin-bottom: 60px;
}

.service-process h2 {
  text-align: center;
  margin-bottom: 40px;
  color: #2c3e50;
  font-size: 2rem;
}

.process-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.process-step {
  display: flex;
  background-color: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
}

.process-step:hover {
  transform: translateY(-5px);
}

.step-number {
  font-size: 2rem;
  font-weight: bold;
  color: #3498db;
  margin-right: 20px;
  line-height: 1;
}

.step-content h4 {
  margin-top: 0;
  color: #2c3e50;
}

.step-content p {
  color: #7f8c8d;
  line-height: 1.6;
}

/* 联系方式 */
.contact-section {
  margin-bottom: 60px;
}

.contact-section h2 {
  text-align: center;
  margin-bottom: 40px;
  color: #2c3e50;
  font-size: 2rem;
}

.contact-methods {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.contact-method {
  display: flex;
  align-items: center;
  background-color: #f8f9fa;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.contact-icon {
  font-size: 2.5rem;
  margin-right: 20px;
}

.contact-info h4 {
  margin-top: 0;
  color: #2c3e50;
  margin-bottom: 10px;
}

.contact-info p {
  margin: 5px 0;
  color: #7f8c8d;
}

/* 留言反馈 */
.feedback-section {
  margin-bottom: 60px;
}

.feedback-section h2 {
  text-align: center;
  margin-bottom: 40px;
  color: #2c3e50;
  font-size: 2rem;
}

.feedback-form {
  max-width: 800px;
  margin: 0 auto;
  background-color: #fff;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #2c3e50;
  font-weight: bold;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 5px;
  outline: none;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #3498db;
}

.submit-btn {
  display: block;
  width: 100%;
  padding: 15px;
  font-size: 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover {
  background-color: #2980b9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }
  
  .process-steps,
  .contact-methods {
    grid-template-columns: 1fr;
  }
  
  .contact-method {
    flex-direction: column;
    text-align: center;
  }
  
  .contact-icon {
    margin-right: 0;
    margin-bottom: 15px;
  }
}
</style>
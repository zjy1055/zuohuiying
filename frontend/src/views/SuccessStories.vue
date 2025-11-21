<template>
  <div class="success-stories-container">
    <!-- 页面标题部分 -->
    <div class="page-header">
      <h1>成功案例</h1>
      <p>真实留学成功案例，助您把握申请方向</p>
    </div>

    <!-- 筛选部分 -->
    <div class="filter-section">
      <div class="filter-tabs">
        <button 
          v-for="tab in filterTabs" 
          :key="tab.value"
          :class="['filter-tab', { active: activeFilter === tab.value }]"
          @click="activeFilter = tab.value"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- 案例展示部分 -->
    <div class="stories-grid">
      <div 
        v-for="story in filteredStories" 
        :key="story.id"
        class="story-card"
        @click="showStoryDetails(story.id)"
      >
        <div class="story-image">
          <img :src="getStoryImage(story.id)" :alt="story.title">
        </div>
        <div class="story-content">
          <div class="story-badge">{{ story.country }}</div>
          <h3 class="story-title">{{ story.title }}</h3>
          <p class="story-summary">{{ story.summary }}</p>
          <div class="story-meta">
            <span class="university">{{ story.university }}</span>
            <span class="date">{{ story.date }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 案例详情模态框 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <button class="close-btn" @click="closeModal">×</button>
        <div v-if="currentStory" class="story-details">
          <h2>{{ currentStory.title }}</h2>
          <div class="story-badges">
            <span class="badge country">{{ currentStory.country }}</span>
            <span class="badge university">{{ currentStory.university }}</span>
          </div>
          <div class="story-full-content">
            <img :src="getStoryImage(currentStory.id)" :alt="currentStory.title" class="detail-image">
            <div class="student-info">
              <h4>学生背景</h4>
              <p>{{ currentStory.background }}</p>
            </div>
            <div class="application-process">
              <h4>申请过程</h4>
              <p>{{ currentStory.process }}</p>
            </div>
            <div class="experience-sharing">
              <h4>经验分享</h4>
              <p>{{ currentStory.sharing }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SuccessStories',
  data() {
    return {
      activeFilter: 'all',
      filterTabs: [
        { label: '全部案例', value: 'all' },
        { label: '美国', value: 'usa' },
        { label: '英国', value: 'uk' },
        { label: '澳大利亚', value: 'australia' },
        { label: '加拿大', value: 'canada' }
      ],
      showModal: false,
      currentStory: null,
      stories: [
        {
          id: 1,
          title: '从国内普通本科到美国藤校金融学硕士',
          summary: '李同学通过精准规划和专业指导，成功申请到哥伦比亚大学金融学硕士项目。',
          country: '美国',
          university: '哥伦比亚大学',
          date: '2024-03',
          background: '李同学毕业于国内一所非985/211的财经类院校，GPA 3.7，托福108分，GRE 325分。本科期间有两次相关实习经历。',
          process: '我们为李同学制定了详细的申请规划，包括提升学术背景、丰富实习经历、优化文书质量等方面。通过多次修改和完善个人陈述，突出了学生的学术潜力和职业规划。',
          sharing: '建议申请者提前1-2年开始准备，注重实习经历的质量而非数量，在文书中真实展现自己的独特视角和职业目标。'
        },
        {
          id: 2,
          title: '转专业申请英国顶尖大学计算机科学硕士',
          summary: '张同学从英语专业成功转专业申请到帝国理工学院计算机科学硕士项目。',
          country: '英国',
          university: '帝国理工学院',
          date: '2024-02',
          background: '张同学本科就读于北京外国语大学英语专业，GPA 3.8，雅思8.0分。自学了多门计算机课程并获得相关证书。',
          process: '我们帮助张同学规划了一系列在线课程和项目实践，弥补了专业背景的不足。在申请文书中强调了学生的学习能力和对计算机科学的热情，同时提供了详细的学习计划。',
          sharing: '转专业申请需要提前规划课程学习，参加相关实践项目，在文书中清晰展示自己的知识储备和学习能力。'
        },
        {
          id: 3,
          title: '低分逆袭澳洲八大名校商科硕士',
          summary: '王同学以GPA 3.2的成绩成功申请到墨尔本大学商业分析硕士项目。',
          country: '澳大利亚',
          university: '墨尔本大学',
          date: '2023-12',
          background: '王同学毕业于上海财经大学市场营销专业，GPA 3.2，雅思7.5分。有三段市场营销相关实习经历。',
          process: '我们重点突出了王同学丰富的实习经历和项目成果，在文书中展示了学生在实际工作中的分析能力和解决问题的能力。同时，通过专业的申请策略，成功说服了招生官。',
          sharing: '成绩不是唯一的评判标准，丰富的实习经历和实际项目成果同样重要，在申请中要突出自己的实践能力。'
        },
        {
          id: 4,
          title: '非英语专业申请加拿大多伦多大学教育学硕士',
          summary: '刘同学从历史专业成功申请到多伦多大学教育学硕士项目。',
          country: '加拿大',
          university: '多伦多大学',
          date: '2024-01',
          background: '刘同学毕业于南京大学历史专业，GPA 3.6，托福105分。在校期间参与了多个教育相关的志愿者活动。',
          process: '我们帮助刘同学将历史专业背景与教育学相结合，在文书中展示了学生对教育研究的独特见解。同时，通过志愿者经历证明了学生对教育事业的热情。',
          sharing: '跨专业申请时，可以寻找专业之间的联系点，将原有专业背景转化为优势，展示自己的多元视角。'
        },
        {
          id: 5,
          title: '本科应届生申请美国常春藤名校法律硕士',
          summary: '陈同学作为本科应届生成功申请到耶鲁大学法律硕士项目。',
          country: '美国',
          university: '耶鲁大学',
          date: '2024-04',
          background: '陈同学毕业于北京大学法学专业，GPA 3.9，托福115分，LSAT 175分。在校期间发表了两篇学术论文。',
          process: '我们为陈同学提供了专业的LSAT备考指导，并帮助优化了个人陈述和推荐信。通过强调学生的学术成就和对法律的独特见解，成功吸引了招生官的注意。',
          sharing: '学术成绩和标准化考试分数是申请顶尖法学院的基础，同时要有明确的职业规划和对法律的深刻理解。'
        },
        {
          id: 6,
          title: '工作三年后申请英国剑桥大学MBA',
          summary: '赵同学拥有三年工作经验，成功申请到剑桥大学MBA项目。',
          country: '英国',
          university: '剑桥大学',
          date: '2023-11',
          background: '赵同学毕业于清华大学经济学专业，GPA 3.5，GMAT 720分，在咨询公司工作了三年。',
          process: '我们帮助赵同学梳理了工作经历，突出了在咨询项目中的领导能力和问题解决能力。通过多次面试辅导，提升了学生的沟通表达能力和案例分析能力。',
          sharing: 'MBA申请注重工作经验的质量和个人成长，面试准备非常重要，需要展示自己的领导潜力和职业规划。'
        }
      ]
    }
  },
  computed: {
    filteredStories() {
      if (this.activeFilter === 'all') {
        return this.stories;
      }
      const countryMap = {
        'usa': '美国',
        'uk': '英国',
        'australia': '澳大利亚',
        'canada': '加拿大'
      };
      return this.stories.filter(story => story.country === countryMap[this.activeFilter]);
    }
  },
  methods: {
    getStoryImage(id) {
      // 使用占位图片服务
      return `https://picsum.photos/seed/${id + 100}/800/500`;
    },
    showStoryDetails(id) {
      this.currentStory = this.stories.find(story => story.id === id);
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
      this.currentStory = null;
    }
  }
}
</script>

<style scoped>
.success-stories-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 80px);
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
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

.filter-section {
  margin-bottom: 30px;
}

.filter-tabs {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-tab {
  padding: 10px 20px;
  background-color: #f5f5f5;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.filter-tab:hover {
  background-color: #e0e0e0;
}

.filter-tab.active {
  background-color: #3498db;
  color: white;
}

.stories-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 30px;
  }

.story-card {
  background-color: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

.story-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.story-image {
  height: 200px;
  overflow: hidden;
}

.story-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.story-card:hover .story-image img {
  transform: scale(1.05);
}

.story-content {
  padding: 20px;
}

.story-badge {
  display: inline-block;
  background-color: #3498db;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  margin-bottom: 10px;
}

.story-title {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 10px;
  line-height: 1.4;
}

.story-summary {
  color: #7f8c8d;
  font-size: 0.95rem;
  line-height: 1.6;
  margin-bottom: 15px;
}

.story-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #95a5a6;
}

.university {
  font-weight: 500;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background-color: white;
  border-radius: 10px;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
  padding: 5px;
  transition: color 0.3s ease;
}

.close-btn:hover {
  color: #2c3e50;
}

.story-details h2 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin-bottom: 15px;
}

.story-badges {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.badge {
  padding: 5px 15px;
  border-radius: 15px;
  font-size: 0.85rem;
}

.badge.country {
  background-color: #3498db;
  color: white;
}

.badge.university {
  background-color: #2ecc71;
  color: white;
}

.detail-image {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 20px;
}

.story-full-content h4 {
  font-size: 1.2rem;
  color: #34495e;
  margin: 20px 0 10px 0;
}

.story-full-content p {
  line-height: 1.7;
  color: #5a6c7d;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stories-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    padding: 20px;
  }
  
  .story-details h2 {
    font-size: 1.5rem;
  }
}
</style>
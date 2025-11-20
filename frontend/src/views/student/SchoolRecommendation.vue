<template>
  <div class="school-recommendation">
    <h2>学校推荐</h2>
    <div class="recommendation-content">
      <!-- 学校列表展示 -->
      <div v-if="schools.length > 0" class="school-list">
        <div v-for="school in schools" :key="school.id" class="school-card">
          <div class="school-header">
            <h3>{{ school.chinese_name }}</h3>
            <p class="english-name">{{ school.english_name }}</p>
          </div>
          <div class="school-info">
            <div class="info-item">
              <span class="label">排名：</span>
              <span class="value">{{ school.ranking }}</span>
            </div>
            <div class="info-item">
              <span class="label">地点：</span>
              <span class="value">{{ school.location }}</span>
            </div>
            <div class="info-item">
              <span class="label">推荐分数：</span>
              <span class="value score">{{ school.recommendation_score }}</span>
            </div>
          </div>
          <div class="school-majors">
            <h4>推荐专业</h4>
            <ul>
              <li v-for="(major, index) in school.majors" :key="index">
                {{ major.major_name }} (排名：{{ major.major_rank }})
              </li>
            </ul>
          </div>
          <div class="school-intro">
            <p>{{ school.introduction }}</p>
          </div>
        </div>
      </div>
      
      <!-- 未完善成绩提示 -->
      <div v-else-if="!hasScores" class="no-scores-tip">
        <p>{{ error }}</p>
        <button @click="$router.push('/student/profile')" class="btn-primary">
          去完善成绩
        </button>
      </div>
      
      <!-- 无推荐学校 -->
      <div v-else-if="!loading && schools.length === 0 && !error" class="no-recommendations">
        <p>暂无推荐学校</p>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-spinner">
        <div class="spinner"></div>
        <p>正在获取推荐学校...</p>
      </div>
      
      <!-- 错误信息显示 -->
      <div v-if="error && hasScores" class="error-message">
        <p>{{ error }}</p>
        <button @click="fetchSchoolRecommendations()" class="btn-secondary">
          重试
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SchoolRecommendation',
  data() {
    return {
      schools: [], // 推荐学校列表
      loading: false, // 加载状态
      error: null, // 错误信息
      hasScores: true // 是否已有完整的成绩信息
    }
  },
  methods: {
    // 获取认证令牌
    getAuthToken() {
      const accessToken = localStorage.getItem('access_token');
      return accessToken ? `Bearer ${accessToken}` : null;
    },
    
    // 获取学校推荐列表
    async fetchSchoolRecommendations() {
      const token = this.getAuthToken();
      if (!token) {
        this.error = '请先登录';
        return;
      }
      
      this.loading = true;
      this.error = null;
      
      try {
        const response = await fetch('http://localhost:8000/student/recommendation', {
          method: 'GET',
          headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          if (response.status === 400) {
            this.hasScores = false;
            this.error = '请先完善托福、GRE、GPA成绩';
          } else if (response.status === 401) {
            this.error = '认证失败，请重新登录';
          } else {
            this.error = '获取学校推荐失败';
          }
          return;
        }
        
        const data = await response.json();
        this.schools = data;
      } catch (err) {
        this.error = '网络错误，请稍后重试';
        console.error('Error fetching school recommendations:', err);
      } finally {
        this.loading = false;
      }
    }
  },
  
  mounted() {
    // 获取学校推荐列表
    this.fetchSchoolRecommendations();
  }
}
</script>

<style scoped>
.school-recommendation {
  padding: 20px;
  max-width: 1200px;
  margin: 0 10px;
}

h2 {
  color: #333;
  margin-bottom: 30px;
  text-align: center;
  font-size: 28px;
}

.recommendation-content {
  margin-top: 20px;
}

/* 学校列表样式 */
.school-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.school-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 15px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.school-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.12);
}

.school-header h3 {
  margin: 0 0 4px 0;
  color: #2c3e50;
  font-size: 18px;
  line-height: 1.3;
}

.english-name {
  color: #7f8c8d;
  font-style: italic;
  margin: 0 0 10px 0;
  font-size: 13px;
  line-height: 1.4;
}

.school-info {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
  font-size: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  background: #f8f9fa;
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.info-item .label {
  color: #7f8c8d;
  margin-right: 3px;
  font-size: 12px;
}

.info-item .value {
  color: #2c3e50;
  font-weight: 500;
  font-size: 12px;
}

.info-item .score {
  color: #e74c3c;
  font-weight: bold;
  font-size: 13px;
}

.school-majors {
  margin-bottom: 10px;
  flex: 1;
}

.school-majors h4 {
  margin: 0 0 6px 0;
  color: #34495e;
  font-size: 14px;
}

.school-majors ul {
  margin: 0;
  padding-left: 16px;
}

.school-majors li {
  color: #7f8c8d;
  font-size: 12px;
  margin-bottom: 3px;
  line-height: 1.3;
}

.school-intro {
  color: #555;
  font-size: 12px;
  line-height: 1.5;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  margin-top: auto;
}

/* 提示和错误样式 */
.no-scores-tip,
.no-recommendations,
.error-message {
  text-align: center;
  padding: 40px 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 20px;
}

.no-scores-tip p,
.no-recommendations p,
.error-message p {
  color: #7f8c8d;
  margin-bottom: 20px;
  font-size: 16px;
}

/* 按钮样式 */
.btn-primary,
.btn-secondary {
  padding: 10px 25px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

/* 加载状态样式 */
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-spinner p {
  color: #7f8c8d;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .school-list {
    grid-template-columns: repeat(auto-fit, minmax(260px, 3fr));
  }
}

@media (max-width: 1500px) {
  .school-list {
    grid-template-columns: repeat(auto-fit, minmax(240px, 3fr));
  }
  
  .school-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
  
  .school-header h3 {
    font-size: 16px;
  }
  
  .english-name {
    font-size: 12px;
  }
}

@media (max-width: 1000px) {
  .school-list {
    grid-template-columns: 3fr;
  }
  
  .school-card {
    padding: 12px;
  }
}
</style>
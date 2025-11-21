<template>
  <div class="teacher-statistics">
    <h2 class="page-title">学生统计信息</h2>
    
    <!-- 加载状态 -->
    <div class="loading-state" v-if="loading">
      <div class="loading-spinner"></div>
      <p>正在加载统计数据...</p>
    </div>
    
    <!-- 错误状态 -->
    <div class="error-state" v-else-if="error">
      <div class="error-icon">⚠️</div>
      <p>{{ error }}</p>
      <button class="retry-btn" @click="fetchStudentStatistics">重试</button>
    </div>
    
    <!-- 统计数据展示 -->
    <div v-else class="statistics-container">
      <!-- 基础统计卡片 -->
      <div class="statistics-grid">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <h3 class="stat-title">学生总数</h3>
            <div class="stat-value">{{ statistics.total_count }}</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">👨</div>
          <div class="stat-content">
            <h3 class="stat-title">男性学生</h3>
            <div class="stat-value">{{ statistics.male_count }}</div>
            <div class="stat-percentage">{{ calculatePercentage(statistics.male_count, statistics.total_count) }}%</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">👩</div>
          <div class="stat-content">
            <h3 class="stat-title">女性学生</h3>
            <div class="stat-value">{{ statistics.female_count }}</div>
            <div class="stat-percentage">{{ calculatePercentage(statistics.female_count, statistics.total_count) }}%</div>
          </div>
        </div>
      </div>
      
      <!-- 成绩统计卡片 -->
      <div class="statistics-grid">
        <div class="stat-card">
          <div class="stat-icon">📚</div>
          <div class="stat-content">
            <h3 class="stat-title">平均托福成绩</h3>
            <div class="stat-value">{{ statistics.average_toefl }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🎯</div>
          <div class="stat-content">
            <h3 class="stat-title">平均GRE成绩</h3>
            <div class="stat-value">{{ statistics.average_gre }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <h3 class="stat-title">平均GPA成绩</h3>
            <div class="stat-value">{{ statistics.average_gpa }}</div>
          </div>
        </div>
      </div>
      
      <!-- 刷新按钮 -->
      <div class="refresh-section">
        <button class="refresh-btn" @click="fetchStudentStatistics">
          🔄 刷新统计数据
        </button>
        <p class="update-time">更新时间: {{ updateTime }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TeacherStatistics',
  data() {
    return {
      statistics: {
        total_count: 0,
        male_count: 0,
        female_count: 0,
        average_toefl: 0,
        average_gre: 0,
        average_gpa: 0
      },
      loading: false,
      error: '',
      updateTime: ''
    }
  },
  mounted() {
    // 组件挂载时获取统计数据
    this.fetchStudentStatistics()
  },
  methods: {
    // 获取学生统计信息
    async fetchStudentStatistics() {
      this.loading = true
      this.error = ''
      
      try {
        // 获取认证令牌
        const token = this.getAuthToken()
        if (!token) {
          throw new Error('未找到认证信息，请重新登录')
        }
        
        console.log('Token exists:', !!token);
        const response = await fetch('http://localhost:8000/teacher/statistics/student', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('未认证，请重新登录')
          } else if (response.status === 403) {
            throw new Error('无权限访问此资源')
          } else {
            throw new Error(`获取统计数据失败: ${response.status}`)
          }
        }
        
        const data = await response.json()
        this.statistics = data
        
        // 更新时间
        this.updateTime = this.formatDateTime(new Date())
      } catch (err) {
        this.error = err.message
        console.error('获取学生统计信息失败:', err)
      } finally {
        this.loading = false
      }
    },
    
    // 计算百分比
    calculatePercentage(value, total) {
      if (total === 0) return 0
      return ((value / total) * 100).toFixed(1)
    },
    
    // 格式化日期时间
    formatDateTime(date) {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      const seconds = String(date.getSeconds()).padStart(2, '0')
      
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    },
    
    // 获取认证令牌
    getAuthToken() {
      try {
        // 尝试从多个可能的位置获取token
        // 1. 从userInfo对象中获取
        const userInfoStr = localStorage.getItem('userInfo')
        if (userInfoStr) {
          const userInfo = JSON.parse(userInfoStr)
          if (userInfo.access_token) {
            return userInfo.access_token
          }
        }
        // 2. 直接从localStorage获取access_token
        const accessToken = localStorage.getItem('access_token')
        if (accessToken) {
          return accessToken
        }
        // 3. 尝试从token字段获取
        const token = localStorage.getItem('token')
        if (token) {
          return token
        }
        console.warn('未找到认证令牌')
        return null
      } catch (e) {
        console.error('获取认证令牌失败:', e)
        return null
      }
    }
  }
}
</script>

<style scoped>
.teacher-statistics {
  background-color: #f5f7fa;
  min-height: 100%;
}

.page-title {
  margin-bottom: 24px;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

/* 加载状态样式 */
.loading-state {
  text-align: center;
  padding: 60px 0;
  color: #666;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3f51b5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误状态样式 */
.error-state {
  text-align: center;
  padding: 60px 0;
  color: #e53935;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.error-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.retry-btn {
  margin-top: 16px;
  padding: 10px 20px;
  background-color: #3f51b5;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-size: 14px;
}

.retry-btn:hover {
  background-color: #303f9f;
}

/* 统计容器样式 */
.statistics-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 统计卡片网格布局 */
.statistics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

/* 统计卡片样式 */
.stat-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 24px;
  display: flex;
  align-items: center;
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  font-size: 48px;
  margin-right: 20px;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border-radius: 50%;
}

.stat-content {
  flex: 1;
}

.stat-title {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.stat-percentage {
  font-size: 14px;
  color: #3f51b5;
  font-weight: 500;
}

/* 刷新按钮区域 */
.refresh-section {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.refresh-btn {
  padding: 10px 20px;
  background-color: #3f51b5;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.refresh-btn:hover {
  background-color: #303f9f;
}

.update-time {
  margin: 0;
  color: #666;
  font-size: 14px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .statistics-grid {
    grid-template-columns: 1fr;
  }
  
  .refresh-section {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
}
</style>
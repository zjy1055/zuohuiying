<template>
  <div class="success-cases">
    <h2>成功案例</h2>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <p>正在加载案例列表...</p>
    </div>
    
    <!-- 错误提示 -->
    <div v-else-if="error" class="error-state">
      <p class="error-message">{{ error }}</p>
      <button class="retry-btn" @click="fetchSuccessCases">重试</button>
    </div>
    
    <!-- 空状态 -->
    <div v-else-if="cases.length === 0" class="empty-state">
      <p>暂无成功案例</p>
    </div>
    
    <!-- 案例列表 -->
    <div v-else class="cases-content">
      <div class="case-card" v-for="caseItem in cases" :key="caseItem.id">
        <div class="case-header">
          <h3 class="case-title">{{ caseItem.title }}</h3>
          <span v-if="caseItem.has_file" class="file-indicator">
            <i class="file-icon">📄</i>
          </span>
        </div>
        <div class="case-content">
          <p class="case-summary">{{ caseItem.content.length > 100 ? caseItem.content.substring(0, 100) + '...' : caseItem.content }}</p>
        </div>
        <div class="case-footer">
          <button class="view-btn" @click="viewCaseDetail(caseItem.id)">查看详情</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SuccessCases',
  data() {
    return {
      cases: [],
      loading: false,
      error: ''
    }
  },
  mounted() {
    this.fetchSuccessCases();
  },
  methods: {
    async fetchSuccessCases() {
      this.loading = true;
      this.error = '';
      
      try {
        // 获取access_token
        const accessToken = localStorage.getItem('access_token') || localStorage.getItem('token');
        
        // 调用API获取成功案例列表
        const response = await fetch('http://localhost:8000/student/success-cases', {
          headers: {
            'Authorization': accessToken ? `Bearer ${accessToken}` : ''
          }
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          let errorData = {};
          try {
            errorData = JSON.parse(errorText);
          } catch (e) {
            console.error('解析错误响应失败:', errorText);
          }
          throw new Error(errorData.detail || `获取失败: ${response.status}`);
        }
        
        this.cases = await response.json();
        console.log('成功获取案例列表:', this.cases);
      } catch (err) {
        this.error = err.message || '获取案例列表失败';
        console.error('获取案例列表错误:', err);
      } finally {
        this.loading = false;
      }
    },
    
    viewCaseDetail(caseId) {
      // 这里可以实现查看详情的逻辑，例如导航到详情页
      console.log('查看案例详情:', caseId);
      // 示例: this.$router.push(`/student/case-detail/${caseId}`);
    }
  }
}
</script>

<style scoped>
.success-cases {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h2 {
  color: #333;
  font-size: 24px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 10px;
}

/* 状态样式 */
.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-top: 20px;
}

.error-message {
  color: #e74c3c;
  margin-bottom: 15px;
}

.retry-btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.retry-btn:hover {
  background-color: #2980b9;
}

/* 案例列表样式 */
.cases-content {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.case-card {
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.case-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.case-title {
  font-size: 18px;
  color: #2c3e50;
  margin: 0;
  flex: 1;
  margin-right: 10px;
}

.file-indicator {
  display: flex;
  align-items: center;
}

.file-icon {
  font-size: 20px;
}

.case-content {
  margin-bottom: 15px;
}

.case-summary {
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.case-footer {
  text-align: right;
}

.view-btn {
  background-color: #27ae60;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.view-btn:hover {
  background-color: #229954;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .cases-content {
    grid-template-columns: 1fr;
  }
  
  .case-header {
    flex-direction: column;
  }
  
  .file-indicator {
    margin-top: 8px;
  }
}
</style>
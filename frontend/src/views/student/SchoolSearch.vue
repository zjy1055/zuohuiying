<template>
  <div class="school-search">
    <h2>学校查询</h2>
    <div class="search-content">
      <!-- 搜索表单 -->
      <div class="search-form">
        <div class="form-group">
          <label for="schoolName">学校名称</label>
          <input 
            id="schoolName" 
            v-model="searchParams.name" 
            type="text" 
            placeholder="输入学校名称关键词"
          />
        </div>
        
        <div class="form-group">
          <label for="region">地区</label>
          <input 
            id="region" 
            v-model="searchParams.region" 
            type="text" 
            placeholder="输入地区关键词"
          />
        </div>
        <button class="search-button" @click="searchSchools">搜索</button>
      </div>
      
      <!-- 学校列表 -->
      <div class="schools-list" v-if="schools.length > 0">
        <h3>搜索结果 ({{ schools.length }})</h3>
        <div class="school-card" v-for="school in schools" :key="school.id">
          <!-- 卡片头部：学校名称和排名 -->
          <div class="card-header">
            <h3 class="school-name">{{ school.chinese_name }}<span class="english-name">{{ school.english_name }}</span></h3>
            <div class="ranking-badge">全球排名: {{ school.ranking }}</div>
          </div>
          
          <!-- 学校基本信息 -->
          <div class="card-content">
            <!-- 位置信息 -->
            <div class="info-section">
              <div class="info-item location">
                <span class="info-label">地点:</span>
                <span class="info-value">{{ school.location }}</span>
              </div>
            </div>
            
            <!-- 专业信息 -->
            <div class="info-section">
              <div class="info-item majors">
                <span class="info-label">优势专业:</span>
                <div class="majors-container">
                  <span v-for="(major, index) in parseMajors(school.majors)" :key="index" class="major-tag">
                    {{ major.major_name }} ({{ major.major_rank }}名)
                  </span>
                </div>
              </div>
            </div>
            
            <!-- 学校简介 -->
            <div class="info-section">
              <div class="info-item description">
                <span class="info-label">学校简介:</span>
                <p class="school-description">{{ school.introduction }}</p>
              </div>
            </div>
            
            <!-- 查看详情按钮 -->
            <div class="action-section">
              <button class="view-details-btn" @click="viewSchoolDetails(school.id)">查看详情</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 无搜索结果 -->
      <div class="no-results" v-else-if="!hasResults">
        <p>未找到符合条件的学校，请尝试其他搜索条件</p>
      </div>
      
      <!-- 加载状态 -->
      <div class="loading-indicator" v-if="loading">
        <div class="spinner"></div>
        <p>正在搜索学校，请稍候...</p>
      </div>
      
      <!-- 错误信息 -->
      <div class="error-message" v-if="error">
        <p>{{ error }}</p>
        <button class="retry-button" @click="searchSchools">重试</button>
      </div>
    </div>
    
    <!-- 学校详情模态框 -->
    <div class="modal-overlay" v-if="showModal" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ schoolDetails.chinese_name }}<span v-if="schoolDetails.english_name" class="modal-english-name">{{ schoolDetails.english_name }}</span></h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="loadingDetails" class="modal-loading">
            <div class="spinner"></div>
            <p>加载详情中...</p>
          </div>
          <div v-else-if="modalError" class="modal-error">
            <p>{{ modalError }}</p>
            <button class="retry-btn" @click="fetchSchoolDetails(selectedSchoolId)">重试</button>
          </div>
          <div v-else class="school-details-content">
            <!-- 基本信息 -->
            <div class="details-section">
              <h4>基本信息</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <span class="detail-label">全球排名:</span>
                  <span class="detail-value">{{ schoolDetails.ranking }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">地点:</span>
                  <span class="detail-value">{{ schoolDetails.location }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">成立时间:</span>
                  <span class="detail-value">{{ schoolDetails.established_year || '未知' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">学生人数:</span>
                  <span class="detail-value">{{ schoolDetails.student_count || '未知' }}</span>
                </div>
              </div>
            </div>
            
            <!-- 优势专业 -->
            <div class="details-section">
              <h4>优势专业</h4>
              <div class="majors-container">
                <span v-for="(major, index) in parseMajors(schoolDetails.majors)" :key="index" class="major-tag">
                  {{ major.major_name }} ({{ major.major_rank }}名)
                </span>
              </div>
            </div>
            
            <!-- 详细介绍 -->
            <div class="details-section">
              <h4>学校介绍</h4>
              <p class="school-full-description">{{ schoolDetails.introduction || '暂无详细介绍' }}</p>
            </div>
            
            <!-- 申请要求 -->
            <div class="details-section" v-if="schoolDetails.admission_requirements">
              <h4>申请要求</h4>
              <div class="requirements-list">
                <p>{{ schoolDetails.admission_requirements }}</p>
              </div>
            </div>
            
            <!-- 学费信息 -->
            <div class="details-section" v-if="schoolDetails.tuition_fee">
              <h4>学费信息</h4>
              <p>{{ schoolDetails.tuition_fee }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SchoolSearch',
  data() {
    return {
      // 搜索参数
      searchParams: {
        name: '', // 学校名称关键词
        major: '', // 专业名称关键词
        region: '' // 地区关键词
      },
      // 学校列表数据
      schools: [],
      // 加载状态
      loading: false,
      // 错误信息
      error: null,
      // 是否有搜索结果
      hasResults: true,
      // 模态框相关数据
      showModal: false,
      selectedSchoolId: null,
      schoolDetails: {},
      loadingDetails: false,
      modalError: null
    }
  },
  methods: {
    // 获取认证令牌
    getAuthToken() {
      const token = localStorage.getItem('access_token');
      return token ? `Bearer ${token}` : null;
    },
    
    // 搜索学校
    searchSchools() {
      // 设置加载状态
      this.loading = true;
      this.error = null;
      
      // 获取认证令牌
      const authToken = this.getAuthToken();
      if (!authToken) {
        this.error = '未找到认证信息，请重新登录';
        this.loading = false;
        return;
      }
      
      // 构建查询参数
      const queryParams = new URLSearchParams();
      if (this.searchParams.name) queryParams.append('name', this.searchParams.name);
      if (this.searchParams.major) queryParams.append('major', this.searchParams.major);
      if (this.searchParams.region) queryParams.append('region', this.searchParams.region);
      
      // 构建完整URL
      const apiUrl = `http://localhost:8000/student/search-schools?${queryParams.toString()}`;
      
      // 发送请求
      fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Authorization': authToken,
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('认证失败，请重新登录');
          } else if (response.status === 400) {
            throw new Error('请求参数错误');
          } else {
            throw new Error('服务器错误');
          }
        }
        return response.json();
      })
      .then(data => {
        // 更新学校列表
        this.schools = data;
        this.hasResults = data.length > 0;
        this.loading = false;
      })
      .catch(error => {
        this.error = error.message;
        this.loading = false;
        this.schools = [];
        this.hasResults = true; // 错误状态不影响无结果的显示逻辑
      });
    },
    
    parseMajors(majors) {
      // 如果已经是对象数组，直接返回
      if (Array.isArray(majors) && majors.length > 0 && typeof majors[0] === 'object') {
        // 标准化字段名：兼容'name'/'rank'和'major_name'/'major_rank'格式
        return majors.map(major => {
          // 如果字段名是'name'和'rank'，转换为'major_name'和'major_rank'
          if (major.name && major.rank && !major.major_name) {
            return {
              major_name: major.name,
              major_rank: major.rank
            };
          }
          return major;
        });
      }
      
      // 尝试解析JSON字符串
      try {
        let parsedMajors = [];
        
        // 如果majors是字符串，尝试解析
        if (typeof majors === 'string') {
          parsedMajors = JSON.parse(majors);
          // 确保解析后是数组
          if (!Array.isArray(parsedMajors)) {
            parsedMajors = [parsedMajors];
          }
        }
        // 如果majors是包含JSON字符串的数组，逐个解析
        else if (Array.isArray(majors)) {
          parsedMajors = majors.map(major => {
            if (typeof major === 'string') {
              return JSON.parse(major);
            }
            return major;
          });
        }
        
        // 标准化字段名
        return parsedMajors.map(major => {
          if (major.name && major.rank && !major.major_name) {
            return {
              major_name: major.name,
              major_rank: major.rank
            };
          }
          return major;
        });
      } catch (error) {
        console.error('解析专业信息失败:', error);
      }
      
      // 兜底返回空数组
      return [];
    },
    
    // 查看学校详情
    viewSchoolDetails(schoolId) {
      this.selectedSchoolId = schoolId;
      this.showModal = true;
      this.fetchSchoolDetails(schoolId);
    },
    
    // 关闭模态框
    closeModal() {
      this.showModal = false;
      this.schoolDetails = {};
      this.modalError = null;
    },
    
    // 获取学校详情
    fetchSchoolDetails(schoolId) {
      this.loadingDetails = true;
      this.modalError = null;
      
      // 获取认证令牌
      const authToken = this.getAuthToken();
      if (!authToken) {
        this.modalError = '未找到认证信息，请重新登录';
        this.loadingDetails = false;
        return;
      }
      
      // 构建API请求URL
      const apiUrl = `http://localhost:8000/student/school/${schoolId}`;
      
      // 发送请求
      fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Authorization': authToken,
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('认证失败，请重新登录');
          } else if (response.status === 404) {
            throw new Error('未找到该学校信息');
          } else {
            throw new Error('获取学校详情失败');
          }
        }
        return response.json();
      })
      .then(data => {
        this.schoolDetails = data;
        this.loadingDetails = false;
      })
      .catch(error => {
        this.modalError = error.message;
        this.loadingDetails = false;
      });
    }
  },
  
  mounted() {
    // 组件挂载时可以不立即搜索，等待用户输入搜索条件
  }
}
</script>

<style scoped>
.school-search {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.school-search h2 {
  color: #333;
  margin-bottom: 30px;
}

/* 搜索表单样式 */
.search-form {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: flex-end;
  width: 100%;
  max-width: 100%;
}

.form-group {
  flex: 1;
  min-width: 200px;
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #555;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 15px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #4CAF50;
}

.search-button {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  font-size: 15px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 0;
  white-space: nowrap;
  height: 38px; /* 与输入框高度一致 */
}

.search-button:hover {
  background: #45a049;
}

/* 学校列表样式 */
.schools-list h3 {
  margin-bottom: 15px;
  color: #333;
}

.school-card {
      background-color: #ffffff;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      padding: 0;
      margin-bottom: 16px;
      overflow: hidden;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      width: 100%;
    }
    
    .school-card:hover {
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
      transform: translateY(-2px);
    }
    
    /* 卡片头部样式 */
    .card-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 16px 20px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 12px;
    }
    
    .school-name {
      font-size: 22px;
      font-weight: 600;
      margin: 0;
      display: flex;
      align-items: baseline;
      flex-wrap: wrap;
      gap: 10px;
    }
    
    .school-name .english-name {
      font-size: 16px;
      color: rgba(255, 255, 255, 0.8);
      font-style: italic;
      font-weight: 400;
    }
    
    .ranking-badge {
      background-color: rgba(255, 255, 255, 0.2);
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 14px;
      font-weight: 500;
      backdrop-filter: blur(5px);
    }
    
    /* 卡片内容样式 */
    .card-content {
      padding: 18px 20px;
    }

    .info-section {
      margin-bottom: 16px;
    }
    
    .info-section:last-child {
      margin-bottom: 0;
    }
    
    .info-item {
      display: flex;
      flex-direction: column;
    }
    
    .info-label {
      font-weight: 600;
      color: #2c3e50;
      font-size: 14px;
      margin-bottom: 8px;
    }
    
    .info-value {
      color: #5a6c7d;
      font-size: 15px;
    }
    
    /* 专业信息样式 */
    .majors-container {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    
    .major-tag {
      display: inline-flex;
      align-items: center;
      background-color: #f8f9fa;
      color: #495057;
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 13px;
      border: 1px solid #e9ecef;
      transition: all 0.2s ease;
    }
    
    .major-tag:hover {
      background-color: #667eea;
      color: white;
      border-color: #667eea;
      transform: translateY(-1px);
    }
    
    /* 学校简介样式 */
    .school-description {
      color: #5a6c7d;
      line-height: 1.6;
      font-size: 15px;
      margin: 0;
      padding: 4px 0;
    }
    
    /* 操作按钮区域 */
    .action-section {
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid #e9ecef;
    }
    
    .view-details-btn {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      padding: 8px 20px;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .view-details-btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* 模态框样式 */
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(0, 0, 0, 0.5);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 1000;
      animation: fadeIn 0.3s ease;
    }
    
    .modal-content {
      background: white;
      border-radius: 12px;
      width: 90%;
      max-width: 800px;
      max-height: 80vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
      animation: slideIn 0.3s ease;
    }
    
    .modal-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 20px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }
    
    .modal-header h3 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
      display: flex;
      align-items: baseline;
      flex-wrap: wrap;
      gap: 12px;
    }
    
    .modal-english-name {
      font-size: 16px;
      color: rgba(255, 255, 255, 0.8);
      font-style: italic;
      font-weight: 400;
    }
    
    .close-btn {
      background: none;
      border: none;
      color: white;
      font-size: 24px;
      cursor: pointer;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      transition: background-color 0.2s ease;
    }
    
    .close-btn:hover {
      background-color: rgba(255, 255, 255, 0.2);
    }
    
    .modal-body {
      padding: 24px;
      overflow-y: auto;
      flex: 1;
    }
    
    .modal-loading {
      text-align: center;
      padding: 40px;
    }
    
    .modal-error {
      text-align: center;
      padding: 40px;
      color: #c62828;
    }
    
    .retry-btn {
      background: #667eea;
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 4px;
      cursor: pointer;
      margin-top: 10px;
    }
    
    .school-details-content {
      /* 详情内容样式 */
    }
    
    .details-section {
      margin-bottom: 30px;
    }
    
    .details-section h4 {
      color: #2c3e50;
      font-size: 18px;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 2px solid #667eea;
    }
    
    .detail-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
    }
    
    .detail-item {
      display: flex;
      flex-direction: column;
    }
    
    .detail-label {
      font-weight: 500;
      color: #666;
      font-size: 14px;
      margin-bottom: 4px;
    }
    
    .detail-value {
      color: #2c3e50;
      font-size: 16px;
      font-weight: 500;
    }
    
    .school-full-description {
      color: #5a6c7d;
      line-height: 1.8;
      font-size: 15px;
    }
    
    /* 动画效果 */
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    
    @keyframes slideIn {
      from {
        transform: translateY(-20px);
        opacity: 0;
      }
      to {
        transform: translateY(0);
        opacity: 1;
      }
    }

/* 无结果样式 */
.no-results {
  text-align: center;
  padding: 40px;
  color: #666;
  background: #f9f9f9;
  border-radius: 8px;
}

/* 加载状态样式 */
.loading-indicator {
  text-align: center;
  padding: 40px;
}

.spinner {
  border: 4px solid rgba(76, 175, 80, 0.1);
  border-left: 4px solid #4CAF50;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误信息样式 */
.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #c62828;
  margin-bottom: 20px;
}

.retry-button {
  background: #c62828;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.retry-button:hover {
  background: #b71c1c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-form {
    padding: 20px;
  }
  
  .school-card {
    padding: 15px;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
    margin: 20px;
  }
  
  .modal-header h3 {
    font-size: 20px;
  }
  
  .modal-english-name {
    font-size: 14px;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
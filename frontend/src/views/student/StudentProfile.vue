<template>
  <div class="student-profile">
    <!-- 标题区域 -->
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div class="header-left">
            <h1 class="page-title">
              <i class="fas fa-user-circle"></i>
              <span>个人信息</span>
            </h1>
            <p class="page-subtitle">查看和管理您的个人资料和学术信息</p>
          </div>
          <div class="header-actions">
            <button class="btn-primary" @click="toggleEdit" v-if="!isEditing">
              <i class="fas fa-edit"></i> 编辑信息
            </button>
            <button class="btn-secondary" @click="goBack">
              <i class="fas fa-arrow-left"></i> 返回
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p class="loading-text">加载中...</p>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <div class="error-content">
          <i class="fas fa-exclamation-triangle"></i>
          <div class="error-details">
            <h3>获取信息失败</h3>
            <p>{{ error }}</p>
            <button class="btn-primary" @click="fetchProfile">重试</button>
          </div>
        </div>
      </div>
      
      <!-- 个人信息内容 -->
      <div v-else class="profile-content">
        <!-- 个人信息展示模式 -->
        <div v-if="!isEditing" class="profile-display">
          <!-- 个人头像和基本信息头部区域 -->
          <div class="profile-header">
            <div class="avatar">
              <i class="fas fa-user"></i>
            </div>
            <div class="profile-main-info">
              <h2 class="profile-name">{{ profile.name || '未设置姓名' }}</h2>
              <div class="profile-meta">
                <span class="meta-item"><i class="fas fa-user-graduate"></i> 学生</span>
                <span class="meta-item"><i class="fas fa-id-card"></i> 档案编号: {{ generateStudentId() }}</span>
                <span class="meta-item"><i class="fas fa-calendar-alt"></i> 最后更新: {{ formatLastUpdated() }}</span>
              </div>
            </div>
          </div>
          
          <!-- 信息卡片布局 - 两列布局 -->
          <div class="info-section">
            <!-- 基本信息卡片 -->
            <div class="info-card">
              <div class="card-header">
                <i class="fas fa-user-shield"></i>
                <h3>基本信息</h3>
              </div>
              <div class="card-body">
                <div class="info-grid">
                  <div class="info-item">
                    <div class="info-label">真实姓名</div>
                    <div class="info-value">{{ profile.name || '未填写' }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">性别</div>
                    <div class="info-value">{{ profile.gender || '未填写' }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">年龄</div>
                    <div class="info-value">{{ profile.age || '未填写' }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">电子邮箱</div>
                    <div class="info-value">{{ profile.email || '未填写' }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">手机号码</div>
                    <div class="info-value">{{ profile.phone || '未填写' }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 学术成绩卡片 -->
            <div class="info-card">
              <div class="card-header">
                <i class="fas fa-award"></i>
                <h3>学术成绩</h3>
              </div>
              <div class="card-body">
                <div class="score-item">
                  <div class="score-header">
                    <i class="fas fa-language"></i>
                    <h4>托福成绩</h4>
                  </div>
                  <div class="score-value">{{ profile.toefl || '--' }}</div>
                  <div class="score-max">满分: 120</div>
                  <div class="score-bar-container">
                    <div class="score-bar" :style="{width: (profile.toefl ? (profile.toefl/120)*100 : 0) + '%'}"></div>
                  </div>
                </div>
                
                <div class="score-item">
                  <div class="score-header">
                    <i class="fas fa-chart-line"></i>
                    <h4>GRE成绩</h4>
                  </div>
                  <div class="score-value">{{ profile.gre || '--' }}</div>
                  <div class="score-max">满分: 340</div>
                  <div class="score-bar-container">
                    <div class="score-bar" :style="{width: (profile.gre ? ((profile.gre-260)/80)*100 : 0) + '%'}"></div>
                  </div>
                </div>
                
                <div class="score-item">
                  <div class="score-header">
                    <i class="fas fa-star"></i>
                    <h4>GPA成绩</h4>
                  </div>
                  <div class="score-value">{{ profile.gpa || '--' }}</div>
                  <div class="score-max">满分: 4.0</div>
                  <div class="score-bar-container">
                    <div class="score-bar" :style="{width: (profile.gpa ? (profile.gpa/4)*100 : 0) + '%'}"></div>
                  </div>
                </div>
                
                <div class="target-info">
                  <div class="info-label">目标留学地区</div>
                  <div class="info-value">{{ profile.target_region || '未填写' }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 编辑模式 -->
        <div v-else class="profile-edit">
          <div class="edit-form-wrapper">
            <form @submit.prevent="submitUpdate" class="edit-form">
              <div class="form-header">
                <h2>编辑个人信息</h2>
                <p>请填写或更新您的个人和学术信息</p>
              </div>
              
              <!-- 基本信息部分 -->
              <div class="form-section">
                <h3 class="section-title">
                  <i class="fas fa-user-shield"></i>
                  个人基本信息
                </h3>
                <div class="form-grid">
                  <div class="form-group">
                    <label class="form-label" for="name">真实姓名 <span class="required">*</span></label>
                    <input type="text" id="name" v-model="editProfile.name" placeholder="请输入真实姓名" class="form-input">
                  </div>
                  
                  <div class="form-group">
                    <label class="form-label" for="gender">性别</label>
                    <select id="gender" v-model="editProfile.gender" class="form-input">
                      <option value="">请选择</option>
                      <option value="男">男</option>
                      <option value="女">女</option>
                    </select>
                  </div>
                  
                  <div class="form-group">
                    <label class="form-label" for="age">年龄</label>
                    <input type="number" id="age" v-model.number="editProfile.age" min="18" max="100" placeholder="18-100" class="form-input">
                  </div>
                  
                  <div class="form-group">
                    <label class="form-label" for="email">电子邮箱</label>
                    <input type="email" id="email" v-model="editProfile.email" placeholder="请输入电子邮箱" class="form-input">
                  </div>
                  
                  <div class="form-group">
                    <label class="form-label" for="phone">手机号码</label>
                    <input type="tel" id="phone" v-model="editProfile.phone" placeholder="请输入手机号码" class="form-input">
                  </div>
                </div>
              </div>
              
              <!-- 学术信息部分 -->
              <div class="form-section">
                <h3 class="section-title">
                  <i class="fas fa-award"></i>
                  学术成绩信息
                </h3>
                <div class="form-grid">
                  <div class="form-group">
                    <label class="form-label" for="toefl">托福成绩</label>
                    <input type="number" id="toefl" v-model.number="editProfile.toefl" min="0" max="120" step="0.1" placeholder="0-120" class="form-input">
                    <div v-if="editProfile.toefl" class="score-preview">
                      <div class="score-bar-container">
                        <div class="score-bar" :style="{width: (editProfile.toefl/120)*100 + '%'}"></div>
                      </div>
                      <span class="score-text">{{ editProfile.toefl }}/120</span>
                    </div>
                  </div>
                  
                  <div class="form-group">
                    <label class="form-label" for="gre">GRE成绩</label>
                    <input type="number" id="gre" v-model.number="editProfile.gre" min="260" max="340" step="0.1" placeholder="260-340" class="form-input">
                    <div v-if="editProfile.gre" class="score-preview">
                      <div class="score-bar-container">
                        <div class="score-bar" :style="{width: ((editProfile.gre-260)/80)*100 + '%'}"></div>
                      </div>
                      <span class="score-text">{{ editProfile.gre }}/340</span>
                    </div>
                  </div>
                  
                  <div class="form-group">
                    <label class="form-label" for="gpa">GPA成绩</label>
                    <input type="number" id="gpa" v-model.number="editProfile.gpa" min="0" max="4" step="0.1" placeholder="0.0-4.0" class="form-input">
                    <div v-if="editProfile.gpa" class="score-preview">
                      <div class="score-bar-container">
                        <div class="score-bar" :style="{width: (editProfile.gpa/4)*100 + '%'}"></div>
                      </div>
                      <span class="score-text">{{ editProfile.gpa }}/4.0</span>
                    </div>
                  </div>
                  
                  <div class="form-group">
                    <label class="form-label" for="target_region">目标留学地区</label>
                    <input type="text" id="target_region" v-model="editProfile.target_region" placeholder="请输入目标留学地区" class="form-input">
                  </div>
                </div>
              </div>
              
              <!-- 表单操作按钮 -->
              <div class="form-actions">
                <button type="button" class="btn-secondary" @click="cancelEdit">
                  <i class="fas fa-times"></i> 取消
                </button>
                <button type="submit" class="btn-primary" :disabled="submitting">
                  <i class="fas fa-save"></i> {{ submitting ? '提交中...' : '保存更改' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 成功提示 -->
    <div v-if="successMessage" class="success-notification">
      <div class="success-content">
        <i class="fas fa-check-circle"></i>
        <div class="success-text">
          <h3>更新成功</h3>
          <p>{{ successMessage }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentProfile',
  data() {
    return {
      loading: false,
      error: '',
      successMessage: '',
      isEditing: false,
      submitting: false,
      profile: {},
      editProfile: {}
    }
  },
  
  mounted() {
    this.fetchProfile()
  },
  
  methods: {
    // 返回上一页
    goBack() {
      this.$router.back()
    },
    
    // 生成学生ID示例
    generateStudentId() {
      return 'S' + Math.floor(10000 + Math.random() * 90000)
    },
    
    // 格式化最后更新时间
    formatLastUpdated() {
      const now = new Date()
      return now.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    // 获取个人信息
    async fetchProfile() {
      this.loading = true
      this.error = ''
      
      try {
        // 获取access_token
        const accessToken = localStorage.getItem('access_token') || localStorage.getItem('token');
        
        // 直接调用后端API路径，添加认证头
        const response = await fetch('/api/student/profile', {
          headers: {
            'Authorization': accessToken ? `Bearer ${accessToken}` : ''
          }
        })
        
        if (!response.ok) {
          const errorText = await response.text()
          let errorData = {};
          try {
            errorData = JSON.parse(errorText);
          } catch (e) {
            console.error('解析错误响应失败:', errorText);
          }
          throw new Error(errorData.detail || `获取失败: ${response.status}`);
        }
        this.profile = await response.json();
        console.log('成功获取个人信息:', this.profile);
      } catch (err) {
        this.error = err.message || '获取个人信息失败';
        console.error('获取个人信息失败:', err);
      } finally {
        this.loading = false;
      }
    },
    
    // 切换到编辑模式
    toggleEdit() {
      this.isEditing = true
      // 复制当前个人信息到编辑对象
      this.editProfile = { ...this.profile }
    },
    
    // 取消编辑
    cancelEdit() {
      this.isEditing = false
      this.editProfile = {}
    },
    
    // 表单验证
    validateForm() {
      // 姓名为必填项
      if (!this.editProfile.name || !this.editProfile.name.trim()) {
        this.error = '请输入真实姓名'
        return false
      }
      
      // 验证年龄范围
      if (this.editProfile.age && (this.editProfile.age < 18 || this.editProfile.age > 100)) {
        this.error = '年龄必须在18-100之间'
        return false
      }
      
      // 验证电子邮箱格式
      if (this.editProfile.email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(this.editProfile.email)) {
          this.error = '请输入有效的电子邮箱地址'
          return false
        }
      }
      
      // 验证手机号码格式（简单验证）
      if (this.editProfile.phone) {
        const phoneRegex = /^1[3-9]\d{9}$/
        if (!phoneRegex.test(this.editProfile.phone)) {
          this.error = '请输入有效的手机号码'
          return false
        }
      }
      
      // 验证成绩范围
      if (this.editProfile.toefl && (this.editProfile.toefl < 0 || this.editProfile.toefl > 120)) {
        this.error = '托福成绩必须在0-120之间'
        return false
      }
      
      if (this.editProfile.gre && (this.editProfile.gre < 260 || this.editProfile.gre > 340)) {
        this.error = 'GRE成绩必须在260-340之间'
        return false
      }
      
      if (this.editProfile.gpa && (this.editProfile.gpa < 0 || this.editProfile.gpa > 4)) {
        this.error = 'GPA成绩必须在0-4之间'
        return false
      }
      
      return true
    },
    
    // 提交更新
    async submitUpdate() {
      this.error = ''
      
      // 表单验证
      if (!this.validateForm()) {
        return
      }
      
      this.submitting = true
      
      try {
        // 过滤掉未定义或空字符串的字段
        const updateData = {}
        for (const [key, value] of Object.entries(this.editProfile)) {
          if (value !== undefined && value !== null && value !== '') {
            updateData[key] = value
          }
        }
        
        // 获取access_token
        const accessToken = localStorage.getItem('access_token') || localStorage.getItem('token');
        
        // 直接调用后端API路径，添加认证头
        const response = await fetch('/api/student/profile', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': accessToken ? `Bearer ${accessToken}` : ''
          },
          body: JSON.stringify(updateData)
        })
        
        if (!response.ok) {
          const errorText = await response.text();
          let errorData = {};
          try {
            errorData = JSON.parse(errorText);
          } catch (e) {
            console.error('解析错误响应失败:', errorText);
          }
          throw new Error(errorData.detail || `更新失败: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('更新成功响应:', result);
        
        // 更新成功，显示提示并切换回展示模式
        this.successMessage = result.message || '个人信息更新成功'
        this.fetchProfile() // 重新获取最新信息
        this.isEditing = false
        
        // 3秒后清除成功提示
        setTimeout(() => {
          this.successMessage = ''
        }, 3000)
      } catch (err) {
        this.error = err.message || '更新失败，请稍后重试'
        console.error('更新个人信息失败:', err)
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style scoped>
/* 引入Font Awesome */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

/* 基础样式重置 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* 简洁风格的基础样式 */
.student-profile {
  min-height: 100vh;
  background-color: #f5f7fa;
  font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
  color: #333;
  line-height: 1.6;
}

/* 容器样式 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 页面头部样式 */
.page-header {
  background-color: #fff;
  border-bottom: 1px solid #e1e8ed;
  padding: 20px 0;
  margin-bottom: 30px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-subtitle {
  font-size: 16px;
  color: #666;
}

/* 按钮样式 */
.btn-primary {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.3s ease;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #f8f9fa;
  color: #333;
  border: 1px solid #ddd;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  margin-left: 10px;
}

.btn-secondary:hover {
  background-color: #e9ecef;
  border-color: #ccc;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误状态样式 */
.error-container {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.error-content {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  width: 100%;
}

.error-content i {
  font-size: 24px;
  margin-top: 2px;
}

.error-details h3 {
  margin-bottom: 8px;
  font-size: 18px;
}

.error-details p {
  margin-bottom: 12px;
}

.error-details .btn-primary {
  margin: 0;
}

/* 个人信息展示样式 */
.profile-header {
  display: flex;
  align-items: center;
  gap: 15px;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  margin-bottom: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #e3f2fd;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #3498db;
}

.profile-main-info {
  flex: 1;
}

.profile-name {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 10px;
}

.profile-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  font-size: 14px;
  color: #666;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 信息卡片布局 - 左右布局 */
.info-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.info-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  overflow: hidden;
}

.card-header {
  background-color: #f8f9fa;
  padding: 16px 20px;
  border-bottom: 1px solid #e1e8ed;
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.card-header i {
  color: #3498db;
  font-size: 20px;
}

.card-body {
  padding: 15px;
}

/* 信息网格布局 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.info-value {
  font-size: 16px;
  color: #333;
}

/* 成绩样式 */
.score-item {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e1e8ed;
}

.score-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.score-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.score-header i {
  color: #3498db;
  font-size: 18px;
}

.score-header h4 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.score-value {
  font-size: 24px;
  font-weight: 700;
  color: #3498db;
  margin-bottom: 3px;
}

.score-max {
  font-size: 12px;
  color: #999;
  margin-bottom: 10px;
}

.score-bar-container {
  width: 100%;
  height: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.score-bar {
  height: 100%;
  background-color: #3498db;
  transition: width 0.3s ease;
}

/* 编辑模式样式 */
.edit-form-wrapper {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  padding: 30px;
}

.form-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e1e8ed;
}

.form-header h2 {
  font-size: 24px;
  margin-bottom: 8px;
}

.form-header p {
  color: #666;
  font-size: 16px;
}

.form-section {
  margin-bottom: 30px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  margin-bottom: 20px;
  color: #333;
}

.section-title i {
  color: #3498db;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.required {
  color: #e74c3c;
}

.form-input {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #3498db;
}

.score-preview {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-preview .score-bar-container {
  flex: 1;
  height: 6px;
}

.score-text {
  font-size: 12px;
  color: #666;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e1e8ed;
}

/* 成功提示样式 */
.success-notification {
  position: fixed;
  top: 80px;
  right: 20px;
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
  border-radius: 6px;
  padding: 15px 20px;
  max-width: 400px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  animation: slideInRight 0.3s ease;
  z-index: 1000;
}

.success-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.success-content i {
  font-size: 24px;
  color: #28a745;
  margin-top: 2px;
}

.success-text h3 {
  margin-bottom: 5px;
  font-size: 16px;
}

.success-text p {
  font-size: 14px;
  margin: 0;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 15px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .header-actions {
    width: 100%;
    display: flex;
  }
  
  .header-actions button {
    flex: 1;
    margin: 0;
  }
  
  .btn-secondary {
    margin-left: 10px;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
    padding: 20px;
  }
  
  .info-section {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions button {
    width: 100%;
  }
  
  .btn-secondary {
    margin-left: 0;
    margin-top: 10px;
  }
}
</style>
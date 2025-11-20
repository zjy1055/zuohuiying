<template>
  <div class="student-profile">
    <div class="page-header">
      <h2>个人信息</h2>
      <button class="edit-btn" @click="toggleEdit" v-if="!isEditing">
        <i class="icon-edit"></i> 编辑信息
      </button>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchProfile">重试</button>
    </div>
    
    <div v-else class="profile-content">
      <!-- 个人信息展示模式 -->
      <div v-if="!isEditing" class="profile-display">
        <div class="profile-section">
          <h3>基本信息</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>真实姓名：</label>
              <span>{{ profile.name || '未填写' }}</span>
            </div>
            <div class="info-item">
              <label>性别：</label>
              <span>{{ profile.gender || '未填写' }}</span>
            </div>
            <div class="info-item">
              <label>年龄：</label>
              <span>{{ profile.age || '未填写' }}</span>
            </div>
            <div class="info-item">
              <label>电子邮箱：</label>
              <span>{{ profile.email || '未填写' }}</span>
            </div>
            <div class="info-item">
              <label>手机号码：</label>
              <span>{{ profile.phone || '未填写' }}</span>
            </div>
          </div>
        </div>
        
        <div class="profile-section">
          <h3>成绩信息</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>托福成绩：</label>
              <span>{{ profile.toefl || '未填写' }}</span>
            </div>
            <div class="info-item">
              <label>GRE成绩：</label>
              <span>{{ profile.gre || '未填写' }}</span>
            </div>
            <div class="info-item">
              <label>GPA成绩：</label>
              <span>{{ profile.gpa || '未填写' }}</span>
            </div>
            <div class="info-item">
              <label>目标留学地区：</label>
              <span>{{ profile.target_region || '未填写' }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 个人信息编辑模式 -->
      <div v-else class="profile-edit">
        <form @submit.prevent="submitUpdate">
          <div class="form-section">
            <h3>基本信息</h3>
            <div class="form-grid">
              <div class="form-group">
                <label for="name">真实姓名 *</label>
                <input type="text" id="name" v-model="editProfile.name" placeholder="请输入真实姓名">
              </div>
              <div class="form-group">
                <label for="gender">性别</label>
                <select id="gender" v-model="editProfile.gender">
                  <option value="">请选择</option>
                  <option value="男">男</option>
                  <option value="女">女</option>
                </select>
              </div>
              <div class="form-group">
                <label for="age">年龄</label>
                <input type="number" id="age" v-model.number="editProfile.age" min="18" max="100" placeholder="18-100">
              </div>
              <div class="form-group">
                <label for="email">电子邮箱</label>
                <input type="email" id="email" v-model="editProfile.email" placeholder="请输入电子邮箱">
              </div>
              <div class="form-group">
                <label for="phone">手机号码</label>
                <input type="tel" id="phone" v-model="editProfile.phone" placeholder="请输入手机号码">
              </div>
            </div>
          </div>
          
          <div class="form-section">
            <h3>成绩信息</h3>
            <div class="form-grid">
              <div class="form-group">
                <label for="toefl">托福成绩</label>
                <input type="number" id="toefl" v-model.number="editProfile.toefl" min="0" max="120" step="0.1" placeholder="0-120">
              </div>
              <div class="form-group">
                <label for="gre">GRE成绩</label>
                <input type="number" id="gre" v-model.number="editProfile.gre" min="260" max="340" step="0.1" placeholder="260-340">
              </div>
              <div class="form-group">
                <label for="gpa">GPA成绩</label>
                <input type="number" id="gpa" v-model.number="editProfile.gpa" min="0" max="4" step="0.1" placeholder="0.0-4.0">
              </div>
              <div class="form-group">
                <label for="target_region">目标留学地区</label>
                <input type="text" id="target_region" v-model="editProfile.target_region" placeholder="请输入目标留学地区">
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="cancelEdit">取消</button>
            <button type="submit" class="submit-btn" :disabled="submitting">{{ submitting ? '提交中...' : '保存修改' }}</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 成功提示 -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
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
.student-profile {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e0e0e0;
}

.page-header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.edit-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.3s;
}

.edit-btn:hover {
  background-color: #45a049;
}

.loading-container {
  text-align: center;
  padding: 50px 0;
  color: #666;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: #4CAF50;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.error-message button {
  background-color: #c62828;
  color: white;
  border: none;
  padding: 5px 15px;
  border-radius: 3px;
  cursor: pointer;
}

.success-message {
  background-color: #e8f5e9;
  color: #2e7d32;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.profile-section {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.profile-section h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #444;
  font-size: 18px;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.info-item label {
  font-weight: 600;
  color: #666;
  width: 120px;
  flex-shrink: 0;
}

.info-item span {
  color: #333;
  word-break: break-word;
}

.profile-edit {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
}

.form-section {
  margin-bottom: 30px;
}

.form-section h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #444;
  font-size: 18px;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 600;
  color: #666;
}

.form-group input,
.form-group select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.submit-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #45a049;
}

.submit-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .student-profile {
    padding: 15px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .info-grid,
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions button {
    width: 100%;
  }
}
</style>
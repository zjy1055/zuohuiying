<template>
  <div class="teacher-profile">
    <h2 class="page-title"><i class="profile-icon">👤</i> 个人信息</h2>
    
    <div class="profile-card">
      <!-- 加载状态 -->
      <div class="loading-state" v-if="loading">
        <div class="loading-spinner"></div>
        <p>正在加载个人信息...</p>
      </div>
      
      <!-- 错误状态 -->
      <div class="error-state" v-else-if="error">
        <div class="error-icon">⚠️</div>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="fetchTeacherProfile">
          <i class="btn-icon">🔄</i> 重试
        </button>
      </div>
      
      <!-- 个人信息表单 -->
      <div class="profile-form" v-else>
        <div class="form-group">
          <label class="form-label"><i class="field-icon">🆔</i> ID</label>
          <span class="form-value">{{ teacherInfo.id }}</span>
        </div>
        
        <div class="form-group">
          <label class="form-label"><i class="field-icon">👤</i> 姓名</label>
          <input 
            v-if="isEditing" 
            type="text" 
            class="form-input" 
            v-model="tempTeacherInfo.name"
            placeholder="请输入姓名"
            required
          />
          <span v-else class="form-value">{{ teacherInfo.name || '-' }}</span>
        </div>
        
        <div class="form-group">
          <label class="form-label"><i class="field-icon">✉️</i> 邮箱</label>
          <input 
            v-if="isEditing" 
            type="email" 
            class="form-input" 
            v-model="tempTeacherInfo.email"
            placeholder="请输入邮箱"
            required
          />
          <span v-else class="form-value">{{ teacherInfo.email || '-' }}</span>
        </div>
        
        <div class="form-group">
          <label class="form-label"><i class="field-icon">📱</i> 电话</label>
          <input 
            v-if="isEditing" 
            type="tel" 
            class="form-input" 
            v-model="tempTeacherInfo.phone"
            placeholder="请输入电话"
          />
          <span v-else class="form-value">{{ teacherInfo.phone || '-' }}</span>
        </div>
        
        <div class="form-group">
          <label class="form-label"><i class="field-icon">📚</i> 教授科目</label>
          <input 
            v-if="isEditing" 
            type="text" 
            class="form-input" 
            v-model="tempTeacherInfo.subject"
            placeholder="请输入教授科目"
          />
          <span v-else class="form-value">{{ teacherInfo.subject || '-' }}</span>
        </div>
        
        <!-- 操作按钮 -->
        <div class="form-actions">
          <button 
            v-if="!isEditing" 
            class="edit-btn" 
            @click="startEditing"
          >
            <i class="btn-icon">✏️</i> 编辑信息
          </button>
          <div v-else class="action-buttons">
            <button class="cancel-btn" @click="cancelEditing">
              <i class="btn-icon">❌</i> 取消
            </button>
            <button class="save-btn" @click="updateTeacherProfile" :disabled="isSubmitting">
              <i class="btn-icon" v-if="!isSubmitting">💾</i>
              
              {{ isSubmitting ? '保存中...' : '保存修改' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TeacherProfile',
  data() {
    return {
      teacherInfo: {
        id: '',
        name: '',
        email: '',
        phone: '',
        subject: ''
      },
      tempTeacherInfo: {},
      isEditing: false,
      loading: false,
      isSubmitting: false,
      error: ''
    }
  },
  mounted() {
    // 组件挂载时获取教师信息
    this.fetchTeacherProfile()
  },
  methods: {
    // 获取教师个人信息
    async fetchTeacherProfile() {
      this.loading = true
      this.error = ''
      
      try {
        // 获取access_token - 参考学生认证方式
        const accessToken = localStorage.getItem('access_token') || localStorage.getItem('token');
        
        // 调用API - 使用完整路径以确保正确代理
        console.log('正在调用API获取教师信息...');
        console.log('token存在:', !!accessToken);
        const response = await fetch('http://localhost:8000/teacher/profile', {
          method: 'GET',
          headers: {
            'Authorization': accessToken ? `Bearer ${accessToken}` : '',
            'Content-Type': 'application/json'
          }
        })
        
        // 处理响应
        if (!response.ok) {
          const errorText = await response.text();
          let errorData = {};
          try {
            errorData = JSON.parse(errorText);
          } catch (e) {
            console.error('解析错误响应失败:', errorText);
            throw new Error(`获取个人信息失败: ${response.status}. 非JSON响应: ${errorText.substring(0, 100)}...`);
          }
          
          // 根据API文档中的错误响应处理
          if (response.status === 404) {
            throw new Error(errorData.detail || '个人信息不存在')
          } else if (response.status === 401) {
            throw new Error(errorData.detail || '未认证，请重新登录')
          } else if (response.status === 403) {
            throw new Error(errorData.detail || '无权限访问')
          } else {
            throw new Error(errorData.detail || `获取个人信息失败: ${response.status}`)
          }
        }
        
        // 成功响应，检查响应类型
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          this.teacherInfo = data;
        } else {
          const text = await response.text();
          console.error('非JSON响应:', text);
          throw new Error('服务器返回非JSON格式数据');
        }
      } catch (err) {
        this.error = err.message
        console.error('获取教师个人信息失败:', err)
      } finally {
        this.loading = false
      }
    },
    
    // 开始编辑
    startEditing() {
      // 深度复制当前数据到临时对象
      this.tempTeacherInfo = JSON.parse(JSON.stringify(this.teacherInfo))
      this.isEditing = true
    },
    
    // 取消编辑
    cancelEditing() {
      this.isEditing = false
      this.tempTeacherInfo = {}
    },
    
    // 更新教师个人信息
    async updateTeacherProfile() {
      // 表单验证
      if (!this.tempTeacherInfo.name || !this.tempTeacherInfo.email) {
        this.error = '姓名和邮箱为必填项'
        return
      }
      
      this.isSubmitting = true
      this.error = ''
      
      try {
        // 获取access_token - 参考学生认证方式
        const accessToken = localStorage.getItem('access_token') || localStorage.getItem('token');
        
        // 准备请求体，只包含非空字段（根据API文档要求）
        const updateData = {}
        for (const [key, value] of Object.entries(this.tempTeacherInfo)) {
          if (key !== 'id' && value !== undefined && value !== null && value !== '') {
            updateData[key] = value
          }
        }
        
        // 调用API - 使用完整路径以确保正确代理
        console.log('正在调用API更新教师信息...');
        console.log('token存在:', !!accessToken);
        const response = await fetch('http://localhost:8000/teacher/profile', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': accessToken ? `Bearer ${accessToken}` : ''
          },
          body: JSON.stringify(updateData)
        })
        
        // 处理响应
        if (!response.ok) {
          const errorText = await response.text();
          let errorData = {};
          try {
            errorData = JSON.parse(errorText);
          } catch (e) {
            console.error('解析错误响应失败:', errorText);
            throw new Error(`更新个人信息失败: ${response.status}. 非JSON响应: ${errorText.substring(0, 100)}...`);
          }
          
          // 根据API文档中的错误响应处理
          if (response.status === 404) {
            throw new Error(errorData.detail || '个人信息不存在')
          } else if (response.status === 401) {
            throw new Error(errorData.detail || '未认证，请重新登录')
          } else if (response.status === 403) {
            throw new Error(errorData.detail || '无权限访问')
          } else {
            throw new Error(errorData.detail || `更新个人信息失败: ${response.status}`)
          }
        }
        
        // 成功响应，检查响应类型
        const contentType = response.headers.get('content-type');
        let data;
        if (contentType && contentType.includes('application/json')) {
          data = await response.json();
          console.log('更新成功:', data);
        } else {
          const text = await response.text();
          console.error('非JSON响应:', text);
          throw new Error('服务器返回非JSON格式数据');
        }
        
        // 更新本地数据
        this.teacherInfo = {...this.teacherInfo, ...updateData}
        this.isEditing = false
        
        // 显示成功提示
        alert(data.message || '个人信息更新成功')
      } catch (err) {
        this.error = err.message
        console.error('更新教师个人信息失败:', err)
      } finally {
        this.isSubmitting = false
      }
    },
    
    // 移除不再使用的getAuthToken方法
  }
}
</script>

<style scoped>
.teacher-profile {
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  min-height: 80vh;
  padding: 30px 20px;
}

.page-title {
  margin-bottom: 30px;
  color: #2c3e50;
  font-size: 24px;
  font-weight: 700;
  text-align: center;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1);
}

.profile-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  padding: 32px;
  max-width: 800px;
  margin: 0 auto;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.profile-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

/* 加载状态样式 */
.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  background-color: #f8fafc;
  border-radius: 12px;
  margin: 20px 0;
  transition: all 0.3s ease;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(63, 81, 181, 0.1);
  border-top: 4px solid #3f51b5;
  border-radius: 50%;
  animation: spin 1.2s linear infinite;
  margin: 0 auto 20px;
  box-shadow: 0 0 20px rgba(63, 81, 181, 0.1);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  font-size: 16px;
  color: #4a5568;
  margin: 0;
  font-weight: 500;
}

/* 错误状态样式 */
.error-state {
  text-align: center;
  padding: 60px 20px;
  background-color: #fff5f5;
  border: 2px solid #fed7d7;
  border-radius: 12px;
  margin: 20px 0;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.error-state::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #f56565, #ed8936);
}

.error-icon {
  font-size: 64px;
  margin-bottom: 20px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.error-state p {
  font-size: 16px;
  color: #c53030;
  margin: 0 0 20px;
  font-weight: 500;
  line-height: 1.5;
}

.retry-btn {
  padding: 12px 24px;
  background-color: #3f51b5;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  box-shadow: 0 4px 6px rgba(63, 81, 181, 0.2);
  position: relative;
  overflow: hidden;
}

.retry-btn:hover {
  background-color: #303f9f;
  transform: translateY(-1px);
  box-shadow: 0 6px 12px rgba(63, 81, 181, 0.3);
}

.retry-btn:active {
  transform: translateY(1px);
  box-shadow: 0 2px 4px rgba(63, 81, 181, 0.2);
}

/* 按钮波纹效果 */
.retry-btn::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.retry-btn:active::after {
  width: 300px;
  height: 300px;
}

/* 图标样式 */
.profile-icon {
  margin-right: 8px;
  font-size: 24px;
  vertical-align: middle;
}

.field-icon {
  margin-right: 8px;
  font-size: 16px;
  width: 20px;
  display: inline-flex;
  justify-content: center;
  vertical-align: middle;
}

.btn-icon {
  margin-right: 6px;
  font-size: 14px;
  vertical-align: middle;
}

/* 表单样式 */
.profile-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  position: relative;
}

.form-label {
  flex: 0 0 120px;
  min-width: 120px;
  color: #4a5568;
  font-size: 15px;
  font-weight: 600;
  transition: color 0.3s ease;
  margin-right: 16px;
}

.form-input {
  flex: 1;
  min-width: 0;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 15px;
  background-color: #fff;
  transition: all 0.3s ease;
  box-sizing: border-box;
  position: relative;
  z-index: 1;
}

.form-input:focus {
  outline: none;
  border-color: #3f51b5;
  box-shadow: 0 0 0 3px rgba(63, 81, 181, 0.15);
  transform: translateY(-1px);
  background-color: #f8f9ff;
}

.form-input:hover {
  border-color: #cbd5e0;
  background-color: #f7fafc;
}

.form-group:hover .form-label {
  color: #3f51b5;
}

.form-input::placeholder {
  color: #a0aec0;
}

.form-value {
  flex: 1;
  min-width: 0;
  color: #2d3748;
  font-size: 15px;
  font-weight: 500;
  background-color: #f7fafc;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-sizing: border-box;
  min-height: 46px;
  line-height: 22px;
  word-break: break-word;
}

/* 操作按钮样式 */
.form-actions {
  margin-top: 36px;
  padding-top: 24px;
  border-top: 2px solid #f1f5f9;
  text-align: center;
}

.edit-btn,
.cancel-btn,
.save-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 120px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

/* 按钮点击效果 */
.edit-btn:active,
.cancel-btn:active,
.save-btn:active:not(:disabled) {
  transform: translateY(1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 按钮波纹效果 */
.edit-btn::after,
.cancel-btn::after,
.save-btn::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.edit-btn:active::after,
.cancel-btn:active::after,
.save-btn:active:not(:disabled)::after {
  width: 300px;
  height: 300px;
}

.edit-btn {
  background-color: #3f51b5;
  color: white;
}

.edit-btn:hover {
  background-color: #303f9f;
  transform: translateY(-1px);
  box-shadow: 0 6px 12px rgba(63, 81, 181, 0.3);
}

.action-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #666;
  border: 1px solid #e2e8f0;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.save-btn {
  background-color: #4caf50;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background-color: #45a049;
  transform: translateY(-1px);
  box-shadow: 0 6px 12px rgba(76, 175, 80, 0.3);
}

.save-btn:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .teacher-profile {
    padding: 16px;
    background: #f5f7fa;
  }
  
  .profile-card {
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  }
  
  .page-title {
    font-size: 20px;
    margin-bottom: 20px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 12px;
  }
  
  .cancel-btn,
  .save-btn,
  .edit-btn {
    width: 100%;
    padding: 14px 20px;
    font-size: 16px;
  }
  
  .form-input,
  .form-value {
    padding: 14px 16px;
    font-size: 16px;
  }
}
</style>
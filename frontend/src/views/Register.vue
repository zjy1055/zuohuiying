<template>
  <div class="register-wrapper">
    <div class="register-card">
      <div class="register-header">
        <h2>创建账号</h2>
        <p>加入留学服务平台，开启您的留学旅程</p>
        <button class="close-button" @click="$emit('close')" v-if="showCloseButton">×</button>
      </div>
      
      <form @submit.prevent="handleRegister" class="register-form">
        <!-- 基础信息 -->
        <div class="form-section">
          <h3>基础信息</h3>
          
          <div class="form-group">
            <label for="username">用户名 <span class="required">*</span></label>
            <input 
              type="text" 
              id="username" 
              v-model="formData.username" 
              required 
              placeholder="请设置用户名（用于登录）"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="password">密码 <span class="required">*</span></label>
                       <input 
              type="password" 
              id="password" 
              v-model="formData.password" 
              required 
              placeholder="请设置密码"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="role">用户角色 <span class="required">*</span></label>
            <select 
              id="role" 
              v-model="formData.role" 
              class="form-input"
            >
              <option value="student">学生</option>
              <option value="teacher">教师</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="name">真实姓名 <span class="required">*</span></label>
            <input 
              type="text" 
              id="name" 
              v-model="formData.name" 
              required 
              placeholder="请输入您的真实姓名"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="email">电子邮箱 <span class="required">*</span></label>
            <input 
              type="email" 
              id="email" 
              v-model="formData.email" 
              required 
              placeholder="请输入您的电子邮箱"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="phone">手机号码 <span class="required">*</span></label>
            <input 
              type="tel" 
              id="phone" 
              v-model="formData.phone" 
              required 
              placeholder="请输入您的手机号码"
              class="form-input"
            />
          </div>
        </div>
        
        <!-- 学生特有信息 -->
        <div v-if="formData.role === 'student'" class="form-section">
          <h3>学生信息</h3>
          
          <div class="form-group">
            <label for="gender">性别</label>
            <select id="gender" v-model="formData.gender" class="form-input">
              <option value="">请选择</option>
              <option value="男">男</option>
              <option value="女">女</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="age">年龄</label>
            <input 
              type="number" 
              id="age" 
              v-model.number="formData.age" 
              min="18" 
              max="100" 
              placeholder="请输入年龄"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="toefl">托福成绩</label>
            <input 
              type="number" 
              id="toefl" 
              v-model.number="formData.toefl" 
              min="0" 
              max="120" 
              step="0.5" 
              placeholder="请输入托福成绩（0-120分）"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="gre">GRE成绩</label>
            <input 
              type="number" 
              id="gre" 
              v-model.number="formData.gre" 
              min="260" 
              max="340" 
              step="0.5" 
              placeholder="请输入GRE成绩（260-340分）"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="gpa">GPA成绩</label>
            <input 
              type="number" 
              id="gpa" 
              v-model.number="formData.gpa" 
              min="0" 
              max="4" 
              step="0.1" 
              placeholder="请输入GPA成绩（0.0-4.0分）"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="target_region">目标留学地区</label>
            <input 
              type="text" 
              id="target_region" 
              v-model="formData.target_region" 
              placeholder="请输入目标留学地区（如：美国、英国等）"
              class="form-input"
            />
          </div>
        </div>
        
        <!-- 教师特有信息 -->
        <div v-if="formData.role === 'teacher'" class="form-section">
          <h3>教师信息</h3>
          
          <div class="form-group">
            <label for="subject">擅长科目 <span class="required">*</span></label>
            <input 
              type="text" 
              id="subject" 
              v-model="formData.subject" 
              required 
              placeholder="请输入您的擅长科目（如：英语、数学等）"
              class="form-input"
            />
          </div>
        </div>
        
        <button type="submit" class="register-button" :disabled="isLoading">
          {{ isLoading ? '注册中...' : '注册' }}
        </button>
        
        <div class="form-footer">
          <p>已有账号？<a href="#" @click.prevent="$emit('switch-to-login')">返回登录</a></p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RegisterComponent',
  props: {
    showCloseButton: {
      type: Boolean,
      default: true
    }
  },
  emits: ['close', 'switch-to-login', 'register-success'],
  data() {
    return {
      formData: {
        username: '',
        password: '',
        role: 'student',
        name: '',
        email: '',
        phone: '',
        // 学生信息
        gender: '',
        age: null,
        toefl: null,
        gre: null,
        gpa: null,
        target_region: '',
        // 教师信息
        subject: ''
      },
      isLoading: false
    }
  },
  methods: {
    async handleRegister() {
      this.isLoading = true;
      
      try {
        // 调用后端注册接口
        const response = await fetch('http://localhost:8000/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.formData)
        });
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || '注册失败，请稍后重试');
        }
        
        const data = await response.json();
        
        // 注册成功，发送事件通知父组件
        this.$emit('register-success', { 
          user_id: data.user_id 
        });
        
        // 显示成功信息
        alert(`注册成功！用户ID: ${data.user_id}，请登录`);
        
        // 如果不是作为组件使用（直接访问），则跳转首页
        if (this.$route.path === '/register') {
          this.$router.push('/');
        }
      } catch (error) {
        alert(error.message);
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>

<style scoped>
.register-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.register-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 3rem;
  width: 100%;
  max-width: 550px;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.register-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
}

/* 装饰元素 */
.register-card::before {
  content: '';
  position: absolute;
  top: -50px;
  right: -50px;
  width: 250px;
  height: 250px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 50%;
  z-index: 0;
}

.register-card::after {
  content: '';
  position: absolute;
  bottom: -50px;
  left: -50px;
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-radius: 50%;
  z-index: 0;
}

.close-button {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 1.5rem;
  cursor: pointer;
  color: #667eea;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.close-button:hover {
  background-color: rgba(255, 255, 255, 1);
  color: #764ba2;
  transform: rotate(90deg);
}

.register-header {
  text-align: center;
  margin-bottom: 2.5rem;
  position: relative;
  z-index: 1;
}

.register-header h2 {
  color: #2d3748;
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.register-header p {
  color: #718096;
  font-size: 1rem;
  line-height: 1.5;
}

.form-section {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-bottom: 2rem;
  position: relative;
  z-index: 1;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.form-section h3 {
  color: #4a5568;
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e2e8f0;
}

.form-group {
  margin-bottom: 1.75rem;
  position: relative;
  z-index: 1;
}

.form-group label {
  display: block;
  margin-bottom: 0.75rem;
  color: #4a5568;
  font-weight: 600;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.required {
  color: #e74c3c;
}

.form-input {
  width: 100%;
  padding: 1rem 1.25rem;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

.form-input::placeholder {
  color: #a0aec0;
}

.register-button {
  width: 100%;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  margin-top: 1rem;
  z-index: 1;
  letter-spacing: 0.5px;
}

.register-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: all 0.6s ease;
  z-index: -1;
}

.register-button:hover:not(:disabled)::before {
  left: 100%;
}

.register-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.register-button:active:not(:disabled) {
  transform: translateY(0);
}

.register-button:disabled {
  background: linear-gradient(135deg, #a0aec0 0%, #cbd5e0 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.form-footer {
  text-align: center;
  margin-top: 2rem;
  color: #718096;
  font-size: 0.95rem;
  position: relative;
  z-index: 1;
}

.form-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
  padding-bottom: 2px;
}

.form-footer a::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: #667eea;
  transition: width 0.3s ease;
}

.form-footer a:hover {
  color: #764ba2;
}

.form-footer a:hover::after {
  width: 100%;
}

/* 角色选择样式增强 */
.role-selection {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  position: relative;
  z-index: 1;
}

.role-option {
  flex: 1;
  padding: 1.5rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
}

.role-option:hover {
  border-color: #667eea;
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
}

.role-option.active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.2);
}

.role-option h3 {
  color: #4a5568;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.role-option p {
  color: #718096;
  font-size: 0.85rem;
  line-height: 1.4;
}
</style>
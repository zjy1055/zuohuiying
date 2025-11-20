<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="login-header">
        <h2>欢迎登录</h2>
        <p>留学服务平台 - 您的留学之旅从这里开始</p>
        <button class="close-button" @click="$emit('close')" v-if="showCloseButton">×</button>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="formData.username" 
            required 
            placeholder="请输入用户名"
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="formData.password" 
            required 
            placeholder="请输入密码"
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label for="role">用户角色</label>
          <select 
            id="role" 
            v-model="formData.role" 
            class="form-input"
          >
            <option value="student">学生</option>
            <option value="teacher">教师</option>
          </select>
        </div>
        
        <button type="submit" class="login-button" :disabled="isLoading">
          {{ isLoading ? '登录中...' : '登录' }}
        </button>
        
        <div class="form-footer">
          <p>还没有账号？<a href="#" @click.prevent="$emit('switch-to-register')">立即注册</a></p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginComponent',
  props: {
    showCloseButton: {
      type: Boolean,
      default: true
    }
  },
  emits: ['close', 'switch-to-register', 'login-success'],
  data() {
    return {
      formData: {
        username: '',
        password: '',
        role: 'student'
      },
      isLoading: false,
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.isLoading = true;
      this.error = '';
      
      try {
          // 使用JSON格式发送登录请求
          const requestData = {
            username: this.formData.username,
            password: this.formData.password,
            role: this.formData.role
          };
          
          // 调用后端登录接口
          const response = await fetch('http://localhost:8000/auth/login', {
            method: 'POST',
            credentials: 'include', // 允许跨域携带凭证
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
          });
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || '登录失败，请检查用户名和密码');
        }
        
        const data = await response.json();
        
        // 保存令牌到localStorage
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('user_id', data.user_id);
        localStorage.setItem('role', data.role);
        
        // 登录成功后发送事件通知父组件
        this.$emit('login-success', { 
          user_id: data.user_id, 
          role: data.role 
        });
        
        // 如果不是作为组件使用（直接访问），则跳转首页
        if (this.$route.path === '/login') {
          this.$router.push('/');
        }
      } catch (error) {
        this.error = error.message;
        alert(this.error);
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>

<style scoped>
.login-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.login-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 3rem;
  width: 100%;
  max-width: 450px;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
}

/* 装饰元素 */
.login-card::before {
  content: '';
  position: absolute;
  top: -50px;
  right: -50px;
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 50%;
  z-index: 0;
}

.login-card::after {
  content: '';
  position: absolute;
  bottom: -50px;
  left: -50px;
  width: 150px;
  height: 150px;
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

.login-header {
  text-align: center;
  margin-bottom: 2.5rem;
  position: relative;
  z-index: 1;
}

.login-header h2 {
  color: #2d3748;
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-header p {
  color: #718096;
  font-size: 1rem;
  line-height: 1.5;
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

.login-button {
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

.login-button::before {
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

.login-button:hover:not(:disabled)::before {
  left: 100%;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-button:disabled {
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
</style>
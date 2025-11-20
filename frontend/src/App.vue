<template>
  <div class="app-container">
    <!-- 导航栏 -->
    <nav class="navbar" :class="{ 'navbar-scrolled': isScrolled }">
      <div class="container">
        <!-- 左侧品牌标识 -->
        <router-link to="/" style="text-decoration: none; color: inherit;">
          <div class="brand">
            <div class="logo">🏫📚</div>
            <div class="brand-name">
              <span class="chinese-name">留学护航</span>
              <span class="english-name">StudyAid</span>
            </div>
          </div>
        </router-link>

        <!-- 中间核心功能入口（PC端） -->
        <div class="nav-links">
          <div class="nav-item dropdown">
            <router-link to="/schools" style="text-decoration: none; color: inherit;">学校库</router-link>
          </div>
          <div class="nav-item">服务介绍</div>
          <div class="nav-item">成功案例</div>
          <div class="nav-item">帮助中心</div>
        </div>

        <!-- 移动端汉堡菜单 -->
        <div class="mobile-menu-btn" @click="toggleMobileMenu">
          ☰
        </div>

        <!-- 右侧用户操作区 -->
        <div class="user-actions">
          <!-- 未登录状态 -->
          <div class="not-logged-in" v-if="!isLoggedIn">
            <button class="login-btn" @click="openLoginModal">登录</button>
            <button class="register-btn" @click="openRegisterModal">注册</button>
          </div>
          <!-- 已登录状态 -->
          <div class="logged-in" v-else>
            <div class="user-info dropdown">
              <span :class="userInfo.role === 'student' ? 'student-role' : 'teacher-role'">
                {{ userInfo.name || userInfo.username || '用户' }} | {{ userInfo.role === 'student' ? '学生' : '教师' }}
              </span>
              <div class="dropdown-content">
                <a href="#" class="logout" @click="handleLogout">退出登录</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 移动端菜单 -->
    <div class="mobile-menu" :class="{ 'mobile-menu-open': showMobileMenu }">
      <div class="mobile-nav-links">
        <div class="mobile-nav-item"><router-link to="/schools" style="text-decoration: none; color: inherit;">学校库</router-link></div>
        <div class="mobile-nav-item">服务介绍</div>
        <div class="mobile-nav-item">成功案例</div>
        <div class="mobile-nav-item">帮助中心</div>
        <div v-if="!isLoggedIn">
          <div class="mobile-nav-item" @click="openLoginModal">登录</div>
          <div class="mobile-nav-item" @click="openRegisterModal">注册</div>
        </div>
        <div v-else class="mobile-nav-item">
            <div class="mobile-user-info">
              <span>{{ userInfo.name || userInfo.username || userInfo.user_id || '用户' }}</span>
              <span class="logout" @click="handleLogout">退出</span>
            </div>
        </div>
      </div>
    </div>
    
    <!-- 认证模态框 -->
    <div v-if="showLoginModal || showRegisterModal" class="auth-modal-overlay" @click="closeAuthModal">
      <div class="auth-modal-content" @click.stop>
        <!-- 登录表单 -->
        <LoginComponent 
          v-if="activeAuthForm === 'login'"
          :show-close-button="true"
          @close="closeAuthModal"
          @switch-to-register="openRegisterModal"
          @login-success="handleLoginSuccess"
        />
        
        <!-- 注册表单 -->
        <RegisterComponent 
          v-else
          :show-close-button="true"
          @close="closeAuthModal"
          @switch-to-login="openLoginModal"
          @register-success="handleRegisterSuccess"
        />
      </div>
    </div>

    <main>
      <router-view />
    </main>
  </div>
</template>

<script>
import LoginComponent from './views/Login.vue'
import RegisterComponent from './views/Register.vue'

export default {
  name: 'App',
  components: {
    LoginComponent,
    RegisterComponent
  },
  data() {
    return {
      isScrolled: false,
      showMobileMenu: false,
      // 认证相关状态
      isLoggedIn: false,
      userInfo: null,
      showLoginModal: false,
      showRegisterModal: false,
      activeAuthForm: 'login' // 'login' 或 'register'
    }
  },
  mounted() {
    // 监听滚动事件
    window.addEventListener('scroll', this.handleScroll)
    
    // 检查登录状态
    this.checkLoginStatus()
    
    // 监听路由变化，根据路径参数显示相应的认证模态框
    this.$router.afterEach((to) => {
      if (to.query.login === 'true') {
        this.openLoginModal()
      } else if (to.query.register === 'true') {
        this.openRegisterModal()
      }
    })
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.handleScroll)
  },
  methods: {
    // 认证相关方法
    checkLoginStatus() {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token')
      const userInfo = localStorage.getItem('userInfo')
      if (token) {
        this.isLoggedIn = true
        if (userInfo) {
          this.userInfo = JSON.parse(userInfo)
        } else {
          // 兼容旧的存储方式，并添加name字段的处理
          this.userInfo = {
            user_id: localStorage.getItem('user_id'),
            username: localStorage.getItem('username') || localStorage.getItem('user_id'),
            name: localStorage.getItem('name') || localStorage.getItem('username') || localStorage.getItem('user_id'),
            role: localStorage.getItem('role')
          }
        }
      }
    },
    
    openLoginModal() {
      this.showLoginModal = true
      this.showRegisterModal = false
      this.activeAuthForm = 'login'
      // 关闭移动端菜单
      this.showMobileMenu = false
    },
    
    openRegisterModal() {
      this.showRegisterModal = true
      this.showLoginModal = false
      this.activeAuthForm = 'register'
      // 关闭移动端菜单
      this.showMobileMenu = false
    },
    
    closeAuthModal() {
      this.showLoginModal = false
      this.showRegisterModal = false
    },
    
    handleLoginSuccess(userInfo) {
      this.isLoggedIn = true
      // 确保userInfo对象包含必要的字段
      const completeUserInfo = {
        user_id: userInfo.user_id,
        username: userInfo.username || userInfo.user_id,
        name: userInfo.name || userInfo.username || userInfo.user_id,
        role: userInfo.role
      }
      this.userInfo = completeUserInfo
      
      // 保存完整的用户信息到localStorage
      localStorage.setItem('userInfo', JSON.stringify(completeUserInfo))
      
      this.closeAuthModal()
      
      // 登录成功后根据用户角色跳转到对应页面
      if (userInfo.role === 'student') {
        this.$router.push('/student/dashboard')
      } else if (userInfo.role === 'teacher') {
        // 教师角色跳转到教师中心页面
        this.$router.push('/teacher/dashboard')
      }
      // 可以在这里添加登录成功后的提示
    },
    
    handleRegisterSuccess() {
      // 注册成功后自动切换到登录页面
      this.showRegisterModal = false
      this.showLoginModal = true
      this.activeAuthForm = 'login'
    },
    
    handleLogout() {
      // 清除所有可能的认证信息
      localStorage.removeItem('token')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('user_id')
      localStorage.removeItem('role')
      
      this.isLoggedIn = false
      this.userInfo = null
      // 可以在这里添加登出成功后的提示
    },
    
    handleScroll() {
      // 导航栏滚动效果
      this.isScrolled = window.scrollY > 50
    },
    
    toggleMobileMenu() {
      // 切换移动端菜单
      this.showMobileMenu = !this.showMobileMenu
    }
  }
}
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Arial', sans-serif;
  color: #333;
  background-color: #f8f9fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 导航栏样式 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background-color: rgba(255, 255, 255, 0.95);
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.navbar-scrolled {
  background-color: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.navbar .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 5px;
}

/* 品牌标识 */
.brand {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.brand:hover {
  transform: scale(1.05);
}

.logo {
  font-size: 2.5rem;
  margin-right: 10px;
}

.brand-name {
  display: flex;
  flex-direction: column;
}

.chinese-name {
  font-size: 1.2rem;
  font-weight: bold;
  color: #3498db;
}

.english-name {
  font-size: 0.9rem;
  color: #7f8c8d;
}

/* 导航链接 */
.nav-links {
  display: flex;
  gap: 30px;
}

.nav-item {
  position: relative;
  font-size: 1rem;
  color: #34495e;
  cursor: pointer;
  padding: 8px 0;
  transition: color 0.3s ease;
}

.nav-item:hover {
  color: #3498db;
}

/* 下拉菜单 */
.dropdown {
  position: relative;
}

.dropdown-content {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: white;
  min-width: 200px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px);
  transition: all 0.3s ease;
  z-index: 1001;
  display: flex;
}

.dropdown:hover .dropdown-content {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-section {
  padding: 10px 15px;
  min-width: 120px;
}

.dropdown-section h4 {
  margin: 0 0 10px 0;
  font-size: 0.9rem;
  color: #3498db;
}

.dropdown-section a {
  display: block;
  color: #34495e;
  text-decoration: none;
  padding: 5px 0;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.dropdown-section a:hover {
  color: #3498db;
}

/* 用户操作区 */
.user-actions {
  display: flex;
  gap: 10px;
}

.login-btn, .register-btn {
  padding: 8px 20px;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.login-btn {
  background-color: white;
  color: #34495e;
  border: 1px solid #ddd;
}

.login-btn:hover {
  background-color: #f8f9fa;
  border-color: #3498db;
}

.register-btn {
  background-color: #3498db;
  color: white;
}

.register-btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
}

/* 用户信息 */
.user-info {
  cursor: pointer;
  font-weight: bold;
}

.student-role {
  color: #27ae60;
}

.teacher-role {
  color: #e67e22;
}

/* 移动端用户信息 */
.mobile-user-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mobile-user-info .logout {
  color: #e74c3c;
  cursor: pointer;
}

/* 认证模态框 */
.auth-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.auth-modal-content {
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 12px;
  background-color: white;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 移动端菜单按钮 */
.mobile-menu-btn {
  display: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #34495e;
}

.mobile-menu {
  position: fixed;
  top: 70px;
  left: 0;
  right: 0;
  background-color: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-100%);
  transition: transform 0.3s ease;
  z-index: 999;
  max-height: 0;
  overflow: hidden;
}

.mobile-menu-open {
  transform: translateY(0);
  max-height: 500px;
}

.mobile-nav-links {
  padding: 20px;
}

.mobile-nav-item {
  padding: 15px 0;
  border-bottom: 1px solid #eee;
  font-size: 1rem;
  color: #34495e;
  cursor: pointer;
  transition: color 0.3s ease;
}

.mobile-nav-item:hover {
  color: #3498db;
}

.mobile-nav-item:last-child {
  border-bottom: none;
}

/* 应用容器样式 */
.app-container {
  min-height: 80vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
  padding: 1rem;
  max-width: 1500px;
  margin: 60px auto;
  width: 100%;
  /* margin-top: 70px;  */
}

/* 响应式设计 */
@media (max-width: 768px) {
  /* 导航栏 */
  .nav-links,
  .user-actions {
    display: none;
  }
  
  .mobile-menu-btn {
    display: block;
  }
  
  .logo {
    font-size: 2rem;
  }
  
  .chinese-name {
    font-size: 1rem;
  }
  
  .english-name {
    font-size: 0.8rem;
  }
  
  /* 认证模态框 */
  .auth-modal-content {
    margin: 10px;
  }
  
  main {
    padding: 1rem;
    margin-top: 60px;
  }
}
</style>

<template>
  <div class="student-dashboard">
    <!-- 顶部功能导航菜单 -->
    <nav class="top-nav">
      <div class="nav-container">
        <!-- 用户信息区域 -->
        <div class="user-info" v-if="userInfo">
          <span class="welcome-text">欢迎您，{{ userInfo.name || userInfo.username || '同学' }}</span>
        </div>
        
        <!-- 导航菜单 -->
        <ul class="nav-menu">
          <li 
            v-for="item in navItems" 
            :key="item.path"
            :class="{ active: currentPath === item.path }"
            @click="navigateTo(item.path)"
            @mouseenter="showTooltip(item)"
            @mouseleave="hideTooltip"
          >
            {{ item.name }}
            <!-- 导航提示 -->
            <div v-if="tooltip.show && tooltip.item === item" class="nav-tooltip">
              {{ item.description }}
            </div>
          </li>
        </ul>
      </div>
    </nav>
    
    <!-- 主内容区域 -->
    <div class="dashboard-content">

      
      <!-- 全局加载提示 -->
      <div v-if="loading" class="global-loading">
        <div class="loading-spinner"></div>
        <p>{{ loadingMessage || '加载中...' }}</p>
      </div>
      
      <!-- 全局错误提示 -->
      <div v-if="error" class="global-error" @click="clearError">
        <p>{{ errorMessage }}</p>
        <span class="error-close">&times;</span>
      </div>
      
      <!-- 全局成功提示 -->
      <div v-if="success" class="global-success">
        <p>{{ successMessage }}</p>
      </div>
      
      <!-- 路由视图带过渡效果 -->
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" v-if="!loading" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentDashboard',
  data() {
    return {
      navItems: [
        {
          name: '个人信息',
          path: '/student/dashboard/profile',
          api: ['GET /student/profile', 'PUT /student/profile'],
          description: '查看/编辑学生基本信息、成绩等'
        },
        {
          name: '学校推荐',
          path: '/student/dashboard/recommendation',
          api: ['GET /student/recommendation'],
          description: '基于成绩推荐匹配的学校'
        },
        {
          name: '学校查询',
          path: '/student/dashboard/schools',
          api: ['GET /student/search-schools', 'GET /student/schools'],
          description: '搜索/浏览所有学校信息'
        },
        {
          name: '成功案例',
          path: '/student/dashboard/success-cases',
          api: ['GET /student/success-cases'],
          description: '查看留学成功案例列表'
        },
        {
          name: '培训预约',
          path: '/student/dashboard/training',
          api: ['POST /training/reserve', 'GET /training/list'],
          description: '预约语言培训、查看预约记录'
        },

      ],
      currentPath: '',
      // 加载状态
      loading: false,
      loadingMessage: '',
      // 错误状态
      error: false,
      errorMessage: '',
      // 成功提示状态
      success: false,
      successMessage: '',
      // 用户信息
      userInfo: null,
      // 工具提示
      tooltip: {
        show: false,
        item: null
      },

    }
  },
  watch: {
    $route: {
      handler(newRoute) {
        // 获取当前路径，用于高亮显示当前菜单
        this.currentPath = this.getBasePath(newRoute.path)
        // 页面切换时清除提示消息
        this.clearMessages()

      },
      immediate: true
    }
  },
  beforeMount() {
    // 获取用户信息
    this.getUserInfo()
  },
  mounted() {
    console.log('学生中心页面已加载')
    // 添加全局错误处理
    window.addEventListener('error', this.handleGlobalError)
    
    // Vue 3中不再支持$on/$off，使用provide/inject机制替代
    this.provideGlobalMethods()
  },
  beforeUnmount() {
    window.removeEventListener('error', this.handleGlobalError)
  },
  methods: {
    // 提供全局方法供子组件使用
    provideGlobalMethods() {
      // 在Vue 3中，应使用provide/inject API
      // 此处保留方法定义，子组件将通过inject获取这些方法
      this.$nextTick(() => {
        // 全局方法已通过methods定义，子组件可通过其他方式访问
        console.log('全局方法已准备就绪')
      })
    },
    navigateTo(path) {
      // 平滑滚动到页面顶部
      window.scrollTo({ top: 0, behavior: 'smooth' })
      // 添加短暂延迟以提升用户体验
      setTimeout(() => {
        this.$router.push(path)
      }, 100)
    },
    getBasePath(path) {
      // 提取基础路径，用于菜单高亮
      const parts = path.split('/')
      if (parts.length >= 3) {
        return `/${parts[1]}/${parts[2]}`
      }
      return path
    },
    // 设置加载状态
    setLoading(status, message = '') {
      this.loading = status
      this.loadingMessage = message
    },
    // 显示错误信息
    showError(message) {
      this.error = true
      this.errorMessage = message || '操作失败，请稍后重试'
      // 5秒后自动隐藏错误提示
      setTimeout(() => {
        this.error = false
      }, 5000)
    },
    // 显示成功信息
    showSuccess(message) {
      this.success = true
      this.successMessage = message || '操作成功'
      // 3秒后自动隐藏成功提示
      setTimeout(() => {
        this.success = false
      }, 3000)
    },
    // 清除错误信息
    clearError() {
      this.error = false
    },
    // 清除所有消息
    clearMessages() {
      this.error = false
      this.success = false
    },
    // 处理全局错误
    handleGlobalError(event) {
      console.error('全局错误:', event.error || event.message)
      // 可以在这里添加错误日志记录
    },
    // 获取用户信息
    getUserInfo() {
      try {
        const userInfoStr = localStorage.getItem('userInfo')
        if (userInfoStr) {
          this.userInfo = JSON.parse(userInfoStr)
        } else {
          // 兼容旧的存储方式
          this.userInfo = {
            user_id: localStorage.getItem('user_id'),
            role: localStorage.getItem('role'),
            username: localStorage.getItem('username')
          }
        }
      } catch (e) {
        console.error('获取用户信息失败:', e)
      }
    },
    // 显示导航提示
    showTooltip(item) {
      // 延迟显示，避免快速移动鼠标时显示
      setTimeout(() => {
        this.tooltip.show = true
        this.tooltip.item = item
      }, 500)
    },
    // 隐藏导航提示
    hideTooltip() {
      this.tooltip.show = false
      this.tooltip.item = null
    },

  }
}
</script>

<style scoped>
.student-dashboard {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f8f9fa;
  margin-top: 70px; /* 为App.vue的导航栏留出空间 */
}

.top-nav {
  background-color: white;
  color: #34495e;
  position: fixed;
  top: 70px; /* 位于App.vue导航栏下方 */
  left: 0;
  right: 0;
  z-index: 999; /* 比App.vue的z-index小 */
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  border-bottom: 1px solid #eaeaea;
}

.nav-container {
  max-width: 1200px;
  margin: 0 100px;
  padding: 0 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.nav-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-menu li {
  margin-left: 15px;
  padding: 8px 18px;
  cursor: pointer;
  border-radius: 25px;
  transition: all 0.2s ease;
  position: relative;
  font-size: 15px;
  font-weight: 500;
}

.nav-menu li:first-child {
  margin-left: 0;
}

.nav-menu li:hover {
  color: #3498db;
  background-color: rgba(52, 152, 219, 0.08);
  transform: translateY(-1px);
}

.nav-menu li.active {
  color: white;
  background-color: #3498db;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.dashboard-content {
  flex: 1;
  max-width: 1800px;
  margin: 0 auto;
  padding: 0px 10px 10px;
  width: 100%;
  position: relative;
}

/* 添加内容卡片样式 */
.content-card {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
  padding: 30px;
  margin-bottom: 20px;
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
}

.content-card:hover {
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

/* 用户信息样式 */
.user-info {
  display: flex;
  align-items: center;
}

.welcome-text {
  color: #34495e;
  font-size: 14px;
  font-weight: 500;
}

/* 导航提示样式 */
.nav-tooltip {
  position: absolute;
  top: calc(100% + 10px);
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 1000;
  pointer-events: none;
}

.nav-tooltip::after {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-bottom-color: rgba(0, 0, 0, 0.8);
}



/* 路由过渡效果 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 全局加载状态样式 */
.global-loading {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(255, 255, 255, 0.95);
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  min-width: 200px;
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

.global-loading p {
  margin: 0;
  color: #34495e;
  font-size: 16px;
}

/* 全局错误提示样式 */
.global-error {
  position: fixed;
  top: 140px; /* 位于固定导航栏下方 */
  right: 20px;
  background-color: #f8d7da;
  color: #721c24;
  padding: 15px 20px;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 9998;
  max-width: 400px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  animation: slideIn 0.3s ease;
}

/* 全局成功提示样式 */
.global-success {
  position: fixed;
  top: 140px; /* 位于固定导航栏下方 */
  right: 20px;
  background-color: #d4edda;
  color: #155724;
  padding: 15px 20px;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 9998;
  max-width: 400px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.global-error p, .global-success p {
  margin: 0;
  font-size: 14px;
}

.error-close {
  margin-left: 10px;
  font-size: 20px;
  font-weight: bold;
  color: #721c24;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.error-close:hover {
  transform: scale(1.2);
}
</style>
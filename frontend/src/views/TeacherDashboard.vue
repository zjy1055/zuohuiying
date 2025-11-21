<template>
  <div class="teacher-dashboard">
    

    <div class="dashboard-container">
      <!-- 侧边导航菜单 -->
      <div class="sidebar">
        <div class="user-info">
          <span class="welcome-message">欢迎您，{{ userInfo?.user_id || '教师用户' }}</span>
        </div>
        <ul class="nav-menu">
          <li 
            class="nav-item" 
            :class="{ active: currentRoute === '/teacher/dashboard/profile' }"
            @click="navigateTo('/teacher/dashboard/profile')"
          >
            <i class="nav-icon">👤</i>
            <span class="nav-text">个人信息</span>
          </li>
          <li 
            class="nav-item" 
            :class="{ active: currentRoute === '/teacher/dashboard/statistics' }"
            @click="navigateTo('/teacher/dashboard/statistics')"
          >
            <i class="nav-icon">📊</i>
            <span class="nav-text">学生统计</span>
          </li>
          <li 
            class="nav-item" 
            :class="{ active: currentRoute === '/teacher/dashboard/students' }"
            @click="navigateTo('/teacher/dashboard/students')"
          >
            <i class="nav-icon">👥</i>
            <span class="nav-text">学生列表</span>
          </li>
          <li 
            class="nav-item" 
            :class="{ active: currentRoute === '/teacher/dashboard/prediction' }"
            @click="navigateTo('/teacher/dashboard/prediction')"
          >
            <i class="nav-icon">🔮</i>
            <span class="nav-text">留学预测</span>
          </li>
          <li 
            class="nav-item" 
            :class="{ active: currentRoute === '/teacher/dashboard/training' }"
            @click="navigateTo('/teacher/dashboard/training')"
          >
            <i class="nav-icon">📚</i>
            <span class="nav-text">培训管理</span>
          </li>
          <li 
            class="nav-item" 
            :class="{ active: currentRoute === '/teacher/dashboard/schools' }"
            @click="navigateTo('/teacher/dashboard/schools')"
          >
            <i class="nav-icon">🏫</i>
            <span class="nav-text">学校管理</span>
          </li>
        </ul>
      </div>

      <!-- 主内容区域 -->
      <div class="dashboard-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TeacherDashboard',
  data() {
    return {
      teacherData: null,
      userInfo: {
        user_id: '',
        role: 'teacher'
      },
      currentRoute: '/teacher/profile'
    }
  },
  mounted() {
    // 页面加载时获取登录用户信息
    this.loadUserInfo()
    // 设置当前路由
    this.currentRoute = this.$route.path
    console.log('教师中心页面加载完成')
  },
  watch: {
    // 监听路由变化
    '$route.path': function(newPath) {
      this.currentRoute = newPath
    }
  },
  methods: {
    loadUserInfo() {
      try {
        const userInfoStr = localStorage.getItem('userInfo')
        if (userInfoStr) {
          this.userInfo = JSON.parse(userInfoStr)
        } else {
          // 兼容旧的存储方式
          this.userInfo = {
            user_id: localStorage.getItem('user_id'),
            role: localStorage.getItem('role') || 'teacher'
          }
        }
      } catch (e) {
        console.error('解析用户信息失败:', e)
      }
    },
    navigateTo(path) {
      this.$router.push(path)
    }
  }
}
</script>

<style scoped>
/* 全局容器固定定位 */
.teacher-dashboard {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}



/* 主体容器 */
.dashboard-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 侧边导航菜单固定 */
  .sidebar {
    width: 240px;
    background-color: #ffffff;
    box-shadow: 2px 0 4px rgba(0, 0, 0, 0.08);
    padding: 20px;
    overflow-y: auto;
    flex-shrink: 0;
    position: relative;
    z-index: 50;
    margin-top: 20px;
    margin-left: 15px;
    border-radius: 8px;
  }
  
  .sidebar .user-info {
    padding-bottom: 20px;
    border-bottom: 1px solid #e0e0e0;
    margin-bottom: 20px;
  }
  
  .sidebar .welcome-message {
    font-size: 14px;
    color: #333;
    font-weight: 500;
  }

.nav-menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background-color: #f5f5f5;
  border-left-color: #3f51b5;
}

.nav-item.active {
  background-color: #e8eaf6;
  border-left-color: #3f51b5;
  color: #3f51b5;
  font-weight: 500;
}

.nav-icon {
  font-size: 18px;
  margin-right: 12px;
}

.nav-text {
  font-size: 14px;
}

/* 主内容区域 */
.dashboard-content {
  flex: 1;
  padding: 24px;
  padding-top: 94px; /* 添加70px上边距，原padding-top 24px + 70px = 94px */
  overflow-y: auto;
  background-color: #f5f7fa;
  position: relative;
}
</style>
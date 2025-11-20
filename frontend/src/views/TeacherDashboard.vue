<template>
  <div class="teacher-dashboard">
    <div class="dashboard-header">
      <h1>教师中心</h1>
      <div class="user-info">
        <span class="welcome-message">欢迎您，{{ userInfo?.user_id || '教师用户' }}</span>
      </div>
    </div>

    <div class="dashboard-content">
      <!-- 教师界面内容区域 -->
      <div class="empty-state" v-if="!teacherData">
        <div class="empty-icon">👨‍🏫</div>
        <h3>教师信息待加载</h3>
        <p>您的教师信息将在这里显示</p>
      </div>
      
      <div class="teacher-data" v-else>
        <!-- 这里将展示教师数据，目前为空 -->
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
      }
    }
  },
  mounted() {
    // 页面加载时获取登录用户信息
    this.loadUserInfo()
    // 后续可以添加加载教师数据的逻辑
    console.log('教师中心页面加载完成')
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
    }
  }
}
</script>

<style scoped>
.teacher-dashboard {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.dashboard-header {
  background-color: #3f51b5;
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dashboard-header h1 {
  margin: 0;
  font-size: 24px;
}

.user-info {
  display: flex;
  align-items: center;
}

.welcome-message {
  font-size: 14px;
  opacity: 0.9;
}

.dashboard-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  color: #333;
  margin-bottom: 8px;
  font-size: 18px;
}

.empty-state p {
  color: #666;
  font-size: 14px;
}

.teacher-data {
  /* 教师数据样式，目前为空 */
}
</style>
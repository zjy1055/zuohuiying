import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SchoolsView from '../views/SchoolsView.vue'
import StudentDashboard from '../views/StudentDashboard.vue'
import TeacherDashboard from '../views/TeacherDashboard.vue'

// 导入学生功能组件
import StudentProfile from '../views/student/StudentProfile.vue'
import SchoolRecommendation from '../views/student/SchoolRecommendation.vue'
import SchoolSearch from '../views/student/SchoolSearch.vue'
import SuccessCases from '../views/student/SuccessCases.vue'
import TrainingAppointment from '../views/student/TrainingAppointment.vue'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: { title: '首页' }
  },
  {
    path: '/schools',
    name: 'Schools',
    component: SchoolsView,
    meta: { title: '学校库' }
  },
  // 保留登录和注册路由作为备用，在用户直接访问时重定向到首页
  {
    path: '/login',
    redirect: '/' 
  },
  {
    path: '/register',
    redirect: '/' 
  },
  {
      path: '/student/dashboard',
      name: 'StudentDashboard',
      component: StudentDashboard,
      meta: {
        title: '学生中心',
        requiresAuth: true
      },
      children: [
        {
          path: 'profile',
          name: 'studentProfile',
          component: StudentProfile,
          meta: {
            title: '学生资料',
            requiresAuth: true
          }
        },
        {
          path: 'recommendation',
          name: 'schoolRecommendation',
          component: SchoolRecommendation,
          meta: {
            title: '学校推荐',
            requiresAuth: true
          }
        },
        {
          path: 'schools',
          name: 'schoolSearch',
          component: SchoolSearch,
          meta: {
            title: '学校搜索',
            requiresAuth: true
          }
        },
        {
          path: 'success-cases',
          name: 'successCases',
          component: SuccessCases,
          meta: {
            title: '成功案例',
            requiresAuth: true
          }
        },
        {
          path: 'training',
          name: 'trainingAppointment',
          component: TrainingAppointment,
          meta: {
            title: '培训预约',
            requiresAuth: true
          }
        },

      ]
    },
  {
    path: '/teacher/dashboard',
    name: 'TeacherDashboard',
    component: TeacherDashboard,
    meta: {
      title: '教师中心',
      requiresAuth: true // 标记为需要认证的页面
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || '留学服务平台'
  
  // 检查用户是否登录
  const token = localStorage.getItem('token') || localStorage.getItem('access_token')
  const isAuthenticated = !!token
  
  // 获取用户信息
  let userInfo = null
  try {
    const userInfoStr = localStorage.getItem('userInfo')
    if (userInfoStr) {
      userInfo = JSON.parse(userInfoStr)
    } else {
      // 兼容旧的存储方式
      userInfo = {
        user_id: localStorage.getItem('user_id'),
        role: localStorage.getItem('role')
      }
    }
  } catch (e) {
    console.error('解析用户信息失败:', e)
  }
  
  // 如果用户已登录且访问的是首页(/)，根据角色自动跳转到相应的仪表盘
    if (isAuthenticated && to.path === '/' && userInfo && userInfo.role) {
      if (userInfo.role === 'student') {
        next({ path: '/student/dashboard' })
      } else if (userInfo.role === 'teacher') {
        // 教师角色跳转到教师中心页面
        next({ path: '/teacher/dashboard' })
      } else {
        next()
      }
    } 
  // 对于需要认证的页面进行检查
  else if (to.meta.requiresAuth && !isAuthenticated) {
    // 可以在这里触发首页显示登录模态框
    window.showLoginModal = true
    next({ path: '/' })
  } 
  // 其他情况正常跳转
  else {
    next()
  }
})

export default router
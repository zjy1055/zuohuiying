<template>
  <div class="student-list-container">
    <div class="page-header">
      <h2>学生列表</h2>
      <p>管理和查看所有学生信息</p>
    </div>
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在加载学生数据...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p class="error-message">{{ error }}</p>
      <button class="retry-button" @click="fetchStudents">重新加载</button>
    </div>

    <!-- 空状态 -->
    <div v-else-if="students.length === 0" class="empty-state">
      <p v-if="hasSearched">没有找到符合条件的学生</p>
      <p v-else>暂无学生数据</p>
    </div>

    <!-- 学生列表 -->
    <div v-else class="students-table-wrapper">
      <div class="table-responsive">
        <table class="students-table">
          <thead class="thead-light">
            <tr>
              <th class="col-student-id">学生ID</th>
              <th class="col-student-name">姓名</th>
              <th class="col-student-gender">性别</th>
              <th class="col-student-gpa">GPA</th>
              <th class="col-student-score">语言成绩</th>
              <th class="col-student-target">目标地区</th>
              <th class="col-student-action">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in students" :key="student.id" class="student-row">
              <td class="font-monospace">{{ student.id }}</td>
              <td class="font-medium student-name">{{ student.name || '未填写' }}</td>
              <td>{{ student.gender === '男' ? '👨' : (student.gender === '女' ? '👩' : '未填写') }}</td>
              <td>
                <span :class="getGPAClass(student.gpa)">
                  {{ student.gpa !== null && student.gpa !== undefined ? student.gpa.toFixed(2) : '未填写' }}
                </span>
              </td>
              <td class="text-nowrap">{{ formatLanguageScore(student) }}</td>
              <td>{{ student.target_region || '未填写' }}</td>
              <td class="action-buttons">
                <div class="btn-group" role="group">
                  <button class="btn-view" @click="viewStudentDetails(student.id)" title="查看详情">查看详情</button>
                  <button class="btn-contact" @click="contactStudent(student.id)" title="联系学生">联系</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页控件 -->
        <div class="pagination-container">
          <div class="pagination-info">
            共 {{ totalCount }} 条记录
          </div>
        </div>
    </div>

    <!-- 学生详情模态框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>学生详情</h3>
          <button class="close-button" @click="closeDetailModal">×</button>
        </div>
        <div class="modal-body">
          <div v-if="currentStudent" class="student-details">
            <div class="detail-row">
              <span class="detail-label">学生ID：</span>
              <span class="detail-value">{{ currentStudent.id }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">姓名：</span>
              <span class="detail-value">{{ currentStudent.name }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">性别：</span>
              <span class="detail-value">{{ currentStudent.gender || '未填写' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">GPA：</span>
              <span class="detail-value">{{ currentStudent.gpa || '未填写' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">托福成绩：</span>
              <span class="detail-value">{{ currentStudent.toefl || '未提供' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">GRE成绩：</span>
              <span class="detail-value">{{ currentStudent.gre || '未提供' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">目标地区：</span>
              <span class="detail-value">{{ currentStudent.target_region || '未填写' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentList',
  data() {
    return {
      students: [],
      loading: false,
      error: '',
      searchKeyword: '',
      currentPage: 1,
      itemsPerPage: 10,
      totalPages: 0,
      totalCount: 0,
      showDetailModal: false,
      currentStudent: null,
      hasSearched: false,
      pageJumpInput: ''
    }
  },
  
  computed: {
      // API返回的学生列表直接用于显示
      paginatedStudents() {
        return this.students
      },
      
      // 计算可见的页码范围
      visiblePages() {
        const total = this.totalPages
        const current = this.currentPage
        const pages = []
        const maxVisible = 5 // 最多显示5个页码按钮
        
        if (total <= maxVisible) {
          // 如果总页数小于等于最大可见数，显示所有页码
          for (let i = 1; i <= total; i++) {
            pages.push(i)
          }
        } else {
          // 显示当前页前后各2个页码，中间用...代替
          pages.push(1)
          
          if (current > 3) {
            pages.push('...')
          }
          
          const start = Math.max(2, current - 1)
          const end = Math.min(total - 1, current + 1)
          
          for (let i = start; i <= end; i++) {
            pages.push(i)
          }
          
          if (current < total - 2) {
            pages.push('...')
          }
          
          pages.push(total)
        }
        
        return pages
      },
      
      // 验证页码输入是否有效
      isValidPageJump() {
        const page = parseInt(this.pageJumpInput, 10)
        return !isNaN(page) && page >= 1 && page <= this.totalPages
      }
    },
  mounted() {
    this.fetchStudents()
  },
  methods: {
    // 获取学生列表
    async fetchStudents() {
      this.loading = true
      this.error = ''
      try {
        // 验证分页参数
        if (this.currentPage < 1) this.currentPage = 1
        if (this.itemsPerPage < 1 || this.itemsPerPage > 100) this.itemsPerPage = 10
        
        // 获取access_token
        const accessToken = localStorage.getItem('access_token') || localStorage.getItem('token')
        
        // 构建查询参数
        const params = new URLSearchParams()
        params.append('page', this.currentPage.toString())
        params.append('page_size', this.itemsPerPage.toString())
        if (this.searchKeyword && this.searchKeyword.trim()) {
          params.append('search', this.searchKeyword.trim())
        }
        
        const response = await fetch(`http://localhost:8000/teacher/students/list?${params.toString()}`, {
          method: 'GET',
          headers: {
            'Authorization': accessToken ? `Bearer ${accessToken}` : '',
            'Content-Type': 'application/json'
          }
        })
        
        if (!response.ok) {
          // 处理不同的错误状态码
          if (response.status === 401) {
            throw new Error('未认证，请重新登录')
          } else if (response.status === 403) {
            throw new Error('无权限访问此资源')
          } else {
            const errorData = await response.json().catch(() => ({}))
            throw new Error(errorData.detail || `获取学生列表失败 (${response.status})`)
          }
        }
        
        const data = await response.json()
        
        // 数据验证和清理
        if (!data || typeof data !== 'object') {
          throw new Error('无效的响应数据格式')
        }
        
        this.students = Array.isArray(data.students) ? data.students : []
        this.totalPages = Number(data.total_pages) || 0
        this.totalCount = Number(data.total_count) || 0
        this.currentPage = Number(data.current_page) || 1
        
        // 确保分页数据的一致性
        if (this.totalPages < 1) this.totalPages = 1
        if (this.currentPage < 1) this.currentPage = 1
        if (this.currentPage > this.totalPages) this.currentPage = this.totalPages
      } catch (err) {
        console.error('获取学生列表错误:', err)
        this.error = err.message || '获取学生列表失败，请稍后重试'
        // 使用模拟数据
        this.useMockData()
      } finally {
        this.loading = false
      }
    },
    
    // 使用模拟数据
    useMockData() {
      // 根据API返回格式提供模拟数据
      this.students = [
        {
          id: 101,
          name: '张三',
          gender: '男',
          toefl: 105.0,
          gre: 325.0,
          gpa: 3.6,
          target_region: '美国'
        },
        {
          id: 102,
          name: '李四',
          gender: '女',
          toefl: 100.0,
          gre: 315.0,
          gpa: 3.8,
          target_region: '英国'
        },
        {
          id: 103,
          name: '王五',
          gender: '男',
          toefl: 110.0,
          gre: null,
          gpa: 3.9,
          target_region: '澳大利亚'
        },
        {
          id: 104,
          name: '赵六',
          gender: '女',
          toefl: null,
          gre: 330.0,
          gpa: 4.0,
          target_region: '加拿大'
        }
      ]
      this.totalPages = 1
      this.totalCount = 4
      this.currentPage = 1
    },
    
    // 处理搜索
    handleSearch() {
      this.hasSearched = true
      this.currentPage = 1 // 重置到第一页
      this.fetchStudents() // 触发API请求
    },
    
    // 格式化语言成绩
    formatLanguageScore(student) {
      if (!student || typeof student !== 'object') return '未填写'
      const scores = []
      if (student.toefl !== null && student.toefl !== undefined) scores.push(`托福: ${student.toefl}`)
      if (student.gre !== null && student.gre !== undefined) scores.push(`GRE: ${student.gre}`)
      return scores.length > 0 ? scores.join(', ') : '未填写'
    },
    
    // 格式化状态（API没有提供申请状态，这里保留函数以避免错误）
    formatStatus(status) {
      return status !== null && status !== undefined ? status : '未填写'
    },
    
    // 获取GPA对应的CSS类名
    getGPAClass(gpa) {
      if (gpa === null || gpa === undefined) return 'text-muted'
      if (gpa >= 3.8) return 'text-success font-medium'
      if (gpa >= 3.5) return 'text-primary font-medium'
      if (gpa >= 3.0) return 'text-warning font-medium'
      return 'text-danger font-medium'
    },
    
    // 查看学生详情
    viewStudentDetails(studentId) {
      // 添加空值检查和类型转换
      const id = Number(studentId)
      if (isNaN(id)) {
        console.error('无效的学生ID:', studentId)
        return
      }
      this.currentStudent = this.students.find(s => s.id === id)
      this.showDetailModal = true
    },
    
    // 关闭详情模态框
    closeDetailModal() {
      this.showDetailModal = false
      this.currentStudent = null
    },
    
    // 联系学生
    contactStudent(studentId) {
      // 添加空值检查和类型转换
      const id = Number(studentId)
      if (isNaN(id)) {
        console.error('无效的学生ID:', studentId)
        return
      }
      const student = this.students.find(s => s.id === id)
      if (student) {
        alert(`联系学生 ${student.name}`)
        // API没有提供邮箱字段，这里简化处理
      }
    },
    
    // 跳转到指定页面
    goToPage(page) {
      // 输入验证和边界检查
      const targetPage = Number(page)
      if (isNaN(targetPage)) {
        console.error('无效的页码:', page)
        return
      }
      
      if (targetPage >= 1 && targetPage <= this.totalPages) {
        this.currentPage = targetPage
        this.fetchStudents()
      }
    },
    
    // 通过输入框跳转到指定页面
    jumpToPage() {
      if (this.isValidPageJump) {
        this.goToPage(this.pageJumpInput)
        this.pageJumpInput = ''
      }
    },
    
    // 验证页码输入
    validatePageInput() {
      const page = parseInt(this.pageJumpInput, 10)
      if (isNaN(page) || page < 1) {
        this.pageJumpInput = '1'
      } else if (page > this.totalPages) {
        this.pageJumpInput = String(this.totalPages)
      }
    }
  }
}
</script>

<style scoped>
.student-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-header h2 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-header p {
  color: #7f8c8d;
  font-size: 1.1rem;
}
.search-input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
}

.search-button {
  padding: 10px 20px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.search-button:hover {
  background-color: #2980b9;
}

.filter-options {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #3498db;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  text-align: center;
  padding: 40px 20px;
  background-color: #f8d7da;
  color: #721c24;
  border-radius: 8px;
  margin-bottom: 20px;
}

.retry-button {
  margin-top: 15px;
  padding: 8px 16px;
  background-color: #721c24;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.students-table-wrapper {
  overflow-x: auto;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.table-responsive {
    border: 1px solid #dee2e6;
    border-radius: 4px;
    overflow-x: auto;
  }

  .students-table {
    width: 100%;
    border-collapse: collapse;
  }

  .students-table th,
  .students-table td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #e0e0e0;
    vertical-align: middle;
  }

  .thead-light th {
    background-color: #f8f9fa;
    font-weight: 600;
    color: #495057;
  }

  .student-row:hover {
    background-color: #f8f9fa;
  }
  
  /* 响应式列宽调整 */
  .col-student-id {
    width: 80px;
    min-width: 80px;
  }
  
  .col-student-name {
    width: 100px;
    min-width: 100px;
  }
  
  .col-student-gender {
    width: 60px;
    min-width: 60px;
  }
  
  .col-student-gpa {
    width: 80px;
    min-width: 80px;
  }
  
  .col-student-score {
    width: 150px;
    min-width: 150px;
  }
  
  .col-student-target {
    width: 120px;
    min-width: 120px;
  }
  
  .col-student-action {
    width: 120px;
    min-width: 120px;
  }
  
  /* 响应式设计 */
  @media (max-width: 768px) {
    .students-table th,
    .students-table td {
      padding: 8px 10px;
      font-size: 14px;
    }
    
    .col-student-id,
    .col-student-gender,
    .col-student-gpa {
      width: 60px;
      min-width: 60px;
    }
    
    .col-student-score {
      width: 120px;
      min-width: 120px;
    }
    
    .col-student-action {
      width: 100px;
      min-width: 100px;
    }
  }

.student-name {
  font-weight: 500;
  color: #3498db;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-applying {
  background-color: #fff3cd;
  color: #856404;
}

.status-pending {
  background-color: #d1ecf1;
  color: #0c5460;
}

.status-accepted {
  background-color: #d4edda;
  color: #155724;
}

.status-rejected {
  background-color: #f8d7da;
  color: #721c24;
}

.status-waitlisted {
  background-color: #e2e3e5;
  color: #383d41;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-view,
.btn-contact {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.btn-view {
  background-color: #17a2b8;
  color: white;
}

.btn-view:hover {
  background-color: #138496;
}

.btn-contact {
  background-color: #28a745;
  color: white;
}

.btn-contact:hover {
  background-color: #218838;
}

/* 分页控件样式 */
  .pagination-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
    padding: 15px 0;
    border-top: 1px solid #e0e0e0;
    flex-wrap: wrap;
    gap: 15px;
  }
  
  .pagination-info {
    color: #666;
    font-size: 14px;
    min-width: 200px;
  }
  
  .pagination-controls {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 15px;
  }
  
  .pagination-buttons {
    display: flex;
    align-items: center;
    gap: 2px;
  }
  
  .pagination-btn {
    min-width: 32px;
    height: 32px;
    padding: 0 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: all 0.2s ease;
  }
  
  .pagination-btn:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  
  .pagination-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .pagination-ellipsis {
    cursor: default !important;
    background-color: #f8f9fa;
    color: #6c757d;
  }
  
  .page-jump {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
  }
  
  .page-input {
    width: 60px;
    padding: 6px 8px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    text-align: center;
    font-size: 14px;
  }
  
  .page-input:focus {
    outline: none;
    border-color: #4285f4;
    box-shadow: 0 0 0 2px rgba(66, 133, 244, 0.2);
  }
  
  .jump-btn {
    white-space: nowrap;
  }
  
  /* 响应式设计 */
  @media (max-width: 768px) {
    .pagination-container {
      flex-direction: column;
      align-items: stretch;
      gap: 10px;
    }
    
    .pagination-info {
      text-align: center;
      min-width: auto;
    }
    
    .pagination-controls {
      justify-content: center;
      gap: 10px;
    }
    
    .pagination-buttons {
      gap: 1px;
    }
    
    .pagination-btn {
      min-width: 28px;
      height: 28px;
      padding: 0 6px;
      font-size: 12px;
    }
    
    .page-input {
      width: 50px;
      padding: 4px 6px;
      font-size: 12px;
    }
    
    .page-jump {
      font-size: 12px;
    }
  }
  
  @media (max-width: 480px) {
    .pagination-controls {
      flex-direction: column;
    }
    
    .pagination-buttons {
      overflow-x: auto;
      padding-bottom: 5px;
    }
  }

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #7f8c8d;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  color: #2c3e50;
}

.modal-body {
  padding: 20px;
}

.student-details {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 15px;
}

.detail-row {
  display: contents;
}

.detail-row.full-width {
  grid-column: 1 / -1;
  display: block;
}

.detail-row.full-width .detail-label {
  display: block;
  margin-bottom: 5px;
}

.detail-label {
  font-weight: 500;
  color: #7f8c8d;
}

.detail-value {
  color: #2c3e50;
  word-break: break-word;
}

/* 响应式设计 */
@media (max-width: 768px) {
  
  
  .filter-options {
    flex-direction: column;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .students-table {
    font-size: 14px;
  }
  
  .students-table th,
  .students-table td {
    padding: 8px 10px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .student-details {
    grid-template-columns: 1fr;
  }
  
  .detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .detail-row.full-width {
    display: block;
  }
}
</style>
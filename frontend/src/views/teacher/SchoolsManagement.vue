<template>
  <div class="schools-management">
    <h2 class="page-title">学校管理</h2>
    
    <div class="content-card">
      <!-- 操作栏 -->
      <div class="action-bar">
        <button class="btn-primary" @click="openAddSchoolDialog">
          <i class="icon">➕</i> 添加学校
        </button>
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="搜索学校名称..." 
            class="search-input"
            @input="handleSearch"
          />
        </div>
      </div>

      <!-- 学校列表表格 -->
      <div class="table-container" v-if="!loading">
        <table class="schools-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>中文名称</th>
              <th>英文名称</th>
              <th>所在地</th>
              <th>排名</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="school in filteredSchools" :key="school.id" class="school-row">
              <td>{{ school.id }}</td>
              <td>{{ school.chinese_name }}</td>
              <td>{{ school.english_name }}</td>
              <td>{{ school.location }}</td>
              <td>{{ school.ranking }}</td>
              <td class="action-buttons">
                <button class="btn-view" @click="viewSchool(school)">查看</button>
                <button class="btn-edit" @click="editSchool(school)">编辑</button>
                <button class="btn-delete" @click="deleteSchool(school)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="filteredSchools.length === 0" class="empty-state">
          <p>暂无学校数据</p>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 错误提示 -->
      <div v-if="errorMessage" class="error-state">
        <p>{{ errorMessage }}</p>
        <button class="btn-retry" @click="fetchSchools">重试</button>
      </div>
    </div>

    <!-- 添加/编辑学校对话框 -->
    <div class="dialog-overlay" v-if="showDialog">
      <div class="dialog-content">
        <div class="dialog-header">
          <h3>{{ editingSchool ? '编辑学校' : '添加学校' }}</h3>
          <button class="btn-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <form @submit.prevent="saveSchool">
            <div class="form-row">
              <div class="form-group">
                <label for="chinese_name">中文名称 *</label>
                <input 
                  type="text" 
                  id="chinese_name" 
                  v-model="formData.chinese_name" 
                  required
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label for="english_name">英文名称 *</label>
                <input 
                  type="text" 
                  id="english_name" 
                  v-model="formData.english_name" 
                  required
                  class="form-input"
                />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="location">所在地 *</label>
                <input 
                  type="text" 
                  id="location" 
                  v-model="formData.location" 
                  required
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label for="ranking">排名 *</label>
                <input 
                  type="number" 
                  id="ranking" 
                  v-model.number="formData.ranking" 
                  required
                  min="1"
                  class="form-input"
                />
              </div>
            </div>
            <div class="form-group">
              <label for="introduction">学校介绍</label>
              <textarea 
                id="introduction" 
                v-model="formData.introduction" 
                rows="3"
                class="form-input"
              ></textarea>
            </div>
            <div class="form-group">
              <label for="details">详细信息</label>
              <textarea 
                id="details" 
                v-model="formData.details" 
                rows="5"
                class="form-input"
              ></textarea>
            </div>
            <div class="dialog-footer">
              <button type="button" class="btn-cancel" @click="closeDialog">取消</button>
              <button type="submit" class="btn-submit" :disabled="saving">
                {{ saving ? '保存中...' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 确认删除对话框 -->
    <div class="dialog-overlay" v-if="showDeleteDialog">
      <div class="dialog-content delete-dialog">
        <div class="dialog-header">
          <h3>确认删除</h3>
          <button class="btn-close" @click="showDeleteDialog = false">&times;</button>
        </div>
        <div class="dialog-body">
          <p>确定要删除学校 "{{ schoolToDelete?.chinese_name }}" 吗？此操作不可撤销。</p>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showDeleteDialog = false">取消</button>
          <button class="btn-danger" @click="confirmDelete" :disabled="deleting">
            {{ deleting ? '删除中...' : '删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'SchoolsManagement',
  data() {
    return {
      schools: [], // 学校列表数据
      loading: false, // 加载状态
      saving: false, // 保存状态
      deleting: false, // 删除状态
      errorMessage: '', // 错误信息
      searchQuery: '', // 搜索关键词
      showDialog: false, // 添加/编辑对话框显示状态
      showDeleteDialog: false, // 删除确认对话框显示状态
      editingSchool: null, // 当前编辑的学校
      schoolToDelete: null, // 准备删除的学校
      formData: {
        chinese_name: '',
        english_name: '',
        location: '',
        ranking: 1,
        introduction: '',
        details: ''
      }
    }
  },
  computed: {
    // 过滤后的学校列表
    filteredSchools() {
      if (!this.searchQuery) return this.schools
      
      const query = this.searchQuery.toLowerCase()
      return this.schools.filter(school => 
        school.chinese_name.toLowerCase().includes(query) ||
        school.english_name.toLowerCase().includes(query)
      )
    }
  },
  mounted() {
    this.fetchSchools()
  },
  methods: {
    // 获取所有学校列表
    async fetchSchools() {
      this.loading = true
      this.errorMessage = ''
      
      try {
        const response = await axios.get('/api/api/schools', {
          headers: this.getAuthHeaders()
        })
        this.schools = response.data
      } catch (error) {
        console.error('获取学校列表失败:', error)
        this.errorMessage = '获取学校列表失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },
    
    // 获取认证头
    getAuthHeaders() {
      const token = localStorage.getItem('access_token')
      return {
        Authorization: token ? `Bearer ${token}` : ''
      }
    },
    
    // 处理搜索
    handleSearch() {
      // 搜索逻辑已在computed中处理
    },
    
    // 打开添加学校对话框
    openAddSchoolDialog() {
      this.editingSchool = null
      this.resetFormData()
      this.showDialog = true
    },
    
    // 编辑学校
    editSchool(school) {
      this.editingSchool = school
      this.formData = {
        chinese_name: school.chinese_name,
        english_name: school.english_name,
        location: school.location,
        ranking: school.ranking,
        introduction: school.introduction || '',
        details: school.details || ''
      }
      this.showDialog = true
    },
    
    // 查看学校详情
    viewSchool(school) {
      // 可以跳转到详情页或者显示详情弹窗
      console.log('查看学校详情:', school)
      // 暂时复用编辑弹窗显示详情
      this.editSchool(school)
      // 这里可以添加只读模式的逻辑
    },
    
    // 删除学校
    deleteSchool(school) {
      this.schoolToDelete = school
      this.showDeleteDialog = true
    },
    
    // 确认删除
    async confirmDelete() {
      if (!this.schoolToDelete) return
      
      this.deleting = true
      
      try {
        await axios.delete(`/api/api/schools/${this.schoolToDelete.id}`, {
          headers: this.getAuthHeaders()
        })
        
        // 从列表中移除
        this.schools = this.schools.filter(school => school.id !== this.schoolToDelete.id)
        this.showDeleteDialog = false
      } catch (error) {
        console.error('删除学校失败:', error)
        this.errorMessage = '删除学校失败，请稍后重试'
        this.showDeleteDialog = false
      } finally {
        this.deleting = false
        this.schoolToDelete = null
      }
    },
    
    // 保存学校
    async saveSchool() {
      this.saving = true
      
      try {
        if (this.editingSchool) {
          // 更新学校
          const response = await axios.put(`/api/api/schools/${this.editingSchool.id}`, 
            this.formData, 
            {
              headers: this.getAuthHeaders()
            }
          )
          
          // 更新本地数据
          const index = this.schools.findIndex(school => school.id === this.editingSchool.id)
          if (index !== -1) {
            this.schools.splice(index, 1, response.data)
          }
        } else {
          // 添加学校
          const response = await axios.post('/api/api/schools', 
            this.formData, 
            {
              headers: this.getAuthHeaders()
            }
          )
          
          // 添加到列表
          this.schools.push(response.data)
        }
        
        this.closeDialog()
      } catch (error) {
        console.error('保存学校失败:', error)
        this.errorMessage = error.response?.data?.detail || '保存学校失败，请稍后重试'
      } finally {
        this.saving = false
      }
    },
    
    // 关闭对话框
    closeDialog() {
      this.showDialog = false
      this.resetFormData()
    },
    
    // 重置表单数据
    resetFormData() {
      this.formData = {
        chinese_name: '',
        english_name: '',
        location: '',
        ranking: 1,
        introduction: '',
        details: ''
      }
    }
  }
}
</script>

<style scoped>
.schools-management {
  background-color: #f5f7fa;
  min-height: 80vh;
  padding: 20px;
}

.page-title {
  margin-bottom: 24px;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.content-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 24px;
}

/* 操作栏样式 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

/* 按钮样式 */
button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background-color: #1890ff;
  color: white;
}

.btn-primary:hover {
  background-color: #40a9ff;
}

.btn-view {
  background-color: #52c41a;
  color: white;
}

.btn-view:hover {
  background-color: #73d13d;
}

.btn-edit {
  background-color: #faad14;
  color: white;
}

.btn-edit:hover {
  background-color: #ffc53d;
}

.btn-delete {
  background-color: #ff4d4f;
  color: white;
}

.btn-delete:hover {
  background-color: #ff7875;
}

.btn-retry {
  background-color: #1890ff;
  color: white;
  margin-top: 12px;
}

.btn-retry:hover {
  background-color: #40a9ff;
}

.btn-close {
  background: none;
  color: #999;
  font-size: 20px;
  padding: 4px;
  line-height: 1;
}

.btn-close:hover {
  color: #666;
}

.btn-cancel {
  background-color: #f0f0f0;
  color: #333;
}

.btn-cancel:hover {
  background-color: #e6e6e6;
}

.btn-submit {
  background-color: #1890ff;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background-color: #40a9ff;
}

.btn-submit:disabled {
  background-color: #d9d9d9;
  cursor: not-allowed;
}

.btn-danger {
  background-color: #ff4d4f;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #ff7875;
}

.btn-danger:disabled {
  background-color: #d9d9d9;
  cursor: not-allowed;
}

/* 搜索框样式 */
.search-box {
  position: relative;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  width: 240px;
}

.search-input:focus {
  outline: none;
  border-color: #1890ff;
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
  max-height: 600px; /* 设置表格容器的最大高度 */
  position: relative;
}

.schools-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed; /* 固定表格布局 */
}

.schools-table thead {
  position: sticky;
  top: 0;
  background-color: #fafafa;
  z-index: 10; /* 确保表头在内容上方 */
}

.schools-table th,
.schools-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
  white-space: nowrap; /* 防止内容换行 */
  overflow: hidden;
  text-overflow: ellipsis; /* 超出部分显示省略号 */
}

/* 为每列设置适当的宽度 */
.schools-table th:nth-child(1),
.schools-table td:nth-child(1) {
  width: 80px;
}

.schools-table th:nth-child(2),
.schools-table td:nth-child(2) {
  width: 160px;
}

.schools-table th:nth-child(3),
.schools-table td:nth-child(3) {
  width: 220px;
}

.schools-table th:nth-child(4),
.schools-table td:nth-child(4) {
  width: 100px;
}

.schools-table th:nth-child(5),
.schools-table td:nth-child(5) {
  width: 80px;
}

.schools-table th:nth-child(6),
.schools-table td:nth-child(6) {
  width: 250px; /* 增加操作列宽度，确保按钮完整显示 */
}

.schools-table th {
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e8e8e8;
}

.school-row:hover {
  background-color: #f5f5f5;
}

.action-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: nowrap;
}

/* 调整操作按钮样式，确保完整显示 */
.action-buttons button {
  padding: 6px 12px;
  font-size: 13px;
  white-space: nowrap;
  flex-shrink: 0;
}

/* 加载状态 */
.loading-state,
.empty-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f0f0f0;
  border-top: 3px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  color: #ff4d4f;
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-content {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.delete-dialog {
  max-width: 400px;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.dialog-header h3 {
  margin: 0;
  color: #333;
  font-size: 16px;
}

.dialog-body {
  padding: 24px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
}

/* 表单样式 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  color: #333;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.form-input:focus {
  outline: none;
  border-color: #1890ff;
}

textarea.form-input {
  resize: vertical;
}

/* 模态框表单左右布局样式 */
.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.form-row .form-group {
  flex: 1;
  min-width: 200px;
  margin-bottom: 16px;
}

.form-row .form-input {
  box-sizing: border-box;
}

.form-row .form-input:focus {
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .form-row .form-group {
    min-width: auto;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .schools-management {
    padding: 12px;
  }
  
  .content-card {
    padding: 16px;
  }
  
  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    width: 100%;
  }
  
  .schools-table {
    font-size: 14px;
  }
  
  .schools-table th,
  .schools-table td {
    padding: 8px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }
  
  .action-buttons button {
    padding: 4px 8px;
    font-size: 12px;
  }
  
  .dialog-content {
    width: 95%;
    margin: 20px;
  }
  
  .dialog-body {
    padding: 16px;
  }
}
</style>
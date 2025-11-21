<template>
  <div class="training-management">
    <h2>培训管理</h2>
    
    <!-- 错误消息显示 -->
    <div v-if="error" class="error-message">
      <span class="error-icon">⚠</span>
      {{ error }}
      <button class="btn-close" @click="clearError">×</button>
    </div>
    
    <!-- 筛选条件 -->
    <div class="filter-section">
      <div class="filter-item">
        <label>状态筛选：</label>
        <select v-model="filters.status" @change="fetchTrainingList">
          <option value="">全部</option>
          <option value="pending">待处理</option>
          <option value="accepted">已接受</option>
          <option value="rejected">已拒绝</option>
          <option value="completed">已完成</option>
        </select>
      </div>
      <div class="filter-item">
        <label>学生姓名：</label>
        <input type="text" v-model="filters.student_name" @input="handleNameInput" placeholder="输入学生姓名...">
      </div>
      <div class="filter-item">
        <label>培训类型：</label>
        <select v-model="filters.training_type" @change="fetchTrainingList">
          <option value="">全部</option>
          <option value="托福">托福培训</option>
          <option value="GRE">GRE培训</option>
          <option value="GPA">GPA培训</option>
          <option value="其他">其他培训</option>
        </select>
      </div>
    </div>
    
    <!-- 培训列表 -->
    <div class="training-list">
      <table class="training-table">
        <thead>
          <tr>
            <th>学生姓名</th>
            <th>培训类型</th>
            <th>总课时</th>
            <th>已完成课时</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>备注</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="training in trainingList" :key="training.id">
            <td>{{ training.student_name }}</td>
            <td>{{ training.training_type }}</td>
            <td>{{ training.total_hours }}</td>
            <td>{{ training.completed_hours || 0 }}</td>
            <td>
              <span :class="['status-badge', `status-${training.status}`]">
                {{ getStatusText(training.status) }}
              </span>
            </td>
            <td>{{ formatDate(training.created_at) }}</td>
            <td>{{ training.notes || '-' }}</td>
            <td>
              <!-- 根据状态显示不同操作按钮 -->
              <div v-if="training.status === 'pending'" class="action-buttons">
                <button class="btn btn-accept" @click="handleAccept(training)" :disabled="actionLoading">接受</button>
                <button class="btn btn-reject" @click="handleReject(training)" :disabled="actionLoading">拒绝</button>
              </div>
              <div v-else-if="training.status === 'accepted'" class="action-buttons">
                <button class="btn btn-progress" @click="updateProgress(training)" :disabled="actionLoading">更新进度</button>
                <button class="btn btn-feedback" @click="submitFeedback(training)" :disabled="training.feedback || actionLoading">提交反馈</button>
              </div>
              <div v-else class="action-buttons">
                <span>-</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="trainingList.length === 0" class="empty">暂无培训预约记录</div>
    </div>
    
    <!-- 更新进度对话框 -->
    <div v-if="showProgressDialog" class="modal-overlay" @click="closeProgressDialog">
      <div class="modal-content" @click.stop>
        <h3>更新培训进度</h3>
        <div class="form-group">
          <label>已完成课时：</label>
          <input 
            type="number" 
            v-model.number="progressData.hours" 
            min="0" 
            :max="progressData.totalHours"
            placeholder="请输入已完成课时"
          >
        </div>
        <div class="modal-actions">
          <button class="btn btn-primary" @click="confirmProgressUpdate" :disabled="actionLoading">确认</button>
          <button class="btn btn-secondary" @click="closeProgressDialog" :disabled="actionLoading">取消</button>
        </div>
      </div>
    </div>
    
    <!-- 提交反馈对话框 -->
    <div v-if="showFeedbackDialog" class="modal-overlay" @click="closeFeedbackDialog">
      <div class="modal-content" @click.stop>
        <h3>提交培训反馈</h3>
        <div class="form-group">
          <label>反馈内容：</label>
          <textarea 
            v-model="feedbackData.content" 
            rows="4" 
            placeholder="请输入培训反馈内容..."
          ></textarea>
        </div>
        <div class="modal-actions">
          <button class="btn btn-primary" @click="confirmFeedbackSubmit" :disabled="actionLoading">提交</button>
          <button class="btn btn-secondary" @click="closeFeedbackDialog" :disabled="actionLoading">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TrainingManagement',
  data() {
    return {
      trainingList: [],
      loading: false,
      actionLoading: false,
      error: null,
      filters: {
        status: '',
        student_name: '',
        training_type: ''
      },
      nameInputTimer: null,
      showProgressDialog: false,
      progressData: {
        trainingId: null,
        hours: 0,
        totalHours: 0
      },
      showFeedbackDialog: false,
      feedbackData: {
        trainingId: null,
        content: ''
      }
    }
  },
  mounted() {
    this.fetchTrainingList()
  },
  methods: {
    // 获取培训预约列表
    async fetchTrainingList() {
      this.loading = true
      this.error = null
      
      try {
        const queryParams = new URLSearchParams()
        if (this.filters.status) queryParams.append('status', this.filters.status)
        if (this.filters.student_name) queryParams.append('student_name', this.filters.student_name)
        if (this.filters.training_type) queryParams.append('training_type', this.filters.training_type)
        
        const queryString = queryParams.toString()
        const url = `/api/teacher/training/list${queryString ? '?' + queryString : ''}`
        
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': (localStorage.getItem('access_token') || localStorage.getItem('token')) ? `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}` : ''
          }
        })
        
        // 先检查响应内容类型
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('text/html')) {
          // 如果是HTML响应，读取文本内容而不是解析为JSON
          const htmlContent = await response.text();
          console.error('API返回了HTML内容:', htmlContent.substring(0, 100) + '...');
          throw new Error(`API返回了HTML页面而不是JSON数据 (状态码: ${response.status})`);
        }
        
        if (!response.ok) {
          // 尝试解析错误响应中的JSON
          try {
            const errorData = await response.json();
            throw new Error(errorData.detail || `获取培训列表失败: ${response.status}`);
          } catch (jsonError) {
            // 如果解析失败，使用基本错误信息
            throw new Error(`获取培训列表失败: ${response.status}`);
          }
        }
        
        this.trainingList = await response.json()
      } catch (err) {
        this.error = err.message
        console.error('获取培训列表错误:', err)
        // 使用模拟数据
        this.trainingList = [
          {
            id: 1001,
            student_name: "张三",
            training_type: "托福培训",
            total_hours: 20,
            current_progress: 8,
            status: "accepted",
            created_at: "2023-10-01T09:30:00",
            notes: "希望重点辅导听力",
            feedback: null
          },
          {
            id: 1002,
            student_name: "李四",
            training_type: "GRE数学",
            total_hours: 15,
            current_progress: 0,
            status: "pending",
            created_at: "2023-10-02T14:00:00",
            notes: "",
            feedback: null
          },
          {
            id: 1003,
            student_name: "王五",
            training_type: "雅思培训",
            total_hours: 30,
            current_progress: 30,
            status: "completed",
            created_at: "2023-09-15T10:00:00",
            notes: "需要口语辅导",
            feedback: "学生进步明显，口语流利度提升较快"
          }
        ]
      } finally {
        this.loading = false
      }
    },
    
    // 处理姓名输入（防抖）
    handleNameInput() {
      if (this.nameInputTimer) {
        clearTimeout(this.nameInputTimer)
      }
      this.nameInputTimer = setTimeout(() => {
        this.fetchTrainingList()
      }, 500)
    },
    
    // 获取状态文本
    getStatusText(status) {
      const statusMap = {
        pending: '待处理',
        accepted: '已接受',
        rejected: '已拒绝',
        completed: '已完成'
      }
      return statusMap[status] || status
    },
    
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    },
    
    // 接受培训预约
    async handleAccept(training) {
      this.actionLoading = true
      try {
        const response = await fetch(`/api/teacher/training/status`, {
          method: 'PUT',
          headers: {
              'Content-Type': 'application/json',
              'Authorization': (localStorage.getItem('access_token') || localStorage.getItem('token')) ? `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}` : ''
            },
          body: JSON.stringify({
            reservation_id: training.id,
            status: 'accepted'
          })
        })
        
        // 检查响应内容类型
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('text/html')) {
          const htmlContent = await response.text();
          console.error('API返回了HTML内容:', htmlContent.substring(0, 100) + '...');
          throw new Error(`API返回了HTML页面而不是JSON数据 (状态码: ${response.status})`);
        }
        
        if (!response.ok) {
          try {
            const errorData = await response.json();
            throw new Error(errorData.detail || '更新状态失败');
          } catch (jsonError) {
            throw new Error('更新状态失败');
          }
        }
        
        const result = await response.json()
        console.log(result.message)
        // 刷新列表
        this.fetchTrainingList()
      } catch (err) {
        this.error = err.message
        console.error('接受培训预约错误:', err)
        // 本地更新状态（模拟）
        training.status = 'accepted'
      } finally {
        this.actionLoading = false
      }
    },
    
    // 拒绝培训预约
    async handleReject(training) {
      this.actionLoading = true
      this.error = null
      
      try {
        const response = await fetch('/teacher/training/status', {
          method: 'PUT',
          headers: {
              'Content-Type': 'application/json',
              'Authorization': (localStorage.getItem('access_token') || localStorage.getItem('token')) ? `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}` : ''
            },
          body: JSON.stringify({
            reservation_id: training.id,
            status: 'rejected'
          })
        })
        
        // 检查响应内容类型
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('text/html')) {
          const htmlContent = await response.text();
          console.error('API返回了HTML内容:', htmlContent.substring(0, 100) + '...');
          throw new Error(`API返回了HTML页面而不是JSON数据 (状态码: ${response.status})`);
        }
        
        if (!response.ok) {
          try {
            const errorData = await response.json();
            throw new Error(errorData.detail || '更新状态失败');
          } catch (jsonError) {
            throw new Error('更新状态失败');
          }
        }
        
        const result = await response.json()
        console.log(result.message)
        // 刷新列表
        this.fetchTrainingList()
      } catch (err) {
        this.error = err.message
        console.error('拒绝培训预约错误:', err)
        // 本地更新状态（模拟）
        training.status = 'rejected'
      } finally {
        this.actionLoading = false
      }
    },
    
    // 更新培训进度
    updateProgress(training) {
      this.progressData = {
          trainingId: training.id,
          hours: training.completed_hours || 0,
          totalHours: training.total_hours
        }
      this.showProgressDialog = true
    },
    
    // 确认更新进度
    async confirmProgressUpdate() {
      if (this.progressData.hours > this.progressData.totalHours) {
        alert('已完成课时不能超过总课时')
        return
      }
      
      this.actionLoading = true
      try {
        const response = await fetch(`/api/teacher/training/progress`, {
          method: 'PUT',
          headers: {
              'Content-Type': 'application/json',
              'Authorization': (localStorage.getItem('access_token') || localStorage.getItem('token')) ? `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}` : ''
            },
          body: JSON.stringify({
            reservation_id: this.progressData.trainingId,
            attended_hours: this.progressData.hours
          })
        })
        
        // 检查响应内容类型
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('text/html')) {
          const htmlContent = await response.text();
          console.error('API返回了HTML内容:', htmlContent.substring(0, 100) + '...');
          throw new Error(`API返回了HTML页面而不是JSON数据 (状态码: ${response.status})`);
        }
        
        if (!response.ok) {
          try {
            const errorData = await response.json();
            throw new Error(errorData.detail || '更新进度失败');
          } catch (jsonError) {
            throw new Error('更新进度失败');
          }
        }
        
        const result = await response.json()
        console.log(result.message)
        // 如果完成了所有课时，更新状态为completed
        if (result.completed_hours === result.total_hours) {
          const training = this.trainingList.find(t => t.id === this.progressData.trainingId)
          if (training) {
            training.status = 'completed'
          }
        }
        // 刷新列表
        this.fetchTrainingList()
        this.closeProgressDialog()
      } catch (err) {
        this.error = err.message
        console.error('更新进度错误:', err)
        // 本地更新进度（模拟）
        const training = this.trainingList.find(t => t.id === this.progressData.trainingId)
        if (training) {
          training.completed_hours = this.progressData.hours
          if (this.progressData.hours === training.total_hours) {
            training.status = 'completed'
          }
        }
        this.closeProgressDialog()
      } finally {
        this.actionLoading = false
      }
    },
    
    // 关闭进度对话框
    closeProgressDialog() {
      this.showProgressDialog = false
      this.progressData = {
        trainingId: null,
        hours: 0,
        totalHours: 0
      }
    },
    
    // 提交培训反馈
    submitFeedback(training) {
      this.feedbackData = {
        trainingId: training.id,
        content: ''
      }
      this.showFeedbackDialog = true
    },
    
    // 确认提交反馈
    async confirmFeedbackSubmit() {
      if (!this.feedbackData.content.trim()) {
        alert('反馈内容不能为空')
        return
      }
      
      this.actionLoading = true
      try {
        const response = await fetch(`/api/teacher/training/feedback`, {
          method: 'PUT',
          headers: {
              'Content-Type': 'application/json',
              'Authorization': (localStorage.getItem('access_token') || localStorage.getItem('token')) ? `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}` : ''
            },
          body: JSON.stringify({
            reservation_id: this.feedbackData.trainingId,
            feedback: this.feedbackData.content
          })
        })
        
        // 检查响应内容类型
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('text/html')) {
          const htmlContent = await response.text();
          console.error('API返回了HTML内容:', htmlContent.substring(0, 100) + '...');
          throw new Error(`API返回了HTML页面而不是JSON数据 (状态码: ${response.status})`);
        }
        
        if (!response.ok) {
          try {
            const errorData = await response.json();
            throw new Error(errorData.detail || '提交反馈失败');
          } catch (jsonError) {
            throw new Error('提交反馈失败');
          }
        }
        
        const result = await response.json()
        console.log(result.message)
        // 刷新列表
        this.fetchTrainingList()
        this.closeFeedbackDialog()
      } catch (err) {
        this.error = err.message
        console.error('提交反馈错误:', err)
        // 本地更新反馈（模拟）
        const training = this.trainingList.find(t => t.id === this.feedbackData.trainingId)
        if (training) {
          training.feedback = this.feedbackData.content
        }
        this.closeFeedbackDialog()
      } finally {
        this.actionLoading = false
      }
    },
    
    // 关闭反馈对话框
    closeFeedbackDialog() {
      this.showFeedbackDialog = false
      this.feedbackData = {
        trainingId: null,
        content: ''
      }
    },
    
    // 清除错误消息
    clearError() {
      this.error = null
    }
  }
}
</script>

<style scoped>
.training-management {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  margin: 0 0 24px 0;
  color: #333;
  font-size: 20px;
  font-weight: 500;
}

/* 筛选区域样式 */
.filter-section {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 6px;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-item label {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

.filter-item select,
.filter-item input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 120px;
}

.filter-item input {
  min-width: 150px;
}

/* 培训列表样式 */
.training-list {
  overflow-x: auto;
}

.training-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.training-table th {
  background-color: #f8f9fa;
  border-bottom: 2px solid #e9ecef;
  padding: 12px;
  text-align: left;
  font-weight: 500;
  color: #495057;
}

.training-table td {
  padding: 12px;
  border-bottom: 1px solid #e9ecef;
  color: #333;
}

.training-table tr:hover {
  background-color: #f8f9fa;
}

/* 状态标签样式 */
.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background-color: #fff3cd;
  color: #856404;
}

.status-accepted {
  background-color: #d4edda;
  color: #155724;
}

.status-rejected {
  background-color: #f8d7da;
  color: #721c24;
}

.status-completed {
  background-color: #d1ecf1;
  color: #0c5460;
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-accept {
  background-color: #28a745;
  color: white;
}

.btn-accept:hover:not(:disabled) {
  background-color: #218838;
}

.btn-reject {
  background-color: #dc3545;
  color: white;
}

.btn-reject:hover:not(:disabled) {
  background-color: #c82333;
}

.btn-progress {
  background-color: #007bff;
  color: white;
}

.btn-progress:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-feedback {
  background-color: #ffc107;
  color: #212529;
}

.btn-feedback:hover:not(:disabled) {
  background-color: #e0a800;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #545b62;
}

/* 加载和空状态样式 */
.loading,
.empty {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 14px;
}

/* 错误消息样式 */
.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 12px 16px;
  border-radius: 4px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-icon {
  font-size: 16px;
}

.btn-close {
  margin-left: auto;
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #721c24;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  opacity: 0.7;
}

/* 加载中覆盖层 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
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
  padding: 24px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-content h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #666;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
</style>
<template>
  <div class="training-appointment">
    <h2>培训预约</h2>
    
    <div class="training-content">
      <!-- 预约表单 -->
      <div class="reservation-form">
        <h3>语言培训预约</h3>
        
        <!-- 成功提示 -->
        <div v-if="successMessage" class="success-message">
          <p>{{ successMessage }}</p>
          <button class="close-btn" @click="successMessage = ''">关闭</button>
        </div>
        
        <!-- 错误提示 -->
        <div v-if="errorMessage" class="error-message">
          <p>{{ errorMessage }}</p>
          <button class="close-btn" @click="errorMessage = ''">关闭</button>
        </div>
        
        <form @submit.prevent="submitReservation" class="form-container">
          <!-- 左右布局容器 -->
          <div class="form-row">
            <!-- 左侧列 -->
            <div class="form-column">
              <!-- 总课时 -->
              <div class="form-group">
                <label for="total_hours">总课时 <span class="required">*</span></label>
                <input
                  id="total_hours"
                  type="number"
                  v-model.number="reservationForm.total_hours"
                  class="form-control"
                  placeholder="请输入总课时数"
                  min="1"
                  required
                />
                <div v-if="errors.total_hours" class="error-hint">{{ errors.total_hours }}</div>
              </div>
            </div>
            
            <!-- 右侧列 -->
            <div class="form-column">
              <!-- 培训类型 -->
              <div class="form-group">
                <label for="training_type">培训类型（可选）</label>
                <select id="training_type" v-model="reservationForm.training_type" class="form-control">
                  <option value="">请选择培训类型</option>
                  <option value="托福">托福</option>
                  <option value="雅思">雅思</option>
                  <option value="GRE">GRE</option>
                  <option value="GMAT">GMAT</option>
                  <option value="SAT">SAT</option>
                  <option value="其他">其他</option>
                </select>
              </div>
              
              <!-- 备注信息 -->
              <div class="form-group">
                <label for="notes">备注信息（可选）</label>
                <textarea
                  id="notes"
                  v-model="reservationForm.notes"
                  class="form-control"
                  placeholder="请输入您的特殊需求或其他备注信息"
                  rows="3"
                  maxlength="500"
                ></textarea>
                <div class="char-count">{{ reservationForm.notes.length }}/500</div>
              </div>
            </div>
          </div>
          
          <!-- 提交按钮 -->
          <div class="form-actions">
            <button type="submit" class="submit-btn" :disabled="loading">
              <span v-if="loading">提交中...</span>
              <span v-else>提交预约</span>
            </button>
            <button type="reset" class="reset-btn" @click="resetForm">重置</button>
          </div>
        </form>
      </div>
          <!-- 预约列表 -->
      <div class="reservation-list">
        <div class="list-header">
          <h3>我的预约记录</h3>
          <button class="refresh-list-btn" @click="fetchReservations" :disabled="reservationsLoading">
            <span v-if="reservationsLoading">加载中...</span>
            <span v-else>刷新列表</span>
          </button>
        </div>
        
        <!-- 预约列表加载状态 -->
        <div v-if="reservationsLoading" class="loading-state">
          <p>正在加载预约记录...</p>
        </div>
        
        <!-- 预约列表错误提示 -->
        <div v-else-if="reservationsError" class="list-error">
          <p>{{ reservationsError }}</p>
          <button class="retry-btn" @click="fetchReservations">重试</button>
        </div>
        
        <!-- 预约列表为空 -->
        <div v-else-if="reservations.length === 0" class="empty-state">
          <p>暂无预约记录</p>
        </div>
        
        <!-- 预约列表 -->
        <div v-else class="reservations-container">
          <table class="reservations-table">
            <thead>
              <tr>
                <th>预约ID</th>
                <th>培训类型</th>
                <th>总课时</th>
                <th>已完成课时</th>
                <th>教师</th>
                <th>状态</th>
                <th>创建时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="reservation in reservations" :key="reservation.id" class="reservation-item">
                <td>{{ reservation.id }}</td>
                <td>{{ reservation.training_type }}</td>
                <td>{{ reservation.total_hours }}</td>
                <td>{{ reservation.completed_hours || 0 }}</td>
                <td>{{ reservation.teacher_name }}</td>
                <td>
                  <span :class="['status-badge', `status-${reservation.status.toLowerCase()}`]">
                    {{ getStatusText(reservation.status) }}
                  </span>
                </td>
                <td>{{ formatDate(reservation.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TrainingAppointment',
  data() {
      return {
        reservationForm: {
          teacher_id: '14',
          total_hours: null,
          training_type: '',
          notes: ''
        },
      // 教师列表
      teachers: [],
      // 加载状态
      loading: false,
      // 表单验证错误
      errors: {},
      // 提示消息
      successMessage: '',
      errorMessage: '',
      // 预约列表相关数据
      reservations: [], // 预约列表
      reservationsLoading: false, // 预约列表加载状态
      reservationsError: '' // 预约列表错误信息
    }
  },
  mounted() {
    // 页面加载时获取教师列表
    this.fetchTeachers();
    // 页面加载时获取预约列表
    this.fetchReservations();
  },
  methods: {
    // 获取教师列表
    async fetchTeachers() {
      try {
        // 获取access_token
        const accessToken = localStorage.getItem('access_token') || localStorage.getItem('token');
        
        const response = await fetch('http://localhost:8000/api/teachers', {
          headers: {
            'Authorization': accessToken ? `Bearer ${accessToken}` : ''
          }
        });
        
        if (!response.ok) {
          throw new Error('获取教师列表失败');
        }
        
        this.teachers = await response.json();
        console.log('成功获取教师列表:', this.teachers);
      } catch (err) {
        console.error('获取教师列表错误:', err);
        // 教师列表获取失败不影响主要功能，可以静默处理
      }
    },
    
    // 表单验证
    validateForm() {
      this.errors = {};
      let isValid = true;
      
      // 验证总课时
      if (!this.reservationForm.total_hours || this.reservationForm.total_hours <= 0) {
        this.errors.total_hours = '请输入有效的课时数（必须大于0）';
        isValid = false;
      }
      
      return isValid;
    },
    
    // 提交预约
    async submitReservation() {
      // 表单验证
      if (!this.validateForm()) {
        return;
      }
      
      this.loading = true;
      this.successMessage = '';
      this.errorMessage = '';
      
      try {
        // 获取access_token
        const accessToken = localStorage.getItem('access_token') || localStorage.getItem('token');
        
        // 准备请求数据，移除空值字段
        const requestData = {
          ...this.reservationForm
        };
        
        // 确保teacher_id始终包含在请求中，不再根据空字符串判断
        // if (requestData.teacher_id === '') {
        //   delete requestData.teacher_id;
        // }
        
        // 如果training_type为空字符串，则移除该字段
        if (requestData.training_type === '') {
          delete requestData.training_type;
        }
        
        // 如果notes为空字符串，则移除该字段
        if (requestData.notes === '') {
          delete requestData.notes;
        }
        
        const response = await fetch('http://localhost:8000/student/training/reserve', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': accessToken ? `Bearer ${accessToken}` : ''
          },
          body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          let errorData = {};
          try {
            errorData = JSON.parse(errorText);
          } catch (e) {
            console.error('解析错误响应失败:', errorText);
          }
          throw new Error(errorData.detail || `预约失败: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('预约成功:', result);
        
        // 显示成功消息
        this.successMessage = `预约成功！预约ID：${result.reservation_id}`;
        
        // 重置表单
        this.resetForm();
        
        // 自动刷新预约列表
        setTimeout(() => {
          this.fetchReservations();
        }, 500);
        
      } catch (err) {
        this.errorMessage = err.message || '预约提交失败，请稍后重试';
        console.error('预约提交错误:', err);
      } finally {
        this.loading = false;
      }
    },
    
    // 重置表单
    resetForm() {
      this.reservationForm = {
        teacher_id: '14',
        total_hours: null,
        training_type: '',
        notes: ''
      };
      this.errors = {};
    },
    
    // 获取预约列表
    async fetchReservations() {
      this.reservationsLoading = true;
      this.reservationsError = '';
      
      try {
        // 获取access_token
        const accessToken = localStorage.getItem('access_token') || localStorage.getItem('token');
        
        const response = await fetch('http://localhost:8000/student/training/list', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': accessToken ? `Bearer ${accessToken}` : ''
          }
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          let errorData = {};
          try {
            errorData = JSON.parse(errorText);
          } catch (e) {
            console.error('解析错误响应失败:', errorText);
          }
          throw new Error(errorData.detail || `获取预约列表失败: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('获取预约列表成功:', result);
        
        // 处理预约列表数据
        this.reservations = result.map(reservation => ({
          ...reservation,
          // 确保必要字段存在
          training_type: reservation.training_type || '未指定',
          completed_hours: reservation.completed_hours || 0,
          teacher_name: reservation.teacher_name || '系统分配中'
        }));
        
      } catch (err) {
        this.reservationsError = err.message || '获取预约列表失败，请稍后重试';
        console.error('获取预约列表错误:', err);
      } finally {
        this.reservationsLoading = false;
      }
    },
    
    // 获取状态中文文本
    getStatusText(status) {
      const statusMap = {
        'PENDING': '待处理',
        'ACCEPTED': '已接受',
        'COMPLETED': '已完成',
        'REJECTED': '已拒绝'
      };
      return statusMap[status] || status;
    },
    
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return '-';
      
      try {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        
        return `${year}-${month}-${day} ${hours}:${minutes}`;
      } catch (err) {
        console.error('日期格式化错误:', err);
        return dateString;
      }
    }
  }
}
</script>

<style scoped>
.training-appointment {
  padding: 15px;
  max-width: 1400px;
  margin: 0 auto;
}

h2 {
  color: #333;
  font-size: 24px;
  margin-bottom: 15px;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 8px;
}

h3 {
  color: #2c3e50;
  font-size: 18px;
  margin-bottom: 12px;
}

.training-content {
  margin-top: 15px;
}

.reservation-form {
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 15px;
    margin-bottom: 15px;
  }
  
  /* 预约列表样式 */
  .reservation-list {
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
  }
  
  .list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
  
  .refresh-list-btn {
    padding: 8px 16px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .refresh-list-btn:hover:not(:disabled) {
    background-color: #2980b9;
  }
  
  .refresh-list-btn:disabled {
    background-color: #95a5a6;
    cursor: not-allowed;
  }
  
  /* 加载状态 */
  .loading-state, .empty-state {
  padding: 30px;
  text-align: center;
  color: #7f8c8d;
}
  
  /* 错误状态 */
  .list-error {
    padding: 20px;
    text-align: center;
    background-color: #f8d7da;
    color: #721c24;
    border-radius: 4px;
  }
  
  .retry-btn {
    margin-top: 10px;
    padding: 6px 12px;
    background-color: #721c24;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .retry-btn:hover {
    background-color: #5a171d;
  }
  
  /* 预约表格样式 */
  .reservations-container {
    overflow-x: auto;
  }
  
  .reservations-table {
    width: 100%;
    border-collapse: collapse;
  }
  
  .reservations-table th, 
  .reservations-table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #e0e0e0;
  }
  
  .reservations-table th {
    background-color: #f8f9fa;
    font-weight: 600;
    color: #2c3e50;
  }
  
  .reservation-item:hover {
    background-color: #f8f9fa;
  }
  
  /* 状态标签样式 */
  .status-badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 14px;
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
  
  .status-completed {
    background-color: #cce7ff;
    color: #004085;
  }
  
  .status-rejected {
    background-color: #f8d7da;
    color: #721c24;
  }
  
  /* 响应式设计 - 预约列表 */
  @media (max-width: 768px) {
    .reservation-list {
      padding: 15px;
    }
    
    .list-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;
    }
    
    .reservations-table {
      font-size: 14px;
    }
    
    .reservations-table th, 
    .reservations-table td {
      padding: 8px;
    }
  }
  
  @media (max-width: 600px) {
    .reservations-table {
      font-size: 12px;
    }
    
    .training-appointment {
      padding: 10px;
    }
  }

/* 消息提示样式 */
.success-message,
.error-message {
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.close-btn {
  background: none;
  border: none;
  color: inherit;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  margin-left: 10px;
}

.close-btn:hover {
  opacity: 0.7;
}

/* 表单样式 */
.form-container {
  display: flex;
  flex-direction: column;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.form-column {
  flex: 1;
  min-width: 0; /* 防止内容溢出 */
}

.form-group {
  margin-bottom: 12px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
  font-size: 15px;
}

.required {
  color: #e74c3c;
}

.form-control {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 15px;
  transition: border-color 0.3s;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

/* 教师选择包装器 */
.teacher-select-wrapper {
  display: flex;
  gap: 10px;
}

.teacher-select-wrapper select {
  flex: 1;
}

.refresh-btn {
  padding: 10px 16px;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.refresh-btn:hover {
  background-color: #e9ecef;
}

/* 错误提示 */
.error-hint {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 5px;
}

/* 字符计数 */
.char-count {
  text-align: right;
  font-size: 12px;
  color: #888;
  margin-top: 5px;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.submit-btn,
.reset-btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.submit-btn {
  background-color: #27ae60;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background-color: #229954;
}

.submit-btn:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.reset-btn {
  background-color: #f8f9fa;
  color: #333;
  border: 1px solid #ddd;
}

.reset-btn:hover {
  background-color: #e9ecef;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .reservation-form {
      padding: 15px;
    }
    
    .form-actions {
      flex-direction: column;
    }
    
    .submit-btn,
    .reset-btn {
      width: 100%;
    }
    
    .teacher-select-wrapper {
      flex-direction: column;
    }
    
    .refresh-btn {
      width: 100%;
    }
  }
</style>
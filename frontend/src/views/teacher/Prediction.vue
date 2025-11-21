<template>
  <div class="prediction-container">
    <div class="page-header">
      <h2>留学成功率预测</h2>
      <p>根据学生信息预测留学申请成功率</p>
    </div>

    <div class="prediction-content">
      <!-- 预测表单 -->
      <div class="prediction-form compact-form">
        <!-- 合并所有字段为紧凑布局 -->
        <div class="form-content">
          <!-- 第一行：姓名和专业 -->
          <div class="form-row">
            <div class="form-group">
              <label>学生姓名</label>
              <input type="text" v-model="predictionForm.studentName" placeholder="请输入学生姓名" required>
            </div>
            <div class="form-group">
              <label>专业</label>
              <select v-model="predictionForm.major" required>
                <option value="">请选择专业</option>
                <option value="计算机科学">计算机科学</option>
                <option value="电子工程">电子工程</option>
                <option value="金融">金融</option>
                <option value="机械工程">机械工程</option>
              </select>
            </div>
          </div>
          
          <!-- 第二行：GPA和年级 -->
          <div class="form-row">
            <div class="form-group">
              <label>GPA成绩 (0-4.0)</label>
              <input type="number" v-model.number="predictionForm.gpa" min="0" max="4" step="0.1" placeholder="0.0" required>
            </div>
            <div class="form-group">
              <label>年级</label>
              <select v-model="predictionForm.grade" required>
                <option value="">请选择年级</option>
                <option value="3">大三</option>
                <option value="4">大四</option>
              </select>
            </div>
          </div>
          
          <!-- 第三行：语言成绩 -->
          <div class="form-row">
            <div class="form-group">
              <label>托福成绩 (60-120)</label>
              <input type="number" v-model.number="predictionForm.toefl" min="60" max="120" step="1" placeholder="例如：90" required>
              <small class="help-text">竞争力分数：85-100 (一般), 100-110 (良好), 110+ (优秀)</small>
            </div>
            <div class="form-group">
              <label>GRE成绩 (290-340)</label>
              <input type="number" v-model.number="predictionForm.gre" min="290" max="340" step="1" placeholder="例如：320" required>
              <small class="help-text">竞争力分数：310-320 (一般), 320-330 (良好), 330+ (优秀)</small>
            </div>
          </div>
          
          <!-- 第四行：目标学校 -->
          <div class="form-row">
            <div class="form-group full-width">
              <label>目标学校</label>
              <select v-model="predictionForm.targetSchool" required>
                <option value="">请选择目标学校</option>
                <option value="哈佛大学">哈佛大学</option>
                <option value="斯坦福大学">斯坦福大学</option>
                <option value="麻省理工学院">麻省理工学院</option>
                <option value="加州大学伯克利分校">加州大学伯克利分校</option>
                <option value="普林斯顿大学">普林斯顿大学</option>
              </select>
            </div>
          </div>
        </div>

        <button class="predict-button" @click="runPrediction" :disabled="loading">
          {{ loading ? '预测中...' : '开始预测' }}
        </button>
      </div>

      <!-- 预测结果 -->
      <div class="prediction-result">
        <h3>预测结果</h3>
        
        <!-- 初始状态 - 未预测时显示 -->
        <div v-if="!showResult && !loading" class="initial-result-state">
          <div class="initial-icon">📊</div>
          <h4>等待预测</h4>
          <p>请在左侧填写学生信息并点击"开始预测"按钮</p>
          <div class="initial-tips">
            <p>💡 提示：</p>
            <ul>
              <li>填写准确的GPA、托福和GRE成绩以获得更精确的预测</li>
              <li>系统将根据历史数据计算申请成功率</li>
              <li>预测结果仅供参考，实际录取取决于多种因素</li>
            </ul>
          </div>
        </div>
        
        <!-- 预测进行中 -->
        <div v-else-if="loading" class="loading-result">
          <div class="spinner"></div>
          <p>正在分析数据，计算录取概率...</p>
        </div>
        
        <!-- 预测结果显示 -->
        <div v-else class="result-card">
          <div class="success-rate">
            <div class="rate-value">{{ predictionResult.successRate }}%</div>
            <div class="rate-label">申请成功率</div>
          </div>
          <div class="result-details">
            <p>学生：{{ predictionForm.studentName }}</p>
            <p>目标学校：{{ predictionForm.targetSchool }}</p>
            <p>专业：{{ predictionForm.major }}</p>
            <p>符合条件学生数：{{ predictionResult.qualifiedStudents }}</p>
            <p>总学生数：{{ predictionResult.totalStudents }}</p>
            <p class="recommendation">{{ predictionResult.recommendation }}</p>
          </div>
        </div>
        
        <!-- 重新预测按钮 - 仅在有结果时显示 -->
        <button v-if="showResult" class="new-prediction-button" @click="resetPrediction">重新预测</button>
      </div>

      <!-- 历史预测记录 -->
      <div class="prediction-history">
        <h3>历史预测记录</h3>
        <div v-if="historyList.length === 0" class="empty-history">暂无历史记录</div>
        <div v-else class="history-list">
          <div v-for="item in historyList" :key="item.id" class="history-item">
            <div class="history-info">
              <div class="history-main">{{ item.studentName }} - {{ item.targetSchool }}</div>
              <div class="history-sub">{{ item.date }} | 符合条件: {{ item.qualifiedStudents }} / {{ item.totalStudents }}</div>
            </div>
            <span class="history-rate">{{ item.successRate }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Prediction',
  data() {
    return {
      loading: false,
      showResult: false,
      predictionForm: {
        studentName: '',
        major: '',
        gpa: '',
        grade: '',
        toefl: '',
        gre: '',
        targetSchool: ''
      },
      predictionResult: {
        successRate: 0,
        recommendation: '',
        qualifiedStudents: 0,
        totalStudents: 0
      },
      historyList: []
    }
  },
  mounted() {
    this.loadHistory()
  },
  methods: {
    // 获取认证令牌
    getAuthToken() {
      // 尝试从localStorage获取token
      const token = localStorage.getItem('access_token') || localStorage.getItem('token')
      console.log('获取到的token:', token ? '存在' : '不存在')
      return token
    },
    
    // 运行预测
    async runPrediction() {
      // 简单的表单验证
      if (!this.validateForm()) {
        alert('请填写完整的预测信息')
        return
      }

      this.loading = true
      try {
        // 构建查询参数
        const queryParams = new URLSearchParams()
        if (this.predictionForm.toefl) queryParams.append('toefl_min', this.predictionForm.toefl)
        if (this.predictionForm.gre) queryParams.append('gre_min', this.predictionForm.gre)
        if (this.predictionForm.gpa) queryParams.append('gpa_min', this.predictionForm.gpa)
        
        // 获取认证令牌
        const token = this.getAuthToken()
        if (!token) {
          alert('未认证，请重新登录')
          return
        }
        
        // 调用真实API
        const response = await fetch(`http://localhost:8000/teacher/statistics/predict?${queryParams}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        
        // 处理错误状态码
        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('未认证，请重新登录')
          } else if (response.status === 403) {
            throw new Error('无权限访问此资源')
          } else {
            throw new Error(`获取预测信息失败: ${response.statusText}`)
          }
        }
        
        // 解析响应数据
        const data = await response.json()
        
        // 更新预测结果
        this.predictionResult.successRate = data.success_rate || 0
        this.predictionResult.qualifiedStudents = data.qualified_students || 0
        this.predictionResult.totalStudents = data.total_students || 0
        
        // 根据成功率生成建议
        this.generateRecommendation()
        
        // 保存到历史记录
        this.saveToHistory()
        
        this.showResult = true
      } catch (error) {
        console.error('预测失败:', error)
        alert(error.message || '预测失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    // 表单验证
    validateForm() {
      const form = this.predictionForm
      return form.studentName && form.major && form.gpa && form.grade && 
             form.toefl && form.gre && form.targetSchool
    },
    
    // 根据成功率生成建议
    generateRecommendation() {
      const successRate = this.predictionResult.successRate
      
      if (successRate >= 80) {
        this.predictionResult.recommendation = '申请成功率很高，建议积极准备申请材料'
      } else if (successRate >= 60) {
        this.predictionResult.recommendation = '申请成功率良好，可以尝试申请，同时准备几所保底学校'
      } else if (successRate >= 40) {
        this.predictionResult.recommendation = '申请成功率中等，建议提升语言成绩或考虑其他学校'
      } else {
        this.predictionResult.recommendation = '申请成功率较低，建议调整申请目标或提升自身条件'
      }
    },
    
    // 重置预测
    resetPrediction() {
      this.showResult = false
      this.predictionForm = {
        studentName: '',
        major: '',
        gpa: '',
        grade: '',
        toefl: '',
        gre: '',
        targetSchool: ''
      }
    },
    
    // 保存到历史记录
    saveToHistory() {
      const historyItem = {
        id: Date.now(),
        studentName: this.predictionForm.studentName,
        targetSchool: this.predictionForm.targetSchool,
        successRate: this.predictionResult.successRate,
        qualifiedStudents: this.predictionResult.qualifiedStudents,
        totalStudents: this.predictionResult.totalStudents,
        date: new Date().toLocaleDateString()
      }
      
      this.historyList.unshift(historyItem)
      // 只保留最近10条记录
      if (this.historyList.length > 10) {
        this.historyList = this.historyList.slice(0, 10)
      }
      
      // 保存到localStorage
      this.saveHistoryToStorage()
    },
    
    // 加载历史记录
    loadHistory() {
      const savedHistory = localStorage.getItem('predictionHistory')
      if (savedHistory) {
        try {
          this.historyList = JSON.parse(savedHistory)
        } catch (e) {
          console.error('加载历史记录失败:', e)
          this.historyList = []
        }
      }
    },
    
    // 保存历史记录到localStorage
    saveHistoryToStorage() {
      localStorage.setItem('predictionHistory', JSON.stringify(this.historyList))
    }
  }
}
</script>

<style scoped>
  .prediction-container {
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

  .prediction-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
  }

  .prediction-form {
    background-color: white;
    padding: 25px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  /* 紧凑表单样式 */
  .compact-form {
    padding: 15px;
  }
  
  .form-content {
    margin-bottom: 15px;
  }
  
  .form-row {
    display: flex;
    gap: 15px;
    margin-bottom: 12px;
    align-items: flex-end;
    flex-wrap: wrap;
  }
  
  .form-group {
    flex: 1;
    margin-bottom: 0;
    min-width: 200px;
    display: flex;
    flex-direction: column;
  }
  
  .form-group.full-width {
    flex: 1 1 100%;
    min-width: 100%;
  }
  
  .form-group label {
    margin-bottom: 4px;
    color: #666;
    font-weight: 500;
    font-size: 14px;
  }
  
  .form-group input,
  .form-group select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  
  .form-group input:focus,
  .form-group select:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
  }
  
  /* 帮助文本样式 */
  .help-text {
    display: block;
    margin-top: 3px;
    font-size: 12px;
    color: #888;
    line-height: 1.2;
  }

.predict-button {
  width: 100%;
  padding: 12px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 5px;
}

.predict-button:hover:not(:disabled) {
  background-color: #2980b9;
}

.predict-button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.prediction-result {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.prediction-result h3 {
    color: #2c3e50;
    margin-bottom: 20px;
    text-align: center;
  }
  
  /* 初始状态样式 */
  .initial-result-state {
    text-align: center;
    padding: 30px 20px;
    background-color: #f8f9fa;
    border-radius: 8px;
    border: 2px dashed #dee2e6;
    color: #6c757d;
  }
  
  .initial-icon {
    font-size: 3rem;
    margin-bottom: 15px;
    opacity: 0.7;
  }
  
  .initial-result-state h4 {
    color: #2c3e50;
    margin-bottom: 10px;
    font-size: 1.2rem;
  }
  
  .initial-result-state p {
    margin-bottom: 20px;
    line-height: 1.2;
  }
  
  .initial-tips {
    text-align: left;
    background-color: #e9ecef;
    padding: 15px;
    border-radius: 6px;
    margin-top: 15px;
  }
  
  .initial-tips p {
    margin-bottom: 10px;
    font-weight: 500;
    color: #495057;
  }
  
  .initial-tips ul {
    padding-left: 20px;
    margin: 0;
  }
  
  .initial-tips li {
    margin-bottom: 6px;
    font-size: 14px;
    line-height: 1.2;
  }
  
  /* 加载状态样式 */
  .loading-result {
    text-align: center;
    padding: 40px 20px;
    background-color: #f8f9fa;
    border-radius: 8px;
    color: #495057;
  }
  
  .loading-result .spinner {
    margin: 0 auto 15px;
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
  }
  
  .loading-result p {
    margin: 0;
    font-size: 16px;
    font-weight: 500;
  }

  .result-card {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.success-rate {
  margin-bottom: 20px;
}

.rate-value {
  font-size: 3rem;
  font-weight: bold;
  color: #27ae60;
}

.rate-label {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.result-details {
  text-align: left;
  margin-top: 20px;
}

.result-details p {
  margin: 8px 0;
  color: #34495e;
}

.recommendation {
  font-style: italic;
  color: #2980b9;
  margin-top: 15px !important;
  padding: 10px;
  background-color: #ebf5fb;
  border-radius: 4px;
}

.new-prediction-button {
  padding: 10px 20px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.new-prediction-button:hover {
  background-color: #c0392b;
}

.prediction-history {
  grid-column: 1 / -1;
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.prediction-history h3 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 1.2rem;
}

.empty-history {
  text-align: center;
  color: #7f8c8d;
  padding: 20px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background-color: #f8f9fa;
    border-radius: 4px;
    color: #34495e;
  }
  
  .history-info {
    flex: 1;
  }
  
  .history-main {
    font-weight: 500;
    margin-bottom: 4px;
  }
  
  .history-sub {
    font-size: 12px;
    color: #7f8c8d;
  }

.history-rate {
  font-weight: bold;
  color: #27ae60;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .prediction-content {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .form-group {
    min-width: 100%;
  }
}
</style>
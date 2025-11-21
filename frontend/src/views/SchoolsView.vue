<template>
  <div class="schools-container">
    <header class="schools-header">
      <h1>学校库</h1>
      <p>全球顶尖留学院校信息平台</p>
    </header>

    <div class="filter-section">
      <div class="search-group">
        <input 
          type="text" 
          placeholder="搜索学校名称..." 
          v-model="searchKeyword"
          @input="handleSearch"
        />
        <button class="search-btn">搜索</button>
      </div>
    </div>

    <div class="schools-content">
      <div v-if="loading" class="loading">
        <p>加载中...</p>
      </div>

      <div v-else-if="filteredSchools.length === 0" class="no-results">
        <p>没有找到符合条件的学校</p>
      </div>

      <div v-else class="schools-grid">
        <div 
          v-for="school in paginatedSchools" 
          :key="school.id" 
          class="school-card"
          @click="viewSchoolDetail(school.id)"
        >
          <div class="school-ranking">排名 #{{ school.ranking || 'N/A' }}</div>
          <h3 class="school-name">{{ school.chinese_name }}</h3>
          <p class="school-english-name">{{ school.english_name }}</p>
          <div class="school-info">
            <span class="school-location">{{ school.location }}</span>
          </div>
          <div class="school-preview">
            {{ school.introduction ? school.introduction.substring(0, 100) + '...' : '暂无介绍' }}
          </div>
        </div>
      </div>
    </div>

    <div class="pagination" v-if="totalPages > 1">
      <button @click="currentPage = 1" :disabled="currentPage === 1">首页</button>
      <button @click="currentPage--" :disabled="currentPage === 1">上一页</button>
      <span>第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
      <button @click="currentPage++" :disabled="currentPage === totalPages">下一页</button>
      <button @click="currentPage = totalPages" :disabled="currentPage === totalPages">末页</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'SchoolsView',
  data() {
    return {
      schools: [],
      filteredSchools: [],

      searchKeyword: '',
      loading: false,
      currentPage: 1,
      pageSize: 12,
      totalPages: 1
    };
  },
  computed: {
    paginatedSchools() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.filteredSchools.slice(start, end);
    }
  },
  watch: {
    filteredSchools() {
      this.totalPages = Math.ceil(this.filteredSchools.length / this.pageSize);
      this.currentPage = 1;
    }
  },
  mounted() {
    this.fetchSchools();
  },
  methods: {
    async fetchSchools() {
      this.loading = true;
      try {
        const response = await axios.get('http://localhost:8000/api/schools');
        this.schools = response.data;
        this.filteredSchools = [...this.schools];
      } catch (error) {
        console.error('获取学校列表失败:', error);
        alert('获取学校信息失败，请稍后重试');
      } finally {
        this.loading = false;
      }
    },
    filterSchools() {
      let filtered = [...this.schools];

      // 关键词搜索
      if (this.searchKeyword) {
        const keyword = this.searchKeyword.toLowerCase();
        filtered = filtered.filter(school => 
          school.chinese_name.toLowerCase().includes(keyword) ||
          school.english_name.toLowerCase().includes(keyword)
        );
      }

      this.filteredSchools = filtered;
    },
    handleSearch() {
      this.filterSchools();
    },
    viewSchoolDetail(schoolId) {
      // 这里可以跳转到学校详情页，暂时先用alert模拟
      alert(`查看学校ID: ${schoolId} 的详细信息`);
    }
  }
};
</script>

<style scoped>
.schools-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.schools-header {
  text-align: center;
  margin-bottom: 40px;
}

.schools-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.schools-header p {
  font-size: 1.1rem;
  color: #7f8c8d;
}

.filter-section {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group label {
  font-weight: 500;
  color: #34495e;
  white-space: nowrap;
}

.filter-group select,
.search-group input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-group {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
}

.search-group input {
  width: 250px;
}

.search-btn {
  padding: 8px 20px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-btn:hover {
  background-color: #2980b9;
}

.loading,
.no-results {
  text-align: center;
  padding: 60px;
  color: #7f8c8d;
  font-size: 1.1rem;
}

.schools-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 25px;
  margin-bottom: 30px;
}

.school-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
  position: relative;
  padding: 20px;
}

.school-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}

.school-ranking {
  position: absolute;
  top: 15px;
  right: 15px;
  background-color: #e74c3c;
  color: white;
  font-size: 0.85rem;
  font-weight: bold;
  padding: 5px 10px;
  border-radius: 15px;
}

.school-name {
  font-size: 1.3rem;
  color: #2c3e50;
  margin: 0 0 8px 0;
  line-height: 1.3;
}

.school-english-name {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin: 0 0 15px 0;
  line-height: 1.4;
}

.school-info {
  margin-bottom: 15px;
}

.school-location {
  background-color: #ecf0f1;
  color: #34495e;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
}

.school-preview {
  color: #555;
  font-size: 0.9rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
}

.pagination button {
  padding: 8px 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.pagination button:hover:not(:disabled) {
  background-color: #2980b9;
}

.pagination button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.pagination span {
  color: #34495e;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }

  .search-group {
    margin-left: 0;
  }

  .search-group input {
    width: 100%;
  }

  .schools-grid {
    grid-template-columns: 1fr;
  }

  .pagination {
    flex-wrap: wrap;
  }
}
</style>
// src/views/WasteView.vue
<template>
  <div class="waste-management">
    <h2>Waste Management</h2>

    <!-- Add New Waste Log Form -->
    <div class="log-form-card">
      <h3>Add New Waste Log</h3>
      <form @submit.prevent="submitLog" class="waste-form">
        <div class="form-row">
          <div class="form-group">
            <label>Category</label>
            <select v-model="newLog.category" required>
              <option value="">Select Category</option>
              <option v-for="category in categories" 
                      :key="category" 
                      :value="category">
                {{ category }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Amount</label>
            <input 
              type="number" 
              v-model="newLog.amount" 
              step="0.01" 
              min="0.01" 
              required
            >
          </div>

          <div class="form-group">
            <label>Unit</label>
            <select v-model="newLog.unit" required>
              <option value="">Select Unit</option>
              <option v-for="unit in units" 
                      :key="unit" 
                      :value="unit">
                {{ unit }}
              </option>
            </select>
          </div>
        </div>

        <button type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Adding...' : 'Add Log' }}
        </button>
      </form>
    </div>

    <!-- Statistics Section -->
    <div class="stats-section">
      <div class="stats-card">
        <h3>Waste Statistics (Last 30 Days)</h3>
        <div v-if="stats" class="stats-grid">
          <div v-for="(amount, category) in stats.category_totals" 
               :key="category" 
               class="stat-item">
            <div class="stat-label">{{ category }}</div>
            <div class="stat-value">{{ amount.toFixed(2) }} kg</div>
          </div>
        </div>
        <div v-else class="no-data">No statistics available</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-group">
        <label>Filter by Category:</label>
        <select v-model="filters.category" @change="fetchLogs">
          <option value="">All Categories</option>
          <option v-for="category in categories" 
                  :key="category" 
                  :value="category">
            {{ category }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>Time Period:</label>
        <select v-model="filters.days" @change="fetchLogs">
          <option :value="7">Last 7 Days</option>
          <option :value="30">Last 30 Days</option>
          <option :value="90">Last 90 Days</option>
        </select>
      </div>
    </div>

    <!-- Waste Logs Table -->
    <div class="logs-section">
      <h3>Waste Logs</h3>
      <div v-if="loading" class="loading">Loading logs...</div>
      <div v-else-if="wasteLogs.length === 0" class="no-data">
        No waste logs found for the selected filters
      </div>
      <table v-else class="logs-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Category</th>
            <th>Amount</th>
            <th>Unit</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in wasteLogs" :key="log.id">
            <td>{{ formatDate(log.date) }}</td>
            <td>{{ log.category }}</td>
            <td>{{ log.amount }}</td>
            <td>{{ log.unit }}</td>
            <td>
              <button 
                @click="deleteLog(log.id)" 
                class="delete-btn"
                :disabled="isDeleting === log.id"
              >
                {{ isDeleting === log.id ? 'Deleting...' : 'Delete' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'WasteView',
  data() {
    return {
      categories: ['plastic', 'paper', 'glass', 'metal', 'organic'],
      units: ['kg', 'g'],
      wasteLogs: [],
      stats: null,
      loading: true,
      isSubmitting: false,
      isDeleting: null,
      newLog: {
        category: '',
        amount: '',
        unit: 'kg'
      },
      filters: {
        category: '',
        days: 30
      }
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      await Promise.all([
        this.fetchLogs(),
        this.fetchStats()
      ])
    },

    async fetchLogs() {
      this.loading = true
      try {
        let url = `http://localhost:5000/api/waste/logs?days=${this.filters.days}`
        if (this.filters.category) {
          url += `&category=${this.filters.category}`
        }
        
        const response = await axios.get(url)
        this.wasteLogs = response.data.logs
      } catch (error) {
        console.error('Error fetching logs:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchStats() {
      try {
        const response = await axios.get(`http://localhost:5000/api/waste/stats?days=${this.filters.days}`)
        this.stats = response.data
      } catch (error) {
        console.error('Error fetching stats:', error)
      }
    },

    async submitLog() {
      this.isSubmitting = true
      try {
        await axios.post('http://localhost:5000/api/waste/log', this.newLog)
        this.newLog = { category: '', amount: '', unit: 'kg' }
        await this.fetchData()
      } catch (error) {
        console.error('Error creating log:', error)
        alert('Failed to add waste log: ' + (error.response?.data?.error || 'Unknown error'))
      } finally {
        this.isSubmitting = false
      }
    },

    async deleteLog(id) {
      if (!confirm('Are you sure you want to delete this log?')) return

      this.isDeleting = id
      try {
        await axios.delete(`http://localhost:5000/api/waste/log/${id}`)
        await this.fetchData()
      } catch (error) {
        console.error('Error deleting log:', error)
        alert('Failed to delete log: ' + (error.response?.data?.error || 'Unknown error'))
      } finally {
        this.isDeleting = null
      }
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.waste-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.log-form-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.waste-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-group {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input, select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.stats-section {
  margin-bottom: 30px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.stat-item {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  text-align: center;
}

.stat-label {
  text-transform: capitalize;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 1.2em;
  font-weight: bold;
  color: #42b983;
}

.filters-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

.logs-table th,
.logs-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.logs-table th {
  background: #f8f9fa;
  font-weight: bold;
}

button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background-color: #42b983;
  color: white;
  font-weight: bold;
}

button:hover:not(:disabled) {
  opacity: 0.9;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.delete-btn {
  background-color: #ff4444;
  padding: 4px 8px;
  font-size: 0.9em;
}

.loading, .no-data {
  text-align: center;
  padding: 20px;
  color: #666;
}

.stats-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
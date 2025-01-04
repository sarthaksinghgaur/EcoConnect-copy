// src/views/DashboardView.vue
<template>
  <div class="dashboard">
    <!-- Navigation -->
    <nav class="top-nav">
      <div class="nav-links">
        <router-link to="/waste">Waste Management</router-link>
        <router-link to="/businesses">Sustainable Businesses</router-link>
        <router-link to="/initiatives">Initiatives</router-link>
        <router-link to="/leaderboard">Leaderboard</router-link>
        <router-link to="/profile">Profile</router-link>
      </div>
      <button @click="logout" class="logout-btn">Logout</button>
    </nav>

    <!-- Main Dashboard Content -->
    <div class="dashboard-content">
      <div class="welcome-section">
        <h2>Welcome, {{ user?.username }}!</h2>
        <p class="subtitle">Here's your impact summary</p>
      </div>

      <!-- Stats Grid -->
      <div class="stats-grid">
        <!-- Waste Tracking Stats -->
        <div class="stat-card">
          <h3>Waste Tracking</h3>
          <div v-if="wasteStats">
            <div v-for="(amount, category) in wasteStats.category_totals" 
                 :key="category" 
                 class="waste-stat">
              <span class="category">{{ category }}:</span>
              <span class="amount">{{ amount.toFixed(2) }} kg</span>
            </div>
          </div>
          <div v-else class="placeholder-text">
            Start tracking your waste to see statistics
          </div>
          <router-link to="/waste" class="card-link">Track Waste →</router-link>
        </div>

        <!-- Leaderboard Position -->
        <div class="stat-card">
          <h3>Your Ranking</h3>
          <div v-if="leaderboardStats">
            <p class="ranking">
              #{{ leaderboardStats.rank }} this week
            </p>
            <p class="ranking-details">
              Total Contributions: {{ leaderboardStats.total_logs || 0 }}
            </p>
          </div>
          <div v-else class="placeholder-text">
            #- on the leaderboard
          </div>
          <router-link to="/leaderboard" class="card-link">View Leaderboard →</router-link>
        </div>

        <!-- Recent Activity -->
        <div class="stat-card">
          <h3>Recent Activity</h3>
          <div v-if="activities.length > 0" class="activities-list">
            <div v-for="activity in activities.slice(0, 3)" 
                 :key="activity.id" 
                 class="activity-item">
              <span class="activity-content">{{ activity.content }}</span>
              <span class="activity-date">{{ formatDate(activity.created_at) }}</span>
            </div>
          </div>
          <div v-else class="placeholder-text">
            No recent activities
          </div>
          <router-link to="/feed" class="card-link">View All Activities →</router-link>
        </div>

        <!-- Joined Initiatives -->
        <div class="stat-card">
          <h3>Your Initiatives</h3>
          <div v-if="initiatives.length > 0" class="initiatives-list">
            <div v-for="initiative in initiatives.slice(0, 2)" 
                 :key="initiative.id" 
                 class="initiative-item">
              <h4>{{ initiative.title }}</h4>
              <p>{{ formatDate(initiative.event_date) }}</p>
            </div>
          </div>
          <div v-else class="placeholder-text">
            No initiatives joined yet
          </div>
          <router-link to="/initiatives" class="card-link">Browse Initiatives →</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'DashboardView',
  data() {
    return {
      user: null,
      wasteStats: null,
      leaderboardStats: null,
      activities: [],
      initiatives: []
    }
  },
  async created() {
    this.user = JSON.parse(localStorage.getItem('user'))
    await this.fetchDashboardData()
  },
  methods: {
    async fetchDashboardData() {
      try {
        const [wasteResponse, leaderboardResponse, activitiesResponse, initiativesResponse] = 
          await Promise.all([
            axios.get('http://localhost:5000/api/waste/stats'),
            axios.get('http://localhost:5000/api/social/leaderboard?timeframe=week'),
            axios.get('http://localhost:5000/api/social/feed'),
            axios.get('http://localhost:5000/api/initiatives')
          ])

        this.wasteStats = wasteResponse.data
        
        // Find user's position in leaderboard
        const userRank = leaderboardResponse.data.leaders.findIndex(
          leader => leader.username === this.user.username
        )
        this.leaderboardStats = {
          rank: userRank !== -1 ? userRank + 1 : null,
          ...leaderboardResponse.data.leaders[userRank]
        }

        this.activities = activitiesResponse.data.activities
        this.initiatives = initiativesResponse.data.initiatives?.filter(
          i => i.participants?.includes(this.user.id)
        ) || []

      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      }
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  margin-bottom: 30px;
  border-bottom: 1px solid #eee;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-links a {
  text-decoration: none;
  color: #333;
  padding: 5px 10px;
  border-radius: 4px;
}

.nav-links a:hover {
  background-color: #f5f5f5;
}

.nav-links a.router-link-active {
  color: #42b983;
  font-weight: bold;
}

.logout-btn {
  padding: 5px 15px;
  background-color: #ff4444;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.welcome-section {
  text-align: center;
  margin-bottom: 30px;
}

.subtitle {
  color: #666;
  margin-top: 5px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-card h3 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.waste-stat {
  display: flex;
  justify-content: space-between;
  margin: 5px 0;
}

.category {
  text-transform: capitalize;
}

.activities-list, .initiatives-list {
  margin: 10px 0;
}

.activity-item, .initiative-item {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.activity-date {
  font-size: 0.8em;
  color: #666;
}

.placeholder-text {
  color: #999;
  font-style: italic;
  margin: 10px 0;
}

.card-link {
  display: block;
  margin-top: 15px;
  color: #42b983;
  text-decoration: none;
}

.card-link:hover {
  text-decoration: underline;
}

.ranking {
  font-size: 1.5em;
  font-weight: bold;
  color: #42b983;
}

.ranking-details {
  color: #666;
  font-size: 0.9em;
  margin-top: 5px;
}
</style>
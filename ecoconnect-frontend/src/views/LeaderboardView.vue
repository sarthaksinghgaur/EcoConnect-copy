// src/views/LeaderboardView.vue
<template>
  <div class="leaderboard-page">
    <h2>Community Impact</h2>

    <!-- Time Period Selector -->
    <div class="time-selector">
      <button 
        v-for="period in timePeriods" 
        :key="period.value"
        @click="selectedPeriod = period.value"
        :class="{ active: selectedPeriod === period.value }"
      >
        {{ period.label }}
      </button>
    </div>

    <!-- Leaderboard Section -->
    <div class="leaderboard-section">
      <h3>Top Contributors</h3>
      
      <div v-if="loading" class="loading">
        Loading leaderboard...
      </div>
      
      <div v-else-if="leaderboard.length === 0" class="no-data">
        No data available for this time period
      </div>
      
      <div v-else class="leaderboard">
        <div v-for="(user, index) in leaderboard" 
             :key="user.username"
             class="leaderboard-item"
             :class="{ 
               'top-1': index === 0,
               'top-2': index === 1,
               'top-3': index === 2
             }"
        >
          <div class="rank">{{ index + 1 }}</div>
          <div class="user-info">
            <div class="username">{{ user.username }}</div>
            <div class="stats">
              <span>{{ user.total_logs }} contributions</span>
              <span>{{ user.total_amount?.toFixed(2) || 0 }} kg tracked</span>
            </div>
          </div>
          <div class="position-indicator">
            {{ isCurrentUser(user) ? '(You)' : '' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Your Achievements Section -->
    <div class="achievements-section">
      <h3>Your Achievements</h3>
      
      <div v-if="loadingAchievements" class="loading">
        Loading achievements...
      </div>
      
      <div v-else-if="achievements.length === 0" class="no-data">
        No achievements yet. Start contributing to earn badges!
      </div>
      
      <div v-else class="achievements-grid">
        <div v-for="achievement in achievements" 
             :key="achievement.id"
             class="achievement-card"
        >
          <div class="achievement-icon">🏆</div>
          <div class="achievement-details">
            <h4>{{ achievement.title }}</h4>
            <p>{{ achievement.description }}</p>
            <span class="achievement-date">
              Earned on {{ formatDate(achievement.created_at) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Activity Feed -->
    <div class="activity-feed">
      <h3>Recent Activities</h3>
      
      <div v-if="loadingFeed" class="loading">
        Loading activities...
      </div>
      
      <div v-else-if="feed.length === 0" class="no-data">
        No recent activities
      </div>
      
      <div v-else class="feed-list">
        <div v-for="activity in feed" 
             :key="activity.id"
             class="activity-item"
        >
          <div class="activity-content">
            {{ activity.content }}
          </div>
          <div class="activity-meta">
            {{ formatDate(activity.created_at) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'LeaderboardView',
  data() {
    return {
      selectedPeriod: 'week',
      timePeriods: [
        { label: 'This Week', value: 'week' },
        { label: 'This Month', value: 'month' },
        { label: 'All Time', value: 'all-time' }
      ],
      currentUser: JSON.parse(localStorage.getItem('user')),
      leaderboard: [],
      achievements: [],
      feed: [],
      loading: false,
      loadingAchievements: false,
      loadingFeed: false
    }
  },
  watch: {
    selectedPeriod() {
      this.fetchLeaderboard()
    }
  },
  created() {
    this.fetchAllData()
  },
  methods: {
    async fetchAllData() {
      Promise.all([
        this.fetchLeaderboard(),
        this.fetchAchievements(),
        this.fetchActivityFeed()
      ])
    },

    async fetchLeaderboard() {
      this.loading = true
      try {
        const response = await axios.get(
          `http://localhost:5000/api/social/leaderboard?timeframe=${this.selectedPeriod}`
        )
        this.leaderboard = response.data.leaders
      } catch (error) {
        console.error('Error fetching leaderboard:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchAchievements() {
      this.loadingAchievements = true
      try {
        const response = await axios.get('http://localhost:5000/api/social/achievements')
        this.achievements = response.data.achievements
      } catch (error) {
        console.error('Error fetching achievements:', error)
      } finally {
        this.loadingAchievements = false
      }
    },

    async fetchActivityFeed() {
      this.loadingFeed = true
      try {
        const response = await axios.get('http://localhost:5000/api/social/feed')
        this.feed = response.data.activities
      } catch (error) {
        console.error('Error fetching activity feed:', error)
      } finally {
        this.loadingFeed = false
      }
    },

    isCurrentUser(user) {
      return user.username === this.currentUser.username
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
  }
}
</script>

<style scoped>
.leaderboard-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.time-selector {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.time-selector button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: #f5f5f5;
  color: #666;
}

.time-selector button.active {
  background: #42b983;
  color: white;
}

.leaderboard-section, .achievements-section, .activity-feed {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.leaderboard-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
  gap: 15px;
}

.leaderboard-item:last-child {
  border-bottom: none;
}

.top-1 {
  background: #fff5e6;
}

.top-2 {
  background: #f8f9fa;
}

.top-3 {
  background: #fff8f8;
}

.rank {
  font-size: 1.5em;
  font-weight: bold;
  width: 40px;
  text-align: center;
}

.top-1 .rank {
  color: #ffa500;
}

.top-2 .rank {
  color: #808080;
}

.top-3 .rank {
  color: #cd7f32;
}

.user-info {
  flex-grow: 1;
}

.username {
  font-weight: bold;
}

.stats {
  color: #666;
  font-size: 0.9em;
  display: flex;
  gap: 15px;
}

.position-indicator {
  color: #42b983;
  font-weight: bold;
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.achievement-card {
  display: flex;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.achievement-icon {
  font-size: 2em;
}

.achievement-details h4 {
  margin: 0 0 5px 0;
}

.achievement-details p {
  margin: 0;
  color: #666;
  font-size: 0.9em;
}

.achievement-date {
  display: block;
  margin-top: 5px;
  color: #999;
  font-size: 0.8em;
}

.feed-list {
  margin-top: 15px;
}

.activity-item {
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-meta {
  color: #999;
  font-size: 0.8em;
  margin-top: 5px;
}

.loading, .no-data {
  text-align: center;
  padding: 20px;
  color: #666;
}
</style>
// src/views/ProfileView.vue
<template>
  <div class="profile">
    <!-- User Info Section -->
    <div class="profile-header">
      <div class="user-info">
        <h2>{{ user?.username }}</h2>
        <p class="email">{{ user?.email }}</p>
        <div class="stats">
          <div class="stat-item">
            <span class="stat-value">{{ followersCount }}</span>
            <span class="stat-label">Followers</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ followingCount }}</span>
            <span class="stat-label">Following</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ totalContributions }}</span>
            <span class="stat-label">Contributions</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="profile-content">
      <!-- Left Column -->
      <div class="profile-left">
        <!-- Achievements Section -->
        <div class="section achievements-section">
          <h3>Your Achievements</h3>
          <div v-if="loadingAchievements" class="loading">
            Loading achievements...
          </div>
          <div v-else-if="achievements.length === 0" class="empty-state">
            No achievements yet. Start contributing to earn badges!
          </div>
          <div v-else class="achievements-list">
            <div v-for="achievement in achievements" 
                 :key="achievement.id" 
                 class="achievement-card">
              <div class="achievement-icon">🏆</div>
              <div class="achievement-info">
                <h4>{{ achievement.title }}</h4>
                <p>{{ achievement.description }}</p>
                <span class="date">{{ formatDate(achievement.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity Section -->
        <div class="section activity-section">
          <h3>Recent Activity</h3>
          <div v-if="loadingActivities" class="loading">
            Loading activities...
          </div>
          <div v-else-if="activities.length === 0" class="empty-state">
            No recent activities
          </div>
          <div v-else class="activity-list">
            <div v-for="activity in activities" 
                 :key="activity.id" 
                 class="activity-item">
              <div class="activity-content">{{ activity.content }}</div>
              <div class="activity-meta">
                <span class="date">{{ formatDate(activity.created_at) }}</span>
                <span class="activity-type">{{ activity.activity_type }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="profile-right">
        <!-- Following & Followers Lists -->
        <div class="section connections-section">
          <div class="tabs">
            <button 
              @click="activeTab = 'followers'"
              :class="{ active: activeTab === 'followers' }"
            >
              Followers
            </button>
            <button 
              @click="activeTab = 'following'"
              :class="{ active: activeTab === 'following' }"
            >
              Following
            </button>
          </div>

          <div v-if="loadingConnections" class="loading">
            Loading...
          </div>
          <div v-else>
            <!-- Followers Tab -->
            <div v-if="activeTab === 'followers'" class="connections-list">
              <div v-if="followers.length === 0" class="empty-state">
                No followers yet
              </div>
              <div v-else v-for="follower in followers" 
                   :key="follower.id" 
                   class="connection-item">
                <span class="username">{{ follower.username }}</span>
                <button v-if="follower.isFollowingYou" 
                        @click="followUser(follower.id)"
                        class="follow-btn">
                  Follow Back
                </button>
              </div>
            </div>

            <!-- Following Tab -->
            <div v-else class="connections-list">
              <div v-if="following.length === 0" class="empty-state">
                Not following anyone yet
              </div>
              <div v-else v-for="followedUser in following" 
                   :key="followedUser.id" 
                   class="connection-item">
                <span class="username">{{ followedUser.username }}</span>
                <button @click="unfollowUser(followedUser.id)" 
                        class="unfollow-btn">
                  Unfollow
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Impact Stats -->
        <div class="section stats-section">
          <h3>Your Impact</h3>
          <div v-if="loadingStats" class="loading">
            Loading stats...
          </div>
          <div v-else>
            <div class="impact-stats">
              <div class="impact-item">
                <h4>Waste Tracked</h4>
                <div class="impact-value">{{ totalWasteTracked }} kg</div>
              </div>
              <div class="impact-item">
                <h4>Initiatives Joined</h4>
                <div class="impact-value">{{ initiativesCount }}</div>
              </div>
              <div class="impact-item">
                <h4>Business Reviews</h4>
                <div class="impact-value">{{ reviewsCount }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ProfileView',
  data() {
    return {
      user: null,
      achievements: [],
      activities: [],
      followers: [],
      following: [],
      activeTab: 'followers',
      stats: null,
      loadingAchievements: false,
      loadingActivities: false,
      loadingConnections: false,
      loadingStats: false,
      followersCount: 0,
      followingCount: 0,
      totalContributions: 0,
      totalWasteTracked: 0,
      initiativesCount: 0,
      reviewsCount: 0
    }
  },
  created() {
    this.user = JSON.parse(localStorage.getItem('user'))
    this.fetchAllData()
  },
  methods: {
    async fetchAllData() {
      Promise.all([
        this.fetchAchievements(),
        this.fetchActivities(),
        this.fetchConnections(),
        this.fetchStats()
      ])
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

    async fetchActivities() {
      this.loadingActivities = true
      try {
        const response = await axios.get('http://localhost:5000/api/social/feed')
        this.activities = response.data.activities
      } catch (error) {
        console.error('Error fetching activities:', error)
      } finally {
        this.loadingActivities = false
      }
    },

    async fetchConnections() {
      this.loadingConnections = true
      try {
        const [followersRes, followingRes] = await Promise.all([
          axios.get(`http://localhost:5000/api/social/followers`),
          axios.get(`http://localhost:5000/api/social/following`)
        ])
        this.followers = followersRes.data.followers
        this.following = followingRes.data.following
        this.followersCount = this.followers.length
        this.followingCount = this.following.length
      } catch (error) {
        console.error('Error fetching connections:', error)
      } finally {
        this.loadingConnections = false
      }
    },

    async fetchStats() {
      this.loadingStats = true
      try {
        const wasteResponse = await axios.get('http://localhost:5000/api/waste/stats')
        this.totalWasteTracked = Object.values(wasteResponse.data.category_totals || {})
          .reduce((sum, val) => sum + val, 0)
        
        // You might need to implement these endpoints
        const initiativesResponse = await axios.get('http://localhost:5000/api/initiatives/joined')
        this.initiativesCount = initiativesResponse.data.initiatives?.length || 0
        
        const reviewsResponse = await axios.get('http://localhost:5000/api/businesses/my-reviews')
        this.reviewsCount = reviewsResponse.data.reviews?.length || 0
        
        this.totalContributions = this.achievements.length
      } catch (error) {
        console.error('Error fetching stats:', error)
      } finally {
        this.loadingStats = false
      }
    },

    async followUser(userId) {
      try {
        await axios.post(`http://localhost:5000/api/social/follow/${userId}`)
        await this.fetchConnections()
      } catch (error) {
        console.error('Error following user:', error)
        alert('Failed to follow user')
      }
    },

    async unfollowUser(userId) {
      try {
        await axios.post(`http://localhost:5000/api/social/unfollow/${userId}`)
        await this.fetchConnections()
      } catch (error) {
        console.error('Error unfollowing user:', error)
        alert('Failed to unfollow user')
      }
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
.profile {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.profile-header {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.user-info {
  text-align: center;
}

.email {
  color: #666;
  margin: 5px 0;
}

.stats {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 20px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.5em;
  font-weight: bold;
  color: #42b983;
}

.stat-label {
  color: #666;
  font-size: 0.9em;
}

.profile-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.achievements-list, .activity-list, .connections-list {
  margin-top: 15px;
}

.achievement-card {
  display: flex;
  gap: 15px;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.achievement-icon {
  font-size: 2em;
}

.achievement-info h4 {
  margin: 0;
}

.activity-item {
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.activity-meta {
  display: flex;
  justify-content: space-between;
  color: #666;
  font-size: 0.8em;
  margin-top: 5px;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.tabs button {
  padding: 8px 16px;
  border: none;
  background: #f5f5f5;
  border-radius: 4px;
  cursor: pointer;
}

.tabs button.active {
  background: #42b983;
  color: white;
}

.connection-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.follow-btn, .unfollow-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
}

.follow-btn {
  background: #42b983;
  color: white;
}

.unfollow-btn {
  background: #ff4444;
  color: white;
}

.impact-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.impact-item {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
}

.impact-item h4 {
  margin: 0;
  color: #666;
  font-size: 0.9em;
}

.impact-value {
  font-size: 1.2em;
  font-weight: bold;
  color: #42b983;
  margin-top: 5px;
}

.loading, .empty-state {
  text-align: center;
  padding: 20px;
  color: #666;
}

.date {
  color: #999;
  font-size: 0.8em;
}
</style>
<template>
  <div class="initiatives">
    <h2>Community Initiatives</h2>

    <!-- Create Initiative Button -->
    <button @click="showCreateForm = !showCreateForm" class="create-btn">
      {{ showCreateForm ? 'Cancel' : '+ Create New Initiative' }}
    </button>

    <!-- Create Initiative Form -->
    <div v-if="showCreateForm" class="create-form">
      <h3>Create New Initiative</h3>
      <form @submit.prevent="createInitiative">
        <div class="form-group">
          <label>Title *</label>
          <input 
            type="text" 
            v-model="newInitiative.title" 
            required
            placeholder="Enter initiative title"
          >
        </div>

        <div class="form-group">
          <label>Description *</label>
          <textarea 
            v-model="newInitiative.description" 
            required
            rows="3"
            placeholder="Describe your initiative"
          ></textarea>
        </div>

        <div class="form-group">
          <label>Location *</label>
          <input 
            type="text" 
            v-model="newInitiative.location" 
            required
            placeholder="Event location"
          >
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Event Date *</label>
            <input 
              type="datetime-local" 
              v-model="newInitiative.event_date" 
              required
            >
          </div>

          <div class="form-group">
            <label>Duration (hours) *</label>
            <input 
              type="number" 
              v-model="newInitiative.duration_hours" 
              required
              min="1"
            >
          </div>
        </div>

        <div class="form-group">
          <label>Maximum Participants</label>
          <input 
            type="number" 
            v-model="newInitiative.max_participants" 
            min="1"
            placeholder="Default: 50"
          >
        </div>

        <div class="form-group">
          <label>Requirements</label>
          <textarea 
            v-model="newInitiative.requirements" 
            rows="2"
            placeholder="What should participants bring?"
          ></textarea>
        </div>

        <div class="form-group">
          <label>Contact Info</label>
          <input 
            type="text" 
            v-model="newInitiative.contact_info" 
            placeholder="How can participants reach you?"
          >
        </div>

        <button type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Creating...' : 'Create Initiative' }}
        </button>
      </form>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <input 
          type="text" 
          v-model="filters.location" 
          placeholder="Filter by location..."
          @input="filterInitiatives"
        >
      </div>
      <div class="filter-group">
        <select v-model="filters.status" @change="filterInitiatives">
          <option value="upcoming">Upcoming</option>
          <option value="all">All Initiatives</option>
          <option value="completed">Completed</option>
        </select>
      </div>
    </div>

    <!-- Initiatives Content -->
    <div v-if="!loading">
      <div class="initiatives-grid">
        <div v-for="initiative in initiatives" 
             :key="initiative.id" 
             class="initiative-card"
             :class="initiative.status"
        >
          <div class="initiative-status">{{ initiative.status }}</div>
          
          <div class="initiative-content">
            <h3>{{ initiative.title }}</h3>
            <p class="description">{{ initiative.description }}</p>
            
            <div class="initiative-details">
              <p>📍 {{ initiative.location }}</p>
              <p>📅 {{ formatDate(initiative.event_date) }}</p>
              <p>⏱️ Duration: {{ initiative.duration_hours }} hours</p>
              
              <div class="participants-info">
                <p>
                  👥 Participants: {{ getParticipantCount(initiative) }}/
                  {{ initiative.max_participants || 50 }}
                </p>
                <button v-if="showParticipants[initiative.id]" 
                        @click="hideParticipants(initiative.id)"
                        class="small-btn">
                  Hide Participants
                </button>
                <button v-else 
                        @click="showParticipantsList(initiative.id)"
                        class="small-btn">
                  Show Participants
                </button>
              </div>

              <!-- Participants List -->
            <div class="participants-section">
              <div v-if="showParticipants[initiative.id]" class="participants-list">
                <template v-if="initiative.participantsList?.length">
                  <div 
                    v-for="participant in initiative.participantsList" 
                    :key="participant.id"
                    class="participant-item"
                  >
                    {{ participant.username }}
                  </div>
                </template>
                <div v-else>No participants yet</div>
              </div>
            </div>
            </div>

            <div v-if="initiative.requirements" class="requirements">
              <strong>Requirements:</strong>
              <p>{{ initiative.requirements }}</p>
            </div>

            <div v-if="initiative.contact_info" class="contact-info">
              <strong>Contact:</strong>
              <p>{{ initiative.contact_info }}</p>
            </div>

            <!-- Action Buttons -->
            <div class="initiative-actions">
              <div v-if="isCreator(initiative)">
                <span class="creator-badge">You created this initiative</span>
                <div v-if="initiative.status === 'upcoming'" class="creator-actions">
                  <button @click="initiative.showEditForm = !initiative.showEditForm">
                    Edit
                  </button>
                  <button @click="updateStatus(initiative.id, 'completed')" 
                          class="complete-btn">
                    Mark as Completed
                  </button>
                </div>
              </div>
              <div v-else-if="initiative.status === 'upcoming'">
                <button 
                  v-if="!hasJoined(initiative)"
                  @click="joinInitiative(initiative.id)"
                  :disabled="isJoining"
                  class="join-btn"
                >
                  Join Initiative
                </button>
                <div v-else class="joined-status">
                  You have joined this initiative
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading and Empty States -->
    <div v-else-if="loading" class="loading">
      Loading initiatives...
    </div>
    <div v-else class="no-initiatives">
      No initiatives found
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'InitiativesView',
  data() {
    return {
      initiatives: [],
      loading: true,
      showCreateForm: false,
      isSubmitting: false,
      isJoining: false,
      currentUser: JSON.parse(localStorage.getItem('user')),
      showParticipants: {},
      filters: {
        location: '',
        status: 'upcoming'
      },
      newInitiative: {
        title: '',
        description: '',
        location: '',
        event_date: '',
        duration_hours: 1,
        max_participants: 50,
        requirements: '',
        contact_info: ''
      }
    }
  },
  async created() {
    await this.fetchInitiatives()
  },
  methods: {
    async fetchInitiatives() {
      this.loading = true
      try {
        let url = 'http://localhost:5000/api/initiatives'
        const params = new URLSearchParams()
        
        if (this.filters.location) {
          params.append('location', this.filters.location)
        }
        if (this.filters.status !== 'all') {
          params.append('status', this.filters.status)
        }

        if (params.toString()) {
          url += `?${params.toString()}`
        }

        const response = await axios.get(url)
        this.initiatives = response.data.initiatives.map(initiative => ({
          ...initiative,
          showEditForm: false,
          participantsList: []
        }))

      } catch (error) {
        console.error('Error fetching initiatives:', error)
      } finally {
        this.loading = false
      }
    },

    async showParticipantsList(initiativeId) {
      try {
        const response = await axios.get(
          `http://localhost:5000/api/initiatives/${initiativeId}/participants`
        )
        const initiative = this.initiatives.find(i => i.id === initiativeId)
        if (initiative) {
          initiative.participantsList = response.data.participants
        }
        this.$set(this.showParticipants, initiativeId, true)
      } catch (error) {
        console.error('Error fetching participants:', error)
      }
    },

    hideParticipants(initiativeId) {
      this.$set(this.showParticipants, initiativeId, false)
    },

    async createInitiative() {
      this.isSubmitting = true
      try {
        await axios.post('http://localhost:5000/api/initiatives', this.newInitiative)
        this.showCreateForm = false
        this.resetForm()
        await this.fetchInitiatives()
        alert('Initiative created successfully!')
      } catch (error) {
        console.error('Error creating initiative:', error)
        alert(error.response?.data?.error || 'Failed to create initiative')
      } finally {
        this.isSubmitting = false
      }
    },

    async joinInitiative(id) {
      this.isJoining = true
      try {
        await axios.post(`http://localhost:5000/api/initiatives/${id}/join`)
        await this.fetchInitiatives()
        alert('Successfully joined the initiative!')
      } catch (error) {
        console.error('Error joining initiative:', error)
        alert(error.response?.data?.error || 'Failed to join initiative')
      } finally {
        this.isJoining = false
      }
    },

    async updateStatus(id, status) {
      try {
        await axios.put(`http://localhost:5000/api/initiatives/${id}`, {
          status: status
        })
        await this.fetchInitiatives()
      } catch (error) {
        console.error('Error updating initiative:', error)
        alert('Failed to update initiative status')
      }
    },

    isCreator(initiative) {
      return initiative.created_by === this.currentUser.id
    },

    hasJoined(initiative) {
      return initiative.participants?.includes(this.currentUser.id)
    },

    getParticipantCount(initiative) {
      return initiative.participants?.length || 0
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    resetForm() {
      this.newInitiative = {
        title: '',
        description: '',
        location: '',
        event_date: '',
        duration_hours: 1,
        max_participants: 50,
        requirements: '',
        contact_info: ''
      }
    },

    filterInitiatives() {
      this.fetchInitiatives()
    }
  }
}
</script>

<style scoped>
.initiatives {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.create-btn {
  background: #42b983;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  margin-bottom: 20px;
}

.create-form {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-row {
  display: flex;
  gap: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input, select, textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.initiatives-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.initiative-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative;
  overflow: hidden;
}

.initiative-status {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  text-transform: uppercase;
  background: #e3f2fd;
  color: #1976d2;
}

.initiative-content {
  padding: 20px;
}

.initiative-details {
  margin: 15px 0;
}

.participants-info {
  margin: 10px 0;
}

.participants-list {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}

.participant-item {
  padding: 5px 0;
  border-bottom: 1px solid #eee;
}

.requirements, .contact-info {
  margin: 10px 0;
  font-size: 0.9em;
}

.initiative-actions {
  margin-top: 15px;
  text-align: center;
}

.creator-badge {
  display: block;
  color: #42b983;
  font-weight: bold;
  margin-bottom: 10px;
}

.creator-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 10px;
}

.join-btn {
  background: #42b983;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.complete-btn {
  background: #ff9800;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.small-btn {
  padding: 4px 8px;
  font-size: 0.9em;
  background: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: #666;
}

.joined-status {
  color: #42b983;
  font-weight: bold;
}

.loading, .no-initiatives {
  text-align: center;
  padding: 40px;
  color: #666;
}

/* Status-based styles */
.initiative-card.completed .initiative-status {
  background: #f5f5f5;
  color: #666;
}

.initiative-card.upcoming .initiative-status {
  background: #e3f2fd;
  color: #1976d2;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.description {
  color: #666;
  margin: 10px 0;
}
</style>
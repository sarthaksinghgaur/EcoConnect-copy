// src/views/BusinessesView.vue
<template>
  <div class="businesses">
    <h2>Sustainable Businesses</h2>

    <!-- Add New Business Button -->
    <button @click="showAddForm = !showAddForm" class="add-btn">
      {{ showAddForm ? 'Cancel' : '+ Add New Business' }}
    </button>

    <!-- Add Business Form -->
    <div v-if="showAddForm" class="form-card">
      <h3>Add New Business</h3>
      <form @submit.prevent="addBusiness" class="business-form">
        <div class="form-group">
          <label>Business Name *</label>
          <input 
            type="text" 
            v-model="newBusiness.name" 
            required
            placeholder="Enter business name"
          >
        </div>

        <div class="form-group">
          <label>Category *</label>
          <select v-model="newBusiness.category" required>
            <option value="">Select Category</option>
            <option value="zero_waste_store">Zero Waste Store</option>
            <option value="eco_friendly_cafe">Eco-friendly Café</option>
            <option value="sustainable_fashion">Sustainable Fashion</option>
            <option value="recycling_center">Recycling Center</option>
            <option value="repair_shop">Repair Shop</option>
          </select>
        </div>

        <div class="form-group">
          <label>Description</label>
          <textarea 
            v-model="newBusiness.description" 
            rows="3"
            placeholder="Describe the business"
          ></textarea>
        </div>

        <div class="form-group">
          <label>Address *</label>
          <input 
            type="text" 
            v-model="newBusiness.address" 
            required
            placeholder="Enter business address"
          >
        </div>

        <button type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Adding...' : 'Add Business' }}
        </button>
      </form>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <label>Category:</label>
        <select v-model="filters.category" @change="fetchBusinesses">
          <option value="">All Categories</option>
          <option value="zero_waste_store">Zero Waste Store</option>
          <option value="eco_friendly_cafe">Eco-friendly Café</option>
          <option value="sustainable_fashion">Sustainable Fashion</option>
          <option value="recycling_center">Recycling Center</option>
          <option value="repair_shop">Repair Shop</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Min Rating:</label>
        <select v-model="filters.minRating" @change="fetchBusinesses">
          <option :value="null">Any Rating</option>
          <option v-for="n in 5" :key="n" :value="n">
            {{ n }}+ Stars
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>
          <input 
            type="checkbox" 
            v-model="filters.verified"
            @change="fetchBusinesses"
          >
          Verified Only
        </label>
      </div>
    </div>

    <!-- Businesses Grid -->
    <div v-if="loading" class="loading">
      Loading businesses...
    </div>
    <div v-else-if="businesses.length === 0" class="no-data">
      No businesses found matching your criteria
    </div>
    <div v-else class="businesses-grid">
      <div v-for="business in businesses" 
           :key="business.id" 
           class="business-card"
      >
        <div v-if="business.verified" class="verified-badge">
          ✓ Verified
        </div>
        <h3>{{ business.name }}</h3>
        <div class="business-category">{{ formatCategory(business.category) }}</div>
        <div class="business-rating">
          <span class="stars">{{ '★'.repeat(Math.round(business.rating || 0)) }}</span>
          <span class="rating-text">{{ business.rating?.toFixed(1) || 'No ratings' }}</span>
        </div>
        <p class="business-description">{{ business.description }}</p>
        <p class="business-address">📍 {{ business.address }}</p>

        <!-- Review Form -->
        <button 
          @click="business.showReviewForm = !business.showReviewForm"
          class="review-btn"
        >
          Add Review
        </button>

        <div v-if="business.showReviewForm" class="review-form">
          <form @submit.prevent="submitReview(business.id)">
            <div class="form-group">
              <label>Rating</label>
              <select v-model="newReview.rating" required>
                <option value="">Select Rating</option>
                <option v-for="n in 5" :key="n" :value="n">{{ n }} Stars</option>
              </select>
            </div>

            <div class="form-group">
              <label>Comment</label>
              <textarea 
                v-model="newReview.comment"
                rows="2"
                required
              ></textarea>
            </div>

            <button type="submit" :disabled="isSubmittingReview">
              {{ isSubmittingReview ? 'Submitting...' : 'Submit Review' }}
            </button>
          </form>
        </div>

        <!-- Reviews Section -->
        <div class="reviews-section">
          <h4>Recent Reviews</h4>
          <div v-if="business.reviews?.length" class="reviews-list">
            <div v-for="review in business.reviews.slice(0, 3)" 
                 :key="review.id" 
                 class="review-item">
              <div class="review-stars">{{ '★'.repeat(review.rating) }}</div>
              <p class="review-comment">{{ review.comment }}</p>
              <span class="review-date">{{ formatDate(review.created_at) }}</span>
            </div>
          </div>
          <div v-else class="no-reviews">
            No reviews yet
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'BusinessesView',
  data() {
    return {
      businesses: [],
      loading: true,
      showAddForm: false,
      isSubmitting: false,
      isSubmittingReview: false,
      filters: {
        category: '',
        minRating: null,
        verified: false
      },
      newBusiness: {
        name: '',
        category: '',
        description: '',
        address: ''
      },
      newReview: {
        rating: '',
        comment: ''
      }
    }
  },
  created() {
    this.fetchBusinesses()
  },
  methods: {
    async fetchBusinesses() {
      this.loading = true
      try {
        let url = 'http://localhost:5000/api/businesses'
        const params = new URLSearchParams()

        if (this.filters.category) {
          params.append('category', this.filters.category)
        }
        if (this.filters.minRating) {
          params.append('min_rating', this.filters.minRating)
        }
        if (this.filters.verified) {
          params.append('verified', true)
        }

        if (params.toString()) {
          url += `?${params.toString()}`
        }

        const response = await axios.get(url)
        this.businesses = response.data.businesses.map(business => ({
          ...business,
          showReviewForm: false
        }))

        // Fetch reviews for each business
        await Promise.all(
          this.businesses.map(async (business) => {
            try {
              const reviewsResponse = await axios.get(
                `http://localhost:5000/api/businesses/${business.id}/reviews`
              )
              business.reviews = reviewsResponse.data.reviews
            } catch (error) {
              console.error(`Error fetching reviews for business ${business.id}:`, error)
              business.reviews = []
            }
          })
        )
      } catch (error) {
        console.error('Error fetching businesses:', error)
      } finally {
        this.loading = false
      }
    },

    async addBusiness() {
      this.isSubmitting = true
      try {
        await axios.post('http://localhost:5000/api/businesses', this.newBusiness)
        this.showAddForm = false
        this.resetNewBusiness()
        await this.fetchBusinesses()
      } catch (error) {
        console.error('Error adding business:', error)
        alert('Failed to add business: ' + (error.response?.data?.error || 'Unknown error'))
      } finally {
        this.isSubmitting = false
      }
    },

    async submitReview(businessId) {
      this.isSubmittingReview = true
      try {
        await axios.post(
          `http://localhost:5000/api/businesses/${businessId}/review`,
          this.newReview
        )
        const business = this.businesses.find(b => b.id === businessId)
        if (business) {
          business.showReviewForm = false
        }
        this.resetNewReview()
        await this.fetchBusinesses()
      } catch (error) {
        console.error('Error submitting review:', error)
        alert('Failed to submit review: ' + (error.response?.data?.error || 'Unknown error'))
      } finally {
        this.isSubmittingReview = false
      }
    },

    formatCategory(category) {
      return category
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },

    resetNewBusiness() {
      this.newBusiness = {
        name: '',
        category: '',
        description: '',
        address: ''
      }
    },

    resetNewReview() {
      this.newReview = {
        rating: '',
        comment: ''
      }
    }
  }
}
</script>

<style scoped>
.businesses {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.form-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin: 20px 0;
}

.business-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

label {
  font-weight: bold;
}

input, select, textarea {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.filters {
  display: flex;
  gap: 20px;
  margin: 20px 0;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.businesses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.business-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative;
}

.verified-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #42b983;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8em;
}

.business-category {
  color: #666;
  margin: 5px 0;
}

.business-rating {
  margin: 10px 0;
}

.stars {
  color: #f0ad4e;
  margin-right: 5px;
}

.business-description {
  margin: 10px 0;
  color: #444;
}

.business-address {
  color: #666;
  font-size: 0.9em;
}

.review-btn {
  margin: 10px 0;
  background: #42b983;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.review-form {
  margin: 15px 0;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
}

.reviews-section {
  margin-top: 20px;
}

.review-item {
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.review-item:last-child {
  border-bottom: none;
}

.review-stars {
  color: #f0ad4e;
}

.review-comment {
  margin: 5px 0;
  font-size: 0.9em;
}

.review-date {
  color: #666;
  font-size: 0.8em;
}

.add-btn {
  background: #42b983;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.loading, .no-data {
  text-align: center;
  padding: 20px;
  color: #666;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
<template>
  <div>
    <h1>User Interests</h1>
    <div>
      <input v-model="userId" placeholder="Enter User ID" />
      <button @click="getInterests">Get Interests</button>
      <div v-if="interests.length > 0">
        <h3>Interests:</h3>
        <ul>
          <li v-for="(interest, index) in interests" :key="index">{{ interest }}</li>
        </ul>
      </div>
    </div>

    <div>
      <h3>Update Interests</h3>
      <input v-model="newInterests" placeholder="Enter new interests" />
      <button @click="updateInterests">Update Interests</button>
    </div>

    <div>
      <h3>Find Similar Interests</h3>
      <input v-model="interestId" placeholder="Enter Interest ID" />
      <button @click="findSimilarInterests">Find Similar Interests</button>
      <div v-if="similarInterests.length > 0">
        <h4>Similar Interests:</h4>
        <ul>
          <li v-for="(interest, index) in similarInterests" :key="index">{{ interest }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export default {
  data() {
    return {
      userId: '',
      newInterests: '',
      interestId: '',
      interests: [],
      similarInterests: []
    };
  },
  methods: {
    async getInterests() {
      try {
        const response = await axios.get(`${API_URL}/profile/interests/${this.userId}`);
        this.interests = response.data;
      } catch (error) {
        console.log(error.response?.data?.error || 'Error fetching interests');
      }
    },
    async updateInterests() {
      try {
        const updatedInterests = this.newInterests.split(',');
        const response = await axios.put(
          `${API_URL}/profile/interests/${this.userId}`,
          { interests: updatedInterests }
        );
        console.log(response.data.message || 'Interests updated successfully');
      } catch (error) {
        console.log(error.response?.data?.error || 'Error updating interests');
      }
    },
    async findSimilarInterests() {
      try {
        const response = await axios.get(`${API_URL}/interests/similar/${this.interestId}`, {
          params: { limit: 5 }
        });
        this.similarInterests = response.data;
      } catch (error) {
        console.log(error.response?.data?.error || 'Error finding similar interests');
      }
    }
  }
};
</script>

<style scoped>
button {
  margin: 10px;
}
input {
  margin: 10px;
}
</style>

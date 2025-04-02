<template>
    <div id="app">
      <h1>User Profile</h1>
      
      <!-- Create User Section -->
      <div>
        <h2>Create User</h2>
        <form @submit.prevent="createUser">
          <input v-model="userId" type="text" placeholder="User ID" required />
          <input v-model="userName" type="text" placeholder="Name" required />
          <input v-model="userEmail" type="email" placeholder="Email" required />
          <button type="submit">Create User</button>
        </form>
      </div>
  
      <!-- Get User Interests Section -->
      <div>
        <h2>Get Interests</h2>
        <button @click="getUserInterests">Get Interests</button>
        <ul>
          <li v-for="interest in interests" :key="interest.id">{{ interest.name }}</li>
        </ul>
      </div>
  
      <!-- Update User Interests Section -->
      <div>
        <h2>Update Interests</h2>
        <form @submit.prevent="updateUserInterests">
          <input v-model="interestName" type="text" placeholder="Interest Name" required />
          <textarea v-model="interestDescription" placeholder="Interest Description" required></textarea>
          <button type="submit">Update Interests</button>
        </form>
      </div>
  
      <!-- Similar Interests Section -->
      <div>
        <h2>Find Similar Interests</h2>
        <button @click="findSimilarInterests">Find Similar Interests</button>
        <ul>
          <li v-for="interest in similarInterests" :key="interest.id">{{ interest.name }} (Similarity: {{ interest.similarity }})</li>
        </ul>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'App',
    data() {
      return {
        userId: '',
        userName: '',
        userEmail: '',
        interests: [],
        interestName: '',
        interestDescription: '',
        similarInterests: []
      };
    },
    methods: {
      // Create a user
      async createUser() {
        try {
          const response = await axios.post(`http://localhost:5000/api/profile/${this.userId}`, {
            name: this.userName,
            email: this.userEmail
          });
          alert(response.data.message);
        } catch (error) {
          console.error(error);
          alert('Error creating user');
        }
      },
      
      // Get user interests
      async getUserInterests() {
        try {
          const response = await axios.get(`http://localhost:5000/api/profile/interests/${this.userId}`);
          this.interests = response.data;
        } catch (error) {
          console.error(error);
          alert('Error fetching interests');
        }
      },
  
      // Update user interests
      async updateUserInterests() {
        const newInterest = {
          id: new Date().getTime().toString(), // Unique ID for the interest
          name: this.interestName,
          description: this.interestDescription
        };
  
        try {
          const response = await axios.put(`http://localhost:5000/api/profile/interests/${this.userId}`, [newInterest]);
          alert(response.data.message);
        } catch (error) {
          console.error(error);
          alert('Error updating interests');
        }
      },
  
      // Find similar interests
      async findSimilarInterests() {
        const interestId = this.interests[0]?.id; // Assuming we have at least one interest for the demonstration
        if (!interestId) return;
  
        try {
          const response = await axios.get(`http://localhost:5000/api/interests/similar/${interestId}`, {
            params: { limit: 5 }
          });
          this.similarInterests = response.data;
        } catch (error) {
          console.error(error);
          alert('Error finding similar interests');
        }
      }
    }
  };
  </script>
  
  <style scoped>
  </style>
  
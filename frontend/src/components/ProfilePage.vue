<template>
  <div class="profile">
    <div class="flex flex-col min-h-screen bg-gray-100">
      <main class="flex-grow">
        <div class="container mx-auto pt-12 px-4">
          <h1 class="text-4xl font-bold text-center text-gray-800 mb-6">Manage Profile</h1>
          
          <div v-if="loading" class="text-center mt-8">
            <p class="text-lg text-gray-600">Loading your profile...</p>
          </div>
          <div v-else-if="error" class="text-center mt-8 text-red-600">
            <p class="text-lg">{{ error }}</p>
          </div>
          <div v-else>
            <div v-if="isNewUser" class="bg-blue-50 border border-blue-200 rounded-lg p-6 my-8 mx-auto max-w-2xl shadow-lg">
              <p class="text-center text-lg text-gray-800">
                Welcome! It looks like this is your first time here.
                We've suggested some interests to get you started, but feel free to modify them.
              </p>
            </div>
            
            <p class="text-center text-gray-600 text-lg mt-6">Here are your interests</p>
            
            <ProfileBox 
            :interests="userInterests" 
            :isNewUser="isNewUser"
            @updateInterests="updateUserInterests" 
            />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>


<script setup>
import { defineProps, ref, watch, onMounted } from 'vue';

const props = defineProps({
  userId: String,
});

import ProfileBox from './ProfileBox.vue';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
const USER_ID = ref(props.userId);

const userInterests = ref([]);
const loading = ref(true);
const error = ref(null);
const isNewUser = ref(false);

const defaultInterests = [
  { id: 1, name: 'Technology', description: 'Latest trends and gadgets in tech.' },
  { id: 2, name: 'Sports', description: 'Favorite teams and sports activities.' },
  { id: 3, name: 'Music', description: 'Genres and artists you love.' },
  { id: 4, name: 'Travel', description: 'Places you want to visit and travel tips.' },
  { id: 5, name: 'Books', description: 'Fiction, non-fiction, and reading recommendations.' }
];

const fetchUserInterests = async () => {
  loading.value = true;
  error.value = null;

  console.log("1: ", USER_ID.value)

  try {
    const response = await axios.get(`${API_URL}/profile/interests/${USER_ID.value}`);
    
    if (response.data.length === 0) {
      isNewUser.value = true;
      userInterests.value = [...defaultInterests];
    } else {
      userInterests.value = response.data;
      isNewUser.value = false;
    }
  } catch (err) {
    console.error('Error fetching interests:', err);
    error.value = 'Failed to load interests. Please try again later.';
  } finally {
    loading.value = false;
  }
};

const updateUserInterests = async (newInterests) => {
  loading.value = true;
  error.value = null;
  
  try {
    await axios.put(`${API_URL}/profile/interests/${USER_ID.value}`, newInterests);
    userInterests.value = newInterests;
    isNewUser.value = false;
  } catch (err) {
    console.error('Error updating interests:', err);
    error.value = 'Failed to update interests. Please try again later.';
    await fetchUserInterests();
  } finally {
    loading.value = false;
  }
};

watch(() => props.userId, (newUserId) => {
  console.log('User ID changed to:', newUserId);
  USER_ID.value = newUserId;
  fetchUserInterests(newUserId);
}, { immediate: true });

onMounted(() => {
  fetchUserInterests(props.userId);
});
</script>

<style>
.profile {
  padding-top: 20px;
  padding-bottom: 20px;
}
</style>
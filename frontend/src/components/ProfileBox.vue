<!-- src/components/ProfileBox.vue -->
<template>
    <div class="flex flex-col items-center">
      <div class="grid-container">
        <div class="grid">
            <ProfileCard 
            v-for="(interest, index) in interests" 
            :key="interest.id" 
            :interest="interest" 
            @remove="removeInterest"
            @update="updateInterest"
            />
        </div>
    </div>
  
      <!-- Input for Adding New Interests -->
      <div class="mt-6 flex space-x-4">
        <input 
          v-model="newInterest" 
          type="text" 
          class="p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Add new interest..."
        />
        <button 
        @click="addInterest" 
        class="px-4 py-2 text-white rounded transition"
        style="background-color: #3b82f6;" 
        @mouseover="hover = true"
        @mouseleave="hover = false"
        :style="{ backgroundColor: hover ? '#2563eb' : '#3b82f6' }"
        >
            Add
        </button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { defineProps, defineEmits, ref } from 'vue';
  import ProfileCard from './ProfileCard.vue';
  
  const props = defineProps({
    interests: Array
  });
  
  const emit = defineEmits(['updateInterests']);
  
  const newInterest = ref('');
  
  // Function to add a new interest
  const addInterest = () => {
  const trimmedInterest = newInterest.value.trim().toLowerCase();

  // Check if the interest already exists (case-insensitive)
  const exists = props.interests.some(
    (interest) => interest.name.toLowerCase() === trimmedInterest
  );

    if (trimmedInterest && !exists) {
        const newItem = {
        id: Date.now(),
        name: newInterest.value.trim(),
        description: "Newly added interest"
        };

        emit('updateInterests', [...props.interests, newItem]);
        newInterest.value = ''; // Clear input
    }
    };

  
  // Function to remove an interest
  const removeInterest = (id) => {
    const updatedInterests = props.interests.filter(interest => interest.id !== id);
    emit('updateInterests', updatedInterests);
  };
  
  // Function to update an interest's name
  const updateInterest = ({ id, name }) => {
    const updatedInterests = props.interests.map(interest =>
      interest.id === id ? { ...interest, name } : interest
    );
    emit('updateInterests', updatedInterests);
  };
  </script>
  
  <style scoped>
  .grid-container {
    width: 100%;
    display: flex;
    justify-content: center;
    padding: 16px;
  }
  
  .grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(200px, 1fr)); /* Exactly 4 items per row */
    gap: 80px; /* Space between cards */
    width: 100%;
    max-width: 1024px; /* Prevents excessive stretching */
  }
  </style>
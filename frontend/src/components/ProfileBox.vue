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
      <div class="input-section">
        <input 
          v-model="newInterest" 
          type="text" 
          class="new-text-box"
          placeholder="Add new interest..."
          @keyup.enter="addInterest"
        />
        <button 
        @click="addInterest" 
        class="new-button"
        style="background-color: #3b82f6;">
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
  
  console.log('adding interest: ', trimmedInterest);
  
  // Check if the interest already exists (case-insensitive)
  const exists = props.interests.some(
    (interest) => interest.name.toLowerCase() === trimmedInterest
  );

  console.log('trimmed:', trimmedInterest)
  console.log('!exists:', !exists)

    if (trimmedInterest && !exists) {
        const newItem = {
        id: Date.now(),
        name: newInterest.value.trim(),
        description: "Newly added interest"
        };
        
        console.log('Interests:', newItem)

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
  
  .new-button {
    padding-left: 20px;
padding: 9px 22px;
  border-radius: 6px;
  display: inline-block !important;
  text-align: center;
  transition: all 200ms;
  color: #000;
  margin-top: 1em;
  font-weight: bold;
}

.new-button:hover {
  background-color: #3444ec;
  box-shadow: rgba(0, 0, 0, 0.16) 0px 1px 4px, #3444ec 0px 0px 0px 2px;
  border-radius: 8px;
  font-weight: bold;
  color: #000000;
  transform: scale(1.05);
}

.new-text-box {
  padding: 20px;
  border: 2px solid #ccc;
  border-radius: 8px;
  background-color: #fcf4dc;
}

.input-section {
  display: flex;
  flex-direction: row;
  gap: 16px;
  align-items: center;
  margin-top: 20px;
}

</style>
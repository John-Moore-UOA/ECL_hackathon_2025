<template>
    <div class="card">
      <!-- Editable Text Box (Title) -->
      <input 
        v-model="editableName" 
        type="text" 
        class="editable-title"
      />
  
      <!-- Description -->
      <p class="description">{{ interest.description }}</p>
  
      <!-- Remove Button -->
      <button 
        @click="$emit('remove', interest.id)" 
        class="remove-button"
      >
        Remove
      </button>
    </div>
  </template>
  
  <script setup>
  import { defineProps, defineEmits, ref, watch } from 'vue';
  
  const props = defineProps({
    interest: Object
  });
  const emit = defineEmits(['remove', 'update']);
  
  const editableName = ref(props.interest.name);
  
  watch(editableName, (newName) => {
    emit('update', { id: props.interest.id, name: newName });
  });
  </script>
  
  <style scoped>
  /* Card container */
  .card {
    background-color: white;
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    width: 260px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
  
  /* Editable Title */
  .editable-title {
    font-size: 1.25rem;
    font-weight: bold;
    border: 2px solid transparent;
    text-align: center;
    width: 100%;
    padding: 4px;
    background-color: transparent;
    transition: border-color 0.2s ease-in-out;
  }
  
  .editable-title:focus {
    outline: none;
    border-color: #3b82f6; /* Blue highlight */
  }
  
  /* Description */
  .description {
    color: #4b5563;
    text-align: center;
    font-size: 0.875rem;
  }
  
  /* Remove Button (Force Red) */
  .remove-button {
    background-color: #b06565 !important; /* Force red */
    color: white;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: bold;
    transition: background-color 0.2s ease-in-out;
    width: 100%;
  }
  
  .remove-button:hover {
    background-color: #e35151 !important; /* Darker red */
  }
  </style>
  
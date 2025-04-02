<script setup>
import { defineProps, defineEmits, ref } from 'vue';

const props = defineProps({
  companyName: String,
  navItems: Array
});

const emit = defineEmits(['login']);

// Create a ref for the input field
const userInput = ref('');

const onLogin = () => {
  if (userInput.value.trim() !== '') {
    if (!isNaN(userInput.value)) {
      console.log('Login submitted with:', userInput.value);
      emit('login', userInput.value);
    } else {
      console.log('Please enter a valid number to login');
    }
  } else {
    console.log('Please enter a value to login');
  }
};

const home = () => {
  location.reload();
}

</script>

<template>
  <header class="bg-gradient-to-r from-blue-600 to-indigo-700 text-white shadow-lg">
    <div class="container mx-auto px-6 py-4">
      <div class="flex justify-between items-center">
        <div class="flex items-center">
          <div class="font-bold text-xl">{{ companyName }}</div>
        </div>
        <div class="flex items-center space-x-2">
          <input
            v-model="userInput"
            type="text"
            placeholder="Enter you ID"
            class="px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            @click="onLogin"
            class="bg-blue-500 px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
          >
            Login
          </button>
          <button
            @click="home"
            class="bg-blue-500 px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
          >
            Home
          </button>
        </div>
      </div>
    </div>
  </header>
</template>



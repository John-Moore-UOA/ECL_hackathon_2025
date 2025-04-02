<script setup>
import { ref } from 'vue';

const formTitle = ref('Get in Touch');
const formData = ref({
  name: '',
  email: '',
  message: '',
  subscribe: false
});
const formSubmitted = ref(false);

function submitForm() {
  // Here you would typically send the form data to your backend
  console.log('Form submitted:', formData.value);
  formSubmitted.value = true;
  
  // Reset form after submission (optional)
  setTimeout(() => {
    formData.value = {
      name: '',
      email: '',
      message: '',
      subscribe: false
    };
    formSubmitted.value = false;
  }, 3000);
}
</script>

<template>
  <div class="bg-white rounded-lg shadow-xl p-8">
    <h2 class="text-2xl font-semibold text-gray-800 mb-6">{{ formTitle }}</h2>
    <form @submit.prevent="submitForm">
      <div class="mb-4">
        <label class="block text-gray-700 text-sm font-bold mb-2" for="name">
          Full Name
        </label>
        <input 
          id="name"
          v-model="formData.name" 
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" 
          type="text" 
          placeholder="John Doe"
          required
        >
      </div>
      <div class="mb-4">
        <label class="block text-gray-700 text-sm font-bold mb-2" for="email">
          Email
        </label>
        <input 
          id="email"
          v-model="formData.email" 
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" 
          type="email" 
          placeholder="john@example.com"
          required
        >
      </div>
      <div class="mb-4">
        <label class="block text-gray-700 text-sm font-bold mb-2" for="message">
          Message
        </label>
        <textarea 
          id="message"
          v-model="formData.message" 
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" 
          rows="4" 
          placeholder="How can we help you?"
        ></textarea>
      </div>
      <div class="mb-6">
        <label class="flex items-center">
          <input 
            v-model="formData.subscribe" 
            type="checkbox" 
            class="form-checkbox h-5 w-5 text-blue-600"
          >
          <span class="ml-2 text-gray-700">Subscribe to newsletter</span>
        </label>
      </div>
      <div>
        <button 
          type="submit" 
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:shadow-outline transition-colors duration-200"
        >
          Submit
        </button>
      </div>
    </form>
    <div v-if="formSubmitted" class="mt-4 p-3 bg-green-100 text-green-700 rounded-lg">
      Thank you! Your submission has been received.
    </div>
  </div>
</template>
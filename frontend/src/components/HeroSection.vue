<script setup>
import ContactForm from './ContactForm.vue';

defineProps({
  title: String,
  description: String
});
</script>

<template>
  <section class="hero-pattern py-20 px-6">
    <div class="container mx-auto flex flex-col md:flex-row items-center">
      <div class="md:w-1/2 mb-10 md:mb-0">
        <h1 class="text-4xl md:text-5xl font-bold text-gray-800 leading-tight mb-4">
          {{ title }}
        </h1>
        <p class="text-lg text-gray-600 mb-8 max-w-md">
          {{ description }}
        </p>
        <button class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg shadow-md transition-colors duration-200 transform hover:scale-105">
          Learn More
        </button>
      </div>
      <div class="md:w-1/2 md:pl-10">
        <ContactForm />
      </div>
    </div>
  </section>
</template>
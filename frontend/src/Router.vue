<script setup>
import { ref, computed } from 'vue'
import App from './App.vue'
import Admin from './pages/Admin.vue'

// Define routes for different paths
const routes = {
  '/': App,
  '/admin': Admin
}

// Track the current path
const currentPath = ref(window.location.hash.slice(1) || '/')

// Listen for hash changes
window.addEventListener('hashchange', () => {
  currentPath.value = window.location.hash.slice(1) || '/'
})

// Determine the view to display based on the current path
const currentView = computed(() => {
  return routes[currentPath.value] || NotFound
})
</script>

<template>
  <div class="debug">
      <a href="#/">App</a> |
      <a href="#/admin">Admin</a> |
    </div>
  <component :is="currentView" />
</template>

<style>
.debug {
    background-color: rgb(60, 84, 119);
    border: 3px solid black;
    width: 100%;
}

</style>

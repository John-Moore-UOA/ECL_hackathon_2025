<script setup>
import { ref} from 'vue';
import Header from './components/Header.vue';
import HeroSection from './components/HeroSection.vue';
import FeaturesSection from './components/FeaturesSection.vue';
import Footer from './components/Footer.vue';
import ProfilePage from './components/ProfilePage.vue';

const isProfilePage = ref(false);
const userId = ref('');

const companyName = ref('LatteLink / MugMate / CoasterConnect');
const heroTitle = ref('Welcome to Our Landing Page');
const heroDescription = ref('A powerful solution to help you achieve your goals. Sign up today and start your journey with us.');
const footerDescription = ref('We revolutionize coffee breaks by turning them into seamless networking opportunities. Connect effortlessly over coffee with our smart coaster—reach out to learn more!');

const features = ref([
  {
    title: 'Form Connections',
    description: 'Enjoy a coffee while effortlessly connecting with others.'
  },
  {
    title: 'Stimulating!',
    description: 'Brew a fresh cup. You’ve earned it with all your hard work!'
  },
  {
    title: 'Secure & Reliable',
    description: 'Your data is safe with our enterprise-grade security measures.'
  }
]);

const footerColumns = ref([
  {
    title: 'Resources',
    links: ['About', 'API Status']
  },
]);

const login = (id) => {
  isProfilePage.value = true;

  console.log("ID VALUE: ", id)
  userId.value = id;
};

</script>

<template>
  <div class="app">
    <!-- Header -->
    <Header :company-name="companyName" @login="login" />
    
    <!-- Conditionally render the landing page or profile page -->
    <div>
      <HeroSection v-if="!isProfilePage" :title="heroTitle" :description="heroDescription" />
      <FeaturesSection v-if="!isProfilePage" :features="features" />
      <ProfilePage v-if="isProfilePage" :userId="userId" />
    </div>
    
    <!-- Footer -->
    <Footer
      :company-name="companyName"
      :description="footerDescription"
      :columns="footerColumns"
    />
  </div>
</template>

<style>
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
  line-height: 1.6;
  margin: 0;
  padding: 0;
  min-height: 100vh;
}

.hero-pattern {
  background-color: #f9fafb;
  background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23b0bec5' fill-opacity='0.1' fill-rule='evenodd'/%3E%3C/svg%3E");
}
</style>

<script setup>
import { ref} from 'vue';
import Header from './components/Header.vue';
import HeroSection from './components/HeroSection.vue';
import FeaturesSection from './components/FeaturesSection.vue';
import Footer from './components/Footer.vue';
import ProfilePage from './components/ProfilePage.vue';

const isProfilePage = ref(false);
const userId = ref('');

const companyName = ref('LatteLink'); //  MugMate, CoasterConnect
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
    <div class="hero-section">
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

.app {
  background-color: #f0f0f0;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
  line-height: 1.6;
  margin: 0;
  padding: 0;
  min-height: 100vh;
}

.hero-section {
  min-height: 100vh;
}
</style>

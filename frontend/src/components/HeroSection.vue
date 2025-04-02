<template>
  <section class="hero">
    <div class="hero-content">
      <h1 class="hero-title">{{ title }}</h1>
      <p class="hero-description">{{ description }}</p>
    </div>
    <div class="hero-images">
      <img src="../assets/temp.jpg" alt="hero image" class="hero-image" />
    </div>
  </section>
</template>

<script>
export default {
  data() {
    return {
      title: "Welcome to LatteLink",
      description: "Our Coffee Bump feature helps connect you with people from different groups, encouraging casual coffee meetups that spark meaningful interactions and new connections."
    };
  }
};
</script>

<style scoped>
.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  background-color: #f0f0f0;
}

.hero-content {
  flex: 1;
}

.hero-title {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.hero-description {
  font-size: 1.25rem;
  color: #666;
}

.hero-image {
  display: flex;
  gap: 1rem;
  flex: 1;
  height: 300px;
  width: 600px;
  object-fit: fill;
  padding-left: 80px;
  border-radius: 8px;
}
</style>

<script setup>
import { RouterView } from 'vue-router'

import UserDetailSidebar from '../components/UserDetailSidebar.vue'
</script>

<template>
  <div class="user-detail">
    <UserDetailSidebar />

    <main class="user-detail__content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.user-detail {
  display: flex;
  min-height: 100vh;
}

.user-detail__content {
  flex: 1;
  margin-left: 280px;
  padding: 48px;
}
</style>
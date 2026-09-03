<script setup>
import { RouterView } from 'vue-router'

import UserDetailSidebar from '../components/UserDetailSidebar.vue'
</script>

<template>
  <div class="user-detail-layout">
    <UserDetailSidebar />

    <div class="user-detail-layout__main">
      <AppHeader />

      <main class="user-detail-layout__content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.user-detail-layout {
  min-height: 100vh;
}

.user-detail-layout__main {
  min-height: 100vh;
  margin-left: 210px;

  display: flex;
  flex-direction: column;
}

.user-detail-layout__content {
  min-width: 0;
  flex: 1;

  box-sizing: border-box;
  padding: calc(var(--app-header-height) + 28px) 36px 40px;
}
</style>
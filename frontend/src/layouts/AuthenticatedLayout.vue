<script setup>
import { RouterView } from 'vue-router'

import AppHeader from './AppHeader.vue'
</script>

<template>
  <div class="authenticated-layout">
    <AppHeader />

    <RouterView />
  </div>
</template>

<style>

.authenticated-layout {
  --app-sidebar-width: 210px;
  --app-header-height: 48px;

  min-height: 100vh;
}
</style>
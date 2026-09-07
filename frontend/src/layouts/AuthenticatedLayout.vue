<script setup>
import { computed } from 'vue'
import {
  RouterView,
  useRoute,
} from 'vue-router'

import AppHeader from './AppHeader.vue'

const route = useRoute()

const hasSidebar = computed(() => {
  return route.path.startsWith(
    '/users',
  )
})
</script>

<template>
  <div
    class="authenticated-layout"
    :class="{
      'authenticated-layout--no-sidebar':
        !hasSidebar,
    }"
  >
    <AppHeader />

    <RouterView />
  </div>
</template>

<style scoped>
.authenticated-layout {
  --app-sidebar-width: 210px;
  --app-header-height: 48px;

  min-height: 100vh;

  box-sizing: border-box;
}

.authenticated-layout--no-sidebar {
  --app-sidebar-width: 0px;

  padding-top:
    var(--app-header-height);
}
</style>
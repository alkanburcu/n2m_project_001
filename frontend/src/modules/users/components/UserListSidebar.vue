<script setup>
import { IconUsers } from '@tabler/icons-vue'
import n2mobilLogo from '@/assets/images/n2mobil_amblem.png'
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar__menu">
      <div class="sidebar__item sidebar__item--active">
        <IconUsers :size="18" stroke-width="1.8" />
        <span>Users</span>
      </div>
    </div>

    <div class="sidebar__logo">
  <img
    :src="n2mobilLogo"
    alt="N2Mobil"
    class="sidebar__logo-image"
  />
</div>
  </aside>
</template>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;

  width: 210px;
  height: 100vh;

  display: flex;
  flex-direction: column;
  justify-content: space-between;

  background: #fafafa;
  border-right: 1px solid var(--color-border);
}

.sidebar__menu {
  padding-top: 24px;
}

.sidebar__item {
  display: flex;
  align-items: center;
  gap: 10px;

  padding: 12px 22px;

  font-size: 14px;
  font-weight: 500;

  color: var(--color-subtitle);
}

.sidebar__item--active {
  position: relative;
  color: var(--color-primary);
  background: var(--color-white);
}

.sidebar__item--active::before {
  content: '';

  position: absolute;
  top: 0;
  left: 0;

  width: 4px;
  height: 100%;

  border-radius: 0 4px 4px 0;
  background: var(--color-primary);
}

.sidebar__logo {

  padding: 24px;
}
.sidebar__logo-image {
  display: block;
  width: 105px;
  height: auto;
  object-fit: contain;
}
</style> 
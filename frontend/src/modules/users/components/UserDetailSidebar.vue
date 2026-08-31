<script setup>
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  IconChecklist,
  IconFileText,
  IconPhoto,
} from '@tabler/icons-vue'

import n2mobilLogo from '@/assets/images/n2mobil_amblem.png'

import { useUserStore } from '../store/userStore'

const route = useRoute()
const userStore = useUserStore()

watch(
  () => route.params.id,
  (userId) => {
    if (userId) {
      userStore.fetchUserById(userId)
    }
  },
  {
    immediate: true,
  },
)
</script>

<template>
  <aside class="detail-sidebar">
    <div>
      <section class="detail-sidebar__profile">
        <div class="detail-sidebar__avatar">
          {{
            (
              userStore.selectedUser?.name ||
              userStore.selectedUser?.username ||
              '?'
            )
              .charAt(0)
              .toUpperCase()
          }}
        </div>

        <div>
          <h2>
            {{
              userStore.selectedUser?.name ||
              userStore.selectedUser?.username
            }}
          </h2>

          <p>{{ userStore.selectedUser?.email }}</p>
        </div>
      </section>

      <nav class="detail-sidebar__nav">
        <RouterLink
          :to="{ name: 'user-todos', params: { id: route.params.id } }"
          class="detail-sidebar__link"
        >
          <IconChecklist :size="20" stroke-width="1.7" />
          <span>Todos</span>
        </RouterLink>

        <RouterLink
          :to="{ name: 'user-posts', params: { id: route.params.id } }"
          class="detail-sidebar__link"
        >
          <IconFileText :size="20" stroke-width="1.7" />
          <span>Posts</span>
        </RouterLink>

        <RouterLink
          :to="{ name: 'user-albums', params: { id: route.params.id } }"
          class="detail-sidebar__link"
        >
          <IconPhoto :size="20" stroke-width="1.7" />
          <span>Albums</span>
        </RouterLink>
      </nav>
    </div>

    <div class="detail-sidebar__logo">
      <img :src="n2mobilLogo" alt="N2Mobil" />
    </div>
  </aside>
</template>

<style scoped>
.detail-sidebar {
  position: fixed;
  inset: 0 auto 0 0;

  width: 190px;
  height: 100vh;

  display: flex;
  flex-direction: column;
  justify-content: space-between;

  background: #fafafa;
  border-right: 1px solid var(--color-border);
}

.detail-sidebar__profile {
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 10px;

  padding: 24px 16px;
  border-bottom: 1px solid var(--color-border);
}

.detail-sidebar__avatar {
  width: 44px;
  height: 44px;
  flex-shrink: 0;

  display: grid;
  place-items: center;

  border-radius: 50%;

  background: #eeeeee;
  color: var(--color-primary);

  font-size: 16px;
  font-weight: 600;
}

.detail-sidebar__profile > div:last-child {
  flex: 1;
  min-width: 0;
}


.detail-sidebar__profile h2 {
  margin: 0;

  color: var(--color-title);

  font-size: 14px;
  font-weight: 600;
}

.detail-sidebar__profile p {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin: 2px 0 0;
  color: var(--color-subtitle);
  font-size: 10px;
}

.detail-sidebar__nav {
  margin-top: 38px;
}

.detail-sidebar__link {
  position: relative;

  display: flex;
  align-items: center;
  gap: 12px;

  padding: 14px 24px;

  color: var(--color-subtitle);

  font-size: 14px;
  font-weight: 400;

  text-decoration: none;
}

.detail-sidebar__link.router-link-active {
  color: var(--color-primary);
  background: var(--color-white);
}

.detail-sidebar__link.router-link-active::before {
  content: '';

  position: absolute;
  inset: 0 auto 0 0;

  width: 4px;

  border-radius: 0 4px 4px 0;
  background: var(--color-primary);
}

.detail-sidebar__logo {
  padding: 24px 18px;
}

.detail-sidebar__logo img {
  display: block;
  width: 105px;
  height: auto;
}
</style>
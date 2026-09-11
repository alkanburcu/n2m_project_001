<script setup>
import {
  computed,
  watch,
}from 'vue'

import {
  useRoute,
  useRouter,
} from 'vue-router'

import {
  IconChecklist,
  IconFileText,
  IconPencil,
  IconPhoto,
} from '@tabler/icons-vue'

import n2mobilLogo from '@/assets/images/n2mobil_amblem.png'

import { useAuthStore } from '@/modules/auth/store/authStore'
import { useUserStore } from '../store/userStore'

const route = useRoute()
const router = useRouter()

const userStore = useUserStore()
const authStore = useAuthStore()

const isOwnProfile = computed(() => {
  return (
    String(route.params.id)
    === String(authStore.user?.id)
  )
})

const canViewTodos = computed(() => {
  return (
    isOwnProfile.value
    || authStore.can(
      'todos.manage_others',
    )
  )
})

const goEditProfile = async () => {
  if (!isOwnProfile.value) {
    return
  }

  await router.push({
    name: 'profile',
  })
}

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
        <button
          v-if="isOwnProfile"
          type="button"
          class="detail-sidebar__profile-button"
          aria-label="Edit profile"
          @click="goEditProfile"
        >
          <div class="detail-sidebar__avatar">
            <img
              v-if="userStore.selectedUser?.profile_photo"
              :src="userStore.selectedUser.profile_photo"
              alt=""
              class="detail-sidebar__avatar-image"
            >

            <span v-else>
              {{
                (
                  userStore.selectedUser?.display_name
                  || userStore.selectedUser?.username
                  || '?'
                )
                  .charAt(0)
                  .toUpperCase()
              }}
            </span>
          </div>

          <div class="detail-sidebar__identity">
            <h2>
              {{
                userStore.selectedUser?.display_name
                || userStore.selectedUser?.username
              }}
            </h2>

            <p>
              {{ userStore.selectedUser?.email }}
            </p>
          </div>

          <IconPencil
            :size="15"
            :stroke-width="1.8"
            class="detail-sidebar__edit-icon"
          />
        </button>

        <div
          v-else
          class="detail-sidebar__profile-content"
        >
          <div class="detail-sidebar__avatar">
            <img
              v-if="userStore.selectedUser?.profile_photo"
              :src="userStore.selectedUser.profile_photo"
              alt=""
              class="detail-sidebar__avatar-image"
            >

            <span v-else>
              {{
                (
                  userStore.selectedUser?.display_name
                  || userStore.selectedUser?.username
                  || '?'
                )
                  .charAt(0)
                  .toUpperCase()
              }}
            </span>
          </div>

          <div class="detail-sidebar__identity">
            <h2>
              {{
                userStore.selectedUser?.display_name
                || userStore.selectedUser?.username
              }}
            </h2>

            <p>
              {{ userStore.selectedUser?.email }}
            </p>
          </div>
        </div>
      </section>

      <nav class="detail-sidebar__nav">
        <RouterLink
          v-if="canViewTodos"
          :to="{
            name: 'user-todos',
            params: {
              id: route.params.id,
            },
          }"
          class="detail-sidebar__link"
        >
          <IconChecklist
            :size="20"
            stroke-width="1.7"
          />

          <span>Todos</span>
        </RouterLink>

        <RouterLink
          :to="{
            name: 'user-posts',
            params: {
              id: route.params.id,
            },
          }"
          class="detail-sidebar__link"
        >
          <IconFileText
            :size="20"
            stroke-width="1.7"
          />

          <span>Posts</span>
        </RouterLink>

        <RouterLink
          :to="{
            name: 'user-albums',
            params: {
              id: route.params.id,
            },
          }"
          class="detail-sidebar__link"
        >
          <IconPhoto
            :size="20"
            stroke-width="1.7"
          />

          <span>Albums</span>
        </RouterLink>
      </nav>
    </div>

    <div class="detail-sidebar__logo">
      <img
        :src="n2mobilLogo"
        alt="N2Mobil"
      />
    </div>
  </aside>
</template>

<style scoped>
.detail-sidebar {
  position: fixed;
  inset: 0 auto 0 0;

  width: 210px;
  height: 100vh;

  display: flex;
  flex-direction: column;
  justify-content: space-between;

  background: #fafafa;

  border-right:
    1px solid var(--color-border);
}

.detail-sidebar__avatar {
  width: 44px;
  height: 44px;

  flex-shrink: 0;

  display: grid;
  place-items: center;

  color: var(--color-primary);

  font-size: 16px;
  font-weight: 600;

  background: #eeeeee;

  border-radius: 50%;
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

  background: var(--color-primary);

  border-radius: 0 4px 4px 0;
}

.detail-sidebar__logo {
  padding: 24px 18px;
}

.detail-sidebar__logo img {
  display: block;

  width: 105px;
  height: auto;
}

.detail-sidebar__profile {
  overflow: hidden;

  padding: 0;

  border-bottom:
    1px solid var(--color-border);
}

.detail-sidebar__profile-button,
.detail-sidebar__profile-content {
  width: 100%;

  box-sizing: border-box;

  display: flex;
  align-items: center;
  gap: 10px;

  padding: 24px 16px;
}

.detail-sidebar__profile-button {
  color: inherit;

  font: inherit;
  text-align: left;

  background: transparent;
  border: 0;

  cursor: pointer;

  transition:
    background-color 0.18s ease;
}

.detail-sidebar__profile-button:hover {
  background:
    rgba(82, 63, 158, 0.05);
}

.detail-sidebar__profile-button:focus-visible {
  outline: none;

  box-shadow:
    inset 0 0 0 2px
    rgba(82, 63, 158, 0.22);
}

.detail-sidebar__avatar {
  width: 44px;
  height: 44px;

  flex-shrink: 0;

  display: grid;
  place-items: center;

  overflow: hidden;

  color: var(--color-primary);

  font-size: 16px;
  font-weight: 600;

  background: #eeeeee;

  border-radius: 50%;
}

.detail-sidebar__avatar-image {
  width: 100%;
  height: 100%;

  object-fit: cover;
}

.detail-sidebar__identity {
  min-width: 0;
  flex: 1;
}

.detail-sidebar__identity h2 {
  overflow: hidden;

  margin: 0;

  color: var(--color-title);

  font-size: 14px;
  font-weight: 600;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.detail-sidebar__identity p {
  overflow: hidden;

  margin: 2px 0 0;

  color: var(--color-subtitle);

  font-size: 10px;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.detail-sidebar__edit-icon {
  flex-shrink: 0;

  color: var(--color-subtitle);

  opacity: 0.65;
}

.detail-sidebar__profile-button:hover
.detail-sidebar__edit-icon {
  color: var(--color-primary);
  opacity: 1;
}
</style>
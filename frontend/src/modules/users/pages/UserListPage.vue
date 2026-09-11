<script setup>
import {
  onMounted,
  ref,
} from 'vue'

import { useRouter } from 'vue-router'

import {
  IconUserPlus,
} from '@tabler/icons-vue'

import { useAuthStore } from '@/modules/auth/store/authStore'

import CreateUserDialog from '../components/CreateUserDialog.vue'
import UserCard from '../components/UserCard.vue'
import UserListSidebar from '../components/UserListSidebar.vue'
import { useUserStore } from '../store/userStore'

const userStore = useUserStore()
const authStore = useAuthStore()
const router = useRouter()

const isCreateDialogOpen = ref(false)

onMounted(() => {
  userStore.fetchUsers()
})

const openUser = (userId) => {
  router.push({
    name: 'user-todos',
    params: {
      id: userId,
    },
  })
}

const canEditUser = (user) => {
  if (!authStore.can('users.update')) {
    return false
  }

  return (
    String(user.id)
      === String(authStore.user?.id)
    || authStore.can(
      'users.manage_others',
    )
  )
}

const editUser = (userId) => {
  if (
    String(userId)
    === String(authStore.user?.id)
  ) {
    router.push({
      name: 'profile',
    })

    return
  }

  router.push({
    name: 'user-profile-edit',

    params: {
      id: userId,
    },
  })
}
</script>

<template>
  <div class="users-page">
    <UserListSidebar />

    <main class="users-page__content">
      <header class="users-page__header">
        <h1>All users</h1>

        <button
          v-if="authStore.can('users.create')"
          type="button"
          class="create-user-button"
          @click="isCreateDialogOpen = true"
        >
          <IconUserPlus
            :size="16"
            :stroke-width="1.9"
          />

          <span>Create user</span>
        </button>
      </header>

      <p v-if="userStore.isLoading">
        Loading users...
      </p>

      <p v-else-if="userStore.error">
        {{ userStore.error }}
      </p>

      <section v-else class="users-grid">
        <UserCard
          v-for="user in userStore.users"
          :key="user.id"
          :user="user"
          :can-edit="canEditUser(user)"
          @select="openUser"
          @edit="editUser"
        />
      </section>
      <CreateUserDialog
        v-model="isCreateDialogOpen"
      />
    </main>
  </div>
</template>

<style scoped>
.users-page {
  min-height: 100vh;
  box-sizing: border-box;

  padding-top:
    calc(var(--app-header-height) + 28px);
}

.users-page__content {
  margin-left: 210px;
  padding: 34px 40px;
}

.users-page__header {
  width: 100%;

  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;

  margin-bottom: 32px;
}

.users-page__header h1 {
  margin: 0;

  color: var(--color-title);

  font-size: 18px;
  font-weight: 600;
}

.create-user-button {
  height: 36px;

  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;

  padding: 0 14px;

  color: #ffffff;

  font: inherit;
  font-size: 12.5px;
  font-weight: 600;

  background: var(--color-primary);

  border: 0;
  border-radius: 9px;

  box-shadow:
    0 2px 7px
    rgba(82, 63, 158, 0.18);

  cursor: pointer;

  transition:
    background-color 0.18s ease,
    box-shadow 0.18s ease,
    transform 0.18s ease;
}

.create-user-button:hover {
  background: rgb(71, 54, 140);

  box-shadow:
    0 4px 11px
    rgba(82, 63, 158, 0.22);

  transform: translateY(-1px);
}

.create-user-button:active {
  transform: translateY(0);
}

.create-user-button:focus-visible {
  outline: none;

  box-shadow:
    0 0 0 3px
    rgba(82, 63, 158, 0.14);
}

.users-grid {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));

  gap: 20px;
}

@media (max-width: 1100px) {
  .users-grid {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .users-page__content {
    margin-left: 0;
    padding: 24px;
  }

  .users-page__header {
    align-items: flex-start;
    flex-direction: column;
    gap: 14px;

    margin-bottom: 24px;
  }

  .create-user-button {
    align-self: flex-end;
  }

  .users-grid {
    grid-template-columns: 1fr;
  }
}
</style>
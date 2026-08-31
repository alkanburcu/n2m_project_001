<script setup>
import UserCard from '../components/UserCard.vue'
import UserListSidebar from '../components/UserListSidebar.vue'
import { useUserStore } from '../store/userStore'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

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
</script>

<template>
  <div class="users-page">
    <UserListSidebar />

    <main class="users-page__content">
      <h1>All users</h1>

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
          @select="openUser"
        />
      </section>
    </main>
  </div>
</template>

<style scoped>
.users-page {
  min-height: 100vh;
  background: var(--color-white);
}

.users-page__content {
  margin-left: 210px;
  padding: 34px 40px;
}

.users-page__content h1 {
  margin: 0 0 24px;

  color: var(--color-title);

  font-size: 18px;
  font-weight: 600;
}

.users-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

@media (max-width: 1100px) {
  .users-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .users-page__content {
    margin-left: 0;
    padding: 24px;
  }

  .users-grid {
    grid-template-columns: 1fr;
  }
}
</style>
<script setup>
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/modules/auth/store/authStore'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = async () => {
  await authStore.logout()
  await router.push('/login')
}
</script>

<template>
  <main>
    <h1>Users</h1>

    <p>Login successful.</p>

    <button @click="handleLogout">Logout</button>
  </main>
</template>
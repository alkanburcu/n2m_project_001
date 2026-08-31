<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/authStore'

const router = useRouter()
const authStore = useAuthStore()

const username = ref ('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
    errorMessage.value = ''
    isLoading.value = true

    try {
        await authStore.login({ username: username.value, password: password.value,})

    await router.push('/')
    }
    catch (error) { errorMessage.value = error.response?.data?.error || 'Login failed.Please check your credentials.' }
    finally { isLoading.value = false }
}
</script>

<template>
  <main>
    <h1>Login</h1>

    <form @submit.prevent="handleLogin">
      <div>
        <label for="username">Username</label>
        <input
          id="username"
          v-model="username"
          type="text"
          autocomplete="username"
          required
        />
      </div>

      <div>
        <label for="password">Password</label>
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="current-password"
          required
        />
      </div>

      <p v-if="errorMessage">
        {{ errorMessage }}
      </p>

      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Logging in...' : 'Login' }}
      </button>
    </form>
  </main>
</template>

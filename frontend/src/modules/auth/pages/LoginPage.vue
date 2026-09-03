<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/authStore'
import { IconEye, IconEyeOff } from '@tabler/icons-vue'


const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)
const showPassword = ref(false)

const handleLogin = async () => {
  errorMessage.value = ''
  isLoading.value = true

  try {
    const user = await authStore.login({
      username: username.value,
      password: password.value,
    })

    if (authStore.can('users.list')) {
      await router.push('/users')
    } else {
      await router.push(`/users/${user.id}`)
    }
  } catch (error) {
    errorMessage.value =
      error.response?.data?.error ||
      'Login failed. Please check your credentials.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-card">
      <div class="brand-line"></div>

      <div class="login-content">
        <div class="logo-wrapper">
          <img
            src="/n2mobil_logo.png"
            alt="N2Mobil"
            class="logo"
          />
        </div>

        <div class="login-heading">
          <h1>Welcome</h1>
          <p>Sign in to continue</p>
        </div>

        <form class="login-form" @submit.prevent="handleLogin">
          <div class="form-group">
            <label for="username">Username</label>

            <input
              id="username"
              v-model="username"
              type="text"
              autocomplete="username"
              placeholder="Enter your username"
              required
            />
          </div>

          <div class="form-group">
            <label for="password">Password</label>

            <div class="password-input">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                placeholder="Enter your password"
                required
              />

              <button
                type="button"
                class="password-toggle"
                :title="showPassword ? 'Hide password' : 'Show password'"
                @click="showPassword = !showPassword"
              >
                <IconEyeOff v-if="showPassword" :size="20" :stroke="1.8" />
                <IconEye v-else :size="20" :stroke="1.8" />
              </button>
            </div>
          </div>

          <p
            v-if="errorMessage"
            class="error-message"
            role="alert"
          >
            {{ errorMessage }}
          </p>

          <button
            class="login-button"
            type="submit"
            :disabled="isLoading"
          >
            <span
              v-if="isLoading"
              class="spinner"
              aria-hidden="true"
            ></span>

            {{ isLoading ? 'Signing in...' : 'Sign In' }}
          </button>
        </form>
      </div>
    </section>
  </main>
</template>

<style scoped>
.login-page {
  --brand-pink: #e72f8b;
  --brand-purple: #8c4bb5;
  --brand-blue: #278fc2;

  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;

  padding: 32px 20px;

  background:
    radial-gradient(
      circle at 15% 20%,
      rgba(231, 47, 139, 0.07),
      transparent 28%
    ),
    radial-gradient(
      circle at 85% 80%,
      rgba(39, 143, 194, 0.08),
      transparent 30%
    ),
    #f7f8fb;
}

.login-card {
  width: 100%;
  max-width: 430px;

  overflow: hidden;

  background: #ffffff;
  border: 1px solid #e8eaf0;
  border-radius: 20px;

  box-shadow:
    0 20px 45px rgba(30, 39, 58, 0.08),
    0 3px 10px rgba(30, 39, 58, 0.04);
}

.brand-line {
  height: 5px;

  background: linear-gradient(
    90deg,
    var(--brand-pink),
    var(--brand-purple),
    var(--brand-blue)
  );
}

.login-content {
  padding: 40px;
}

.logo-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 28px;
}

.logo {
  display: block;
  width: 165px;
  max-width: 100%;
  height: auto;
  object-fit: contain;
}

.login-heading {
  margin-bottom: 32px;
  text-align: center;
}

.login-heading h1 {
  margin: 0 0 8px;

  color: #202632;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.4px;
}

.login-heading p {
  margin: 0;

  color: #7a8291;
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #3c4350;
  font-size: 14px;
  font-weight: 600;
}

.form-group input {
  width: 100%;
  height: 48px;

  box-sizing: border-box;
  padding: 0 14px;

  color: #202632;
  font: inherit;

  background: #ffffff;
  border: 1px solid #dfe2e8;
  border-radius: 10px;

  outline: none;

  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    background-color 0.2s ease;
}

.form-group input::placeholder {
  color: #a5abb5;
}

.form-group input:hover {
  border-color: #c9ced8;
}

.form-group input:focus {
  border-color: var(--brand-purple);

  box-shadow:
    0 0 0 3px rgba(140, 75, 181, 0.11);
}

.password-input {
  position: relative;
}

.password-input input {
  padding-right: 52px;
}

.password-toggle {
  position: absolute;
  top: 50%;
  right: 14px;

  display: flex;
  align-items: center;
  justify-content: center;

  width: 28px;
  height: 28px;
  padding: 0;

  color: #737b89;
  font: inherit;
  font-size: 12px;
  font-weight: 600;

  background: transparent;
  border: 0;
  border-radius: 6px;

  cursor: pointer;

  transform: translateY(-50%);
  transition:
    color 0.2s ease,
    background-color 0.2s ease;
}

.password-toggle:hover {
  color: var(--brand-purple);
}


.error-message {
  margin: -5px 0 0;
  padding: 11px 13px;

  color: #b42318;
  font-size: 13px;

  background: #fff3f2;
  border: 1px solid #ffd5d2;
  border-radius: 9px;
}

.login-button {
  min-height: 49px;
  margin-top: 2px;

  display: flex;
  align-items: center;
  justify-content: center;
  gap: 9px;

  color: #ffffff;
  font: inherit;
  font-size: 15px;
  font-weight: 600;

  background: linear-gradient(
    100deg,
    var(--brand-pink),
    var(--brand-purple),
    var(--brand-blue)
  );

  border: 0;
  border-radius: 10px;

  cursor: pointer;

  box-shadow:
    0 8px 18px rgba(123, 76, 173, 0.2);

  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    opacity 0.2s ease;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-1px);

  box-shadow:
    0 11px 22px rgba(123, 76, 173, 0.25);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-button:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.spinner {
  width: 15px;
  height: 15px;

  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #ffffff;
  border-radius: 50%;

  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 520px) {
  .login-page {
    padding: 20px 14px;
  }

  .login-content {
    padding: 32px 24px;
  }

  .login-card {
    border-radius: 16px;
  }

  .login-heading h1 {
    font-size: 25px;
  }
}
</style>
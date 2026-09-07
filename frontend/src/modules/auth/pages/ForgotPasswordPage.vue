<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import {
  IconArrowLeft,
  IconMail,
} from '@tabler/icons-vue'

import authService from '../services/authService'

const router = useRouter()

const email = ref('')

const errorMessage = ref('')
const successMessage = ref('')

const isLoading = ref(false)

const getApiError = (error, fallback) => {
  const data = error.response?.data

  if (!data) {
    return fallback
  }

  if (typeof data.error === 'string') {
    return data.error
  }

  if (typeof data.detail === 'string') {
    return data.detail
  }

  const firstFieldError =
    Object.values(data)
      .flat()
      .find(
        (value) =>
          typeof value === 'string',
      )

  return firstFieldError || fallback
}

const requestPasswordReset = async () => {
  const normalizedEmail =
    email.value.trim()

  if (
    !normalizedEmail
    || isLoading.value
  ) {
    return
  }

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await authService.requestPasswordReset({
      email: normalizedEmail,
    })

    email.value = normalizedEmail

    successMessage.value =
      'If an account exists for this email, a password reset link has been sent.'
  } catch (error) {
    console.error(
      'Password reset request failed:',
      error,
    )

    errorMessage.value =
      getApiError(
        error,
        'Password reset request could not be completed.',
      )
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <main class="reset-page">
    <section class="reset-card">
      <div class="brand-line"></div>

      <div class="reset-content">
        <div class="logo-wrapper">
          <img
            src="/n2mobil_logo.png"
            alt="N2Mobil"
            class="logo"
          />
        </div>

        <div class="reset-heading">
          <h1>Forgot password?</h1>

          <p>
            Enter your email address and
            we'll send you a link to reset
            your password.
          </p>
        </div>

        <form
          class="reset-form"
          @submit.prevent="requestPasswordReset"
        >
          <div class="form-group">
            <label for="reset-email">
              Email
            </label>

            <div class="input-with-icon">
              <IconMail
                :size="18"
                :stroke-width="1.7"
              />

              <input
                id="reset-email"
                v-model="email"
                type="email"
                autocomplete="email"
                placeholder="Enter your email"
                required
              />
            </div>
          </div>

          <p
            v-if="successMessage"
            class="
              message
              message--success
            "
            role="status"
          >
            {{ successMessage }}
          </p>

          <p
            v-if="errorMessage"
            class="
              message
              message--error
            "
            role="alert"
          >
            {{ errorMessage }}
          </p>

          <button
            type="submit"
            class="primary-button"
            :disabled="
              isLoading
              || !email.trim()
            "
          >
            {{
              isLoading
                ? 'Sending...'
                : 'Send reset link'
            }}
          </button>
        </form>

        <button
          type="button"
          class="back-to-login"
          @click="
            router.push({
              name: 'login',
            })
          "
        >
          <IconArrowLeft
            :size="16"
            :stroke-width="1.8"
          />

          Back to sign in
        </button>
      </div>
    </section>
  </main>
</template>

<style scoped>
.reset-page {
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

.reset-card {
  width: 100%;
  max-width: 430px;

  overflow: hidden;

  background: #ffffff;

  border: 1px solid #e8eaf0;
  border-radius: 20px;

  box-shadow:
    0 20px 45px
      rgba(30, 39, 58, 0.08),
    0 3px 10px
      rgba(30, 39, 58, 0.04);
}

.brand-line {
  height: 5px;

  background:
    linear-gradient(
      90deg,
      var(--brand-pink),
      var(--brand-purple),
      var(--brand-blue)
    );
}

.reset-content {
  padding: 40px;
}

.logo-wrapper {
  display: flex;
  justify-content: center;

  margin-bottom: 28px;
}

.logo {
  width: 165px;
  max-width: 100%;

  height: auto;

  display: block;

  object-fit: contain;
}

.reset-heading {
  margin-bottom: 28px;

  text-align: center;
}

.reset-heading h1 {
  margin: 0 0 9px;

  color: #202632;

  font-size: 27px;
  font-weight: 700;

  letter-spacing: -0.4px;
}

.reset-heading p {
  margin: 0;

  color: #7a8291;

  font-size: 13px;
  line-height: 1.6;
}

.reset-form {
  display: flex;
  flex-direction: column;

  gap: 20px;
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
    box-shadow 0.2s ease;
}

.form-group input:focus {
  border-color: var(--brand-purple);

  box-shadow:
    0 0 0 3px
      rgba(140, 75, 181, 0.11);
}

.form-group input::placeholder {
  color: #a5abb5;
}

.input-with-icon {
  position: relative;
}

.input-with-icon svg {
  position: absolute;

  top: 50%;
  left: 14px;

  color: #8a92a0;

  transform: translateY(-50%);

  pointer-events: none;
}

.input-with-icon input {
  padding-left: 42px;
}

.message {
  margin: -4px 0 0;

  padding: 11px 13px;

  font-size: 13px;

  border-radius: 9px;
}

.message--error {
  color: #b42318;

  background: #fff3f2;

  border: 1px solid #ffd5d2;
}

.message--success {
  color: #18794e;

  background: #f0faf5;

  border: 1px solid #c7ead8;
}

.primary-button {
  min-height: 49px;

  display: flex;
  align-items: center;
  justify-content: center;

  color: #ffffff;

  font: inherit;
  font-size: 14px;
  font-weight: 600;

  background:
    linear-gradient(
      100deg,
      var(--brand-pink),
      var(--brand-purple),
      var(--brand-blue)
    );

  border: 0;
  border-radius: 10px;

  cursor: pointer;

  box-shadow:
    0 8px 18px
      rgba(123, 76, 173, 0.2);
}

.primary-button:disabled {
  cursor: not-allowed;

  opacity: 0.6;
}

.back-to-login {
  margin: 26px auto 0;

  display: flex;
  align-items: center;
  justify-content: center;

  gap: 6px;

  padding: 6px;

  color: #7a8291;

  font: inherit;
  font-size: 12px;
  font-weight: 600;

  background: transparent;

  border: 0;

  cursor: pointer;
}

.back-to-login:hover {
  color: var(--brand-purple);
}

@media (max-width: 520px) {
  .reset-page {
    padding: 20px 14px;
  }

  .reset-content {
    padding: 32px 24px;
  }

  .reset-card {
    border-radius: 16px;
  }

  .reset-heading h1 {
    font-size: 24px;
  }
  
}
</style>
<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import {
  IconArrowLeft,
  IconEye,
  IconEyeOff,
} from '@tabler/icons-vue'

import authService from '../services/authService'

const resetToken = ref(null)

const isRedeeming = ref(true)
const isLinkValid = ref(false)

const route = useRoute()
const router = useRouter()

const newPassword = ref('')
const confirmPassword = ref('')

const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const errorMessage = ref('')
const isLoading = ref(false)

const getApiError = (error, fallback) => {
  const data = error.response?.data

  if (!data) {
    return fallback
  }

  if (typeof data.detail === 'string') {
    return data.detail
  }

  if (
    Array.isArray(data.non_field_errors)
    && data.non_field_errors.length > 0
  ) {
    return data.non_field_errors[0]
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

const redeemResetLink = async () => {
  isRedeeming.value = true
  isLinkValid.value = false
  errorMessage.value = ''

  try {
    const response =
      await authService.redeemPasswordReset({
        uid: route.params.uid,
        token: route.params.token,
      })

    resetToken.value =
      response.data.reset_token

    isLinkValid.value = true
  } catch (error) {
    console.error(
      'Password reset link redemption failed:',
      error,
    )

    errorMessage.value = ''

  } finally {
    isRedeeming.value = false
  }
}

onMounted(() => {
  redeemResetLink()
})

const resetPassword = async () => {
  errorMessage.value = ''

  if (
    !newPassword.value
    || !confirmPassword.value
  ) {
    errorMessage.value =
      'Please enter and confirm your new password.'

    return
  }

  if (
    newPassword.value
    !== confirmPassword.value
  ) {
    errorMessage.value =
      'Passwords do not match.'

    return
  }

  if (isLoading.value) {
    return
  }

  if (
  !isLinkValid.value
  || !resetToken.value
) {
  errorMessage.value =
    'This password reset session is invalid or has expired.'

  return
}

  isLoading.value = true

  try {
    await authService.confirmPasswordReset({
  resetToken: resetToken.value,
  newPassword: newPassword.value,
  newPasswordConfirm:
    confirmPassword.value,
})

    await router.replace({
      name: 'login',
      query: {
        passwordReset: 'success',
      },
    })
  } catch (error) {
    console.error(
      'Password reset confirmation failed:',
      error,
    )

    errorMessage.value =
      getApiError(
        error,
        'Password could not be reset. The reset link may be invalid or expired.',
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
          <template v-if="isRedeeming">
            <h1>Checking link</h1>

            <p>
              Please wait while we verify
              your password reset link.
            </p>
          </template>

          <template v-else-if="isLinkValid">
            <h1>Reset password</h1>

            <p>
              Choose a new password for
              your account.
            </p>
          </template>

          <template v-else>
            <h1>Link expired or already used</h1>

            <p>
              This password reset link is
              no longer valid. Please request
              a new link to reset your password.
            </p>
          </template>
        </div>
        <form
          v-if="isLinkValid"
          class="reset-form"
          @submit.prevent="resetPassword"
        >
          <div class="form-group">
            <label for="new-password">
              New password
            </label>

            <div class="password-input">
              <input
                id="new-password"
                v-model="newPassword"
                :type="
                  showNewPassword
                    ? 'text'
                    : 'password'
                "
                autocomplete="new-password"
                placeholder="Enter new password"
                required
              />

              <button
                type="button"
                class="password-toggle"
                :title="
                  showNewPassword
                    ? 'Hide password'
                    : 'Show password'
                "
                @click="
                  showNewPassword =
                    !showNewPassword
                "
              >
                <IconEyeOff
                  v-if="showNewPassword"
                  :size="20"
                  :stroke-width="1.8"
                />

                <IconEye
                  v-else
                  :size="20"
                  :stroke-width="1.8"
                />
              </button>
            </div>
          </div>

          <div class="form-group">
            <label for="confirm-password">
              Confirm password
            </label>

            <div class="password-input">
              <input
                id="confirm-password"
                v-model="confirmPassword"
                :type="
                  showConfirmPassword
                    ? 'text'
                    : 'password'
                "
                autocomplete="new-password"
                placeholder="Enter password again"
                required
              />

              <button
                type="button"
                class="password-toggle"
                :title="
                  showConfirmPassword
                    ? 'Hide password'
                    : 'Show password'
                "
                @click="
                  showConfirmPassword =
                    !showConfirmPassword
                "
              >
                <IconEyeOff
                  v-if="showConfirmPassword"
                  :size="20"
                  :stroke-width="1.8"
                />

                <IconEye
                  v-else
                  :size="20"
                  :stroke-width="1.8"
                />
              </button>
            </div>
          </div>

          <p
            v-if="errorMessage"
            class="message message--error"
            role="alert"
          >
            {{ errorMessage }}
          </p>

          <button
            type="submit"
            class="primary-button"
            :disabled="
              isLoading
              || !newPassword
              || !confirmPassword
            "
          >
            {{
              isLoading
                ? 'Resetting...'
                : 'Reset password'
            }}
          </button>
        </form>
        <button
          v-if="
            !isRedeeming
            && !isLinkValid
          "
          type="button"
          class="primary-button"
          @click="
            router.push({
              name: 'forgot-password',
            })
          "
        >
          Request a new reset link
        </button>
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

  width: 28px;
  height: 28px;

  display: flex;
  align-items: center;
  justify-content: center;

  padding: 0;

  color: #737b89;

  background: transparent;

  border: 0;
  border-radius: 6px;

  cursor: pointer;

  transform: translateY(-50%);
}

.password-toggle:hover {
  color: var(--brand-purple);
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

.primary-button {
  min-height: 49px;
  
  margin: 0 auto;
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

.retry-button {
  width: fit-content;
  margin: 0 auto;
  padding: 0 24px;
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
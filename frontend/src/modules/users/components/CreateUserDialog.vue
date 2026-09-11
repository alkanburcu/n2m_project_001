<script setup>
import {
  reactive,
  ref,
} from 'vue'

import {
  IconUserPlus,
  IconX,
} from '@tabler/icons-vue'

import { useUserStore } from '../store/userStore'


defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits([
  'update:modelValue',
  'created',
])

const userStore = useUserStore()

const isCreating = ref(false)
const errorMessage = ref('')

const form = reactive({
  username: '',
  email: '',
  password: '',
  passwordConfirm: '',
})


const resetForm = () => {
  form.username = ''
  form.email = ''
  form.password = ''
  form.passwordConfirm = ''

  errorMessage.value = ''
}


const close = () => {
  if (isCreating.value) {
    return
  }

  emit(
    'update:modelValue',
    false,
  )

  resetForm()
}


const createUser = async () => {
  errorMessage.value = ''

  if (
    !form.username.trim()
    || !form.email.trim()
    || !form.password
    || !form.passwordConfirm
  ) {
    errorMessage.value =
      'All fields are required.'

    return
  }

  if (
    form.password
    !== form.passwordConfirm
  ) {
    errorMessage.value =
      'Passwords do not match.'

    return
  }

  isCreating.value = true

  try {
    const user =
      await userStore.createUser({
        username: form.username.trim(),
        email: form.email.trim(),
        password: form.password,
        password_confirm:
          form.passwordConfirm,
      })

    emit(
      'created',
      user,
    )

    emit(
      'update:modelValue',
      false,
    )

    resetForm()
  } catch (error) {
    const data =
      error.response?.data

    errorMessage.value =
      data?.username?.[0]
      ?? data?.email?.[0]
      ?? data?.password?.[0]
      ?? data?.password_confirm?.[0]
      ?? data?.detail
      ?? 'User could not be created.'
  } finally {
    isCreating.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="user-dialog-backdrop"
      @click.self="close"
    >
      <section
        class="user-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="user-dialog-title"
      >
        <header class="user-dialog__header">
          <div class="user-dialog__title">
            <div class="user-dialog__icon">
              <IconUserPlus
                :size="19"
                :stroke-width="1.8"
              />
            </div>

            <div>
              <h2 id="user-dialog-title">
                Create user
              </h2>

              <p>
                Create a new account and
                assign an initial password.
              </p>
            </div>
          </div>

          <button
            type="button"
            class="user-dialog__close"
            aria-label="Close"
            :disabled="isCreating"
            @click="close"
          >
            <IconX
              :size="18"
              :stroke-width="1.8"
            />
          </button>
        </header>

        <form
          class="user-dialog__form"
          @submit.prevent="createUser"
        >
          <label class="dialog-field">
            <span>Username</span>

            <input
              v-model="form.username"
              type="text"
              autocomplete="off"
              placeholder="username"
              required
            >
          </label>

          <label class="dialog-field">
            <span>Email</span>

            <input
              v-model="form.email"
              type="email"
              autocomplete="email"
              placeholder="user@example.com"
              required
            >
          </label>

          <div class="dialog-grid">
            <label class="dialog-field">
              <span>Password</span>

              <input
                v-model="form.password"
                type="password"
                autocomplete="new-password"
                required
              >
            </label>

            <label class="dialog-field">
              <span>Confirm password</span>

              <input
                v-model="form.passwordConfirm"
                type="password"
                autocomplete="new-password"
                required
              >
            </label>
          </div>

          <div
            v-if="errorMessage"
            class="user-dialog__error"
          >
            {{ errorMessage }}
          </div>

          <footer class="user-dialog__actions">
            <button
              type="button"
              class="
                dialog-button
                dialog-button--secondary
              "
              :disabled="isCreating"
              @click="close"
            >
              Cancel
            </button>

            <button
              type="submit"
              class="
                dialog-button
                dialog-button--primary
              "
              :disabled="isCreating"
            >
              <IconUserPlus
                :size="16"
                :stroke-width="1.9"
              />

              {{
                isCreating
                  ? 'Creating...'
                  : 'Create user'
              }}
            </button>
          </footer>
        </form>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.user-dialog-backdrop {
  position: fixed;
  inset: 0;

  z-index: 100;

  display: grid;
  place-items: center;

  padding: 24px;

  background:
    rgba(31, 36, 49, 0.32);
}

.user-dialog {
  width: min(100%, 520px);

  overflow: hidden;

  background: #ffffff;

  border:
    1px solid var(--color-border);

  border-radius: 14px;

  box-shadow:
    0 24px 60px
    rgba(31, 36, 49, 0.18);
}

.user-dialog__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;

  padding: 20px 22px;

  border-bottom:
    1px solid var(--color-border);
}

.user-dialog__title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-dialog__icon {
  width: 38px;
  height: 38px;

  flex-shrink: 0;

  display: grid;
  place-items: center;

  color: var(--color-primary);

  background:
    rgba(82, 63, 158, 0.07);

  border-radius: 9px;
}

.user-dialog__title h2 {
  margin: 0;

  color: var(--color-title);

  font-size: 16px;
  font-weight: 650;
}

.user-dialog__title p {
  margin: 4px 0 0;

  color: var(--color-subtitle);

  font-size: 12.5px;
}

.user-dialog__close {
  display: grid;
  place-items: center;

  padding: 6px;

  color: var(--color-subtitle);

  background: transparent;
  border: 0;
  border-radius: 7px;

  cursor: pointer;
}

.user-dialog__close:hover {
  color: var(--color-title);

  background: #f5f5f5;
}

.user-dialog__close:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.user-dialog__form {
  display: flex;
  flex-direction: column;
  gap: 16px;

  padding: 22px;
}

.dialog-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.dialog-field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.dialog-field span {
  color: var(--color-title);

  font-size: 12.5px;
  font-weight: 600;
}

.dialog-field input {
  height: 40px;

  box-sizing: border-box;

  padding: 0 11px;

  color: var(--color-title);

  font: inherit;
  font-size: 13px;

  background: #ffffff;

  border:
    1px solid var(--color-border);

  border-radius: 8px;

  outline: none;
}

.dialog-field input:focus {
  border-color:
    rgba(82, 63, 158, 0.48);

  box-shadow:
    0 0 0 3px
    rgba(82, 63, 158, 0.08);
}

.user-dialog__error {
  padding: 10px 12px;

  color: #b42318;

  font-size: 12.5px;

  background: #fff3f2;

  border-radius: 8px;
}

.user-dialog__actions {
  display: flex;
  justify-content: flex-end;
  gap: 9px;

  padding-top: 4px;
}

.dialog-button {
  height: 37px;

  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;

  padding: 0 14px;

  font: inherit;
  font-size: 12.5px;
  font-weight: 600;

  border-radius: 8px;

  cursor: pointer;
}

.dialog-button--secondary {
  color: var(--color-subtitle);

  background: #ffffff;

  border:
    1px solid var(--color-border);
}

.dialog-button--primary {
  color: #ffffff;

  background: var(--color-primary);

  border:
    1px solid var(--color-primary);
}

.dialog-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 600px) {
  .dialog-grid {
    grid-template-columns: 1fr;
  }
}
</style>
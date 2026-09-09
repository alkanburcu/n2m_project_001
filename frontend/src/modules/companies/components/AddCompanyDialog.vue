<script setup>
import {
  reactive,
  ref,
} from 'vue'

import {
  IconBuilding,
  IconPlus,
  IconX,
} from '@tabler/icons-vue'

import { useCompanyStore } from '../store/companyStore'


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

const companyStore = useCompanyStore()

const errorMessage = ref('')

const form = reactive({
  name: '',
  address: '',
  city: '',
  phoneNumber: '',
  website: '',
})


const resetForm = () => {
  form.name = ''
  form.address = ''
  form.city = ''
  form.phoneNumber = ''
  form.website = ''

  errorMessage.value = ''
}


const close = () => {
  emit(
    'update:modelValue',
    false,
  )

  resetForm()
}


const createCompany = async () => {
  errorMessage.value = ''

  if (!form.name.trim()) {
    errorMessage.value =
      'Company name is required.'

    return
  }

  try {
    const company =
      await companyStore.createCompany({
        name: form.name.trim(),
        address: form.address.trim(),
        city: form.city.trim(),
        phone_number:
          form.phoneNumber.trim(),
        website: form.website.trim(),
      })

    emit(
      'created',
      company,
    )

    close()
  } catch (error) {
    errorMessage.value =
      error.response?.data?.name?.[0]
      ?? error.response?.data?.website?.[0]
      ?? 'Company could not be created.'
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="company-dialog-backdrop"
      @click.self="close"
    >
      <section
        class="company-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="company-dialog-title"
      >
        <header class="company-dialog__header">
          <div class="company-dialog__title">
            <div class="company-dialog__icon">
              <IconBuilding
                :size="19"
                :stroke-width="1.8"
              />
            </div>

            <div>
              <h2 id="company-dialog-title">
                Add company
              </h2>

              <p>
                Create a new workplace
                to use on your profile.
              </p>
            </div>
          </div>

          <button
            type="button"
            class="company-dialog__close"
            aria-label="Close"
            @click="close"
          >
            <IconX
              :size="18"
              :stroke-width="1.8"
            />
          </button>
        </header>

        <form
          class="company-dialog__form"
          @submit.prevent="createCompany"
        >
          <label class="dialog-field">
            <span>Company name</span>

            <input
              v-model="form.name"
              type="text"
              required
              placeholder="N2Mobil"
            >
          </label>

          <div class="dialog-grid">
            <label class="dialog-field">
              <span>City</span>

              <input
                v-model="form.city"
                type="text"
                placeholder="Ankara"
              >
            </label>

            <label class="dialog-field">
              <span>Phone</span>

              <input
                v-model="form.phoneNumber"
                type="tel"
                placeholder="+90 ..."
              >
            </label>
          </div>

          <label class="dialog-field">
            <span>Address</span>

            <input
              v-model="form.address"
              type="text"
              placeholder="Company address"
            >
          </label>

          <label class="dialog-field">
            <span>Website</span>

            <input
              v-model="form.website"
              type="url"
              placeholder="https://example.com"
            >
          </label>

          <div
            v-if="errorMessage"
            class="company-dialog__error"
          >
            {{ errorMessage }}
          </div>

          <footer class="company-dialog__actions">
            <button
              type="button"
              class="dialog-button dialog-button--secondary"
              :disabled="companyStore.isCreating"
              @click="close"
            >
              Cancel
            </button>

            <button
              type="submit"
              class="dialog-button dialog-button--primary"
              :disabled="companyStore.isCreating"
            >
              <IconPlus
                :size="16"
                :stroke-width="1.9"
              />

              {{
                companyStore.isCreating
                  ? 'Creating...'
                  : 'Add company'
              }}
            </button>
          </footer>
        </form>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.company-dialog-backdrop {
  position: fixed;
  inset: 0;

  z-index: 100;

  display: grid;
  place-items: center;

  padding: 24px;

  background:
    rgba(31, 36, 49, 0.32);
}

.company-dialog {
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

.company-dialog__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;

  padding: 20px 22px;

  border-bottom:
    1px solid var(--color-border);
}

.company-dialog__title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.company-dialog__icon {
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

.company-dialog__title h2 {
  margin: 0;

  color: var(--color-title);

  font-size: 16px;
  font-weight: 650;
}

.company-dialog__title p {
  margin: 4px 0 0;

  color: var(--color-subtitle);

  font-size: 12.5px;
}

.company-dialog__close {
  display: grid;
  place-items: center;

  padding: 6px;

  color: var(--color-subtitle);

  background: transparent;
  border: 0;
  border-radius: 7px;

  cursor: pointer;
}

.company-dialog__close:hover {
  color: var(--color-title);

  background: #f5f5f5;
}

.company-dialog__form {
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

.company-dialog__error {
  padding: 10px 12px;

  color: #b42318;

  font-size: 12.5px;

  background: #fff3f2;

  border-radius: 8px;
}

.company-dialog__actions {
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

  border: 1px solid var(--color-primary);
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
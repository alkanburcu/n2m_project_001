<script setup>
import {
  onBeforeUnmount,
  onMounted,
  reactive,
  ref,
} from 'vue'

import {
  IconCamera,
  IconDeviceFloppy,
  IconUser,
} from '@tabler/icons-vue'

import { useProfileStore } from '../store/profileStore'
import CompanySelect from '@/modules/companies/components/CompanySelect.vue'
import AddCompanyDialog from '@/modules/companies/components/AddCompanyDialog.vue'

const profileStore = useProfileStore()

const form = reactive({
  firstName: '',
  lastName: '',
  location: '',
  website: '',
  companyId: null,
})

const selectedPhoto = ref(null)
const photoPreview = ref(null)

const successMessage = ref('')
const validationError = ref('')

const isCompanyDialogOpen = ref(false)
const handleCompanyCreated = (company) => {
  form.companyId = company.id
}


const populateForm = (profile) => {
  form.firstName =
    profile?.first_name ?? ''

  form.lastName =
    profile?.last_name ?? ''

  form.location =
    profile?.location ?? ''

  form.website =
    profile?.website ?? ''

  form.companyId =
    profile?.company?.id ?? null
}


const loadProfile = async () => {
  const profile =
    await profileStore.fetchProfile()

  populateForm(profile)
}


const handlePhotoChange = (event) => {
  const file =
    event.target.files?.[0]

  if (!file) {
    return
  }

  if (photoPreview.value) {
    URL.revokeObjectURL(
      photoPreview.value,
    )
  }

  selectedPhoto.value = file

  photoPreview.value =
    URL.createObjectURL(file)
}


const saveProfile = async () => {
  successMessage.value = ''
  validationError.value = ''

  try {
    await profileStore.updateProfile({
      first_name: form.firstName,
      last_name: form.lastName,
      location: form.location,
      website: form.website,
      company_id: form.companyId,
    })

    if (selectedPhoto.value) {
      await profileStore.updateProfilePhoto(
        selectedPhoto.value,
      )

      selectedPhoto.value = null
    }

    successMessage.value =
      'Profile updated successfully.'
  } catch (error) {
    validationError.value =
      error.response?.data?.profile_photo?.[0]
      ?? error.response?.data?.website?.[0]
      ?? 'Profile could not be updated.'
  }
}


onMounted(() => {
  loadProfile()
})


onBeforeUnmount(() => {
  if (photoPreview.value) {
    URL.revokeObjectURL(
      photoPreview.value,
    )
  }
})


</script>

<template>
  <main class="profile-page">
    <div class="profile-page__container">
      <header class="profile-heading">
        <div>
          <p class="profile-heading__eyebrow">
            Account
          </p>

          <h1>Profile</h1>

          <p class="profile-heading__description">
            Manage your personal information
            and profile details.
          </p>
        </div>
      </header>

      <div
        v-if="profileStore.isLoading"
        class="profile-state"
      >
        Loading profile...
      </div>

      <form
        v-else
        class="profile-card"
        @submit.prevent="saveProfile"
      >
        <section class="photo-section">
          <div class="avatar">
            <img
              v-if="
                photoPreview
                || profileStore.profile?.profile_photo
              "
              :src="
                photoPreview
                || profileStore.profile.profile_photo
              "
              alt="Profile photo"
              class="avatar__image"
            >

            <IconUser
              v-else
              :size="42"
              :stroke-width="1.4"
            />
          </div>

          <div class="photo-section__content">
            <h2>Profile photo</h2>

            <p>
              Choose an image for your profile.
            </p>

            <label
              class="photo-button"
              for="profile-photo"
            >
              <IconCamera
                :size="17"
                :stroke-width="1.8"
              />

              Change photo
            </label>

            <input
              id="profile-photo"
              class="photo-input"
              type="file"
              accept="image/*"
              @change="handlePhotoChange"
            >
          </div>
        </section>

        <div class="profile-divider" />

        <section class="form-section">
          <div class="form-section__heading">
            <h2>Personal information</h2>

            <p>
              Update the information displayed
              on your profile.
            </p>
          </div>

          <div class="form-grid">
            <label class="form-field">
              <span>First name</span>

              <input
                v-model="form.firstName"
                type="text"
                autocomplete="given-name"
              >
            </label>

            <label class="form-field">
              <span>Last name</span>

              <input
                v-model="form.lastName"
                type="text"
                autocomplete="family-name"
              >
            </label>

            <label
              class="form-field form-field--wide"
            >
              <span>Location</span>

              <input
                v-model="form.location"
                type="text"
                placeholder="Ankara, Türkiye"
              >
            </label>

            <label
              class="form-field form-field--wide"
            >
              <span>Website</span>

              <input
                v-model="form.website"
                type="url"
                placeholder="https://example.com"
              >
            </label>

            <div
            class="
                form-field
                form-field--wide
            "
            >
            <span>Company</span>

            <CompanySelect
            v-model="form.companyId"
            :initial-company="
                profileStore.profile?.company
            "
            @add-company="
                isCompanyDialogOpen = true
            "
            />
            </div>
          </div>
        </section>

        <div
          v-if="validationError"
          class="form-message form-message--error"
        >
          {{ validationError }}
        </div>

        <div
          v-if="successMessage"
          class="form-message form-message--success"
        >
          {{ successMessage }}
        </div>

        <footer class="profile-actions">
          <button
            type="submit"
            class="save-button"
            :disabled="profileStore.isSaving"
          >
            <IconDeviceFloppy
              :size="17"
              :stroke-width="1.8"
            />

            {{
              profileStore.isSaving
                ? 'Saving...'
                : 'Save changes'
            }}
          </button>
        </footer>
      </form>
      <AddCompanyDialog
    v-model="isCompanyDialogOpen"
    @created="handleCompanyCreated"
    />
    </div>
  </main>
</template>

<style scoped>
.profile-page {
  min-height: 100%;
  padding: 34px;
}

.profile-page__container {
  width: min(100%, 860px);
  margin: 0 auto;
}

.profile-heading {
  margin-bottom: 22px;
}

.profile-heading__eyebrow {
  margin: 0 0 5px;

  color: var(--color-primary);

  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.profile-heading h1 {
  margin: 0;

  color: var(--color-title);

  font-size: 27px;
  font-weight: 700;
}

.profile-heading__description {
  margin: 7px 0 0;

  color: var(--color-subtitle);

  font-size: 14px;
}

.profile-card {
  padding: 28px;

  background: #ffffff;

  border: 1px solid var(--color-border);
  border-radius: 14px;

  box-shadow:
    0 5px 18px rgba(31, 36, 49, 0.045);
}

.photo-section {
  display: flex;
  align-items: center;
  gap: 22px;
}

.avatar {
  width: 92px;
  height: 92px;

  flex-shrink: 0;

  display: flex;
  align-items: center;
  justify-content: center;

  overflow: hidden;

  color: var(--color-primary);

  background:
    rgba(82, 63, 158, 0.07);

  border:
    1px solid rgba(82, 63, 158, 0.12);

  border-radius: 50%;
}

.avatar__image {
  width: 100%;
  height: 100%;

  object-fit: cover;
}

.photo-section__content h2,
.form-section__heading h2 {
  margin: 0;

  color: var(--color-title);

  font-size: 16px;
  font-weight: 650;
}

.photo-section__content p,
.form-section__heading p {
  margin: 5px 0 13px;

  color: var(--color-subtitle);

  font-size: 13px;
}

.photo-button {
  display: inline-flex;
  align-items: center;
  gap: 7px;

  padding: 8px 11px;

  color: var(--color-primary);

  font-size: 12.5px;
  font-weight: 600;

  background:
    rgba(82, 63, 158, 0.06);

  border:
    1px solid rgba(82, 63, 158, 0.14);

  border-radius: 8px;

  cursor: pointer;
}

.photo-input {
  display: none;
}

.profile-divider {
  height: 1px;

  margin: 27px 0;

  background: var(--color-border);
}

.form-section__heading {
  margin-bottom: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.form-field--wide {
  grid-column: 1 / -1;
}

.form-field > span {
  color: var(--color-title);

  font-size: 12.5px;
  font-weight: 600;
}

.form-field input {
  height: 40px;

  box-sizing: border-box;

  padding: 0 11px;

  color: var(--color-title);

  font: inherit;
  font-size: 13.5px;

  background: #ffffff;

  border: 1px solid var(--color-border);
  border-radius: 8px;

  outline: none;

  transition:
    border-color 0.18s ease,
    box-shadow 0.18s ease;
}

.form-field input:focus {
  border-color:
    rgba(82, 63, 158, 0.48);

  box-shadow:
    0 0 0 3px
    rgba(82, 63, 158, 0.08);
}

.company-placeholder {
  min-height: 40px;

  display: flex;
  align-items: center;

  padding: 0 11px;

  color: var(--color-subtitle);

  font-size: 13.5px;

  background: #fafafa;

  border: 1px solid var(--color-border);
  border-radius: 8px;
}

.form-field small {
  color: var(--color-subtitle);

  font-size: 11.5px;
}

.form-message {
  margin-top: 20px;
  padding: 10px 12px;

  font-size: 12.5px;

  border-radius: 8px;
}

.form-message--error {
  color: #b42318;
  background: #fff3f2;
}

.form-message--success {
  color: #067647;
  background: #ecfdf3;
}

.profile-actions {
  display: flex;
  justify-content: flex-end;

  margin-top: 26px;
}

.save-button {
  height: 38px;

  display: inline-flex;
  align-items: center;
  gap: 7px;

  padding: 0 15px;

  color: #ffffff;

  font: inherit;
  font-size: 13px;
  font-weight: 600;

  background: var(--color-primary);

  border: 0;
  border-radius: 8px;

  cursor: pointer;
}

.save-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.profile-state {
  padding: 28px;

  color: var(--color-subtitle);

  background: #ffffff;

  border: 1px solid var(--color-border);
  border-radius: 14px;
}

@media (max-width: 700px) {
  .profile-page {
    padding: 20px;
  }

  .profile-card {
    padding: 20px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-field--wide {
    grid-column: auto;
  }
}
</style>
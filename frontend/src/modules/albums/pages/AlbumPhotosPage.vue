<script setup>
import {
  onBeforeUnmount,
  ref,
  watch,
} from 'vue'

import {
  useRoute,
  useRouter,
} from 'vue-router'

import {
  IconArrowLeft,
  IconPencil,
  IconPhotoPlus,
  IconTrash,
  IconUpload,
  IconX,
} from '@tabler/icons-vue'

import { useAuthStore } from '@/modules/auth/store/authStore'
import albumService from '../services/albumService'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const album = ref(null)
const photos = ref([])

const isLoading = ref(false)
const errorMessage = ref('')

/* -------------------------
   CREATE STATE
------------------------- */

const isCreateOpen = ref(false)
const isCreating = ref(false)

const newPhotoTitle = ref('')
const newPhotoFile = ref(null)
const newPhotoPreview = ref(null)

const createFileInput = ref(null)

/* -------------------------
   EDIT STATE
------------------------- */

const editingPhotoId = ref(null)
const editPhotoTitle = ref('')

const editPhotoFile = ref(null)
const editPhotoPreview = ref(null)

const editFileInput = ref(null)

const updatingPhotoIds = ref([])
const deletingPhotoIds = ref([])

/* -------------------------
   PREVIEW HELPERS
------------------------- */

const revokePreview = (previewUrl) => {
  if (
    previewUrl
    && previewUrl.startsWith('blob:')
  ) {
    URL.revokeObjectURL(previewUrl)
  }
}

const isImageFile = (file) => {
  return Boolean(
    file
    && file.type
    && file.type.startsWith('image/'),
  )
}

/* -------------------------
   FETCH
------------------------- */

let pageRequestId = 0

const loadAlbumPage = async (albumId) => {
  const requestId = ++pageRequestId

  isLoading.value = true
  errorMessage.value = ''

  try {
    const [
      albumResponse,
      photosResponse,
    ] = await Promise.all([
      albumService.getAlbumById(albumId),
      albumService.getPhotosByAlbum(
        albumId,
      ),
    ])

    if (requestId !== pageRequestId) {
      return
    }

    album.value = albumResponse.data
    photos.value = photosResponse.data
  } catch (error) {
    if (requestId !== pageRequestId) {
      return
    }

    console.error(
      'Failed to load album:',
      error,
    )

    errorMessage.value =
      'Album could not be loaded.'
  } finally {
    if (requestId === pageRequestId) {
      isLoading.value = false
    }
  }
}

/* -------------------------
   CREATE FILE
------------------------- */

const setCreateFile = (file) => {
  revokePreview(
    newPhotoPreview.value,
  )

  newPhotoFile.value = null
  newPhotoPreview.value = null

  if (!file) {
    return
  }

  if (!isImageFile(file)) {
    errorMessage.value =
      'Please select a valid image file.'

    return
  }

  errorMessage.value = ''

  newPhotoFile.value = file
  newPhotoPreview.value =
    URL.createObjectURL(file)
}

const openCreateFilePicker = () => {
  createFileInput.value?.click()
}

const handleCreateFileChange = (
  event,
) => {
  const file =
    event.target.files?.[0]

  if (file) {
    setCreateFile(file)
  }

  /*
   * Aynı dosyayı tekrar seçebilmek için
   * input değerini temizliyoruz.
   */
  event.target.value = ''
}

const handleCreateDrop = (event) => {
  const file =
    event.dataTransfer.files?.[0]

  if (file) {
    setCreateFile(file)
  }
}

const clearCreateFile = () => {
  setCreateFile(null)
}

/* -------------------------
   CREATE PHOTO
------------------------- */

const openCreatePhoto = () => {
  cancelEditing()

  isCreateOpen.value = true
  errorMessage.value = ''
}

const closeCreatePhoto = () => {
  revokePreview(
    newPhotoPreview.value,
  )

  isCreateOpen.value = false

  newPhotoTitle.value = ''
  newPhotoFile.value = null
  newPhotoPreview.value = null

  if (createFileInput.value) {
    createFileInput.value.value = ''
  }
}

const createPhoto = async () => {
  const title =
    newPhotoTitle.value.trim()

  if (
    !title
    || !newPhotoFile.value
    || isCreating.value
    || !authStore.can('photos.create')
  ) {
    return
  }

  isCreating.value = true
  errorMessage.value = ''

  try {
    const response =
      await albumService.createPhoto({
        album: route.params.albumId,
        title,
        image: newPhotoFile.value,
      })

    photos.value.push(response.data)

    closeCreatePhoto()
  } catch (error) {
    console.error(
      'Failed to create photo:',
      error,
    )

    errorMessage.value =
      'Photo could not be uploaded.'
  } finally {
    isCreating.value = false
  }
}

/* -------------------------
   EDIT FILE
------------------------- */

const setEditFile = (file) => {
  revokePreview(
    editPhotoPreview.value,
  )

  editPhotoFile.value = null
  editPhotoPreview.value = null

  if (!file) {
    return
  }

  if (!isImageFile(file)) {
    errorMessage.value =
      'Please select a valid image file.'

    return
  }

  errorMessage.value = ''

  editPhotoFile.value = file
  editPhotoPreview.value =
    URL.createObjectURL(file)
}

const openEditFilePicker = () => {
  editFileInput.value?.click()
}

const handleEditFileChange = (
  event,
) => {
  const file =
    event.target.files?.[0]

  if (file) {
    setEditFile(file)
  }

  event.target.value = ''
}

const handleEditDrop = (event) => {
  const file =
    event.dataTransfer.files?.[0]

  if (file) {
    setEditFile(file)
  }
}

/* -------------------------
   EDIT PHOTO
------------------------- */

const startEditing = (photo) => {
  closeCreatePhoto()
  cancelEditing()

  editingPhotoId.value = photo.id
  editPhotoTitle.value = photo.title
}

const cancelEditing = () => {
  revokePreview(
    editPhotoPreview.value,
  )

  editingPhotoId.value = null

  editPhotoTitle.value = ''
  editPhotoFile.value = null
  editPhotoPreview.value = null

  if (editFileInput.value) {
    editFileInput.value.value = ''
  }
}

const updatePhoto = async (photo) => {
  const title =
    editPhotoTitle.value.trim()

  if (
    !title
    || updatingPhotoIds.value.includes(
      photo.id,
    )
    || !authStore.can('photos.update')
  ) {
    return
  }

  const titleChanged =
    title !== photo.title

  const imageChanged =
    Boolean(editPhotoFile.value)

  if (
    !titleChanged
    && !imageChanged
  ) {
    cancelEditing()

    return
  }

  updatingPhotoIds.value.push(
    photo.id,
  )

  errorMessage.value = ''

  try {
    const payload = {
      title,
    }

    /*
     * Yeni görsel seçilmediyse image
     * request'e hiç eklenmiyor.
     */
    if (editPhotoFile.value) {
      payload.image =
        editPhotoFile.value
    }

    const response =
      await albumService.updatePhoto(
        photo.id,
        payload,
      )

    const index =
      photos.value.findIndex(
        (item) =>
          item.id === photo.id,
      )

    if (index !== -1) {
      photos.value[index] =
        response.data
    }

    cancelEditing()
  } catch (error) {
    console.error(
      'Failed to update photo:',
      error,
    )

    errorMessage.value =
      'Photo could not be updated.'
  } finally {
    updatingPhotoIds.value =
      updatingPhotoIds.value.filter(
        (id) => id !== photo.id,
      )
  }
}

/* -------------------------
   DELETE
------------------------- */

const deletePhoto = async (
  photoId,
) => {
  if (
    deletingPhotoIds.value.includes(
      photoId,
    )
    || !authStore.can('photos.delete')
  ) {
    return
  }

  deletingPhotoIds.value.push(
    photoId,
  )

  errorMessage.value = ''

  try {
    await albumService.deletePhoto(
      photoId,
    )

    photos.value =
      photos.value.filter(
        (photo) =>
          photo.id !== photoId,
      )

    if (
      editingPhotoId.value
      === photoId
    ) {
      cancelEditing()
    }
  } catch (error) {
    console.error(
      'Failed to delete photo:',
      error,
    )

    errorMessage.value =
      'Photo could not be deleted.'
  } finally {
    deletingPhotoIds.value =
      deletingPhotoIds.value.filter(
        (id) => id !== photoId,
      )
  }
}

/* -------------------------
   NAVIGATION
------------------------- */

const goBack = () => {
  router.push({
    name: 'user-albums',

    params: {
      id: route.params.id,
    },
  })
}

/* -------------------------
   HELPERS
------------------------- */

const isUpdating = (
  photoId,
) => {
  return updatingPhotoIds.value.includes(
    photoId,
  )
}

const isDeleting = (
  photoId,
) => {
  return deletingPhotoIds.value.includes(
    photoId,
  )
}

/* -------------------------
   ROUTE
------------------------- */

watch(
  () => route.params.albumId,
  (albumId) => {
    if (!albumId) {
      return
    }

    album.value = null
    photos.value = []

    closeCreatePhoto()
    cancelEditing()

    loadAlbumPage(albumId)
  },
  {
    immediate: true,
  },
)

onBeforeUnmount(() => {
  revokePreview(
    newPhotoPreview.value,
  )

  revokePreview(
    editPhotoPreview.value,
  )
})
</script>

<template>
  <section class="photos-page">
    <!-- HEADER -->

    <div class="photos-header">
      <div>
        <button
          type="button"
          class="back-button"
          @click="goBack"
        >
          <IconArrowLeft
            :size="17"
            :stroke-width="1.8"
          />

          Albums
        </button>

        <h1>
          {{ album?.title || 'Album' }}
        </h1>
      </div>

      <button
        v-if="
          authStore.can('photos.create')
          && !isCreateOpen
        "
        type="button"
        class="new-photo-button"
        @click="openCreatePhoto"
      >
        <IconPhotoPlus
          :size="18"
          :stroke-width="1.8"
        />

        Add Photo
      </button>
    </div>

    <!-- ERROR -->

    <p
      v-if="errorMessage"
      class="
        page-state
        page-state--error
      "
    >
      {{ errorMessage }}
    </p>

    <!-- CREATE -->

    <form
      v-if="isCreateOpen"
      class="photo-create"
      @submit.prevent="createPhoto"
    >
      <button
        type="button"
        class="drop-zone"
        @click="openCreateFilePicker"
        @dragover.prevent
        @drop.prevent="
          handleCreateDrop
        "
      >
        <img
          v-if="newPhotoPreview"
          :src="newPhotoPreview"
          alt="Selected image preview"
          class="drop-zone__preview"
        />

        <template v-else>
          <IconUpload
            :size="28"
            :stroke-width="1.5"
          />

          <strong>
            Drop an image here
          </strong>

          <span>
            or choose a file
          </span>
        </template>
      </button>

      <input
        ref="createFileInput"
        type="file"
        accept="image/*"
        class="hidden-file-input"
        @change="
          handleCreateFileChange
        "
      />

      <div
        v-if="newPhotoFile"
        class="selected-file"
      >
        <span>
          {{ newPhotoFile.name }}
        </span>

        <button
          type="button"
          aria-label="Remove selected image"
          @click="clearCreateFile"
        >
          <IconX
            :size="15"
            :stroke-width="1.8"
          />
        </button>
      </div>

      <input
        v-model="newPhotoTitle"
        type="text"
        class="photo-input"
        placeholder="Photo title"
        maxlength="200"
        autocomplete="off"
      />

      <div class="form-actions">
        <button
          type="button"
          class="text-button"
          @click="closeCreatePhoto"
        >
          Cancel
        </button>

        <button
          type="submit"
          class="primary-button"
          :disabled="
            isCreating
            || !newPhotoTitle.trim()
            || !newPhotoFile
          "
        >
          {{
            isCreating
              ? 'Uploading...'
              : 'Add Photo'
          }}
        </button>
      </div>
    </form>

    <!--
      Tek bir edit file input.
      Artık v-for içinde değil.
    -->

    <input
      ref="editFileInput"
      type="file"
      accept="image/*"
      class="hidden-file-input"
      @change="
        handleEditFileChange
      "
    />

    <!-- STATES -->

    <p
      v-if="isLoading"
      class="page-state"
    >
      Loading photos...
    </p>

    <p
      v-else-if="
        photos.length === 0
        && !isCreateOpen
      "
      class="page-state"
    >
      No photos found.
    </p>

    <!-- GALLERY -->

    <div
      v-else
      class="photo-grid"
    >
      <article
        v-for="photo in photos"
        :key="photo.id"
        class="photo-card"
      >
        <!-- EDIT MODE -->

        <form
          v-if="
            editingPhotoId
            === photo.id
          "
          class="photo-edit"
          @submit.prevent="
            updatePhoto(photo)
          "
        >
          <button
            type="button"
            class="edit-image"
            @click="
              openEditFilePicker
            "
            @dragover.prevent
            @drop.prevent="
              handleEditDrop
            "
          >
            <img
              :src="
                editPhotoPreview
                || photo.image
              "
              :alt="photo.title"
            />

            <span>
              Change image
            </span>
          </button>

          <div
            v-if="editPhotoFile"
            class="selected-file"
          >
            <span>
              {{
                editPhotoFile.name
              }}
            </span>

            <button
              type="button"
              aria-label="
                Remove replacement image
              "
              @click="
                setEditFile(null)
              "
            >
              <IconX
                :size="15"
                :stroke-width="1.8"
              />
            </button>
          </div>

          <input
            v-model="
              editPhotoTitle
            "
            type="text"
            class="photo-input"
            maxlength="200"
            autocomplete="off"
          />

          <div class="form-actions">
            <button
              type="button"
              class="text-button"
              @click="cancelEditing"
            >
              Cancel
            </button>

            <button
              type="submit"
              class="primary-button"
              :disabled="
                isUpdating(photo.id)
                || !editPhotoTitle.trim()
              "
            >
              {{
                isUpdating(photo.id)
                  ? 'Saving...'
                  : 'Save'
              }}
            </button>
          </div>
        </form>

        <!-- NORMAL MODE -->

        <template v-else>
          <div
            class="
              photo-card__image-wrapper
            "
          >
            <img
              :src="photo.image"
              :alt="photo.title"
              class="
                photo-card__image
              "
              loading="lazy"
            />

            <div
              class="
                photo-card__overlay
              "
            >
              <button
                v-if="
                  authStore.can(
                    'photos.update',
                  )
                "
                type="button"
                class="
                  overlay-button
                "
                aria-label="Edit photo"
                @click="
                  startEditing(photo)
                "
              >
                <IconPencil
                  :size="17"
                  :stroke-width="1.8"
                />
              </button>

              <button
                v-if="
                  authStore.can(
                    'photos.delete',
                  )
                "
                type="button"
                class="
                  overlay-button
                  overlay-button--danger
                "
                :disabled="
                  isDeleting(photo.id)
                "
                aria-label="
                  Delete photo
                "
                @click="
                  deletePhoto(photo.id)
                "
              >
                <IconTrash
                  :size="17"
                  :stroke-width="1.8"
                />
              </button>
            </div>
          </div>

          <div
            class="
              photo-card__footer
            "
          >
            {{ photo.title }}
          </div>
        </template>
      </article>
    </div>
  </section>
</template>

<style scoped>
.photos-page {
  width: 100%;
}

/* HEADER */

.photos-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;

  gap: 24px;

  margin-bottom: 24px;
}

.photos-header h1 {
  margin: 8px 0 0;

  color: var(--color-title);

  font-size: 28px;
  font-weight: 700;
}

.back-button,
.new-photo-button {
  display: inline-flex;
  align-items: center;

  gap: 6px;

  padding: 6px 8px;

  color: var(--color-subtitle);

  font: inherit;
  font-size: 12px;
  font-weight: 600;

  background: transparent;

  border: 0;
  border-radius: 7px;

  cursor: pointer;
}

.back-button:hover,
.new-photo-button:hover {
  color: var(--color-primary);

  background:
    rgba(82, 63, 158, 0.06);
}

.new-photo-button svg {
  color: var(--color-primary);
}

/* STATES */

.page-state {
  color: var(--color-subtitle);

  font-size: 13px;
}

.page-state--error {
  color: #b42318;
}

/* CREATE */

.photo-create {
  max-width: 620px;

  display: flex;
  flex-direction: column;

  gap: 12px;

  margin-bottom: 28px;

  padding: 18px;

  background: #ffffff;

  border:
    1px solid var(--color-border);

  border-radius: 12px;
}

.drop-zone {
  position: relative;

  height: 270px;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  gap: 8px;

  overflow: hidden;

  color: var(--color-subtitle);

  background: #fafafd;

  border:
    1px dashed
    rgba(82, 63, 158, 0.3);

  border-radius: 10px;

  cursor: pointer;
}

.drop-zone:hover {
  background:
    rgba(82, 63, 158, 0.035);

  border-color:
    rgba(82, 63, 158, 0.55);
}

.drop-zone svg {
  color: var(--color-primary);
}

.drop-zone strong {
  color: var(--color-title);

  font-size: 13px;
}

.drop-zone span {
  font-size: 12px;
}

.drop-zone__preview {
  position: absolute;

  inset: 0;

  width: 100%;
  height: 100%;

  object-fit: cover;
}

.hidden-file-input {
  display: none;
}

.selected-file {
  display: flex;
  align-items: center;
  justify-content: space-between;

  gap: 10px;

  color: var(--color-subtitle);

  font-size: 11px;
}

.selected-file > span {
  min-width: 0;

  overflow: hidden;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.selected-file button {
  flex-shrink: 0;

  display: grid;

  place-items: center;

  padding: 4px;

  color: var(--color-subtitle);

  background: transparent;

  border: 0;

  cursor: pointer;
}

/* INPUT */

.photo-input {
  width: 100%;

  box-sizing: border-box;

  padding: 9px 11px;

  color: var(--color-title);

  font: inherit;
  font-size: 12px;

  background: #ffffff;

  border:
    1px solid var(--color-border);

  border-radius: 8px;

  outline: none;
}

.photo-input:focus {
  border-color:
    rgba(82, 63, 158, 0.45);
}

/* GALLERY */

.photo-grid {
  display: grid;

  grid-template-columns:
    repeat(
      auto-fill,
      minmax(250px, 1fr)
    );

  align-items: start;

  gap: 20px;
}

.photo-card {
  min-width: 0;

  overflow: hidden;

  background: #ffffff;

  border:
    1px solid var(--color-border);

  border-radius: 12px;

  transition:
    transform 0.16s ease,
    box-shadow 0.16s ease,
    border-color 0.16s ease;
}

.photo-card:hover {
  transform: translateY(-2px);

  border-color:
    rgba(82, 63, 158, 0.2);

  box-shadow:
    0 8px 22px
    rgba(30, 34, 45, 0.07);
}

.photo-card__image-wrapper {
  position: relative;

  height: 240px;

  overflow: hidden;

  background: #f6f6f8;
}

.photo-card__image {
  width: 100%;
  height: 100%;

  display: block;

  object-fit: cover;
}

.photo-card__overlay {
  position: absolute;

  inset: 0;

  display: flex;
  align-items: flex-start;
  justify-content: flex-end;

  gap: 5px;

  padding: 10px;

  box-sizing: border-box;

  background:
    linear-gradient(
      to bottom,
      rgba(0, 0, 0, 0.24),
      transparent 38%
    );

  opacity: 0;

  transition:
    opacity 0.16s ease;
}

.photo-card:hover
.photo-card__overlay {
  opacity: 1;
}

.overlay-button {
  width: 31px;
  height: 31px;

  display: grid;

  place-items: center;

  padding: 0;

  color: #ffffff;

  background:
    rgba(20, 20, 24, 0.48);

  border: 0;
  border-radius: 8px;

  cursor: pointer;
}

.overlay-button:hover {
  background:
    rgba(82, 63, 158, 0.88);
}

.overlay-button--danger:hover {
  background:
    rgba(180, 35, 24, 0.88);
}

.overlay-button:disabled {
  cursor: wait;

  opacity: 0.5;
}

.photo-card__footer {
  padding: 12px 14px;

  overflow: hidden;

  color: var(--color-title);

  font-size: 12px;
  font-weight: 600;

  text-overflow: ellipsis;
  white-space: nowrap;
}

/* EDIT */

.photo-edit {
  display: flex;
  flex-direction: column;

  gap: 11px;

  padding: 12px;
}

.edit-image {
  position: relative;

  height: 240px;

  padding: 0;

  overflow: hidden;

  background: #f6f6f8;

  border: 0;
  border-radius: 9px;

  cursor: pointer;
}

.edit-image img {
  width: 100%;
  height: 100%;

  display: block;

  object-fit: cover;
}

.edit-image::after {
  content: '';

  position: absolute;

  inset: 0;

  background:
    rgba(0, 0, 0, 0);

  transition:
    background 0.16s ease;
}

.edit-image:hover::after {
  background:
    rgba(0, 0, 0, 0.08);
}

.edit-image span {
  position: absolute;

  right: 9px;
  bottom: 9px;

  z-index: 1;

  padding: 6px 9px;

  color: #ffffff;

  font-size: 10px;
  font-weight: 600;

  background:
    rgba(20, 20, 24, 0.65);

  border-radius: 6px;
}

/* ACTIONS */

.form-actions {
  display: flex;
  justify-content: flex-end;

  gap: 8px;
}

.text-button,
.primary-button {
  padding: 7px 11px;

  font: inherit;
  font-size: 12px;
  font-weight: 600;

  border: 0;
  border-radius: 7px;

  cursor: pointer;
}

.text-button {
  color: var(--color-subtitle);

  background: transparent;
}

.primary-button {
  color: #ffffff;

  background: var(--color-primary);
}

.primary-button:disabled {
  cursor: not-allowed;

  opacity: 0.5;
}

/* RESPONSIVE */

@media (max-width: 650px) {
  .photos-header {
    align-items: flex-start;

    flex-direction: column;
  }

  .photo-grid {
    grid-template-columns: 1fr;
  }

  .photo-card__image-wrapper,
  .edit-image {
    height: 260px;
  }

  .photo-card__overlay {
    opacity: 1;
  }

  .photo-create {
    max-width: none;
  }

  .drop-zone {
    height: 230px;
  }
}
</style>
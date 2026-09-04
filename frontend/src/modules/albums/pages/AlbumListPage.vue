<script setup>
import {
  nextTick,
  ref,
  watch,
} from 'vue'

import {
  useRoute,
  useRouter,
} from 'vue-router'

import {
  IconFolder,
  IconFolderPlus,
  IconPencil,
  IconPhoto,
  IconTrash,
} from '@tabler/icons-vue'

import { useAuthStore } from '@/modules/auth/store/authStore'
import albumService from '../services/albumService'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const albums = ref([])

const isLoading = ref(false)
const errorMessage = ref('')

/* -------------------------
   CREATE
------------------------- */

const isCreateOpen = ref(false)
const isCreating = ref(false)

const newAlbumTitle = ref('')
const newAlbumInput = ref(null)

/* -------------------------
   EDIT / DELETE
------------------------- */

const editingAlbumId = ref(null)
const editAlbumTitle = ref('')

const updatingAlbumIds = ref([])
const deletingAlbumIds = ref([])

/* -------------------------
   FETCH
------------------------- */

let albumRequestId = 0

const fetchAlbums = async (userId) => {
  const requestId = ++albumRequestId

  isLoading.value = true
  errorMessage.value = ''

  try {
    const response =
      await albumService.getAlbumsByUser(
        userId,
      )

    if (requestId !== albumRequestId) {
      return
    }

    albums.value = response.data
  } catch (error) {
    if (requestId !== albumRequestId) {
      return
    }

    console.error(
      'Failed to fetch albums:',
      error,
    )

    errorMessage.value =
      'Albums could not be loaded.'
  } finally {
    if (requestId === albumRequestId) {
      isLoading.value = false
    }
  }
}

/* -------------------------
   CREATE
------------------------- */

const openCreateAlbum = async () => {
  isCreateOpen.value = true

  await nextTick()

  newAlbumInput.value?.focus()
}

const closeCreateAlbum = () => {
  isCreateOpen.value = false
  newAlbumTitle.value = ''
}

const createAlbum = async () => {
  const title =
    newAlbumTitle.value.trim()

  if (
    !title
    || isCreating.value
    || !authStore.can('albums.create')
  ) {
    return
  }

  isCreating.value = true
  errorMessage.value = ''

  try {
    const response =
      await albumService.createAlbum({
        user: route.params.id,
        title,
      })

    albums.value.push(response.data)

    closeCreateAlbum()
  } catch (error) {
    console.error(
      'Failed to create album:',
      error,
    )

    errorMessage.value =
      'Album could not be created.'
  } finally {
    isCreating.value = false
  }
}

/* -------------------------
   EDIT
------------------------- */

const startEditing = (album) => {
  editingAlbumId.value = album.id
  editAlbumTitle.value = album.title
}

const cancelEditing = () => {
  editingAlbumId.value = null
  editAlbumTitle.value = ''
}

const updateAlbum = async (album) => {
  const title =
    editAlbumTitle.value.trim()

  if (
    !title
    || updatingAlbumIds.value.includes(
      album.id,
    )
    || !authStore.can('albums.update')
  ) {
    return
  }

  if (title === album.title) {
    cancelEditing()
    return
  }

  updatingAlbumIds.value.push(
    album.id,
  )

  errorMessage.value = ''

  try {
    const response =
      await albumService.updateAlbum(
        album.id,
        {
          title,
        },
      )

    const index =
      albums.value.findIndex(
        (item) => item.id === album.id,
      )

    if (index !== -1) {
      albums.value[index] =
        response.data
    }

    cancelEditing()
  } catch (error) {
    console.error(
      'Failed to update album:',
      error,
    )

    errorMessage.value =
      'Album could not be updated.'
  } finally {
    updatingAlbumIds.value =
      updatingAlbumIds.value.filter(
        (id) => id !== album.id,
      )
  }
}

/* -------------------------
   DELETE
------------------------- */

const deleteAlbum = async (albumId) => {
  if (
    deletingAlbumIds.value.includes(
      albumId,
    )
    || !authStore.can('albums.delete')
  ) {
    return
  }

  deletingAlbumIds.value.push(
    albumId,
  )

  errorMessage.value = ''

  try {
    await albumService.deleteAlbum(
      albumId,
    )

    albums.value =
      albums.value.filter(
        (album) =>
          album.id !== albumId,
      )

    if (
      editingAlbumId.value === albumId
    ) {
      cancelEditing()
    }
  } catch (error) {
    console.error(
      'Failed to delete album:',
      error,
    )

    errorMessage.value =
      'Album could not be deleted.'
  } finally {
    deletingAlbumIds.value =
      deletingAlbumIds.value.filter(
        (id) => id !== albumId,
      )
  }
}

/* -------------------------
   NAVIGATION
------------------------- */

const openAlbum = (album) => {
  router.push({
    name: 'album-photos',

    params: {
      id: route.params.id,
      albumId: album.id,
    },
  })
}

/* -------------------------
   HELPERS
------------------------- */

const isUpdating = (albumId) => {
  return updatingAlbumIds.value.includes(
    albumId,
  )
}

const isDeleting = (albumId) => {
  return deletingAlbumIds.value.includes(
    albumId,
  )
}

const getPreviewPhotos = (album) => {
  if (
    !Array.isArray(
      album.preview_photos,
    )
  ) {
    return []
  }

  return album.preview_photos.slice(
    0,
    4,
  )
}

const getPreviewLayoutClass = (
  album,
) => {
  const count =
    getPreviewPhotos(album).length

  return `album-preview--${count}`
}

/* -------------------------
   ROUTE
------------------------- */

watch(
  () => route.params.id,
  (userId) => {
    if (!userId) {
      return
    }

    albums.value = []

    closeCreateAlbum()
    cancelEditing()

    fetchAlbums(userId)
  },
  {
    immediate: true,
  },
)
</script>

<template>
  <section class="albums-page">
    <!-- HEADER -->

    <div class="albums-header">
      <h1>Albums</h1>

      <button
        v-if="
          authStore.can('albums.create')
          && !isCreateOpen
        "
        type="button"
        class="new-album-button"
        @click="openCreateAlbum"
      >
        <IconFolderPlus
          :size="18"
          :stroke-width="1.8"
        />

        <span>New Album</span>
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
      class="album-create"
      @submit.prevent="createAlbum"
    >
      <IconFolder
        :size="20"
        :stroke-width="1.7"
        class="album-create__icon"
      />

      <input
        ref="newAlbumInput"
        v-model="newAlbumTitle"
        type="text"
        class="album-create__input"
        placeholder="Album title"
        maxlength="200"
        autocomplete="off"
        :disabled="isCreating"
      />

      <button
        type="button"
        class="text-button"
        @click="closeCreateAlbum"
      >
        Cancel
      </button>

      <button
        type="submit"
        class="primary-button"
        :disabled="
          isCreating
          || !newAlbumTitle.trim()
        "
      >
        {{
          isCreating
            ? 'Creating...'
            : 'Create'
        }}
      </button>
    </form>

    <!-- STATES -->

    <p
      v-if="isLoading"
      class="page-state"
    >
      Loading albums...
    </p>

    <p
      v-else-if="
        albums.length === 0
        && !isCreateOpen
      "
      class="page-state"
    >
      No albums found.
    </p>

    <!-- GRID -->

    <div
      v-else
      class="album-grid"
    >
      <article
        v-for="album in albums"
        :key="album.id"
        class="album-card"
      >
        <!-- EDIT MODE -->

        <form
          v-if="
            editingAlbumId === album.id
          "
          class="album-edit"
          @submit.prevent="
            updateAlbum(album)
          "
        >
          <IconFolder
            :size="28"
            :stroke-width="1.5"
            class="album-card__folder"
          />

          <input
            v-model="editAlbumTitle"
            type="text"
            class="album-edit__input"
            maxlength="200"
            autocomplete="off"
          />

          <div
            class="album-edit__actions"
          >
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
                isUpdating(album.id)
                || !editAlbumTitle.trim()
              "
            >
              {{
                isUpdating(album.id)
                  ? 'Saving...'
                  : 'Save'
              }}
            </button>
          </div>
        </form>

        <!-- NORMAL MODE -->

        <template v-else>
          <button
            type="button"
            class="album-card__open"
            @click="openAlbum(album)"
          >
            <!-- PREVIEW -->

            <div
              class="album-preview"
              :class="
                getPreviewLayoutClass(
                  album,
                )
              "
            >
              <template
                v-if="
                  getPreviewPhotos(
                    album,
                  ).length
                "
              >
                <img
                  v-for="
                    photo
                    in getPreviewPhotos(
                      album,
                    )
                  "
                  :key="photo.id"
                  :src="photo.image"
                  alt=""
                  class="
                    album-preview__image
                  "
                  loading="lazy"
                />
              </template>

              <div
                v-else
                class="
                  album-preview__empty
                "
              >
                <IconPhoto
                  :size="30"
                  :stroke-width="1.4"
                />

                <span>
                  No photos yet
                </span>
              </div>
            </div>

            <!-- META -->

            <div
              class="album-card__meta"
            >
              <span
                class="
                  album-card__title
                "
              >
                {{ album.title }}
              </span>

              <span
                class="
                  album-card__count
                "
              >
                {{
                  album.photo_count ?? 0
                }}

                {{
                  (
                    album.photo_count
                    ?? 0
                  ) === 1
                    ? 'photo'
                    : 'photos'
                }}
              </span>
            </div>
          </button>

          <!-- ACTIONS -->

          <div
            class="album-card__actions"
          >
            <button
              v-if="
                authStore.can(
                  'albums.update',
                )
              "
              type="button"
              class="icon-button"
              aria-label="Edit album"
              @click.stop="
                startEditing(album)
              "
            >
              <IconPencil
                :size="16"
                :stroke-width="1.7"
              />
            </button>

            <button
              v-if="
                authStore.can(
                  'albums.delete',
                )
              "
              type="button"
              class="
                icon-button
                icon-button--danger
              "
              :disabled="
                isDeleting(album.id)
              "
              aria-label="Delete album"
              @click.stop="
                deleteAlbum(album.id)
              "
            >
              <IconTrash
                :size="16"
                :stroke-width="1.7"
              />
            </button>
          </div>
        </template>
      </article>
    </div>
  </section>
</template>

<style scoped>
.albums-page {
  width: 100%;
}

/* HEADER */

.albums-header {
  display: flex;
  align-items: center;
  justify-content: space-between;

  gap: 24px;

  margin-bottom: 24px;
}

.albums-header h1 {
  margin: 0;

  color: var(--color-title);

  font-size: 28px;
  font-weight: 700;
}

/* STATES */

.page-state {
  margin: 16px 0;

  color: var(--color-subtitle);

  font-size: 13px;
}

.page-state--error {
  color: #b42318;
}

/* CREATE */

.new-album-button {
  display: inline-flex;
  align-items: center;

  gap: 7px;

  padding: 7px 9px;

  color: var(--color-title);

  font: inherit;
  font-size: 12px;
  font-weight: 600;

  background: transparent;

  border: 0;
  border-radius: 7px;

  cursor: pointer;
}

.new-album-button svg {
  color: var(--color-primary);
}

.new-album-button:hover {
  color: var(--color-primary);

  background:
    rgba(82, 63, 158, 0.06);
}

.album-create {
  display: flex;
  align-items: center;

  gap: 10px;

  margin-bottom: 24px;

  padding: 14px;

  background: #ffffff;

  border:
    1px solid var(--color-border);

  border-radius: 10px;
}

.album-create__icon {
  flex-shrink: 0;

  color: var(--color-primary);
}

.album-create__input {
  min-width: 0;

  flex: 1;

  padding: 9px 10px;

  color: var(--color-title);

  font: inherit;
  font-size: 13px;

  border:
    1px solid var(--color-border);

  border-radius: 7px;

  outline: none;
}

.album-create__input:focus {
  border-color:
    rgba(82, 63, 158, 0.45);
}

/* GRID */

.album-grid {
  display: grid;

  grid-template-columns:
    repeat(
      auto-fill,
      minmax(220px, 1fr)
    );

  gap: 18px;
}

/* CARD */

.album-card {
  position: relative;

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

.album-card:hover {
  transform: translateY(-2px);

  border-color:
    rgba(82, 63, 158, 0.2);

  box-shadow:
    0 8px 22px
    rgba(30, 34, 45, 0.07);
}

.album-card__open {
  width: 100%;

  display: block;

  padding: 0;

  text-align: left;

  background: transparent;

  border: 0;

  cursor: pointer;
}

/* PREVIEW */

.album-preview {
  width: 100%;
  height: 240px;

  display: grid;

  gap: 2px;

  overflow: hidden;

  background: #f1eff6;
}

.album-preview__image {
  width: 100%;
  height: 100%;

  min-width: 0;
  min-height: 0;

  display: block;

  object-fit: cover;
}

/* 0 PHOTOS */

.album-preview--0 {
  display: grid;

  place-items: center;
}

.album-preview__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  gap: 7px;

  color: #9994a6;

  font-size: 11px;
}

/* 1 PHOTO */

.album-preview--1 {
  grid-template-columns: 1fr;
}

/* 2 PHOTOS */

.album-preview--2 {
  grid-template-columns:
    repeat(2, 1fr);
}

/* 3 PHOTOS */

.album-preview--3 {
  grid-template-columns:
    1.35fr 1fr;

  grid-template-rows:
    repeat(2, 1fr);
}

.album-preview--3
.album-preview__image:first-child {
  grid-row:
    1 / span 2;
}

/* 4 PHOTOS */

.album-preview--4 {
  grid-template-columns:
    repeat(2, 1fr);

  grid-template-rows:
    repeat(2, 1fr);
}

/* META */

.album-card__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;

  gap: 12px;

  padding: 12px 14px;
}

.album-card__title {
  min-width: 0;

  overflow: hidden;

  color: var(--color-title);

  font-size: 13px;
  font-weight: 600;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.album-card__count {
  flex-shrink: 0;

  color: var(--color-subtitle);

  font-size: 11px;
}

/* CARD ACTIONS */

.album-card__actions {
  position: absolute;

  top: 9px;
  right: 9px;

  z-index: 2;

  display: flex;

  gap: 3px;

  opacity: 0;

  transition:
    opacity 0.16s ease;
}

.album-card:hover
.album-card__actions {
  opacity: 1;
}

/* EDIT */

.album-edit {
  min-height: 170px;

  display: flex;
  flex-direction: column;

  gap: 12px;

  padding: 18px;
}

.album-card__folder {
  color: var(--color-primary);
}

.album-edit__input {
  width: 100%;

  box-sizing: border-box;

  padding: 8px 9px;

  color: var(--color-title);

  font: inherit;
  font-size: 13px;

  border:
    1px solid var(--color-border);

  border-radius: 7px;

  outline: none;
}

.album-edit__input:focus {
  border-color:
    rgba(82, 63, 158, 0.45);
}

.album-edit__actions {
  display: flex;

  justify-content: flex-end;

  gap: 6px;

  margin-top: auto;
}

/* BUTTONS */

.icon-button {
  width: 29px;
  height: 29px;

  display: grid;

  place-items: center;

  padding: 0;

  color: #858b97;

  background:
    rgba(255, 255, 255, 0.94);

  border: 0;
  border-radius: 7px;

  box-shadow:
    0 2px 8px
    rgba(20, 20, 30, 0.08);

  cursor: pointer;
}

.icon-button:hover {
  color: var(--color-primary);

  background: #ffffff;
}

.icon-button--danger:hover {
  color: #b42318;

  background: #ffffff;
}

.icon-button:disabled {
  cursor: wait;

  opacity: 0.4;
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
  .album-grid {
  display: grid;

  grid-template-columns:
    repeat(
      auto-fill,
      minmax(300px, 1fr)
    );

  gap: 20px;

  align-items: start;
}

  .album-card__actions {
    opacity: 1;
  }

  .album-create {
    align-items: stretch;

    flex-wrap: wrap;
  }

  .album-create__input {
    flex-basis:
      calc(100% - 35px);
  }
}
</style>
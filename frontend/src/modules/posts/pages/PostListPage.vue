<script setup>
import {
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from 'vue'

import { useRoute } from 'vue-router'

import {
  IconCirclePlus,
  IconEdit,
  IconMessageCircle,
  IconSend,
  IconTrash,
  IconX,
} from '@tabler/icons-vue'

import { useAuthStore } from '@/modules/auth/store/authStore'
import postService from '../services/postService'

const route = useRoute()
const authStore = useAuthStore()

/* -------------------------
   POSTS
------------------------- */

const posts = ref([])

const isLoading = ref(false)
const errorMessage = ref('')

/* -------------------------
   CREATE POST
------------------------- */

const isCreateOpen = ref(false)
const isCreatingPost = ref(false)

const newPostTitle = ref('')
const newPostBody = ref('')

const newPostTitleInput = ref(null)

/* -------------------------
   EDIT POST
------------------------- */

const editingPostId = ref(null)

const editTitle = ref('')
const editBody = ref('')

const updatingPostIds = ref([])
const deletingPostIds = ref([])

/* -------------------------
   MODAL + COMMENTS
------------------------- */

const selectedPost = ref(null)

const comments = ref([])
const newComment = ref('')

const isCommentsLoading = ref(false)
const isCreatingComment = ref(false)

const commentsErrorMessage = ref('')

const commentInput = ref(null)

/* -------------------------
   FETCH POSTS
------------------------- */

const fetchPosts = async (userId) => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response =
      await postService.getPostsByUser(userId)

    posts.value = response.data
  } catch (error) {
    console.error(
      'Failed to fetch posts:',
      error,
    )

    errorMessage.value =
      'Posts could not be loaded.'
  } finally {
    isLoading.value = false
  }
}

/* -------------------------
   CREATE POST
------------------------- */

const openCreatePost = async () => {
  isCreateOpen.value = true

  await nextTick()

  newPostTitleInput.value?.focus()
}

const closeCreatePost = () => {
  isCreateOpen.value = false

  newPostTitle.value = ''
  newPostBody.value = ''
}

const createPost = async () => {
  const title = newPostTitle.value.trim()
  const body = newPostBody.value.trim()

  if (
    !title
    || !body
    || isCreatingPost.value
    || !authStore.can('posts.create')
  ) {
    return
  }

  isCreatingPost.value = true
  errorMessage.value = ''

  try {
    const response =
      await postService.createPost({
        user: route.params.id,
        title,
        body,
      })

    posts.value.push(response.data)

    closeCreatePost()
  } catch (error) {
    console.error(
      'Failed to create post:',
      error,
    )

    errorMessage.value =
      'Post could not be created.'
  } finally {
    isCreatingPost.value = false
  }
}

/* -------------------------
   EDIT POST
------------------------- */

const startEditing = (post) => {
  editingPostId.value = post.id

  editTitle.value = post.title
  editBody.value = post.body
}

const cancelEditing = () => {
  editingPostId.value = null

  editTitle.value = ''
  editBody.value = ''
}

const updatePost = async (post) => {
  const title = editTitle.value.trim()
  const body = editBody.value.trim()

  if (
    !title
    || !body
    || updatingPostIds.value.includes(post.id)
    || !authStore.can('posts.update')
  ) {
    return
  }

  if (
    title === post.title
    && body === post.body
  ) {
    cancelEditing()

    return
  }

  updatingPostIds.value.push(post.id)

  errorMessage.value = ''

  try {
    const response =
      await postService.updatePost(
        post.id,
        {
          title,
          body,
        },
      )

    const index =
      posts.value.findIndex(
        (item) => item.id === post.id,
      )

    if (index !== -1) {
      posts.value[index] = response.data
    }

    if (selectedPost.value?.id === post.id) {
      selectedPost.value = response.data
    }

    cancelEditing()
  } catch (error) {
    console.error(
      'Failed to update post:',
      error,
    )

    errorMessage.value =
      'Post could not be updated.'
  } finally {
    updatingPostIds.value =
      updatingPostIds.value.filter(
        (id) => id !== post.id,
      )
  }
}

/* -------------------------
   DELETE POST
------------------------- */

const deletePost = async (postId) => {
  if (
    deletingPostIds.value.includes(postId)
    || !authStore.can('posts.delete')
  ) {
    return
  }

  deletingPostIds.value.push(postId)

  errorMessage.value = ''

  try {
    await postService.deletePost(postId)

    posts.value =
      posts.value.filter(
        (post) => post.id !== postId,
      )

    if (selectedPost.value?.id === postId) {
      closePost()
    }

    if (editingPostId.value === postId) {
      cancelEditing()
    }
  } catch (error) {
    console.error(
      'Failed to delete post:',
      error,
    )

    errorMessage.value =
      'Post could not be deleted.'
  } finally {
    deletingPostIds.value =
      deletingPostIds.value.filter(
        (id) => id !== postId,
      )
  }
}

/* -------------------------
   COMMENTS
------------------------- */

const fetchComments = async (postId) => {
  isCommentsLoading.value = true

  commentsErrorMessage.value = ''

  try {
    const response =
      await postService.getCommentsByPost(
        postId,
      )

    comments.value = response.data
  } catch (error) {
    console.error(
      'Failed to fetch comments:',
      error,
    )

    commentsErrorMessage.value =
      'Comments could not be loaded.'
  } finally {
    isCommentsLoading.value = false
  }
}

const openPost = async (post) => {
  selectedPost.value = post

  comments.value = []
  newComment.value = ''

  commentsErrorMessage.value = ''

  document.body.style.overflow = 'hidden'

  await fetchComments(post.id)
}

const closePost = () => {
  selectedPost.value = null

  comments.value = []
  newComment.value = ''

  commentsErrorMessage.value = ''

  document.body.style.overflow = ''
}

const createComment = async () => {
  const body = newComment.value.trim()

  if (
    !body
    || !selectedPost.value
    || isCreatingComment.value
    || !authStore.can('comments.create')
  ) {
    return
  }

  isCreatingComment.value = true

  commentsErrorMessage.value = ''

  try {
    const response =
      await postService.createComment({
        post: selectedPost.value.id,
        body,
      })

    comments.value.push(response.data)

    newComment.value = ''

    await nextTick()

    commentInput.value?.focus()
  } catch (error) {
    console.error(
      'Failed to create comment:',
      error,
    )

    commentsErrorMessage.value =
      'Comment could not be added.'
  } finally {
    isCreatingComment.value = false
  }
}

const getInitial = (displayName) => {
  return (
    displayName
      ?.trim()
      ?.charAt(0)
      ?.toUpperCase()
    || '?'
  )
}

/* -------------------------
   HELPERS
------------------------- */

const isUpdating = (postId) => {
  return updatingPostIds.value.includes(
    postId,
  )
}

const isDeleting = (postId) => {
  return deletingPostIds.value.includes(
    postId,
  )
}

const handleKeydown = (event) => {
  if (
    event.key === 'Escape'
    && selectedPost.value
  ) {
    closePost()
  }
}

watch(
  () => route.params.id,
  (userId) => {
    if (!userId) {
      return
    }

    posts.value = []

    closeCreatePost()
    cancelEditing()
    closePost()

    fetchPosts(userId)
  },
  {
    immediate: true,
  },
)

onMounted(() => {
  document.addEventListener(
    'keydown',
    handleKeydown,
  )
})

onBeforeUnmount(() => {
  document.removeEventListener(
    'keydown',
    handleKeydown,
  )

  document.body.style.overflow = ''
})
</script>

<template>
  <section class="posts-page">
    <div class="posts-page__header">
      <h1>Posts</h1>

      <button
        v-if="
          authStore.can('posts.create')
          && !isCreateOpen
        "
        type="button"
        class="new-post-button"
        @click="openCreatePost"
      >
        <IconCirclePlus
          :size="17"
          :stroke-width="1.8"
        />

        <span>New Post</span>
      </button>
    </div>

    <p
      v-if="errorMessage"
      class="page-state page-state--error"
    >
      {{ errorMessage }}
    </p>

    <!-- CREATE POST -->

    <form
      v-if="isCreateOpen"
      class="post-editor post-editor--new"
      @submit.prevent="createPost"
    >
      <input
        ref="newPostTitleInput"
        v-model="newPostTitle"
        type="text"
        class="post-editor__title"
        placeholder="Post title"
        maxlength="200"
        autocomplete="off"
        :disabled="isCreatingPost"
      />

      <textarea
        v-model="newPostBody"
        class="post-editor__body"
        placeholder="Write something..."
        rows="4"
        :disabled="isCreatingPost"
      />

      <div class="post-editor__actions">
        <button
          type="button"
          class="text-button"
          @click="closeCreatePost"
        >
          Cancel
        </button>

        <button
          type="submit"
          class="primary-button"
          :disabled="
            isCreatingPost
            || !newPostTitle.trim()
            || !newPostBody.trim()
          "
        >
          {{
            isCreatingPost
              ? 'Publishing...'
              : 'Publish'
          }}
        </button>
      </div>
    </form>

    <!-- STATES -->

    <p
      v-if="isLoading"
      class="page-state"
    >
      Loading posts...
    </p>

    <p
      v-else-if="
        posts.length === 0
        && !isCreateOpen
      "
      class="page-state"
    >
      No posts found.
    </p>

    <!-- POSTS -->

    <div
      v-else
      class="posts-list"
    >
      <article
        v-for="post in posts"
        :key="post.id"
        class="post-row"
      >
        <!-- EDIT MODE -->

        <form
          v-if="editingPostId === post.id"
          class="post-editor"
          @submit.prevent="updatePost(post)"
        >
          <input
            v-model="editTitle"
            type="text"
            class="post-editor__title"
            maxlength="200"
            autocomplete="off"
          />

          <textarea
            v-model="editBody"
            class="post-editor__body"
            rows="4"
          />

          <div class="post-editor__actions">
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
                isUpdating(post.id)
                || !editTitle.trim()
                || !editBody.trim()
              "
            >
              {{
                isUpdating(post.id)
                  ? 'Saving...'
                  : 'Save'
              }}
            </button>
          </div>
        </form>

        <!-- READ MODE -->

        <template v-else>
          <div class="post-row__content">
            <h2>
              {{ post.title }}
            </h2>

            <p>
              {{ post.body }}
            </p>
          </div>

          <div class="post-row__actions">
            <button
              v-if="authStore.can('posts.update')"
              type="button"
              class="icon-button"
              aria-label="Edit post"
              @click="startEditing(post)"
            >
              <IconEdit
                :size="16"
                :stroke-width="1.7"
              />
            </button>

            <button
              v-if="authStore.can('posts.delete')"
              type="button"
              class="icon-button icon-button--danger"
              :disabled="isDeleting(post.id)"
              aria-label="Delete post"
              @click="deletePost(post.id)"
            >
              <IconTrash
                :size="16"
                :stroke-width="1.7"
              />
            </button>

            <button
              type="button"
              class="see-more-button"
              @click="openPost(post)"
            >
              <span>See More</span>

              <IconCirclePlus
                :size="17"
                :stroke-width="1.8"
              />
            </button>
          </div>
        </template>
      </article>
    </div>

    <!-- POST MODAL -->

    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="selectedPost"
          class="modal-backdrop"
          @click.self="closePost"
        >
          <section
            class="post-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="post-modal-title"
          >
            <button
              type="button"
              class="post-modal__close"
              aria-label="Close post details"
              @click="closePost"
            >
              <IconX
                :size="18"
                :stroke-width="1.8"
              />
            </button>

            <!-- POST DETAIL -->

            <div class="post-modal__post">
              <h2 id="post-modal-title">
                {{ selectedPost.title }}
              </h2>

              <p>
                {{ selectedPost.body }}
              </p>
            </div>

            <!-- COMMENTS -->

            <div class="post-modal__comments">
              <div class="comments-header">
                <IconMessageCircle
                  :size="17"
                  :stroke-width="1.8"
                />

                <h3>Comments</h3>
              </div>

              <div class="comments-content">
                <p
                  v-if="isCommentsLoading"
                  class="comments-state"
                >
                  Loading comments...
                </p>

                <p
                  v-else-if="
                    commentsErrorMessage
                    && comments.length === 0
                  "
                  class="comments-state comments-state--error"
                >
                  {{ commentsErrorMessage }}
                </p>

                <p
                  v-else-if="comments.length === 0"
                  class="comments-state"
                >
                  No comments yet.
                </p>

                <div
                  v-else
                  class="comments-list"
                >
                  <article
                    v-for="comment in comments"
                    :key="comment.id"
                    class="comment"
                  >
                    <div class="comment__avatar">
                      {{
                        getInitial(
                          comment.display_name,
                        )
                      }}
                    </div>

                    <div class="comment__content">
                      <strong>
                        {{ comment.display_name }}
                      </strong>

                      <p>
                        {{ comment.body }}
                      </p>
                    </div>
                  </article>
                </div>
              </div>

              <!-- INSTAGRAM-LIKE COMMENT INPUT -->

              <form
                v-if="
                  authStore.can('comments.create')
                "
                class="comment-composer"
                @submit.prevent="createComment"
              >
                <input
                  ref="commentInput"
                  v-model="newComment"
                  type="text"
                  class="comment-composer__input"
                  placeholder="Add a comment..."
                  autocomplete="off"
                  :disabled="isCreatingComment"
                />

                <button
                  type="submit"
                  class="comment-composer__send"
                  aria-label="Send comment"
                  :disabled="
                    isCreatingComment
                    || !newComment.trim()
                  "
                >
                  <IconSend
                    :size="18"
                    :stroke-width="1.8"
                  />
                </button>
              </form>

              <p
                v-if="
                  commentsErrorMessage
                  && comments.length > 0
                "
                class="comment-composer__error"
              >
                {{ commentsErrorMessage }}
              </p>
            </div>
          </section>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>

<style scoped>
.posts-page {
  width: 100%;
}

.posts-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;

  margin-bottom: 24px;
}

.posts-page h1 {
  margin: 0;

  color: var(--color-title);
  font-size: 28px;
  font-weight: 700;
}

.page-state {
  margin: 16px 0;

  color: var(--color-subtitle);
  font-size: 13px;
}

.page-state--error {
  color: #b42318;
}

/* -------------------------
   BUTTONS
------------------------- */

.new-post-button,
.see-more-button {
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

  transition:
    color 0.18s ease,
    background-color 0.18s ease;
}

.new-post-button svg,
.see-more-button svg {
  color: var(--color-primary);
}

.new-post-button:hover,
.see-more-button:hover {
  color: var(--color-primary);

  background:
    rgba(82, 63, 158, 0.06);
}

.icon-button {
  width: 30px;
  height: 30px;

  display: grid;
  place-items: center;

  padding: 0;

  color: #858b97;

  background: transparent;
  border: 0;
  border-radius: 7px;

  cursor: pointer;

  transition:
    color 0.18s ease,
    background-color 0.18s ease;
}

.icon-button:hover {
  color: var(--color-primary);

  background:
    rgba(82, 63, 158, 0.06);
}

.icon-button--danger:hover {
  color: #b42318;

  background:
    rgba(180, 35, 24, 0.07);
}

.icon-button:disabled {
  cursor: wait;
  opacity: 0.4;
}

/* -------------------------
   POST LIST
------------------------- */

.posts-list {
  border-top:
    1px solid var(--color-border);
}

.post-row {
  min-height: 115px;

  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;

  padding: 18px;

  border-bottom:
    1px solid var(--color-border);
}

.post-row__content {
  min-width: 0;
  max-width: 700px;
}

.post-row__content h2 {
  margin: 0 0 8px;

  color: var(--color-title);
  font-size: 14px;
  font-weight: 600;
}

.post-row__content p {
  margin: 0;

  color: var(--color-subtitle);
  font-size: 12px;
  line-height: 1.55;

  white-space: pre-line;
}

.post-row__actions {
  flex-shrink: 0;

  display: flex;
  align-items: center;
  gap: 4px;
}

/* -------------------------
   POST EDITOR
------------------------- */

.post-editor {
  width: 100%;

  display: flex;
  flex-direction: column;
  gap: 10px;
}

.post-editor--new {
  margin-bottom: 22px;
  padding: 18px;

  background: #ffffff;
  border:
    1px solid var(--color-border);
  border-radius: 12px;
}

.post-editor__title,
.post-editor__body {
  width: 100%;
  box-sizing: border-box;

  color: var(--color-title);

  font: inherit;

  background: transparent;
  border:
    1px solid var(--color-border);
  border-radius: 8px;

  outline: none;

  transition:
    border-color 0.18s ease,
    box-shadow 0.18s ease;
}

.post-editor__title {
  padding: 10px 12px;

  font-size: 13px;
  font-weight: 600;
}

.post-editor__body {
  min-height: 90px;

  padding: 10px 12px;

  font-size: 12px;
  line-height: 1.6;

  resize: vertical;
}

.post-editor__title:focus,
.post-editor__body:focus {
  border-color:
    rgba(82, 63, 158, 0.45);

  box-shadow:
    0 0 0 3px
    rgba(82, 63, 158, 0.06);
}

.post-editor__actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.text-button,
.primary-button {
  padding: 7px 12px;

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

.text-button:hover {
  background: #f5f5f7;
}

.primary-button {
  color: #ffffff;

  background: var(--color-primary);
}

.primary-button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

/* -------------------------
   MODAL
------------------------- */

.modal-backdrop {
  position: fixed;
  inset: 0;

  display: grid;
  place-items: center;

  padding: 28px;

  background:
    rgba(32, 37, 45, 0.42);

  z-index: 1000;
}

.post-modal {
  position: relative;

  width: min(820px, 92vw);
  height: min(500px, 80vh);

  display: grid;
  grid-template-columns:
    minmax(0, 1.1fr)
    minmax(300px, 0.9fr);

  overflow: hidden;

  background: #ffffff;
  border-radius: 16px;

  box-shadow:
    0 24px 60px
    rgba(25, 30, 42, 0.2);
}

.post-modal__close {
  position: absolute;
  top: 14px;
  right: 14px;

  width: 28px;
  height: 28px;

  display: grid;
  place-items: center;

  padding: 0;

  color: var(--color-title);

  background: transparent;
  border: 0;
  border-radius: 7px;

  cursor: pointer;

  z-index: 5;
}

.post-modal__close:hover {
  color: var(--color-primary);

  background:
    rgba(82, 63, 158, 0.07);
}

/* -------------------------
   MODAL POST
------------------------- */

.post-modal__post {
  overflow-y: auto;

  padding: 30px 28px;
}

.post-modal__post h2 {
  margin: 0 0 18px;

  color: var(--color-title);
  font-size: 17px;
  font-weight: 600;
}

.post-modal__post p {
  margin: 0;

  color: var(--color-subtitle);
  font-size: 13px;
  line-height: 1.7;

  white-space: pre-line;
}

/* -------------------------
   COMMENTS
------------------------- */

.post-modal__comments {
  min-width: 0;
  min-height: 0;

  display: flex;
  flex-direction: column;

  border-left:
    1px solid var(--color-border);
}

.comments-header {
  flex-shrink: 0;

  display: flex;
  align-items: center;
  gap: 7px;

  padding: 28px 48px 18px 24px;
}

.comments-header h3 {
  margin: 0;

  color: var(--color-title);
  font-size: 15px;
  font-weight: 600;
}

.comments-header svg {
  color: var(--color-primary);
}

.comments-content {
  min-height: 0;
  flex: 1;

  overflow-y: auto;

  padding: 0 24px 18px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comment {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.comment__avatar {
  width: 32px;
  height: 32px;

  flex-shrink: 0;

  display: grid;
  place-items: center;

  color: var(--color-primary);

  font-size: 11px;
  font-weight: 700;

  background: #f0eef6;
  border-radius: 50%;
}

.comment__content {
  min-width: 0;
}

.comment__content strong {
  display: block;

  margin-bottom: 4px;

  color: var(--color-title);
  font-size: 11px;
  font-weight: 600;
}

.comment__content p {
  margin: 0;

  color: var(--color-subtitle);
  font-size: 11px;
  line-height: 1.5;
}

.comments-state {
  margin: 0;

  color: var(--color-subtitle);
  font-size: 12px;
}

.comments-state--error {
  color: #b42318;
}

/* -------------------------
   COMMENT COMPOSER
------------------------- */

.comment-composer {
  flex-shrink: 0;

  display: flex;
  align-items: center;
  gap: 8px;

  padding: 12px 14px;

  border-top:
    1px solid var(--color-border);
}

.comment-composer__input {
  min-width: 0;
  flex: 1;

  padding: 9px 11px;

  color: var(--color-title);

  font: inherit;
  font-size: 12px;

  background: #f8f8fa;
  border: 1px solid transparent;
  border-radius: 18px;

  outline: none;

  transition:
    border-color 0.18s ease,
    background-color 0.18s ease;
}

.comment-composer__input:focus {
  background: #ffffff;

  border-color:
    rgba(82, 63, 158, 0.3);
}

.comment-composer__send {
  width: 32px;
  height: 32px;

  flex-shrink: 0;

  display: grid;
  place-items: center;

  padding: 0;

  color: var(--color-primary);

  background: transparent;
  border: 0;
  border-radius: 50%;

  cursor: pointer;
}

.comment-composer__send:hover {
  background:
    rgba(82, 63, 158, 0.07);
}

.comment-composer__send:disabled {
  cursor: not-allowed;
  opacity: 0.35;
}

.comment-composer__error {
  flex-shrink: 0;

  margin: 0;
  padding: 0 16px 10px;

  color: #b42318;
  font-size: 11px;
}

/* -------------------------
   TRANSITION
------------------------- */

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.18s ease;
}

.modal-enter-active .post-modal,
.modal-leave-active .post-modal {
  transition:
    transform 0.18s ease,
    opacity 0.18s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .post-modal,
.modal-leave-to .post-modal {
  opacity: 0;

  transform:
    translateY(8px)
    scale(0.985);
}

/* -------------------------
   RESPONSIVE
------------------------- */

@media (max-width: 760px) {
  .post-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .post-row__actions {
    align-self: flex-end;
  }

  .post-modal {
    height: min(700px, 90vh);

    grid-template-columns: 1fr;
    grid-template-rows:
      minmax(180px, auto)
      minmax(0, 1fr);
  }

  .post-modal__comments {
    border-top:
      1px solid var(--color-border);

    border-left: 0;
  }
}
</style>
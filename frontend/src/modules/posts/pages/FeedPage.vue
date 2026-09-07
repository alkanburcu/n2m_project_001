<script setup>
import {
  nextTick,
  onMounted,
  ref,
} from 'vue'

import { useRouter } from 'vue-router'

import {
  IconMessageCircle,
  IconSend,
  IconX,
} from '@tabler/icons-vue'

import { useAuthStore } from '@/modules/auth/store/authStore'

import postService from '../services/postService'

const router = useRouter()
const authStore = useAuthStore()

const posts = ref([])

const isLoading = ref(false)
const errorMessage = ref('')

const selectedPost = ref(null)

const comments = ref([])
const isCommentsLoading = ref(false)
const commentsErrorMessage = ref('')

const newComment = ref('')
const isCreatingComment = ref(false)

const commentInput = ref(null)

const fetchFeed = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response =
      await postService.getAllPosts()

    posts.value = response.data
  } catch (error) {
    console.error(
      'Failed to load feed:',
      error,
    )

    errorMessage.value =
      'Feed could not be loaded.'
  } finally {
    isLoading.value = false
  }
}

const openProfile = (post) => {
  router.push({
    name: 'user-posts',

    params: {
      id: post.user,
    },
  })
}

const loadComments = async (
  postId,
) => {
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
      'Failed to load comments:',
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

  document.body.style.overflow =
    'hidden'

  await loadComments(
    post.id,
  )

  await nextTick()

  commentInput.value?.focus()
}

const closePost = () => {
  selectedPost.value = null

  comments.value = []
  newComment.value = ''

  commentsErrorMessage.value = ''

  document.body.style.overflow = ''
}

const createComment = async () => {
  const body =
    newComment.value.trim()

  if (
    !body
    || !selectedPost.value
    || isCreatingComment.value
    || !authStore.can(
      'comments.create',
    )
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

    comments.value.push(
      response.data,
    )

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

const getInitial = (value) => {
  if (!value) {
    return '?'
  }

  return value
    .trim()
    .charAt(0)
    .toUpperCase()
}

onMounted(() => {
  fetchFeed()
})
</script>

<template>
  <section class="feed-page">
    <div class="feed-header">
      <div>
        <h1>Feed</h1>

        <p>
          See what people are sharing.
        </p>
      </div>
    </div>

    <p
      v-if="errorMessage"
      class="
        page-state
        page-state--error
      "
    >
      {{ errorMessage }}
    </p>

    <p
      v-if="isLoading"
      class="page-state"
    >
      Loading feed...
    </p>

    <p
      v-else-if="posts.length === 0"
      class="page-state"
    >
      No posts yet.
    </p>

    <div
      v-else
      class="feed"
    >
      <article
        v-for="post in posts"
        :key="post.id"
        class="feed-card"
      >
        <button
          type="button"
          class="feed-author"
          @click="openProfile(post)"
        >
          <span
            class="feed-author__avatar"
          >
            {{
              getInitial(
                post.display_name
                || post.username,
              )
            }}
          </span>

          <span
            class="feed-author__info"
          >
            <strong>
              {{
                post.display_name
                || post.username
                || 'User'
              }}
            </strong>

            <small
              v-if="post.username"
            >
              @{{ post.username }}
            </small>
          </span>
        </button>

        <div
          class="feed-card__content"
        >
          <h2>
            {{ post.title }}
          </h2>

          <p>
            {{ post.body }}
          </p>
        </div>

        <div
          class="feed-card__footer"
        >
          <button
            type="button"
            class="comments-button"
            @click="openPost(post)"
          >
            <IconMessageCircle
              :size="17"
              :stroke-width="1.8"
            />

            <span>
              View comments
            </span>
          </button>
        </div>
      </article>
    </div>

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
          >
            <button
              type="button"
              class="post-modal__close"
              aria-label="Close"
              @click="closePost"
            >
              <IconX
                :size="18"
                :stroke-width="1.8"
              />
            </button>

            <div
              class="post-modal__post"
            >
              <button
                type="button"
                class="modal-author"
                @click="
                  openProfile(
                    selectedPost,
                  )
                "
              >
                <span
                  class="
                    modal-author__avatar
                  "
                >
                  {{
                    getInitial(
                      selectedPost.display_name
                      || selectedPost.username,
                    )
                  }}
                </span>

                <span
                  class="
                    modal-author__info
                  "
                >
                  <strong>
                    {{
                      selectedPost.display_name
                      || selectedPost.username
                      || 'User'
                    }}
                  </strong>

                  <small
                    v-if="
                      selectedPost.username
                    "
                  >
                    @{{
                      selectedPost.username
                    }}
                  </small>
                </span>
              </button>

              <h2>
                {{ selectedPost.title }}
              </h2>

              <p>
                {{ selectedPost.body }}
              </p>
            </div>

            <div
              class="
                post-modal__comments
              "
            >
              <div
                class="comments-header"
              >
                <IconMessageCircle
                  :size="17"
                  :stroke-width="1.8"
                />

                <h3>
                  Comments
                </h3>
              </div>

              <div
                class="
                  comments-content
                "
              >
                <p
                  v-if="
                    isCommentsLoading
                  "
                  class="comments-state"
                >
                  Loading comments...
                </p>

                <p
                  v-else-if="
                    commentsErrorMessage
                    && comments.length
                      === 0
                  "
                  class="
                    comments-state
                    comments-state--error
                  "
                >
                  {{
                    commentsErrorMessage
                  }}
                </p>

                <p
                  v-else-if="
                    comments.length === 0
                  "
                  class="comments-state"
                >
                  No comments yet.
                </p>

                <div
                  v-else
                  class="comments-list"
                >
                  <article
                    v-for="
                      comment in comments
                    "
                    :key="comment.id"
                    class="comment"
                  >
                    <div
                      class="
                        comment__avatar
                      "
                    >
                      {{
                        getInitial(
                          comment.display_name,
                        )
                      }}
                    </div>

                    <div
                      class="
                        comment__content
                      "
                    >
                      <strong>
                        {{
                          comment.display_name
                          || 'User'
                        }}
                      </strong>

                      <p>
                        {{ comment.body }}
                      </p>
                    </div>
                  </article>
                </div>
              </div>

              <form
                v-if="
                  authStore.can(
                    'comments.create',
                  )
                "
                class="
                  comment-composer
                "
                @submit.prevent="
                  createComment
                "
              >
                <input
                  ref="commentInput"
                  v-model="newComment"
                  type="text"
                  placeholder="
                    Add a comment...
                  "
                  autocomplete="off"
                  :disabled="
                    isCreatingComment
                  "
                />

                <button
                  type="submit"
                  aria-label="
                    Send comment
                  "
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
                class="comments-error"
              >
                {{
                  commentsErrorMessage
                }}
              </p>
            </div>
          </section>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>

<style scoped>
.feed-page {
  width: min(100% - 40px, 760px);

  margin: 0 auto;

  padding:
    32px 0
    56px;
}

.feed-header {
  margin-bottom: 24px;
}

.feed-header h1 {
  margin: 0;

  color: var(--color-title);

  font-size: 28px;
  font-weight: 700;
}

.feed-header p {
  margin: 6px 0 0;

  color: var(--color-subtitle);

  font-size: 13px;
}

.page-state {
  margin: 24px 0;

  color: var(--color-subtitle);

  font-size: 13px;
}

.page-state--error {
  color: #b42318;
}

.feed {
  display: flex;
  flex-direction: column;

  gap: 18px;
}

.feed-card {
  overflow: hidden;

  background: #ffffff;

  border:
    1px solid var(--color-border);

  border-radius: 14px;

  box-shadow:
    0 5px 18px
    rgba(30, 34, 45, 0.045);
}

.feed-author {
  width: 100%;

  display: flex;
  align-items: center;

  gap: 10px;

  padding: 15px 18px;

  font: inherit;
  text-align: left;

  background: transparent;

  border: 0;

  cursor: pointer;
}

.feed-author:hover
.feed-author__info strong {
  color: var(--color-primary);
}

.feed-author__avatar,
.modal-author__avatar,
.comment__avatar {
  flex-shrink: 0;

  display: grid;
  place-items: center;

  color: var(--color-primary);

  font-weight: 700;

  background: #f0eef6;

  border-radius: 50%;
}

.feed-author__avatar {
  width: 38px;
  height: 38px;

  font-size: 12px;
}

.feed-author__info,
.modal-author__info {
  min-width: 0;

  display: flex;
  flex-direction: column;

  gap: 2px;
}

.feed-author__info strong,
.modal-author__info strong {
  color: var(--color-title);

  font-size: 12px;
  font-weight: 600;
}

.feed-author__info small,
.modal-author__info small {
  color: var(--color-subtitle);

  font-size: 10px;
}

.feed-card__content {
  padding:
    4px 18px
    22px;
}

.feed-card__content h2 {
  margin: 0 0 10px;

  color: var(--color-title);

  font-size: 16px;
  font-weight: 650;
}

.feed-card__content p {
  margin: 0;

  color: var(--color-subtitle);

  font-size: 13px;
  line-height: 1.7;

  white-space: pre-line;
}

.feed-card__footer {
  padding: 10px 14px;

  border-top:
    1px solid var(--color-border);
}

.comments-button {
  display: inline-flex;
  align-items: center;

  gap: 7px;

  padding: 7px 8px;

  color: var(--color-subtitle);

  font: inherit;
  font-size: 11px;
  font-weight: 600;

  background: transparent;

  border: 0;
  border-radius: 7px;

  cursor: pointer;
}

.comments-button:hover {
  color: var(--color-primary);

  background:
    rgba(82, 63, 158, 0.06);
}

.modal-backdrop {
  position: fixed;

  inset: 0;

  z-index: 1000;

  display: grid;
  place-items: center;

  padding: 28px;

  background:
    rgba(32, 37, 45, 0.42);
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

  z-index: 5;

  width: 29px;
  height: 29px;

  display: grid;
  place-items: center;

  padding: 0;

  color: var(--color-title);

  background: #ffffff;

  border: 0;
  border-radius: 7px;

  cursor: pointer;
}

.post-modal__post {
  overflow-y: auto;

  padding: 30px 28px;
}

.modal-author {
  display: flex;
  align-items: center;

  gap: 9px;

  margin: 0 0 24px;
  padding: 0;

  font: inherit;
  text-align: left;

  background: transparent;

  border: 0;

  cursor: pointer;
}

.modal-author__avatar {
  width: 34px;
  height: 34px;

  font-size: 11px;
}

.post-modal__post h2 {
  margin: 0 0 15px;

  color: var(--color-title);

  font-size: 17px;
}

.post-modal__post p {
  margin: 0;

  color: var(--color-subtitle);

  font-size: 13px;
  line-height: 1.7;

  white-space: pre-line;
}

.post-modal__comments {
  min-width: 0;
  min-height: 0;

  display: flex;
  flex-direction: column;

  border-left:
    1px solid var(--color-border);
}

.comments-header {
  display: flex;
  align-items: center;

  gap: 7px;

  padding:
    28px 48px
    18px 24px;
}

.comments-header h3 {
  margin: 0;

  color: var(--color-title);

  font-size: 15px;
}

.comments-content {
  min-height: 0;

  flex: 1;

  overflow-y: auto;

  padding:
    0 24px
    18px;
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

  font-size: 10px;
}

.comment__content {
  min-width: 0;
}

.comment__content strong {
  display: block;

  margin-bottom: 4px;

  color: var(--color-title);

  font-size: 11px;
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

.comment-composer {
  display: flex;
  align-items: center;

  gap: 8px;

  padding: 12px 14px;

  border-top:
    1px solid var(--color-border);
}

.comment-composer input {
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
}

.comment-composer input:focus {
  background: #ffffff;

  border-color:
    rgba(82, 63, 158, 0.3);
}

.comment-composer button {
  width: 32px;
  height: 32px;

  display: grid;
  place-items: center;

  padding: 0;

  color: var(--color-primary);

  background: transparent;

  border: 0;
  border-radius: 50%;

  cursor: pointer;
}

.comment-composer button:disabled {
  cursor: not-allowed;

  opacity: 0.35;
}

.comments-error {
  margin: 0;

  padding:
    0 16px
    10px;

  color: #b42318;

  font-size: 11px;
}

.modal-enter-active,
.modal-leave-active {
  transition:
    opacity 0.18s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

@media (max-width: 760px) {
  .feed-page {
    width:
      min(
        100% - 24px,
        760px
      );

    padding-top: 22px;
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
<script setup>
import {
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from 'vue'

import { useRoute } from 'vue-router'

import {
  IconCirclePlus,
  IconX,
} from '@tabler/icons-vue'

import postService from '../services/postService'

const route = useRoute()

const posts = ref([])
const selectedPost = ref(null)
const comments = ref([])

const isLoading = ref(false)
const isCommentsLoading = ref(false)

const errorMessage = ref('')
const commentsErrorMessage = ref('')

const fetchPosts = async (userId) => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response =
      await postService.getPostsByUser(userId)

    posts.value = response.data
  } catch (error) {
    console.error('Failed to fetch posts:', error)

    errorMessage.value =
      'Posts could not be loaded.'
  } finally {
    isLoading.value = false
  }
}

const openPost = async (post) => {
  selectedPost.value = post
  comments.value = []
  commentsErrorMessage.value = ''
  isCommentsLoading.value = true

  document.body.style.overflow = 'hidden'

  try {
    const response =
      await postService.getCommentsByPost(post.id)

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

const closePost = () => {
  selectedPost.value = null
  comments.value = []
  commentsErrorMessage.value = ''

  document.body.style.overflow = ''
}

const handleKeydown = (event) => {
  if (
    event.key === 'Escape' &&
    selectedPost.value
  ) {
    closePost()
  }
}

watch(
  () => route.params.id,
  (userId) => {
    if (userId) {
      posts.value = []
      closePost()
      fetchPosts(userId)
    }
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

const getInitial = (displayName) => {
  return displayName?.charAt(0).toUpperCase() || '?'
}

</script>

<template>
  <section class="posts-page">
    <h1>Posts</h1>

    <p
      v-if="isLoading"
      class="posts-state"
    >
      Loading posts...
    </p>

    <p
      v-else-if="errorMessage"
      class="posts-state posts-state--error"
    >
      {{ errorMessage }}
    </p>

    <p
      v-else-if="posts.length === 0"
      class="posts-state"
    >
      No posts found.
    </p>

    <!-- POST LIST -->

    <div
      v-else
      class="posts-list"
    >
      <article
        v-for="post in posts"
        :key="post.id"
        class="post-row"
      >
        <div class="post-row__content">
          <h2>
            {{ post.title }}
          </h2>

          <p>
            {{ post.body }}
          </p>
        </div>

        <button
          type="button"
          class="post-row__more"
          @click="openPost(post)"
        >
          <span>See More</span>

          <IconCirclePlus
            :size="17"
            :stroke-width="1.8"
          />
        </button>
      </article>
    </div>

    <!-- POST DETAIL MODAL -->

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

            <!-- LEFT SIDE -->

            <div class="post-modal__post">
              <h2 id="post-modal-title">
                {{ selectedPost.title }}
              </h2>

              <p>
                {{ selectedPost.body }}
              </p>
            </div>

            <!-- RIGHT SIDE -->

            <div class="post-modal__comments">
              <h3>Comments</h3>

              <p
                v-if="isCommentsLoading"
                class="comments-state"
              >
                Loading comments...
              </p>

              <p
                v-else-if="commentsErrorMessage"
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
                    {{ getInitial(comment.display_name) }}
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
          </section>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>

<style scoped>
.posts-page h1 {
  margin: 0 0 24px;

  color: var(--color-title);
  font-size: 28px;
  font-weight: 700;
}

/* -------------------------
   POST LIST
------------------------- */

.posts-list {
  border-top: 1px solid var(--color-border);
}

.post-row {
  min-height: 115px;

  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;

  box-sizing: border-box;
  padding: 18px 18px 16px;

  border-bottom:
    1px solid var(--color-border);
}

.post-row__content {
  max-width: 700px;
}

.post-row h2 {
  margin: 0 0 8px;

  color: var(--color-title);
  font-size: 14px;
  font-weight: 600;
}

.post-row p {
  margin: 0;

  color: var(--color-subtitle);
  font-size: 12px;
  line-height: 1.55;
}

.post-row__more {
  flex-shrink: 0;

  display: inline-flex;
  align-items: center;
  gap: 8px;

  padding: 6px 7px;

  color: var(--color-title);

  font: inherit;
  font-size: 11px;
  font-weight: 600;

  background: transparent;
  border: 0;
  border-radius: 7px;

  cursor: pointer;

  transition:
    color 0.18s ease,
    background-color 0.18s ease;
}

.post-row__more svg {
  color: var(--color-primary);
}

.post-row__more:hover {
  color: var(--color-primary);

  background:
    rgba(82, 63, 158, 0.06);
}

/* -------------------------
   MODAL BACKDROP
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

/* -------------------------
   MODAL
------------------------- */

.post-modal {
  position: relative;

  width: min(760px, 90vw);
  height: min(460px, 76vh);

  display: grid;
  grid-template-columns:
    minmax(0, 1.15fr)
    minmax(260px, 0.85fr);

  overflow: hidden;

  background: #ffffff;
  border-radius: 16px;

  box-shadow:
    0 24px 60px rgba(25, 30, 42, 0.2);
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

  z-index: 2;

  transition:
    color 0.18s ease,
    background-color 0.18s ease;
}

.post-modal__close:hover {
  color: var(--color-primary);

  background:
    rgba(82, 63, 158, 0.07);
}

/* -------------------------
   POST DETAIL
------------------------- */

.post-modal__post {
  overflow-y: auto;

  padding: 28px 26px;
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
  overflow-y: auto;

  padding: 28px 24px;

  border-left:
    1px solid var(--color-border);
}

.post-modal__comments h3 {
  margin: 0 0 20px;

  color: var(--color-title);
  font-size: 15px;
  font-weight: 600;
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
  font-weight: 600;

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

.comments-state,
.posts-state {
  color: var(--color-subtitle);
  font-size: 13px;
}

.comments-state--error,
.posts-state--error {
  color: #b42318;
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
  transform: translateY(8px) scale(0.985);
}

/* -------------------------
   MOBILE
------------------------- */

@media (max-width: 760px) {
  .post-modal {
    height: min(650px, 88vh);

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

  .post-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .post-row__more {
    align-self: flex-end;
  }
}
</style>
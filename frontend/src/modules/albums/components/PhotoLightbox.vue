<script setup>
import {
  onBeforeUnmount,
  onMounted,
  ref,
} from 'vue'

import {
  IconX,
} from '@tabler/icons-vue'

defineProps({
  photo: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits([
  'close',
])

const isZoomed = ref(false)

const toggleZoom = () => {
  isZoomed.value =
    !isZoomed.value
}

const close = () => {
  emit('close')
}

const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    close()
  }
}

onMounted(() => {
  document.addEventListener(
    'keydown',
    handleKeydown,
  )

  document.body.style.overflow =
    'hidden'
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
  <Teleport to="body">
    <div
      class="lightbox"
      @click.self="close"
    >
      <button
        type="button"
        class="lightbox__close"
        aria-label="Close image preview"
        @click="close"
      >
        <IconX
          :size="26"
          :stroke-width="1.8"
        />
      </button>

      <div
        class="lightbox__content"
      >
        <img
          :src="photo.image"
          :alt="
            photo.title
            || 'Album photo'
          "
          class="lightbox__image"
          :class="{
            'lightbox__image--zoomed':
              isZoomed,
          }"
          @dblclick="
            toggleZoom
          "
        />

        <p
          v-if="photo.title"
          class="lightbox__title"
        >
          {{ photo.title }}
        </p>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.lightbox {
  position: fixed;

  inset: 0;

  z-index: 2000;

  display: flex;
  align-items: center;
  justify-content: center;

  box-sizing: border-box;

  padding: 40px 70px;

  background:
    rgba(12, 12, 16, 0.82);

  backdrop-filter:
    blur(3px);
}

.lightbox__content {
  max-width: 92vw;
  max-height: 92vh;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  gap: 12px;
}

.lightbox__image {
  transform-origin: center center;
  display: block;

  max-width: 90vw;
  max-height: 84vh;

  width: auto;
  height: auto;

  object-fit: contain;

  border-radius: 10px;

  box-shadow:
    0 20px 60px
    rgba(0, 0, 0, 0.35);

  cursor: zoom-in;

  transition:
    transform 0.2s ease;
}

.lightbox__image--zoomed {
  transform: scale(1.7);

  cursor: zoom-out;
}

.lightbox__title {
  max-width: 760px;

  margin: 0;

  overflow: hidden;

  color: #ffffff;

  font-size: 13px;
  font-weight: 500;

  text-align: center;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.lightbox__close {
  position: fixed;

  top: 22px;
  right: 24px;

  width: 42px;
  height: 42px;

  display: grid;
  place-items: center;

  padding: 0;

  color: #ffffff;

  background:
    rgba(255, 255, 255, 0.1);

  border: 0;
  border-radius: 50%;

  cursor: pointer;

  transition:
    background 0.16s ease,
    transform 0.16s ease;
}

.lightbox__close:hover {
  background:
    rgba(255, 255, 255, 0.18);

  transform: scale(1.05);
}

@media (max-width: 650px) {
  .lightbox {
    padding: 24px 16px;
  }

  .lightbox__image {
    max-width: 94vw;
    max-height: 82vh;
  }

  .lightbox__close {
    top: 14px;
    right: 14px;
  }
}
</style>
<script setup>
import {
  IconBuilding,
  IconMapPin,
  IconPencil,
  IconWorld,
} from '@tabler/icons-vue'

defineProps({
  user: {
    type: Object,
    required: true,
  },

  canEdit: {
    type: Boolean,
    default: false,
  },
})

defineEmits([
  'select',
  'edit',
])
</script>

<template>
  <article
    class="user-card"
    tabindex="0"
    role="button"
    @click="$emit('select', user.id)"
    @keydown.enter="$emit('select', user.id)"
  >
    <button
      v-if="canEdit"
      type="button"
      class="user-card__edit"
      aria-label="Edit user profile"
      @click.stop="$emit('edit', user.id)"
    >
      <IconPencil
        :size="15"
        :stroke-width="1.8"
      />
    </button>

    <div class="user-card__profile">
      <div class="user-card__avatar">
        <img
          v-if="user.profile_photo"
          :src="user.profile_photo"
          alt=""
          class="user-card__avatar-image"
        >

        <span v-else>
          {{
            (
              user.display_name
              || user.username
              || '?'
            )
              .charAt(0)
              .toUpperCase()
          }}
        </span>
      </div>

      <div class="user-card__identity">
        <h2>
          {{
            user.display_name
            || user.username
          }}
        </h2>

        <p class="user-card__username">
          @{{ user.username }}
        </p>

        <p class="user-card__email">
          {{ user.email }}
        </p>

        <span
          v-if="user.phone_number"
          class="user-card__phone"
        >
          {{ user.phone_number }}
        </span>
      </div>
    </div>

    <div class="user-card__details">
      <div class="user-card__detail">
        <IconMapPin
          :size="18"
          stroke-width="1.7"
        />

        <div>
          <strong>Location</strong>

          <p>
            {{ user.location || '-' }}
          </p>
        </div>
      </div>

      <div class="user-card__detail">
        <IconBuilding
          :size="18"
          stroke-width="1.7"
        />

        <div>
          <strong>Company</strong>

          <p>
            {{ user.company?.name || '-' }}
          </p>
        </div>
      </div>

      <div class="user-card__detail">
        <IconWorld
          :size="18"
          stroke-width="1.7"
        />

        <div>
          <strong>Website</strong>

          <p>
            {{ user.website || '-' }}
          </p>
        </div>
      </div>
    </div>
  </article>
</template>

<style scoped>
.user-card {
  position: relative;

  min-width: 0;
  min-height: 285px;

  overflow: hidden;

  padding: 20px;

  background: var(--color-white);

  border: 1px solid var(--color-border);
  border-radius: 10px;

  cursor: pointer;

  transition:
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.user-card:hover {
  transform: translateY(-2px);

  box-shadow:
    0 8px 24px
    rgb(38 48 62 / 12%);
}

.user-card__edit {
  position: absolute;
  top: 14px;
  right: 14px;

  width: 31px;
  height: 31px;

  display: grid;
  place-items: center;

  padding: 0;

  color: var(--color-subtitle);

  background: transparent;

  border: 0;
  border-radius: 8px;

  cursor: pointer;

  transition:
    color 0.18s ease,
    background-color 0.18s ease;
}

.user-card__edit:hover {
  color: var(--color-primary);

  background:
    rgba(82, 63, 158, 0.07);
}

.user-card__edit:focus-visible {
  outline: none;

  box-shadow:
    0 0 0 3px
    rgba(82, 63, 158, 0.12);
}

.user-card__profile {
  display: flex;
  align-items: center;
  gap: 14px;

  padding-right: 36px;
  margin-bottom: 28px;
}

.user-card__avatar {
  width: 58px;
  height: 58px;

  flex-shrink: 0;

  display: grid;
  place-items: center;

  overflow: hidden;

  color: var(--color-primary);

  font-size: 20px;
  font-weight: 600;

  background: #eeeeee;

  border-radius: 50%;
}

.user-card__avatar-image {
  width: 100%;
  height: 100%;

  display: block;

  object-fit: cover;
}

.user-card__identity {
  min-width: 0;
  flex: 1;
}

.user-card__identity h2 {
  overflow: hidden;

  margin: 0 0 4px;

  color: var(--color-title);

  font-size: 14px;
  font-weight: 600;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-card__username,
.user-card__email,
.user-card__phone {
  overflow: hidden;

  margin: 0;

  color: var(--color-subtitle);

  font-size: 11px;
  font-weight: 400;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-card__username {
  margin-bottom: 2px;

  color: #626875;
}

.user-card__details {
  min-width: 0;

  display: flex;
  flex-direction: column;
  gap: 15px;
}

.user-card__detail {
  min-width: 0;

  display: flex;
  align-items: flex-start;
  gap: 10px;

  color: var(--color-title);
}

.user-card__detail > div {
  min-width: 0;
  flex: 1;
}

.user-card__detail strong {
  display: block;

  margin-bottom: 2px;

  font-size: 12px;
  font-weight: 600;
}

.user-card__detail p {
  margin: 0;

  overflow-wrap: anywhere;

  color: var(--color-subtitle);

  font-size: 11px;
  line-height: 1.45;
}
</style>
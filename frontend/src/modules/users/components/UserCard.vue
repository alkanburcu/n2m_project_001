<script setup>
import {
  IconBuilding,
  IconMapPin,
  IconWorld,
} from '@tabler/icons-vue'

defineProps({
  user: {
    type: Object,
    required: true,
  },
})
defineEmits(['select'])
</script>

<template>
  <article
  class="user-card"
  tabindex="0"
  role="button"
  @click="$emit('select', user.id)"
  @keydown.enter="$emit('select', user.id)">
    <div class="user-card__profile">
      <div class="user-card__avatar">
        {{ (user.name || user.username).charAt(0).toUpperCase() }}
      </div>

      <div class="user-card__identity">
        <h2>{{ user.name || user.username }}</h2>
        <p>{{ user.email }}</p>

        <span v-if="user.phone_number">
          {{ user.phone_number }}
        </span>
      </div>
    </div>

    <div class="user-card__details">
      <div class="user-card__detail">
        <IconMapPin :size="18" stroke-width="1.7" />

        <div>
          <strong>Location</strong>
          <p v-if="user.addresses">
            {{ user.addresses.street }}<br />
            {{ user.addresses.city }}
          </p>
          <p v-else>-</p>
        </div>
      </div>

      <div class="user-card__detail">
        <IconBuilding :size="18" stroke-width="1.7" />

        <div>
          <strong>Company</strong>
          <p>{{ user.company?.name || '-' }}</p>
        </div>
      </div>

      <div class="user-card__detail">
        <IconWorld :size="18" stroke-width="1.7" />

        <div>
          <strong>Website</strong>
          <p>{{ user.website || '-' }}</p>
        </div>
      </div>
    </div>
  </article>
</template>

<style scoped>
.user-card {
  min-width: 0;
  overflow: hidden;
  min-height: 285px;
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
  box-shadow: 0 8px 24px rgb(38 48 62 / 12%);
}

.user-card__profile {
  display: flex;
  align-items: center;
  gap: 14px;

  margin-bottom: 28px;
}

.user-card__avatar {
  width: 58px;
  height: 58px;
  flex-shrink: 0;

  display: grid;
  place-items: center;

  border-radius: 50%;

  background: #eee;
  color: var(--color-primary);

  font-size: 20px;
  font-weight: 600;
}

.user-card__identity h2 {
  flex: 1;
  min-width: 0;
  margin: 0 0 3px;

  color: var(--color-title);

  font-size: 15px;
  font-weight: 600;
}

.user-card__identity h2,
.user-card__identity p,
.user-card__identity span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
  margin: 0;

  color: var(--color-subtitle);

  font-size: 11px;
  font-weight: 400;
}

.user-card__details {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.user-card__details > div {
  flex: 1;
  min-width: 0
}
.user-card__detail {
  display: flex;
  align-items: flex-start;
  gap: 10px;

  color: var(--color-title);
}

.user-card__detail strong {
  display: block;

  margin-bottom: 2px;

  font-size: 12px;
  font-weight: 600;
}

.user-card__detail p {
  overflow-wrap: anywhere;
  margin: 0;

  color: var(--color-subtitle);

  font-size: 11px;
  line-height: 1.45;
}
</style>
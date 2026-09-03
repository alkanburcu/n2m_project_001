<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
} from 'vue'

import {
  IconArrowLeft,
  IconChevronDown,
  IconLogout,
  IconUser,
} from '@tabler/icons-vue'

import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/modules/auth/store/authStore'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isMenuOpen = ref(false)
const isLoggingOut = ref(false)
const menuRef = ref(null)

/* HOME NAVIGATION */

const homeRoute = computed(() => {
  // User listesini görme yetkisi olan kullanıcıların
  // ana sayfası Users listesi.
  if (authStore.can('users.list')) {
    return {
      name: 'users',
    }
  }

  // Normal kullanıcı için kendi Todos sayfası ana sayfa.
  return {
    name: 'user-todos',
    params: {
      id: authStore.user?.id,
    },
  }
})

const isHomePage = computed(() => {
  if (authStore.can('users.list')) {
    return route.name === 'users'
  }

  return (
    route.name === 'user-todos' &&
    String(route.params.id) === String(authStore.user?.id)
  )
})

const goHome = async () => {
  await router.push(homeRoute.value)
}

/* ACCOUNT MENU */

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const closeMenu = () => {
  isMenuOpen.value = false
}

/*LOGOUT */

const handleLogout = async () => {
  isLoggingOut.value = true

  try {
    await authStore.logout()
  } finally {
    closeMenu()
    isLoggingOut.value = false

    await router.replace('/login')
  }
}

/* CLICK OUTSIDE */

const handleClickOutside = (event) => {
  if (
    menuRef.value &&
    !menuRef.value.contains(event.target)
  ) {
    closeMenu()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <header class="app-header">
    <!-- LEFT SIDE -->
    <div class="app-header__left">
      <button
        v-if="!isHomePage"
        type="button"
        class="home-button"
        @click="goHome"
      >
        <IconArrowLeft
          :size="17"
          :stroke-width="1.9"
        />

        <span>Go Home</span>
      </button>
    </div>

    <!-- RIGHT SIDE -->
    <div
      ref="menuRef"
      class="account"
    >
      <button
        type="button"
        class="account__trigger"
        aria-label="Account menu"
        :aria-expanded="isMenuOpen"
        @click.stop="toggleMenu"
      >
        <IconUser
          :size="19"
          :stroke-width="1.8"
        />

        <IconChevronDown
          :size="13"
          :stroke-width="2"
          class="account__chevron"
          :class="{
            'account__chevron--open': isMenuOpen,
          }"
        />
      </button>

      <Transition name="dropdown">
        <div
          v-if="isMenuOpen"
          class="account-dropdown"
        >
          <button
            type="button"
            class="account-dropdown__logout"
            :disabled="isLoggingOut"
            @click="handleLogout"
          >
            <IconLogout
              :size="18"
              :stroke-width="1.8"
            />

            <span>
              {{
                isLoggingOut
                  ? 'Signing out...'
                  : 'Sign out'
              }}
            </span>
          </button>
        </div>
      </Transition>
    </div>
  </header>
</template>

<style scoped>

/* HEADER */

.app-header {
  position: fixed;
  top: 0;
  right: 0;
  left: var(--app-sidebar-width);

  height: var(--app-header-height);

  box-sizing: border-box;

  display: flex;
  align-items: center;
  justify-content: space-between;

  padding: 0 18px;

  background:
    linear-gradient(
      90deg,
      rgba(82, 63, 158, 0.055),
      rgba(82, 63, 158, 0.1)
    );

  border-bottom:
    1px solid rgba(82, 63, 158, 0.1);

  z-index: 20;
}

/* GO HOME*/

.app-header__left {
  min-width: 0;

  display: flex;
  align-items: center;
}

.home-button {
  height: 32px;

  display: inline-flex;
  align-items: center;
  gap: 7px;

  padding: 0 9px;

  color: var(--color-title);

  font: inherit;
  font-size: 13px;
  font-weight: 600;

  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;

  cursor: pointer;

  transition:
    color 0.18s ease,
    background-color 0.18s ease,
    border-color 0.18s ease;
}

.home-button:hover {
  color: var(--color-primary);

  background: rgba(255, 255, 255, 0.72);

  border-color:
    rgba(82, 63, 158, 0.12);
}

.home-button:focus-visible {
  outline: none;

  color: var(--color-primary);

  background: rgba(255, 255, 255, 0.72);

  box-shadow:
    0 0 0 3px rgba(82, 63, 158, 0.1);
}

/* ACCOUNT */

.account {
  position: relative;
  margin-left: auto;
}

.account__trigger {
  height: 34px;
  min-width: 43px;

  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;

  padding: 0 8px;

  color: var(--color-primary);

  background: rgba(255, 255, 255, 0.75);

  border:
    1px solid rgba(82, 63, 158, 0.16);

  border-radius: 9px;

  cursor: pointer;

  box-shadow:
    0 1px 3px rgba(41, 33, 77, 0.04);

  transition:
    background-color 0.18s ease,
    border-color 0.18s ease,
    box-shadow 0.18s ease;
}

.account__trigger:hover,
.account__trigger[aria-expanded='true'] {
  background: #ffffff;

  border-color:
    rgba(82, 63, 158, 0.32);

  box-shadow:
    0 3px 9px rgba(62, 47, 117, 0.1);
}

.account__chevron {
  transition:
    transform 0.18s ease;
}

.account__chevron--open {
  transform: rotate(180deg);
}

/* DROPDOWN */

.account-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;

  width: 132px;

  padding: 6px;

  background: #ffffff;

  border:
    1px solid var(--color-border);

  border-radius: 10px;

  box-shadow:
    0 12px 26px rgba(31, 36, 49, 0.1),
    0 2px 5px rgba(31, 36, 49, 0.04);
}

.account-dropdown__logout {
  width: 100%;

  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;

  padding: 8px 10px;

  color: var(--color-subtitle);

  font: inherit;
  font-size: 12.5px;
  font-weight: 500;

  background: transparent;
  border: 0;
  border-radius: 7px;

  cursor: pointer;

  transition:
    color 0.18s ease,
    background-color 0.18s ease;
}

.account-dropdown__logout:hover:not(:disabled) {
  color: #b42318;
  background: #fff3f2;
}

.account-dropdown__logout:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

  /*DROPDOWN ANIMATION*/


.dropdown-enter-active,
.dropdown-leave-active {
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
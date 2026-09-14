import {
  ref,
} from 'vue'

import {
  defineStore,
} from 'pinia'

const THEME_STORAGE_KEY = 'theme'

const THEMES = {
  LIGHT: 'light',
  DARK: 'dark',
}

export const useThemeStore = defineStore(
  'theme',
  () => {
    const theme = ref(THEMES.LIGHT)

    const applyTheme = () => {
      document.documentElement.dataset.theme =
        theme.value
    }

    const setTheme = (newTheme) => {
      if (!Object.values(THEMES).includes(newTheme)) {
        return
      }

      theme.value = newTheme

      localStorage.setItem(
        THEME_STORAGE_KEY,
        newTheme,
      )

      applyTheme()
    }

    const toggleTheme = () => {
      setTheme(
        theme.value === THEMES.LIGHT
          ? THEMES.DARK
          : THEMES.LIGHT,
      )
    }

    const initializeTheme = () => {
      const storedTheme =
        localStorage.getItem(
          THEME_STORAGE_KEY,
        )

      if (
        Object.values(THEMES).includes(
          storedTheme,
        )
      ) {
        theme.value = storedTheme
      }

      applyTheme()
    }

    return {
      theme,
      setTheme,
      toggleTheme,
      initializeTheme,
    }
  },
)
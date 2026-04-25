import { ref, watch } from 'vue'

const isDark = ref(localStorage.getItem('theme') !== 'light')

function applyTheme(dark) {
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
}

applyTheme(isDark.value)

watch(isDark, (dark) => {
  localStorage.setItem('theme', dark ? 'dark' : 'light')
  applyTheme(dark)
})

export function useTheme() {
  return {
    isDark,
    toggleTheme: () => { isDark.value = !isDark.value },
  }
}

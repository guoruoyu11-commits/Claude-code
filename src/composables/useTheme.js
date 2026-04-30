import { ref, watch } from 'vue'

const isSSR = typeof window === 'undefined'
const isDark = ref(isSSR ? true : localStorage.getItem('theme') !== 'light')

function applyTheme(dark) {
  if (isSSR) return
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
}

applyTheme(isDark.value)

watch(isDark, (dark) => {
  if (isSSR) return
  localStorage.setItem('theme', dark ? 'dark' : 'light')
  applyTheme(dark)
})

export function useTheme() {
  return {
    isDark,
    toggleTheme: () => { isDark.value = !isDark.value },
  }
}

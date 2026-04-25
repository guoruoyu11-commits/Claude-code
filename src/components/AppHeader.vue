<template>
  <header>
    <div class="header-inner">
      <a href="/" class="logo">
        <span class="logo-main">EXVSDB-CN</span>
        <span class="logo-divider">|</span>
        <span class="logo-sub">极限爆发</span>
      </a>
      <div class="header-badge">非官方</div>
      <button class="theme-toggle" @click="toggleTheme" :title="isDark ? '切换日间模式' : '切换夜间模式'">
        <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="5"/>
          <line x1="12" y1="1" x2="12" y2="3"/>
          <line x1="12" y1="21" x2="12" y2="23"/>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
          <line x1="1" y1="12" x2="3" y2="12"/>
          <line x1="21" y1="12" x2="23" y2="12"/>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      </button>
    </div>
  </header>
</template>

<script setup>
import { useTheme } from '../composables/useTheme.js'

const { isDark, toggleTheme } = useTheme()
</script>

<style scoped>
header {
  background: linear-gradient(180deg, var(--header-bg-top) 0%, var(--header-bg-bottom) 100%);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 20px var(--header-shadow);
  transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

/* red accent line at very top */
header::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, var(--accent) 20%, var(--accent) 80%, transparent 100%);
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px;
  height: 54px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.logo-main {
  font-family: var(--font-ui);
  font-size: 22px;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: 3px;
  text-shadow: 0 0 20px var(--accent-glow);
}

.logo-divider {
  color: var(--border-bright);
  font-size: 16px;
  font-weight: 300;
}

.logo-sub {
  font-size: 11px;
  font-weight: 400;
  color: var(--text-muted);
  letter-spacing: 1px;
  white-space: nowrap;
}

.header-badge {
  font-family: var(--font-ui);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--text-muted);
  border: 1px solid var(--border-bright);
  padding: 2px 7px;
  border-radius: 3px;
  margin-left: auto;
}

.theme-toggle {
  background: transparent;
  border: 1px solid var(--border-bright);
  color: var(--text-muted);
  border-radius: 6px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: color 0.15s ease, border-color 0.15s ease, background 0.15s ease;
}

.theme-toggle:hover {
  color: var(--text-primary);
  border-color: var(--accent);
  background: var(--accent-glow);
}
</style>

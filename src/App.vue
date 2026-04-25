<template>
  <AppHeader />
  <RouterView />
  <footer>
    <p>EXVSDB - 极限爆发数据库 &nbsp;|&nbsp; 高达 EXVS.2 极限爆发 非官方数据库</p>
    <p>※ 本站与万代南梦宫娱乐株式会社没有任何关联。</p>
    <p>© 机动战士高达 EXVS.2 极限爆发 ™ &amp; © BANDAI NAMCO Entertainment Inc.</p>
  </footer>
</template>

<script setup>
import { RouterView } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import { useTheme } from './composables/useTheme.js'

useTheme()
</script>

<style scoped>
footer {
  margin-top: 60px;
  padding: 28px 24px;
  border-top: 1px solid var(--border);
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.9;
  opacity: .7;
}
</style>

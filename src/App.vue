<template>
  <AppHeader />
  <RouterView />
  <footer>
    <p>EXVSDB - エクバデータベース &nbsp;|&nbsp; ガンダム EXVS.2 インフィニットブースト 非公式データベース</p>
    <p>※ 本サイトはバンダイナムコエンターテインメント株式会社とは一切関係ありません。</p>
    <p>© 機動戦士ガンダム EXVS.2 インフィニットブースト ™ &amp; © BANDAI NAMCO Entertainment Inc.</p>
  </footer>
</template>

<script setup>
import { RouterView } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
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

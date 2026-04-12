<template>
  <AppHeader />

  <main>
    <!-- Breadcrumb -->
    <nav class="breadcrumb" aria-label="breadcrumb">
      <a href="#">EXVSDB</a><span>›</span>
      <a href="#">イニブ</a><span>›</span>
      機体ランク・Tier表
    </nav>

    <!-- Title -->
    <h1>【2026年4月最新】イニブ機体ランク・Tier表</h1>
    <p class="update-meta">
      最終更新：<b>2026年4月12日</b>　|　対象バージョン：インフィニットブースト Ver.2.40
    </p>

    <!-- Description -->
    <div class="desc-box">
      ガンダム EXVS.2 インフィニットブースト（イニブ）の<b>機体ランク・Tier表</b>です。<br />
      対戦勝率・使用率・上位プレイヤー実績をもとに独自ランク付けしています。
      コストタブでフィルタリングして確認できます。ランクはあくまでも参考情報です。
    </div>

    <!-- Cost filter -->
    <CostFilter v-model="selectedCost" />

    <!-- Tier table -->
    <TierTable :machines="filteredMachines" />
  </main>

  <footer>
    <p>EXVSDB - エクバデータベース &nbsp;|&nbsp; ガンダム EXVS.2 インフィニットブースト 非公式データベース</p>
    <p>※ 本サイトはバンダイナムコエンターテインメント株式会社とは一切関係ありません。</p>
    <p>© 機動戦士ガンダム EXVS.2 インフィニットブースト ™ &amp; © BANDAI NAMCO Entertainment Inc.</p>
  </footer>
</template>

<script setup>
import { ref, computed } from 'vue'
import { MACHINES } from './data/machines.js'
import AppHeader from './components/AppHeader.vue'
import CostFilter from './components/CostFilter.vue'
import TierTable  from './components/TierTable.vue'

const selectedCost = ref('3000')

const filteredMachines = computed(() =>
  MACHINES.filter(m => String(m.cost) === selectedCost.value)
)
</script>

<style scoped>
main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 28px 20px 60px;
}

.breadcrumb {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 14px;
}
.breadcrumb a { color: var(--accent); }
.breadcrumb a:hover { text-decoration: underline; }
.breadcrumb span { margin: 0 5px; }

h1 {
  font-size: 21px;
  font-weight: 700;
  line-height: 1.4;
  margin-bottom: 6px;
}

.update-meta {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 16px;
}
.update-meta b { color: var(--text-primary); }

.desc-box {
  background: var(--bg-secondary);
  border-left: 3px solid var(--accent);
  border-radius: 0 6px 6px 0;
  padding: 12px 16px;
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.7;
  margin-bottom: 28px;
}
.desc-box b { color: var(--text-primary); }

footer {
  margin-top: 50px;
  padding: 24px 20px;
  border-top: 1px solid var(--border);
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.8;
}

@media (max-width: 600px) {
  h1 { font-size: 17px; }
}
</style>

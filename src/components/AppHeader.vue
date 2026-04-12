<template>
  <header>
    <div class="header-inner">
      <a href="#" class="logo">
        EXVSDB<span class="logo-sub">エクバデータベース</span>
      </a>
    </div>
  </header>
</template>

<style scoped>
header {
  background: var(--bg-secondary);
  border-bottom: 2px solid var(--accent);
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
  height: 52px;
  display: flex;
  align-items: center;
}
.logo {
  font-size: 18px;
  font-weight: 900;
  color: var(--accent);
  text-decoration: none;
  letter-spacing: 2px;
  white-space: nowrap;
}
.logo-sub {
  font-size: 11px;
  font-weight: 400;
  color: var(--text-muted);
  letter-spacing: 0;
  margin-left: 6px;
}
</style>

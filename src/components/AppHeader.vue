<template>
  <header>
    <div class="header-inner">
      <a href="#" class="logo">
        <span class="logo-main">EXVSDB</span>
        <span class="logo-divider">|</span>
        <span class="logo-sub">エクバデータベース</span>
      </a>
      <div class="header-badge">非公式</div>
    </div>
  </header>
</template>

<style scoped>
header {
  background: linear-gradient(180deg, #0d1520 0%, #0a1018 100%);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 20px rgba(0,0,0,0.6);
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
</style>

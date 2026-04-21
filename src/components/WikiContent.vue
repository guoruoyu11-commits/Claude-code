<script>
import { h, ref, computed, watchEffect, defineComponent } from 'vue'

export default defineComponent({
  name: 'WikiContent',
  props: {
    nodes: { type: Array,  default: null },
    html:  { type: String, default: null }
  },
  setup(props) {
    const collapseStates = ref({})

    // ── HTML 路径：DOMParser（兼容旧数据） ──────────────────────
    const parsedBody = computed(() => {
      if (!props.html) return null
      const doc = new DOMParser().parseFromString(props.html, 'text/html')
      return doc.body
    })

    watchEffect(() => {
      if (!parsedBody.value) return
      parsedBody.value.querySelectorAll('.plugin-openclose').forEach((el, i) => {
        const key = `poc_${i}`
        if (key in collapseStates.value) return
        const contentsEl = el.querySelector('.plugin-openclose-contents')
        collapseStates.value[key] = !contentsEl || contentsEl.style.display !== 'none'
      })
    })

    // ── Nodes 路径：初始化折叠状态 ─────────────────────────────
    watchEffect(() => {
      if (!props.nodes) return
      let i = 0
      function walk(nodes) {
        for (const n of nodes) {
          if (n.t === 'collapse') {
            const key = `poc_${i++}`
            if (!(key in collapseStates.value)) {
              collapseStates.value[key] = n.open !== false
            }
            if (n.c) walk(n.c)
          } else if (n.c) {
            walk(n.c)
          }
        }
      }
      walk(props.nodes)
    })

    function toggle(key) {
      collapseStates.value[key] = !collapseStates.value[key]
    }

    // ── 渲染 JSON 节点 ─────────────────────────────────────────

    // 将含 \n 的文本展开为 [text, h('br'), text, ...] 数组
    function expandText(v) {
      const parts = v.split('\n')
      if (parts.length === 1) return v
      const result = []
      parts.forEach((p, i) => {
        if (p) result.push(p)
        if (i < parts.length - 1) result.push(h('br'))
      })
      return result
    }

    function renderJsonNode(n, poc) {
      if (n.t === '#') return n.v ? expandText(n.v) : null

      if (n.t === 'collapse') {
        const key = `poc_${poc.n++}`
        const isOpen = collapseStates.value[key] !== false
        const rawLabel = (n.label || '').replace(/^[▼▶]\s*/, '')
        const label = (isOpen ? '▼' : '▶') + (rawLabel ? ' ' + rawLabel : '')

        const inner = (n.c || []).map(c => renderJsonNode(c, poc)).flat().filter(Boolean)
        return h('div', { class: 'plugin-openclose' }, [
          h('div', { class: 'plugin-openclose-link' }, [
            h('a', { onClick: () => toggle(key) }, label)
          ]),
          h('div', { class: 'plugin-openclose-contents', style: isOpen ? '' : 'display:none' }, inner)
        ])
      }

      const tag = n.t
      const attrs = n.a ? { ...n.a } : {}

      // 外链新标签页打开；去掉 js void 链接
      if (tag === 'a') {
        if (attrs.href === 'javascript:void(0)') {
          delete attrs.href
        } else if (attrs.href && /^(https?:)?\/\//.test(attrs.href)) {
          attrs.target = '_blank'
          attrs.rel = 'noopener noreferrer'
        }
      }

      if (['br', 'hr', 'img', 'source'].includes(tag)) return h(tag, attrs)

      // v 字段：内联文本（可能含 \n）
      if (n.v !== undefined) {
        const textContent = expandText(n.v)
        return h(tag, attrs, Array.isArray(textContent) ? textContent : [textContent])
      }

      const children = (n.c || []).map(c => renderJsonNode(c, poc)).flat().filter(c => c !== null && c !== undefined)
      return h(tag, attrs, children.length ? children : undefined)
    }

    // ── 渲染 DOM 节点（兼容 html prop） ───────────────────────
    function renderDomNode(node, poc) {
      if (node.nodeType === 3) return node.textContent || null
      if (node.nodeType !== 1) return null

      const tag = node.tagName.toLowerCase()
      if (node.classList.contains('atwiki-ads-margin')) return null

      if (node.classList.contains('plugin-openclose')) {
        const key = `poc_${poc.n++}`
        const isOpen = collapseStates.value[key] !== false
        const linkEl = node.querySelector('.plugin-openclose-link a')
        const rawText = linkEl?.textContent?.trim().replace(/^[▼▶]\s*/, '') ?? ''
        const label = (isOpen ? '▼' : '▶') + (rawText ? ' ' + rawText : '')
        const contentsEl = node.querySelector('.plugin-openclose-contents')
        const inner = contentsEl
          ? Array.from(contentsEl.childNodes).map(c => renderDomNode(c, poc)).filter(Boolean)
          : []
        return h('div', { class: 'plugin-openclose' }, [
          h('div', { class: 'plugin-openclose-link' }, [
            h('a', { onClick: () => toggle(key) }, label)
          ]),
          h('div', { class: 'plugin-openclose-contents', style: isOpen ? '' : 'display:none' }, inner)
        ])
      }

      const attrs = {}
      if (node.id) attrs.id = node.id
      if (node.className) attrs.class = node.className
      const styleAttr = node.getAttribute('style')
      if (styleAttr) attrs.style = styleAttr

      if (tag === 'a') {
        const href = node.getAttribute('href')
        if (href && href !== 'javascript:void(0)') {
          attrs.href = href
          if (/^(https?:)?\/\//.test(href)) {
            attrs.target = '_blank'
            attrs.rel = 'noopener noreferrer'
          }
        }
      }

      for (const attr of [
        'src', 'alt', 'width', 'height', 'srcset', 'type', 'media',
        'rowspan', 'colspan', 'bgcolor', 'align', 'valign'
      ]) {
        const v = node.getAttribute(attr)
        if (v !== null) attrs[attr] = v
      }

      if (['br', 'hr', 'img', 'source'].includes(tag)) return h(tag, attrs)

      const children = Array.from(node.childNodes)
        .map(c => renderDomNode(c, poc))
        .filter(c => c !== null && c !== undefined)
      return h(tag, attrs, children.length ? children : undefined)
    }

    return () => {
      const poc = { n: 0 }

      if (props.nodes) {
        const children = props.nodes.map(n => renderJsonNode(n, poc)).filter(Boolean)
        return h('div', { class: 'wiki-content' }, children)
      }

      if (parsedBody.value) {
        const children = Array.from(parsedBody.value.childNodes)
          .map(c => renderDomNode(c, poc))
          .filter(Boolean)
        return h('div', { class: 'wiki-content' }, children)
      }

      return h('div', { class: 'wiki-content' })
    }
  }
})
</script>

<style scoped>
.wiki-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 28px 32px;
  line-height: 1.8;
  font-size: 14px;
  color: var(--text-primary);
}

.wiki-content h1,
.wiki-content h2,
.wiki-content h3 {
  color: var(--text-primary);
  margin: 1.2em 0 0.5em;
  font-weight: 700;
  border-bottom: 1px solid var(--border);
  padding-bottom: 4px;
}

.wiki-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
  font-size: 13px;
}
.wiki-content th,
.wiki-content td {
  border: 1px solid var(--border);
  padding: 6px 10px;
  text-align: left;
}
.wiki-content th {
  background: rgba(255,255,255,0.05);
  color: var(--text-primary);
  font-weight: 600;
}

.wiki-content a {
  color: var(--accent);
  text-decoration: none;
}
.wiki-content a:hover { text-decoration: underline; }

.wiki-content img { max-width: 100%; border-radius: 4px; }

/* atwiki 折叠目次块 */
.plugin-openclose { margin: 12px 0; }

.plugin-openclose-link {
  display: inline-block;
  padding: 4px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 13px;
  color: var(--accent);
  user-select: none;
  transition: background .15s;
}
.plugin-openclose-link:hover { background: rgba(255,255,255,0.06); }
.plugin-openclose-link a { cursor: pointer; }

.plugin-openclose-contents {
  margin-top: 6px;
  border: 1px solid var(--border) !important;
  border-radius: 4px;
  padding: 12px 16px !important;
  background: var(--bg-secondary);
}

/* atwiki 背景色的 td 强制用深色文字 */
.wiki-content :deep(td[style*="background-color"]),
.wiki-content :deep(th[style*="background-color"]),
.wiki-content :deep(span[style*="background-color"]) {
  color: #111 !important;
}

/* 隐藏残余 atwiki 广告占位 */
.wiki-content :deep(.atwiki-ads-margin),
.wiki-content :deep([class*="atwiki_autoads"]),
.wiki-content :deep([id^="gpt-"]) {
  display: none !important;
}

@media (max-width: 600px) {
  .wiki-content { padding: 16px; }
}
</style>

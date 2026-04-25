<script>
import { h, ref, computed, watchEffect, defineComponent } from 'vue'

export default defineComponent({
  name: 'WikiContent',
  props: {
    nodes:     { type: Array,  default: null },
    html:      { type: String, default: null },
    subPages:  { type: Array,  default: () => [] }, // [{file, url}, ...]
    parentUrl: { type: String, default: '' },        // 主页面 wiki URL，用于子页面中的返回链接
    machineId: { type: String, default: '' },        // 当前机体 ID，用于生成 SPA 内部链接
  },
  emits: ['select-sub'],
  setup(props, { emit }) {
    const collapseStates = ref({})

    // 兼容旧数据：html prop 通过 DOMParser 渲染
    const parsedBody = computed(() => {
      if (!props.html) return null
      return new DOMParser().parseFromString(props.html, 'text/html').body
    })

    function setDefaultCollapse(key, isOpen) {
      if (!(key in collapseStates.value)) collapseStates.value[key] = isOpen
    }

    watchEffect(() => {
      if (!parsedBody.value) return
      parsedBody.value.querySelectorAll('.plugin-openclose').forEach((el, i) => {
        const contentsEl = el.querySelector('.plugin-openclose-contents')
        setDefaultCollapse(`poc_${i}`, !contentsEl || contentsEl.style.display !== 'none')
      })
    })

    watchEffect(() => {
      if (!props.nodes) return
      let i = 0
      function walk(nodes) {
        for (const n of nodes) {
          if (n.t === 'collapse') {
            setDefaultCollapse(`poc_${i++}`, n.open !== false)
          }
          if (n.c) walk(n.c)
        }
      }
      walk(props.nodes)
    })

    function toggle(key) {
      collapseStates.value[key] = !collapseStates.value[key]
    }

    function renderCollapse(key, rawLabel, inner) {
      const isOpen = collapseStates.value[key] !== false
      const label = (isOpen ? '▼' : '▶') + (rawLabel ? ' ' + rawLabel : '')
      return h('div', { class: 'plugin-openclose' }, [
        h('div', { class: 'plugin-openclose-link' }, [
          h('a', { onClick: () => toggle(key) }, label)
        ]),
        h('div', { class: 'plugin-openclose-contents', style: isOpen ? '' : 'display:none' }, inner)
      ])
    }

    const EXTERNAL_URL_RE = /^(https?:)?\/\//
    const ALLOWED_EXTERNAL_RE = /^https?:\/\/web\.vsmobile\.jp/
    const VOID_TAGS = ['br', 'hr', 'img', 'source']

    function applyExternalLink(attrs) {
      attrs.target = '_blank'
      attrs.rel = 'noopener noreferrer'
    }

    function addClass(attrs, cls) {
      attrs.class = attrs.class ? `${attrs.class} ${cls}` : cls
    }

    // 将含 \n 的文本展开为 [text, <br>, text, ...]
    function expandText(v) {
      if (!v.includes('\n')) return v
      const parts = v.split('\n')
      const result = []
      parts.forEach((p, i) => {
        if (p) result.push(p)
        if (i < parts.length - 1) result.push(h('br'))
      })
      return result
    }

    function resolveAnchorAttrs(attrs) {
      const href = attrs.href || ''
      const pageNumMatch = href.match(/\/pages\/(\d+)\.html/)

      if (pageNumMatch) {
        const pageNum = pageNumMatch[1]
        const subPage = props.subPages.find(sp => sp.url.includes(`/pages/${pageNum}.html`))
        if (subPage) {
          attrs.href = props.machineId ? `/machine/${props.machineId}?sub=${subPage.file}` : subPage.url
          attrs.onClick = (e) => { e.preventDefault(); emit('select-sub', subPage.file) }
          addClass(attrs, 'local-link')
          return
        }
        if (props.parentUrl && props.parentUrl.includes(`/pages/${pageNum}.html`)) {
          attrs.href = props.machineId ? `/machine/${props.machineId}` : props.parentUrl
          attrs.onClick = (e) => { e.preventDefault(); emit('select-sub', null) }
          addClass(attrs, 'local-link')
          return
        }
      } else if (href === 'javascript:void(0)') {
        delete attrs.href
        return
      }

      if (EXTERNAL_URL_RE.test(href)) {
        if (ALLOWED_EXTERNAL_RE.test(href)) applyExternalLink(attrs)
        else delete attrs.href
      }
    }

    function renderJsonNode(n, poc) {
      if (n.t === '#') return n.v ? expandText(n.v) : null

      if (n.t === 'collapse') {
        const key = `poc_${poc.n++}`
        const rawLabel = (n.label || '').replace(/^[▼▶]\s*/, '')
        const inner = (n.c || []).flatMap(c => renderJsonNode(c, poc)).filter(Boolean)
        return renderCollapse(key, rawLabel, inner)
      }

      const tag = n.t
      const attrs = n.a ? { ...n.a } : {}

      if (tag === 'a') resolveAnchorAttrs(attrs)

      if (VOID_TAGS.includes(tag)) return h(tag, attrs)

      if (n.v !== undefined) {
        const textContent = expandText(n.v)
        return h(tag, attrs, Array.isArray(textContent) ? textContent : [textContent])
      }

      const children = (n.c || []).flatMap(c => renderJsonNode(c, poc)).filter(c => c != null)
      return h(tag, attrs, children.length ? children : undefined)
    }

    const DOM_PASSTHROUGH_ATTRS = [
      'src', 'alt', 'width', 'height', 'srcset', 'type', 'media',
      'rowspan', 'colspan', 'bgcolor', 'align', 'valign'
    ]

    function renderDomNode(node, poc) {
      if (node.nodeType === 3) return node.textContent || null
      if (node.nodeType !== 1) return null

      const tag = node.tagName.toLowerCase()
      if (node.classList.contains('atwiki-ads-margin')) return null

      if (node.classList.contains('plugin-openclose')) {
        const key = `poc_${poc.n++}`
        const linkEl = node.querySelector('.plugin-openclose-link a')
        const rawLabel = linkEl?.textContent?.trim().replace(/^[▼▶]\s*/, '') ?? ''
        const contentsEl = node.querySelector('.plugin-openclose-contents')
        const inner = contentsEl
          ? Array.from(contentsEl.childNodes).map(c => renderDomNode(c, poc)).filter(Boolean)
          : []
        return renderCollapse(key, rawLabel, inner)
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
          if (EXTERNAL_URL_RE.test(href)) {
            if (ALLOWED_EXTERNAL_RE.test(href)) applyExternalLink(attrs)
            else delete attrs.href
          }
        }
      }

      for (const attr of DOM_PASSTHROUGH_ATTRS) {
        const v = node.getAttribute(attr)
        if (v !== null) attrs[attr] = v
      }

      if (VOID_TAGS.includes(tag)) return h(tag, attrs)

      const children = Array.from(node.childNodes)
        .map(c => renderDomNode(c, poc))
        .filter(c => c != null)
      return h(tag, attrs, children.length ? children : undefined)
    }

    const REF_SECTION_RE = /参考|外部[リ链]/

    function filterTocUl(n) {
      if (n.t !== 'ul' && n.t !== 'ol') return n
      const filtered = (n.c || [])
        .filter(li => {
          const anchor = (li.c || []).find(c => c.t === 'a')
          return !anchor || !REF_SECTION_RE.test(anchor.v || '')
        })
        .map(li => ({ ...li, c: (li.c || []).map(c => filterTocUl(c)) }))
      return { ...n, c: filtered }
    }

    function filterRefSection(nodes) {
      let skip = false
      return nodes
        .filter(n => {
          if ((n.t === 'h2' || n.t === 'h3') && typeof n.v === 'string') {
            skip = REF_SECTION_RE.test(n.v)
          }
          return !skip
        })
        .map(n => {
          if (n.t !== 'collapse') return n
          return {
            ...n,
            c: (n.c || []).map(child =>
              child.t === 'div' && child.a?.class?.includes('plugin_contents')
                ? { ...child, c: (child.c || []).map(filterTocUl) }
                : child
            )
          }
        })
    }

    return () => {
      const poc = { n: 0 }

      if (props.nodes) {
        const children = filterRefSection(props.nodes).map(n => renderJsonNode(n, poc)).filter(Boolean)
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
  margin: 12px 0;
  font-size: 13px;
  display: block;
  overflow-x: auto;
  width: max-content;
  max-width: 100%;
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
.wiki-content a.local-link { cursor: pointer; }

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
.plugin-openclose-contents ul,
.plugin-openclose-contents ol {
  list-style: none;
  margin: 0;
  padding: 0;
}
.plugin-openclose-contents li { padding: 2px 0; }

.wiki-content :deep(ul),
.wiki-content :deep(ol) {
  list-style: none;
  margin: 0;
  padding: 0;
}
.wiki-content :deep(li) { padding: 2px 0; }

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

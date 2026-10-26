/**
 * HTML sanitising for admin-authored rich text.
 *
 * Anything that ends up in `v-html` must go through `sanitizeHtml()` first.
 * The admin editors store real HTML (headings, lists, links, emphasis), which
 * `v-html` will happily inject into the page — including `<script>`, `onerror=`
 * handlers and `javascript:` URLs, so unsanitised rendering is a stored-XSS hole.
 *
 * DOMPurify is allow-list based: anything not explicitly permitted is removed,
 * so this fails closed. Rendering goes through `safeHtml()`, which sanitises on
 * the way out, so content that predates the editors (or arrives from elsewhere)
 * is cleaned too rather than trusted.
 */
import DOMPurify from 'dompurify'

// Tags an editor legitimately produces. `style` is deliberately absent: inline
// styles are the usual way to smuggle in `position:fixed` overlays and
// `expression()`-style tricks, and nothing in the content needs them.
const ALLOWED_TAGS = [
  'p', 'br', 'hr', 'div', 'span',
  'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
  'strong', 'b', 'em', 'i', 'u', 's', 'sub', 'sup', 'mark', 'small',
  'ul', 'ol', 'li',
  'blockquote', 'pre', 'code',
  'a', 'img',
  'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'caption',
]

const ALLOWED_ATTR = [
  'href', 'title', 'target', 'rel',
  'src', 'alt', 'width', 'height',
  'colspan', 'rowspan', 'dir',
]

let hookInstalled = false

function installHook () {
  if (hookInstalled) return
  hookInstalled = true

  DOMPurify.addHook('afterSanitizeAttributes', (node) => {
    // DOMPurify hard-codes an allowance for `data:` URIs on media tags
    // (img/audio/video/source/image/track) and that branch runs *before*
    // ALLOWED_URI_REGEXP, so a `data:text/html` payload would otherwise survive
    // in an <img src>. Nothing in the content needs data: URIs — uploads are
    // served over http(s) — so drop them here.
    for (const attr of ['src', 'href', 'xlink:href', 'poster']) {
      const value = node.getAttribute?.(attr)
      if (typeof value === 'string' && value.trim().toLowerCase().startsWith('data:')) {
        node.removeAttribute(attr)
      }
    }

    // Every link leaves in a new tab, and `noopener`/`noreferrer` deny the opened
    // page any handle on `window.opener`.
    if (node.tagName === 'A' && node.hasAttribute('href')) {
      node.setAttribute('target', '_blank')
      node.setAttribute('rel', 'noopener noreferrer')
    }
  })
}

/**
 * Clean untrusted HTML, returning a string safe to hand to `v-html`.
 * @param {unknown} html
 * @returns {string}
 */
export function sanitizeHtml (html) {
  if (html === null || html === undefined || html === '') return ''
  installHook()
  return DOMPurify.sanitize(String(html), {
    ALLOWED_TAGS,
    ALLOWED_ATTR,
    // No data: URIs, no scripts, no iframes — images may still be referenced by
    // the same origin or by https, which is what the uploads actually produce.
    ALLOWED_URI_REGEXP: /^(?:https?:|mailto:|tel:|\/|#|\.\/)/i,
    FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed', 'form', 'input', 'link', 'meta'],
    FORBID_ATTR: ['style', 'srcset', 'formaction', 'xlink:href'],
    KEEP_CONTENT: true,
  })
}

/**
 * Computed property for templates: `v-html="safeHtml(product.description)"`.
 */
export function safeHtml (html) {
  return sanitizeHtml(html)
}

/**
 * Collapse an HTML fragment to plain text — for meta descriptions, previews and
 * any other place the raw markup would be shown literally.
 */
export function htmlToText (html, maxLength = 0) {
  if (!html) return ''
  const stripped = sanitizeHtml(html)
    .replace(/<\/(p|div|h[1-6]|li|tr)>/gi, ' ')
    .replace(/<br\s*\/?>/gi, ' ')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .replace(/\s+/g, ' ')
    .trim()

  if (maxLength > 0 && stripped.length > maxLength) {
    return `${stripped.slice(0, maxLength).trimEnd()}…`
  }
  return stripped
}

export default { sanitizeHtml, safeHtml, htmlToText }

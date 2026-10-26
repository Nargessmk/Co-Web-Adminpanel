/**
 * Per-page SEO metadata for Quasar v2.
 *
 * Conforms strictly to Quasar's useMeta schema:
 * - title: string
 * - meta: { [key]: { name/property: string, content: string } }
 * - link: { [key]: { rel: string, href: string } }
 * - script: { [key]: { type: string, innerHTML: string } }
 */
import { useMeta } from 'quasar'

export const SITE_ORIGIN = 'https://ailand.ai'

/** Trim a description to a sensible SERP length without cutting mid-word. */
function clip (text, max = 160) {
  const value = (text || '').replace(/\s+/g, ' ').trim()
  if (value.length <= max) return value
  const cut = value.slice(0, max)
  const lastSpace = cut.lastIndexOf(' ')
  return `${(lastSpace > max * 0.6 ? cut.slice(0, lastSpace) : cut).trim()}…`
}

/**
 * Set title/description/canonical/OpenGraph for one page.
 * Accepts either an options object or a getter function returning an options object.
 *
 * @param {object|Function} options
 */
export function usePageMeta (options = {}) {
  useMeta(() => {
    const resolved = typeof options === 'function' ? options() : (options || {})
    const {
      title,
      description = '',
      path = '/',
      image,
      type = 'website',
      jsonLd
    } = resolved

    const url = SITE_ORIGIN + (path || '/')
    const fullTitle = title ? `${title} | CloudLand` : 'CloudLand'
    const desc = clip(description)

    return {
      title: fullTitle,

      meta: {
        description: { name: 'description', content: desc },

        // OpenGraph protocol tags
        ogTitle: { property: 'og:title', content: fullTitle },
        ogDescription: { property: 'og:description', content: desc },
        ogUrl: { property: 'og:url', content: url },
        ogType: { property: 'og:type', content: type },
        ...(image ? { ogImage: { property: 'og:image', content: image } } : {}),

        // Twitter Cards tags
        twitterCard: { name: 'twitter:card', content: 'summary_large_image' },
        twitterTitle: { name: 'twitter:title', content: fullTitle },
        twitterDescription: { name: 'twitter:description', content: desc },
        ...(image ? { twitterImage: { name: 'twitter:image', content: image } } : {})
      },

      link: {
        canonical: { rel: 'canonical', href: url }
      },

      script: jsonLd
        ? {
            ldJson: {
              type: 'application/ld+json',
              innerHTML: JSON.stringify({
                '@context': 'https://schema.org',
                ...jsonLd,
              }),
            }
          }
        : {}
    }
  })
}

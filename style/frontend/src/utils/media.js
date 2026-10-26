/**
 * Media and image URL normalizer and fallback handler.
 * Ensures consistent handling of S3 object keys, local uploads, and static assets.
 */

export const DEFAULT_ARTICLE_IMAGE = '/uploads/articles/edge-computing.jpg'
export const DEFAULT_TECH_IMAGE = '/uploads/home/contact-datacenter.jpg'
export const S3_BASE = 'https://s3.ailand.ai/cloudland'

/**
 * Normalizes any image or file URL into a valid browser-fetchable URL.
 * Supports:
 * - Full URLs: https://... or http://...
 * - S3 object keys: solutions/abc.png, products/xyz.jpg -> https://s3.ailand.ai/cloudland/...
 * - Local uploads: /uploads/... or uploads/... -> /uploads/...
 * - Static assets: /assets/... or /images/...
 */
export function formatMediaUrl(url, fallback = DEFAULT_ARTICLE_IMAGE) {
  if (!url || typeof url !== 'string') return fallback
  const trimmed = url.trim()
  if (!trimmed) return fallback

  // Already a full URL
  if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
    return trimmed
  }

  // Blob or Data URLs (e.g. from local file previews)
  if (trimmed.startsWith('blob:') || trimmed.startsWith('data:')) {
    return trimmed
  }

  // Local uploads path
  if (trimmed.startsWith('/uploads/')) {
    return trimmed
  }
  if (trimmed.startsWith('uploads/')) {
    return '/' + trimmed
  }

  // Known S3 folder prefixes
  if (/^(solutions|products|catalogs|team|media)\//i.test(trimmed)) {
    return `${S3_BASE}/${trimmed}`
  }

  // Static site assets starting with slash (e.g. /assets/articles/..., /images/...)
  if (trimmed.startsWith('/')) {
    return trimmed
  }

  // Object keys containing folder structure
  if (trimmed.includes('/') && !trimmed.includes(' ')) {
    return `${S3_BASE}/${trimmed}`
  }

  return '/' + trimmed
}

/**
 * Image error handler to safely switch to a fallback without loops.
 */
export function handleImageError(event, fallback = DEFAULT_ARTICLE_IMAGE) {
  const el = event?.target
  if (el) {
    el.onerror = null
    el.src = fallback
  }
}

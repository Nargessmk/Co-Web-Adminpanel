<template>
  <q-page class="article-detail-page-new">

    <!-- 0. Reading Progress Bar -->
    <div class="reading-progress-track">
      <div class="reading-progress-fill" :style="{ width: `${scrollProgress}%` }"></div>
    </div>

    <!-- 1. Loading State -->
    <div v-if="loading" class="detail-loading-state">
      <div class="luxury-spinner"></div>
      <p>در حال بارگذاری مقاله تخصصی و مستندات...</p>
    </div>

    <!-- 2. Not Found State -->
    <div v-else-if="!article" class="detail-not-found-state">
      <div class="not-found-icon-wrap">
        <q-icon name="article" size="56px" color="grey-6" />
      </div>
      <h2>مقاله یافت نشد</h2>
      <p>مقاله مورد نظر وجود ندارد یا غیرفعال شده است.</p>
      <router-link :to="backRoute" class="btn-pill btn-pill-yellow">
        <q-icon name="arrow_forward" size="16px" />
        <span>{{ isArticleRoute ? 'بازگشت به مقالات مهندسی' : 'بازگشت به راهکارها' }}</span>
      </router-link>
    </div>

    <!-- 3. Article Content -->
    <template v-else>
      <!-- Top Navigation & Breadcrumbs Bar -->
      <section class="article-nav-section">
        <div class="container">
          <div class="detail-nav-bar">
            <router-link :to="backRoute" class="back-nav-pill">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
              </svg>
              <span>{{ isArticleRoute ? 'بازگشت به همه مقالات' : 'بازگشت به راهکارها' }}</span>
            </router-link>

            <div class="detail-badges-wrap">
              <span class="category-tag-pill">
                <span class="tag-dot"></span>
                <span>{{ articleCategory }}</span>
              </span>

              <span class="meta-item-pill">
                <q-icon name="schedule" size="14px" />
                <span>{{ articleReadTime }}</span>
              </span>

              <span class="meta-item-pill" v-if="articleDate">
                <q-icon name="event" size="14px" />
                <span>{{ articleDate }}</span>
              </span>

              <router-link
                v-if="isAdmin"
                to="/admin/solutions"
                class="btn-pill btn-pill-dark btn-pill-sm mr-2"
              >
                <q-icon name="settings" size="14px" />
                <span>مدیریت مقالات در پنل ادمین</span>
              </router-link>
            </div>
          </div>
        </div>
      </section>

      <!-- Hero Header Section -->
      <section class="article-hero-section">
        <div class="container">
          <div class="article-hero-head">
            <div class="section-tag">
              <span class="tag-dot"></span>
              <span>{{ isArticleRoute ? 'پایگاه دانش و تحلیل‌های مهندسی' : (settings.detail_eyebrow || 'راهکار ابری و سازمانی') }}</span>
            </div>

            <h1 class="article-main-title">{{ articleTitle }}</h1>

            <!-- Summary / Excerpt Highlight Card -->
            <div v-if="articleExcerpt" class="article-lead-box">
              <p>{{ articleExcerpt }}</p>
            </div>

            <!-- Author & Sharing Bar -->
            <div class="article-author-bar">
              <div class="author-info-group">
                <img
                  :src="authorAvatar"
                  :alt="authorName"
                  class="author-avatar"
                  @error="e => handleImageError(e)"
                />
                <div class="author-text-meta">
                  <div class="author-name">{{ authorName }}</div>
                  <div class="author-role">{{ authorRole }}</div>
                </div>
              </div>

              <div class="header-action-group">
                <button
                  type="button"
                  class="btn-pill btn-pill-dark btn-pill-sm"
                  :class="{ 'btn-pill-copied': linkCopied }"
                  @click="copyArticleLink"
                  title="کپی لینک مقاله"
                >
                  <q-icon :name="linkCopied ? 'done' : 'share'" size="14px" />
                  <span>{{ linkCopied ? 'لینک کپی شد' : 'اشتراک‌گذاری' }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Featured Cover Image -->
          <div v-if="articleImage" class="article-cover-frame">
            <img
              :src="articleImage"
              :alt="articleTitle"
              fetchpriority="high"
              decoding="async"
              @error="e => handleImageError(e)"
            />
            <div class="cover-topic-chip" v-if="articleTopic">
              <span class="chip-dot"></span>
              <span>{{ articleTopic }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Main Article Editorial Layout -->
      <section class="article-body-section">
        <div class="container">
          <div class="article-editorial-grid">
            <!-- Main Content Column -->
            <main class="article-content-column">
              <div class="article-card-paper">
                <!-- Rich Content Prose -->
                <div class="article-prose" v-html="processedHtml"></div>

                <!-- Showcase for Related Product (Inside main content card, right after descriptions) -->
                <div v-if="relatedProduct" class="article-related-product-spotlight">
                  <div class="product-spotlight-inner">
                    <!-- Product Media Thumbnail -->
                    <div class="spotlight-media-wrap">
                      <img
                        :src="relatedProduct.image"
                        :alt="relatedProduct.title"
                        loading="lazy"
                        @error="e => handleImageError(e)"
                      />
                      <div class="spotlight-media-badge">سامانه سازمانی</div>
                    </div>

                    <!-- Product Content & CTA -->
                    <div class="spotlight-content-wrap">
                      <div class="spotlight-badge-row">
                        <span class="spotlight-tag">
                          <span class="pulse-beacon"></span>
                          <span>محصول و سامانه مرتبط با این راهکار</span>
                        </span>
                        <span class="spotlight-status-pill" v-if="relatedProduct.badge">
                          {{ relatedProduct.badge }}
                        </span>
                      </div>

                      <h3 class="spotlight-title">{{ relatedProduct.title }}</h3>

                      <p class="spotlight-desc" v-if="relatedProduct.description">
                        {{ relatedProduct.description }}
                      </p>

                      <div class="spotlight-actions-row">
                        <router-link
                          :to="`/products/${relatedProduct.slug}`"
                          class="btn-pill btn-pill-yellow btn-pill-sm"
                        >
                          <span class="btn-text">مشاهده مشخصات و دمو سامانه</span>
                          <span class="btn-icon-bubble">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                              <path d="M5 12h14"></path>
                              <path d="M12 5l7 7-7 7"></path>
                            </svg>
                          </span>
                        </router-link>

                        <router-link
                          to="/contact"
                          class="btn-pill btn-pill-dark btn-pill-sm"
                        >
                          <q-icon name="support_agent" size="14px" />
                          <span>درخواست استقرار و مشاوره</span>
                        </router-link>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Tags List -->
                <div v-if="tagsList.length" class="article-tags-container">
                  <span class="tags-headline">برچسب‌های موضوعی:</span>
                  <div class="tags-flex">
                    <span v-for="tag in tagsList" :key="tag" class="tag-chip">
                      #{{ tag }}
                    </span>
                  </div>
                </div>

                <!-- End Article Share & Navigation -->
                <div class="article-bottom-actions">
                  <div class="share-box-bottom">
                    <span class="share-label">اشتراک‌گذاری این مطلب:</span>
                    <div class="share-pills-row">
                      <a :href="shareTelegramUrl" target="_blank" rel="noopener noreferrer" class="social-pill tg">
                        تلگرام
                      </a>
                      <a :href="shareTwitterUrl" target="_blank" rel="noopener noreferrer" class="social-pill tw">
                        توییتر (X)
                      </a>
                      <a :href="shareLinkedinUrl" target="_blank" rel="noopener noreferrer" class="social-pill in">
                        لینکدین
                      </a>
                      <button type="button" class="social-pill copy" @click="copyArticleLink">
                        {{ linkCopied ? 'کپی شد ✓' : 'کپی لینک' }}
                      </button>
                    </div>
                  </div>

                  <div class="end-nav-row">
                    <router-link :to="backRoute" class="btn-pill btn-pill-dark btn-pill-sm">
                      <q-icon name="arrow_forward" size="14px" />
                      <span>{{ isArticleRoute ? 'سایر مقالات مهندسی' : (settings.detail_others_label || 'سایر راهکارها') }}</span>
                    </router-link>
                    <router-link to="/contact" class="btn-pill btn-pill-yellow btn-pill-sm">
                      <span>{{ settings.detail_consult_label || 'درخواست مشاوره فنی' }}</span>
                      <span class="btn-icon-bubble">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                          <path d="M5 12h14"></path>
                          <path d="M12 5l7 7-7 7"></path>
                        </svg>
                      </span>
                    </router-link>
                  </div>
                </div>
              </div>
            </main>

            <!-- Sticky Sidebar Column -->
            <aside class="article-sidebar-column">
              <div class="sidebar-sticky-wrapper">
                <!-- Author Bento Card -->
                <div class="sidebar-bento-box author-bento">
                  <div class="sidebar-box-head">
                    <span class="dot-indicator"></span>
                    <span>درباره نویسنده</span>
                  </div>

                  <div class="author-bento-profile">
                    <img
                      :src="authorAvatar"
                      :alt="authorName"
                      class="author-bento-avatar"
                      @error="e => handleImageError(e)"
                    />
                    <div class="author-bento-info">
                      <h4 class="author-bento-name">{{ authorName }}</h4>
                      <p class="author-bento-role">{{ authorRole }}</p>
                    </div>
                  </div>

                  <router-link
                    v-if="article.author_id"
                    :to="`/about#team-member-${article.author_id}`"
                    class="author-bento-link"
                  >
                    <span>مشاهده پروفایل در تیم کهکشان</span>
                    <q-icon name="arrow_back" size="14px" />
                  </router-link>
                </div>

                <!-- Source Citation Card (if linked) -->
                <div v-if="article.source_url || article.source_title" class="sidebar-bento-box source-bento">
                  <div class="sidebar-box-head">
                    <q-icon name="verified" size="16px" color="amber-8" />
                    <span>{{ settings.detail_source_label || 'مرجع و منبع مقاله' }}</span>
                  </div>

                  <a
                    v-if="article.source_url"
                    :href="article.source_url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="source-bento-link"
                  >
                    <span>{{ article.source_title || article.source_url }}</span>
                    <q-icon name="open_in_new" size="14px" />
                  </a>
                  <p v-else class="source-bento-text">{{ article.source_title }}</p>
                </div>

                <!-- Quick Consultation Banner -->
                <div class="sidebar-bento-box consult-bento">
                  <h4 class="consult-title">مشاوره تخصصی و استقرار راهکار</h4>
                  <p class="consult-text">
                    برای پیاده‌سازی این الگوها یا ارزیابی زیرساخت سازمان خود، با مهندسان کهکشان هوشمند گفتگو کنید.
                  </p>
                  <router-link to="/contact" class="btn-pill btn-pill-yellow btn-pill-sm full-width">
                    <span>درخواست جلسه مشاوره</span>
                    <span class="btn-icon-bubble">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <path d="M5 12h14"></path>
                        <path d="M12 5l7 7-7 7"></path>
                      </svg>
                    </span>
                  </router-link>
                </div>
              </div>
            </aside>
          </div>
        </div>
      </section>

      <!-- 4. Related Suggested Articles -->
      <section v-if="relatedArticles.length" class="related-articles-section">
        <div class="container">
          <div class="related-head-bar">
            <div class="section-tag">
              <span class="tag-dot"></span>
              <span>مطالعه بیشتر</span>
            </div>
            <h2 class="related-title">سایر مقالات مهندسی و پیشنهادی</h2>
          </div>

          <div class="related-cards-grid">
            <article
              v-for="rel in relatedArticles"
              :key="rel.id || rel.slug"
              class="article-card"
              @click="navigateToArticle(rel)"
            >
              <div class="card-thumb-wrap">
                <img :src="rel.image" :alt="rel.title" loading="lazy" @error="e => handleImageError(e)" />
                <span class="card-cat-pill">{{ rel.category }}</span>
              </div>

              <div class="card-body">
                <div class="card-meta">
                  <span class="read-pill">{{ rel.readTime }}</span>
                  <span class="dot-sep">•</span>
                  <span>{{ rel.date }}</span>
                </div>

                <h3 class="card-title">{{ rel.title }}</h3>
                <p class="card-excerpt">{{ rel.excerpt }}</p>
              </div>

              <div class="card-footer">
                <div class="author-mini">
                  <img :src="rel.authorAvatar" class="mini-avatar" alt="" />
                  <span class="mini-name">{{ rel.authorName }}</span>
                </div>
                <div class="read-action">
                  <span>مطالعه مقاله</span>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M5 12h14"></path>
                    <path d="M12 5l7 7-7 7"></path>
                  </svg>
                </div>
              </div>
            </article>
          </div>
        </div>
      </section>

      <!-- 5. Unified Bottom Consultation CTA -->
      <CloudlandCTA page-name="مقاله" />
    </template>

  </q-page>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import moment from 'moment-jalaali'
import api from 'src/services/api'
import { usePageMeta, SITE_ORIGIN } from 'src/composables/usePageMeta'
import { useAuth } from 'src/composables/useAuth'
import { useSolutionsContent } from 'src/composables/useSolutionsContent'
import { formatMediaUrl, handleImageError, DEFAULT_ARTICLE_IMAGE } from 'src/utils/media'
import { safeHtml } from 'src/utils/sanitize'
import CloudlandCTA from 'src/components/CTA/CloudlandCTA.vue'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()

const { isAdmin } = useAuth()
const { settings, loadSettings } = useSolutionsContent()

const article = ref(null)
const loading = ref(true)
const relatedArticles = ref([])
const linkCopied = ref(false)
const scrollProgress = ref(0)

// --------------------------------------------------------------------------
// Computed Fields
// --------------------------------------------------------------------------
const isArticleRoute = computed(() => {
  const p = route.path.toLowerCase()
  return p.includes('article') || p.includes('blog')
})

const backRoute = computed(() => (isArticleRoute.value ? '/articles' : '/solutions'))

const articleTitle = computed(() => article.value?.title || '')

const articleExcerpt = computed(() => article.value?.summary || article.value?.excerpt || '')

const articleImage = computed(() => {
  const raw = article.value?.image_url || article.value?.image
  return raw ? formatMediaUrl(raw, DEFAULT_ARTICLE_IMAGE) : null
})

const articleCategory = computed(() => {
  return article.value?.category || (isArticleRoute.value ? 'پایگاه دانش' : 'راهکار تخصصی')
})

const articleReadTime = computed(() => {
  return article.value?.read_time || article.value?.readTime || '۵ دقیقه مطالعه'
})

const articleTopic = computed(() => {
  return article.value?.topic || article.value?.category || null
})

function formatDate (date) {
  if (!date) return ''
  return moment(date).format('jYYYY/jMM/jDD')
}

const articleDate = computed(() => {
  if (article.value?.date) return article.value.date
  if (article.value?.created_at) return formatDate(article.value.created_at)
  return 'شهریور ۱۴۰۵'
})

const authorName = computed(() => {
  return article.value?.author?.name || article.value?.author_name || 'تیم مهندسی کهکشان هوشمند'
})

const authorRole = computed(() => {
  return article.value?.author?.role || article.value?.author_role || 'معمار سیستم‌های ابری'
})

const authorAvatar = computed(() => {
  const raw = article.value?.author?.avatar || article.value?.author_image_url
  return formatMediaUrl(raw, '/Modern 3D Tech Dashboard Illustration(1).png')
})

const tagsList = computed(() => {
  const t = article.value?.tags
  if (Array.isArray(t)) return t.filter(Boolean)
  if (typeof t === 'string' && t.trim()) {
    try {
      const parsed = JSON.parse(t)
      if (Array.isArray(parsed)) return parsed.filter(Boolean)
    } catch {
      return t.split(',').map(s => s.trim()).filter(Boolean)
    }
  }
  return []
})

const loadedProducts = ref([])

async function loadProductsList () {
  try {
    const res = await api.get('/api/products', { params: { limit: 100 } })
    if (res?.data?.data && Array.isArray(res.data.data)) {
      loadedProducts.value = res.data.data
    }
  } catch (err) {
    console.warn('Could not load products list:', err)
  }
}

const relatedProduct = computed(() => {
  const item = article.value
  if (!item) return null

  // 1. Direct joined product fields from backend
  if (item.product_title || item.product_slug) {
    return {
      id: item.product_id || item.related_product_id,
      title: item.product_title,
      slug: item.product_slug || item.product_id,
      description: item.product_short_description || item.product_description || '',
      image: formatMediaUrl(item.product_image_url, '/Modern 3D Tech Dashboard Illustration(1).png'),
      badge: 'استقرار فعال سازمانی',
    }
  }

  // 2. Lookup by related_product_id or product_id in loadedProducts
  const pid = item.related_product_id || item.product_id
  if (pid && loadedProducts.value.length) {
    const found = loadedProducts.value.find(p => String(p.id) === String(pid))
    if (found) {
      return {
        id: found.id,
        title: found.title,
        slug: found.slug || found.id,
        description: found.short_description || found.description || '',
        image: formatMediaUrl(found.image_url, '/Modern 3D Tech Dashboard Illustration(1).png'),
        badge: found.badge || 'استقرار فعال سازمانی',
      }
    }
  }

  return null
})

// Markdown to HTML conversion if markdown syntax exists in article content
const processedHtml = computed(() => {
  const raw = article.value?.content
  if (!raw) return ''
  let text = String(raw).trim()

  // Headings
  text = text
    .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/gim, '<em>$1</em>')

  // Check if content is plain markdown without wrapper paragraphs
  if (!text.includes('<p>') && !text.includes('<div>')) {
    const blocks = text.split(/\n\s*\n/)
    text = blocks
      .map(block => {
        const b = block.trim()
        if (!b) return ''
        if (/^<h[1-6]/.test(b) || /^<ul/.test(b) || /^<ol/.test(b) || /^<blockquote/.test(b)) {
          return b
        }
        // Lists with - or *
        if (b.startsWith('- ') || b.includes('\n- ')) {
          const items = b.split(/\n?- /).filter(Boolean)
          return '<ul>' + items.map(it => `<li>${it.trim()}</li>`).join('') + '</ul>'
        }
        // Lists with numbered items (e.g. 1. or ۱.)
        if (/^[0-9۱-۹]\./.test(b)) {
          const items = b.split(/\n?[0-9۱-۹]\.\s*/).filter(Boolean)
          return '<ol>' + items.map(it => `<li>${it.trim()}</li>`).join('') + '</ol>'
        }
        return `<p>${b.replace(/\n/g, '<br>')}</p>`
      })
      .join('')
  }

  return safeHtml(text)
})

// Share URLs
const currentUrl = computed(() => {
  if (typeof window !== 'undefined') {
    return window.location.href
  }
  return `${SITE_ORIGIN}${route.path}`
})
const shareTelegramUrl = computed(() => `https://t.me/share/url?url=${encodeURIComponent(currentUrl.value)}&text=${encodeURIComponent(articleTitle.value)}`)
const shareTwitterUrl = computed(() => `https://twitter.com/intent/tweet?url=${encodeURIComponent(currentUrl.value)}&text=${encodeURIComponent(articleTitle.value)}`)
const shareLinkedinUrl = computed(() => `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(currentUrl.value)}`)

function copyArticleLink () {
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    navigator.clipboard.writeText(window.location.href).then(() => {
      linkCopied.value = true
      $q.notify({
        type: 'positive',
        message: 'لینک این مقاله با موفقیت کپی شد',
        position: 'top',
        timeout: 2200,
      })
      setTimeout(() => {
        linkCopied.value = false
      }, 2500)
    }).catch(() => {})
  }
}

function navigateToArticle (art) {
  if (!art) return
  const identifier = art.slug || art.id
  router.push(`/articles/${encodeURIComponent(identifier)}`)
}

// --------------------------------------------------------------------------
// SEO & Meta Tags
// --------------------------------------------------------------------------
usePageMeta(() => {
  const item = article.value
  if (!item) {
    return { title: 'راهکار و مقاله مهندسی', path: '/articles' }
  }
  return {
    title: item.title,
    description: item.summary || item.excerpt || '',
    path: `/articles/${item.slug || item.id}`,
    type: 'article',
    image: item.image_url || item.image,
    jsonLd: {
      '@type': 'Article',
      headline: item.title,
      description: item.summary || item.excerpt || '',
      image: item.image_url || item.image,
      url: `${SITE_ORIGIN}/articles/${item.slug || item.id}`,
      ...(authorName.value ? { author: { '@type': 'Person', name: authorName.value } } : {}),
      ...(item.created_at ? { datePublished: item.created_at } : {}),
      ...(item.updated_at ? { dateModified: item.updated_at } : {}),
    },
  }
})

// --------------------------------------------------------------------------
// Data Loading
// --------------------------------------------------------------------------
async function fetchArticle (slug) {
  loading.value = true
  article.value = null

  try {
    // 1. Try /api/articles/:slug_or_id
    let res = await api.get(`/api/articles/${encodeURIComponent(slug)}`).catch(() => null)
    if (!res?.data?.data) {
      // 2. Fallback to /api/solutions/:slug
      res = await api.get(`/api/solutions/${encodeURIComponent(slug)}`).catch(() => null)
    }
    article.value = res?.data?.data || null
  } catch (error) {
    console.error('Failed to load article:', error)
    article.value = null
  } finally {
    loading.value = false
    if (typeof window !== 'undefined') {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
    fetchRelatedArticles()
  }
}

async function fetchRelatedArticles () {
  try {
    const res = await api.get('/api/articles', { params: { limit: 6 } })
    if (res?.data?.data && Array.isArray(res.data.data)) {
      const currentSlug = String(route.params.slug || '')
      relatedArticles.value = res.data.data
        .filter(a => String(a.slug || a.id) !== currentSlug)
        .slice(0, 3)
        .map(art => ({
          id: art.id,
          slug: art.slug || art.id,
          title: art.title,
          excerpt: art.excerpt || art.summary || '',
          category: art.category || 'رایانش ابری',
          readTime: art.readTime || art.read_time || '۵ دقیقه مطالعه',
          image: formatMediaUrl(art.image || art.image_url, DEFAULT_ARTICLE_IMAGE),
          date: art.date || 'شهریور ۱۴۰۵',
          authorName: art.author?.name || art.author_name || 'تیم مهندسی',
          authorAvatar: formatMediaUrl(art.author?.avatar || art.author_image_url, '/Modern 3D Tech Dashboard Illustration(1).png'),
        }))
    }
  } catch (err) {
    console.warn('Could not load related articles:', err)
  }
}

// Scroll progress listener
function updateScrollProgress () {
  if (typeof window === 'undefined') return
  const totalHeight = document.documentElement.scrollHeight - window.innerHeight
  if (totalHeight > 0) {
    scrollProgress.value = Math.min(100, Math.max(0, (window.scrollY / totalHeight) * 100))
  }
}

watch(
  () => route.params.slug,
  (newSlug) => {
    if (newSlug) fetchArticle(newSlug)
  }
)

onMounted(() => {
  loadSettings().catch(() => {})
  loadProductsList().catch(() => {})
  if (route.params.slug) {
    fetchArticle(route.params.slug)
  }
  if (typeof window !== 'undefined') {
    window.addEventListener('scroll', updateScrollProgress, { passive: true })
  }
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('scroll', updateScrollProgress)
  }
})
</script>

<style scoped>
/* ==========================================================================
   SINGLE ARTICLE / SOLUTION PAGE - MODERN MINIMAL LUXURY TECH DESIGN
   ========================================================================== */

.article-detail-page-new {
  background-color: var(--bg-canvas, #f7f7f7);
  color: var(--text-dark, #0a0a0a);
  direction: rtl;
  min-height: 100vh;
  padding: 0 0 40px 0;
  position: relative;
  font-family: var(--font-fa, 'Estedad', system-ui, sans-serif);
}

/* 0. Top Reading Progress Bar */
.reading-progress-track {
  position: fixed;
  top: 0;
  right: 0;
  left: 0;
  height: 3.5px;
  background: rgba(0, 0, 0, 0.04);
  z-index: 1000;
  pointer-events: none;
}

.reading-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ffcc00, #ffdd44);
  box-shadow: 0 0 10px rgba(255, 204, 0, 0.7);
  transition: width 0.1s ease-out;
}

/* Loading & Not Found */
.detail-loading-state,
.detail-not-found-state {
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  text-align: center;
  padding: 140px 24px 60px;
}

.detail-not-found-state h2 {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-dark, #0a0a0a);
  margin: 0;
}

.detail-not-found-state p {
  color: var(--text-dark-muted, #737373);
  font-size: 0.95rem;
  margin: 0 0 12px;
}

.not-found-icon-wrap {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
}

.luxury-spinner {
  width: 44px;
  height: 44px;
  border: 3.5px solid rgba(10, 10, 10, 0.08);
  border-top-color: var(--yellow, #ffcc00);
  border-radius: 50%;
  animation: spin 0.8s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 1. Navigation & Breadcrumb Bar */
.article-nav-section {
  padding-top: 110px;
  padding-bottom: 20px;
}

.detail-nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 14px;
  padding: 12px 18px;
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: var(--radius-pill, 9999px);
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03);
}

.back-nav-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: var(--radius-pill, 9999px);
  background: var(--bg-canvas, #f7f7f7);
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-dark, #0a0a0a);
  transition: all 0.2s ease;
}

.back-nav-pill:hover {
  background: #0a0a0a;
  color: #ffffff;
  transform: translateX(3px);
}

.detail-badges-wrap {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.category-tag-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 204, 0, 0.14);
  color: #8f6b00;
  border: 1px solid rgba(255, 204, 0, 0.35);
  padding: 4px 12px;
  border-radius: var(--radius-pill, 9999px);
  font-size: 0.8rem;
  font-weight: 700;
}

.meta-item-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 11px;
  background: var(--bg-canvas, #f7f7f7);
  border-radius: var(--radius-pill, 9999px);
  font-size: 0.8rem;
  color: var(--text-dark-dim, #4a4a4a);
}

/* 2. Hero Section */
.article-hero-section {
  padding: 24px 0 40px;
}

.article-hero-head {
  max-width: 920px;
  margin: 0 auto 34px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.article-main-title {
  font-size: clamp(1.6rem, 3.8vw, 2.65rem);
  font-weight: 900;
  line-height: 1.36;
  color: var(--text-dark, #0a0a0a);
  margin: 16px 0 20px;
  letter-spacing: -0.02em;
}

.article-lead-box {
  width: 100%;
  max-width: 820px;
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-right: 4px solid var(--yellow, #ffcc00);
  border-radius: var(--radius-md, 20px);
  padding: 18px 24px;
  margin-bottom: 24px;
  text-align: right;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
}

.article-lead-box p {
  margin: 0;
  font-size: 1.05rem;
  line-height: 1.8;
  color: var(--text-dark-dim, #383838);
  font-weight: 500;
}

/* Author Toolbar */
.article-author-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 820px;
  padding: 10px 16px;
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: var(--radius-pill, 9999px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
}

.author-info-group {
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: right;
}

.author-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--yellow, #ffcc00);
}

.author-name {
  font-size: 0.92rem;
  font-weight: 800;
  color: var(--text-dark, #0a0a0a);
  line-height: 1.25;
}

.author-role {
  font-size: 0.78rem;
  color: var(--text-dark-muted, #737373);
  margin-top: 2px;
}

/* Cover Frame */
.article-cover-frame {
  max-width: 1120px;
  margin: 0 auto;
  position: relative;
  border-radius: var(--radius-bento, 28px);
  overflow: hidden;
  box-shadow: 0 16px 44px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border-light, #e5e5e5);
  background: #000000;
  max-height: 520px;
}

.article-cover-frame img {
  width: 100%;
  height: 100%;
  max-height: 520px;
  object-fit: cover;
  display: block;
}

.cover-topic-chip {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: rgba(10, 10, 10, 0.78);
  backdrop-filter: blur(8px);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 6px 16px;
  border-radius: var(--radius-pill, 9999px);
  font-size: 0.82rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chip-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--yellow, #ffcc00);
}

/* 3. Article Editorial Body Layout */
.article-body-section {
  padding: 30px 0 60px;
}

.article-editorial-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 36px;
  align-items: start;
}

/* Main Content Card Paper */
.article-content-column {
  min-width: 0;
}

.article-card-paper {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: var(--radius-bento, 28px);
  padding: 44px 48px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03);
}

/* Luxury Typography Inside Article Prose */
.article-prose {
  font-size: 1.08rem;
  line-height: 1.94;
  color: #262626;
  direction: rtl;
  text-align: justify;
}

.article-prose :deep(> :first-child) {
  margin-top: 0;
}

.article-prose :deep(p) {
  margin: 0 0 1.45em;
  color: #2b2b2b;
}

.article-prose :deep(h1),
.article-prose :deep(h2),
.article-prose :deep(h3),
.article-prose :deep(h4) {
  color: var(--text-dark, #0a0a0a);
  font-weight: 850;
  line-height: 1.42;
  margin: 2.1em 0 0.8em;
  letter-spacing: -0.01em;
}

.article-prose :deep(h1) {
  font-size: 1.7rem;
  border-bottom: 2px solid var(--yellow, #ffcc00);
  padding-bottom: 10px;
}

.article-prose :deep(h2) {
  font-size: 1.48rem;
  border-right: 4px solid var(--yellow, #ffcc00);
  padding-right: 14px;
}

.article-prose :deep(h3) {
  font-size: 1.28rem;
  border-right: 3px solid var(--yellow, #ffcc00);
  padding-right: 12px;
}

.article-prose :deep(h4) {
  font-size: 1.12rem;
  font-weight: 800;
  color: #1a1a1a;
}

.article-prose :deep(strong),
.article-prose :deep(b) {
  font-weight: 800;
  color: #000000;
}

.article-prose :deep(ul),
.article-prose :deep(ol) {
  margin: 0 0 1.5em;
  padding-right: 28px;
  padding-left: 0;
}

.article-prose :deep(li) {
  margin-bottom: 0.7em;
  line-height: 1.82;
}

.article-prose :deep(ul > li) {
  list-style: square;
}

.article-prose :deep(blockquote) {
  background: rgba(255, 204, 0, 0.06);
  border-right: 4px solid var(--yellow, #ffcc00);
  padding: 16px 20px;
  margin: 1.8em 0;
  border-radius: 12px;
  font-style: italic;
  color: #383838;
}

.article-prose :deep(pre),
.article-prose :deep(code) {
  font-family: var(--font-code, 'Fira Code', monospace);
}

.article-prose :deep(code) {
  background: #f0f0f0;
  padding: 2px 7px;
  border-radius: 6px;
  font-size: 0.9em;
  color: #c7254e;
}

.article-prose :deep(pre) {
  background: #0e0e11;
  color: #f8f8f2;
  padding: 18px 22px;
  border-radius: 16px;
  overflow-x: auto;
  direction: ltr;
  text-align: left;
  border: 1px solid #27272a;
  margin: 1.8em 0;
}

.article-prose :deep(pre code) {
  background: none;
  color: inherit;
  padding: 0;
  font-size: 0.92rem;
}

.article-prose :deep(img) {
  border-radius: 18px;
  margin: 2em auto;
  border: 1px solid var(--border-light, #e5e5e5);
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.05);
}

/* Spotlight for Related Product inside Main Article Section */
.article-related-product-spotlight {
  margin: 36px 0 28px;
  background: linear-gradient(135deg, #0d0d0f 0%, #17171a 100%);
  border: 1px solid #27272a;
  border-radius: var(--radius-bento, 28px);
  padding: 24px;
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.16);
  position: relative;
  overflow: hidden;
}

.article-related-product-spotlight::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 180px;
  height: 180px;
  background: radial-gradient(circle, rgba(255, 204, 0, 0.16) 0%, transparent 70%);
  pointer-events: none;
}

.product-spotlight-inner {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 24px;
  align-items: center;
}

.spotlight-media-wrap {
  width: 100%;
  height: 175px;
  border-radius: var(--radius-md, 20px);
  overflow: hidden;
  position: relative;
  background: #000000;
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.spotlight-media-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.article-related-product-spotlight:hover .spotlight-media-wrap img {
  transform: scale(1.05);
}

.spotlight-media-badge {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(10, 10, 10, 0.82);
  backdrop-filter: blur(6px);
  color: var(--yellow, #ffcc00);
  font-size: 0.72rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: var(--radius-pill, 9999px);
  border: 1px solid rgba(255, 204, 0, 0.3);
}

.spotlight-content-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.spotlight-badge-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.spotlight-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.76rem;
  font-weight: 700;
  color: var(--yellow, #ffcc00);
  background: rgba(255, 204, 0, 0.1);
  padding: 3px 10px;
  border-radius: var(--radius-pill, 9999px);
  border: 1px solid rgba(255, 204, 0, 0.25);
}

.pulse-beacon {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--yellow, #ffcc00);
  box-shadow: 0 0 8px var(--yellow, #ffcc00);
  animation: pulseBeacon 1.8s infinite;
}

@keyframes pulseBeacon {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(1.3); }
}

.spotlight-status-pill {
  font-size: 0.72rem;
  color: #a1a1aa;
}

.spotlight-title {
  font-size: 1.28rem;
  font-weight: 850;
  color: #ffffff;
  margin: 4px 0 0;
  line-height: 1.35;
}

.spotlight-desc {
  font-size: 0.88rem;
  color: #a1a1aa;
  line-height: 1.7;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.spotlight-actions-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

/* Tags */
.article-tags-container {
  margin-top: 36px;
  padding-top: 26px;
  border-top: 1px solid var(--border-light, #e5e5e5);
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.tags-headline {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-dark-dim, #4a4a4a);
}

.tags-flex {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  display: inline-block;
  padding: 5px 13px;
  border-radius: var(--radius-pill, 9999px);
  background: var(--bg-canvas, #f7f7f7);
  border: 1px solid var(--border-light, #e5e5e5);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-dark-dim, #4a4a4a);
  transition: all 0.2s ease;
}

.tag-chip:hover {
  background: #0a0a0a;
  color: #ffffff;
  border-color: #0a0a0a;
}

/* Bottom Actions */
.article-bottom-actions {
  margin-top: 36px;
  padding-top: 28px;
  border-top: 1px solid var(--border-light, #e5e5e5);
}

.share-box-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 28px;
  padding: 16px 20px;
  background: var(--bg-canvas, #f7f7f7);
  border-radius: var(--radius-md, 20px);
}

.share-label {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-dark, #0a0a0a);
}

.share-pills-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.social-pill {
  padding: 6px 14px;
  border-radius: var(--radius-pill, 9999px);
  font-size: 0.78rem;
  font-weight: 600;
  border: 1px solid var(--border-light, #e5e5e5);
  background: #ffffff;
  color: var(--text-dark, #0a0a0a);
  cursor: pointer;
  transition: all 0.2s ease;
}

.social-pill:hover {
  background: #0a0a0a;
  color: #ffffff;
  border-color: #0a0a0a;
}

.social-pill.copy {
  background: rgba(255, 204, 0, 0.16);
  border-color: rgba(255, 204, 0, 0.4);
  color: #8a6500;
}

.social-pill.copy:hover {
  background: var(--yellow, #ffcc00);
  color: #000000;
}

.end-nav-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 14px;
}

/* Sticky Sidebar */
.article-sidebar-column {
  min-width: 0;
}

.sidebar-sticky-wrapper {
  position: sticky;
  top: 96px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-bento-box {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: var(--radius-bento, 28px);
  padding: 22px 20px;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.02);
}

.sidebar-box-head {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  font-weight: 800;
  color: var(--text-dark-muted, #737373);
  margin-bottom: 14px;
}

.dot-indicator {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--text-dark, #0a0a0a);
}

.dot-indicator.gold {
  background: var(--yellow, #ffcc00);
}

/* Author Bento */
.author-bento-profile {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 14px;
}

.author-bento-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--yellow, #ffcc00);
}

.author-bento-name {
  font-size: 0.98rem;
  font-weight: 800;
  color: var(--text-dark, #0a0a0a);
  margin: 0 0 3px;
}

.author-bento-role {
  font-size: 0.78rem;
  color: var(--text-dark-muted, #737373);
  margin: 0;
}

.author-bento-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--bg-canvas, #f7f7f7);
  border-radius: var(--radius-sm, 14px);
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-dark, #0a0a0a);
  transition: all 0.2s ease;
}

.author-bento-link:hover {
  background: #0a0a0a;
  color: #ffffff;
}

/* Product Bento */
.related-product-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.product-bento-thumb {
  width: 100%;
  height: 110px;
  border-radius: var(--radius-sm, 14px);
  overflow: hidden;
  margin-bottom: 4px;
}

.product-bento-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-bento-title {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--text-dark, #0a0a0a);
  margin: 0;
}

.product-bento-desc {
  font-size: 0.78rem;
  color: var(--text-dark-muted, #737373);
  line-height: 1.6;
  margin: 0 0 6px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Source Bento */
.source-bento-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 0.82rem;
  font-weight: 700;
  color: #1e40af;
  word-break: break-all;
  padding: 8px 12px;
  background: #eff6ff;
  border-radius: var(--radius-sm, 14px);
  transition: all 0.2s ease;
}

.source-bento-link:hover {
  background: #dbeafe;
}

.source-bento-text {
  font-size: 0.82rem;
  color: var(--text-dark, #0a0a0a);
  margin: 0;
}

/* Consult Bento */
.consult-bento {
  background: #0a0a0a;
  color: #ffffff;
  border-color: #262626;
}

.consult-title {
  font-size: 1rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0 0 8px;
}

.consult-text {
  font-size: 0.8rem;
  color: #a3a3a3;
  line-height: 1.68;
  margin: 0 0 16px;
}

.full-width {
  width: 100%;
  justify-content: center;
}

/* 4. Related Articles Section */
.related-articles-section {
  padding: 50px 0 20px;
  border-top: 1px solid var(--border-light, #e5e5e5);
}

.related-head-bar {
  text-align: center;
  margin-bottom: 34px;
}

.related-title {
  font-size: clamp(1.4rem, 2.5vw, 1.85rem);
  font-weight: 850;
  color: var(--text-dark, #0a0a0a);
  margin-top: 10px;
}

.related-cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

/* Article Card in Related Grid */
.article-card {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: var(--radius-bento, 28px);
  padding: 18px 18px 16px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
}

.article-card:hover {
  transform: translateY(-5px);
  border-color: var(--yellow-border, rgba(255, 204, 0, 0.45));
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.06);
}

.card-thumb-wrap {
  width: 100%;
  height: 180px;
  border-radius: var(--radius-md, 20px);
  overflow: hidden;
  position: relative;
  margin-bottom: 16px;
  background: #000000;
}

.card-thumb-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.article-card:hover .card-thumb-wrap img {
  transform: scale(1.05);
}

.card-cat-pill {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(10, 10, 10, 0.75);
  backdrop-filter: blur(6px);
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: var(--radius-pill, 9999px);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.76rem;
  color: var(--text-dark-muted, #737373);
  margin-bottom: 8px;
}

.read-pill {
  background: var(--bg-canvas, #f7f7f7);
  padding: 2px 8px;
  border-radius: var(--radius-pill, 9999px);
  font-weight: 600;
}

.dot-sep {
  opacity: 0.5;
}

.card-title {
  font-size: 1.04rem;
  font-weight: 800;
  color: var(--text-dark, #0a0a0a);
  line-height: 1.45;
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-excerpt {
  font-size: 0.82rem;
  color: var(--text-dark-dim, #4a4a4a);
  line-height: 1.68;
  margin: 0 0 16px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid var(--border-light, #e5e5e5);
  margin-top: auto;
}

.author-mini {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mini-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  object-fit: cover;
}

.mini-name {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-dark, #0a0a0a);
}

.read-action {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.78rem;
  font-weight: 800;
  color: #000000;
  background: var(--yellow, #ffcc00);
  padding: 4px 10px;
  border-radius: var(--radius-pill, 9999px);
  transition: all 0.2s ease;
}

.article-card:hover .read-action {
  background: #0a0a0a;
  color: #ffffff;
}

/* ==========================================================================
   RESPONSIVE MEDIA QUERIES
   ========================================================================== */
@media (max-width: 1080px) {
  .article-editorial-grid {
    grid-template-columns: 1fr;
  }

  .sidebar-sticky-wrapper {
    position: static;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }

  .related-cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .article-nav-section {
    padding-top: 90px;
  }

  .detail-nav-bar {
    border-radius: var(--radius-md, 20px);
    flex-direction: column;
    align-items: flex-start;
  }

  .article-card-paper {
    padding: 24px 20px;
    border-radius: var(--radius-md, 20px);
  }

  .product-spotlight-inner {
    grid-template-columns: 1fr;
  }

  .spotlight-media-wrap {
    height: 180px;
  }

  .article-prose {
    font-size: 0.98rem;
    line-height: 1.82;
  }

  .sidebar-sticky-wrapper {
    grid-template-columns: 1fr;
  }

  .related-cards-grid {
    grid-template-columns: 1fr;
  }

  .article-author-bar {
    border-radius: var(--radius-md, 20px);
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-action-group {
    width: 100%;
    display: flex;
    justify-content: flex-end;
  }
}

@media (max-width: 480px) {
  .article-main-title {
    font-size: 1.38rem;
  }

  .article-lead-box {
    padding: 14px 16px;
  }

  .article-lead-box p {
    font-size: 0.92rem;
  }

  .article-card-paper {
    padding: 18px 14px;
  }

  .article-cover-frame {
    border-radius: var(--radius-md, 20px);
  }
}
</style>

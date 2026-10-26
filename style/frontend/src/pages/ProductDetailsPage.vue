<template>
  <q-page class="product-detail-page-new" :class="{ 'lightbox-open': lightboxOpen || videoLightboxOpen }">

    <!-- Loading State -->
    <div v-if="loading" class="detail-loading-state">
      <div class="luxury-spinner"></div>
      <p>در حال بارگذاری اطلاعات سامانه و مستندات...</p>
    </div>

    <!-- Not Found State -->
    <div v-else-if="!product" class="detail-not-found-state">
      <div class="not-found-icon-wrap">
        <q-icon name="search_off" size="56px" color="grey-6" />
      </div>
      <h2>محصول یا سامانه یافت نشد</h2>
      <p>ممکن است آدرس تغییر کرده باشد یا سامانه موقتاً غیرفعال شده باشد.</p>
      <router-link to="/projects" class="btn-pill btn-pill-yellow">
        <q-icon name="arrow_forward" size="16px" />
        <span>بازگشت به پروژه‌ها و محصولات</span>
      </router-link>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- 1. Hero / Header Section -->
      <section class="detail-hero-section">
        <div class="container">
          <!-- Breadcrumb & Status Row -->
          <div class="detail-nav-bar">
            <router-link to="/projects" class="back-nav-pill">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
              <span>بازگشت به همه پروژه‌ها</span>
            </router-link>

            <div class="detail-badges-wrap">
              <router-link
                v-if="product.category_name"
                :to="`/projects?category=${product.category_slug}`"
                class="category-tag-pill"
              >
                <span class="tag-dot"></span>
                <span>{{ product.category_name }}</span>
              </router-link>

              <span class="status-tag-pill">
                <span class="status-pulse-dot"></span>
                <span>{{ product.badge || 'استقرار فعال سازمانی' }}</span>
              </span>

              <router-link
                v-if="isAdmin"
                to="/admin/products"
                class="btn-pill btn-pill-dark btn-pill-sm mr-2"
              >
                <q-icon name="settings" size="14px" />
                <span>مدیریت این محصول</span>
              </router-link>
            </div>
          </div>

          <!-- Top Bento Overview: Title & Visual Split -->
          <div class="overview-bento-grid">
            <!-- Content & Actions Column -->
            <div class="overview-info-col">
              <div class="section-tag">
                <span class="tag-dot"></span>
                <span>مشخصات و دستاوردهای سامانه</span>
              </div>

              <h1 class="product-main-title">{{ product.title }}</h1>
              <div class="product-slug-code">{{ product.slug }}</div>

              <p v-if="product.short_description" class="product-summary-text">
                {{ product.short_description }}
              </p>

              <!-- Live Key Metrics Cards (SLA, Speed, Scale) -->
              <div v-if="productMetrics.length" class="metrics-bento-strip">
                <div
                  v-for="(metric, mIdx) in productMetrics"
                  :key="mIdx"
                  class="metric-bento-card"
                >
                  <strong class="metric-val">{{ metric.val }}</strong>
                  <span class="metric-lbl">{{ metric.lbl }}</span>
                </div>
              </div>

              <!-- Tech Tags Row -->
              <div v-if="productTags.length" class="tech-tags-strip">
                <span v-for="tag in productTags" :key="tag" class="tech-tag-chip">
                  {{ tag }}
                </span>
              </div>

              <!-- Action Buttons -->
              <div class="overview-actions-strip">
                <router-link to="/contact" class="btn-pill btn-pill-yellow">
                  <span class="btn-text">{{ settings.detail_consult_label || 'درخواست مشاوره و استقرار' }}</span>
                  <span class="btn-icon-bubble">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                  </span>
                </router-link>

                <a
                  v-if="product.url"
                  :href="product.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn-pill btn-pill-dark"
                >
                  <span class="btn-text">{{ settings.detail_site_label || 'مشاهده آنلاین سامانه' }}</span>
                  <span class="btn-icon-bubble">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                  </span>
                </a>

                <button
                  v-if="videos.length"
                  type="button"
                  class="btn-pill btn-pill-ghost-light"
                  @click="scrollToSection('sec-product-videos')"
                >
                  <q-icon name="play_circle" size="18px" color="amber-8" />
                  <span>ویدیوهای معرفی ({{ videos.length }})</span>
                </button>
              </div>
            </div>

            <!-- Visual Media Bento Card -->
            <div class="overview-visual-col">
              <div class="hero-media-card">
                <div class="hero-media-frame" @click="openMainImageLightbox">
                  <img
                    v-if="product.image_url"
                    :src="formatMediaUrl(product.image_url)"
                    :alt="product.title"
                    class="hero-media-img"
                    fetchpriority="high"
                    decoding="async"
                  />
                  <div v-else class="hero-media-placeholder">
                    <q-icon name="inventory_2" size="64px" color="grey-5" />
                  </div>

                  <div class="media-zoom-overlay">
                    <div class="zoom-badge">
                      <q-icon name="zoom_in" size="18px" />
                      <span>بزرگ‌نمایی تصویر</span>
                    </div>
                  </div>
                </div>

                <div class="hero-media-footer">
                  <div class="security-chip">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    <span>معماری امن و ایزوله ابری</span>
                  </div>
                  <div class="sla-chip">
                    <span>SLA تضمینی ۹۹.۹۹٪</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 2. Product Video Showcase (Requirement 4: بخش ویدیوی محصول) -->
      <section v-if="videos.length > 0 || isAdmin" class="detail-video-section" id="sec-product-videos">
        <div class="container">
          <div class="section-head text-center">
            <div class="section-tag">
              <span class="tag-dot"></span>
              <span>ویدیو و دموی عملکرد سامانه</span>
            </div>
            <h2 class="section-title">بررسی ویدیویی معماری و امکانات سامانه</h2>
            <p class="section-desc">
              مشاهده ویدیوهای عملکرد، دمو داشبوردها و جزئیات پیاده‌سازی این محصول سازمانی.
            </p>
          </div>

          <!-- Video Player Showcase Card -->
          <div v-if="videos.length > 0" class="video-showcase-card">
            <!-- Main Video Stage -->
            <div class="video-player-frame">
              <video
                :key="activeVideoIndex"
                ref="mainVideoPlayer"
                :src="activeVideo?.video_url"
                :poster="activeVideo?.thumbnail_url || formatMediaUrl(product.image_url)"
                controls
                playsinline
                preload="metadata"
                class="main-html5-video"
              >
                مرورگر شما از پخش مستقیم ویدیو پشتیبانی نمی‌کند.
              </video>

              <div class="video-meta-top-strip">
                <div class="video-title-pill">
                  <q-icon name="videocam" size="16px" color="amber-8" />
                  <span>{{ activeVideo?.title || `ویدیو شماره ${activeVideoIndex + 1}` }}</span>
                </div>
                <button
                  type="button"
                  class="btn-theater-mode"
                  @click="openVideoLightbox(activeVideoIndex)"
                  title="مشاهده تمام‌صفحه سینمایی"
                >
                  <q-icon name="fullscreen" size="18px" />
                  <span>حالت سینمایی</span>
                </button>
              </div>
            </div>

            <!-- Video Playlist Selector (if multiple videos) -->
            <div v-if="videos.length > 1" class="video-playlist-bar">
              <div class="playlist-label">سایر ویدیوهای این محصول ({{ videos.length }} ویدیو):</div>
              <div class="video-thumbnails-row">
                <button
                  v-for="(vid, vIdx) in videos"
                  :key="vid.id || vIdx"
                  type="button"
                  class="video-thumb-card"
                  :class="{ active: activeVideoIndex === vIdx }"
                  @click="selectVideo(vIdx)"
                >
                  <div class="thumb-mini-frame">
                    <img
                      :src="vid.thumbnail_url || formatMediaUrl(product.image_url)"
                      :alt="vid.title"
                      loading="lazy"
                    />
                    <div class="mini-play-icon">
                      <q-icon name="play_arrow" size="16px" />
                    </div>
                  </div>
                  <div class="thumb-mini-info">
                    <span class="mini-title">{{ vid.title || `ویدیو شماره ${vIdx + 1}` }}</span>
                    <span class="mini-order">قسمت {{ vIdx + 1 }}</span>
                  </div>
                </button>
              </div>
            </div>
          </div>

          <!-- Admin Empty State Helper for Videos -->
          <div v-else-if="isAdmin" class="admin-empty-video-card">
            <q-icon name="video_library" size="48px" color="amber-8" class="q-mb-sm" />
            <h3>هنوز ویدیویی برای این محصول ثبت نشده است</h3>
            <p>می‌توانید از پنل مدیریت در بخش «محصولات سازمانی» ویدیوهای معرفی (MP4 / WebM) را با قابلیت تولید خودکار تصویر بندانگشتی آپلود نمایید.</p>
            <router-link to="/admin/products" class="btn-pill btn-pill-dark btn-pill-sm">
              <q-icon name="add" size="14px" />
              <span>افزودن ویدیوی جدید در پنل مدیریت</span>
            </router-link>
          </div>
        </div>
      </section>

      <!-- 3. Technical Specifications & Full Description -->
      <section v-if="product.description" class="detail-description-section">
        <div class="container">
          <div class="description-bento-card">
            <div class="desc-card-head">
              <div class="section-tag">
                <span class="tag-dot"></span>
                <span>مستندات و مشخصات فنی</span>
              </div>
              <h2 class="section-title mb-0">{{ settings.detail_description_title || 'شرح معماری، استانداردها و کارکرد سیستم' }}</h2>
            </div>

            <div class="desc-body-content">
              <RichContent :html="product.description" />
            </div>
          </div>
        </div>
      </section>

      <!-- 4. Interactive Product Image Gallery -->
      <section v-if="images.length > 0" class="detail-gallery-section">
        <div class="container">
          <div class="section-head text-center">
            <div class="section-tag">
              <span class="tag-dot"></span>
              <span>گالری تصاویر محیط کاربری</span>
            </div>
            <h2 class="section-title">{{ settings.detail_gallery_title || 'نماهای داشبورد و رابط کاربری سامانه' }}</h2>
            <p class="section-desc">تصاویر ثبت‌شده از محیط عملیاتی و قابلیت‌های سامانه.</p>
          </div>

          <div class="gallery-bento-grid">
            <div
              v-for="(img, idx) in images"
              :key="img.id || idx"
              class="gallery-bento-item"
              @click="openLightbox(idx)"
            >
              <img :src="formatMediaUrl(img.image_url)" :alt="'عکس سامانه ' + (idx + 1)" loading="lazy" decoding="async" />
              <div class="gallery-hover-veil">
                <div class="zoom-circle">
                  <q-icon name="zoom_in" size="20px" />
                </div>
                <span class="gallery-item-index">{{ idx + 1 }} / {{ images.length }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 5. Catalogs & Downloadable Documentation -->
      <section v-if="catalogs.length > 0" class="detail-catalogs-section">
        <div class="container">
          <div class="section-head text-center">
            <div class="section-tag">
              <span class="tag-dot"></span>
              <span>مستندات و دفترچه‌های فنی</span>
            </div>
            <h2 class="section-title">{{ settings.detail_catalogs_title || 'کاتالوگ‌ها و فایل‌های پیوست' }}</h2>
            <p class="section-desc">دریافت اسناد RFC، بروشورهای معرفی و راهنمای کاربری سیستم.</p>
          </div>

          <div class="catalogs-bento-grid">
            <a
              v-for="(catalog, cIdx) in catalogs"
              :key="catalog.id || cIdx"
              :href="formatMediaUrl(catalog.file_url)"
              target="_blank"
              class="catalog-bento-card"
            >
              <div class="catalog-icon-box">
                <q-icon :name="getFileIcon(catalog.file_url)" size="30px" />
              </div>
              <div class="catalog-info-col">
                <h4 class="catalog-title">{{ catalog.title }}</h4>
                <div class="catalog-meta">
                  <span class="catalog-ext-badge">{{ getFileExtension(catalog.file_url) }}</span>
                  <span class="catalog-hint">کلیک جهت دریافت و مطالعه فایل</span>
                </div>
              </div>
              <div class="catalog-download-circle">
                <q-icon name="download" size="18px" />
              </div>
            </a>
          </div>
        </div>
      </section>

      <!-- 6. Related Products & Enterprise Systems -->
      <section v-if="relatedProducts.length > 0" class="detail-related-section">
        <div class="container">
          <div class="section-head text-center">
            <div class="section-tag">
              <span class="tag-dot"></span>
              <span>سامانه‌های مرتبط</span>
            </div>
            <h2 class="section-title">{{ settings.detail_related_title || 'سایر سامانه‌ها و پروژه‌های شاخص' }}</h2>
            <p class="section-desc">پلتفرم‌های ابری و راهکارهای سازمانی هم‌راستا با این سامانه.</p>
          </div>

          <div class="related-bento-grid">
            <router-link
              v-for="rp in relatedProducts"
              :key="rp.id"
              :to="`/products/${rp.slug}`"
              class="related-project-card"
            >
              <div class="related-card-media">
                <img
                  v-if="rp.image_url"
                  :src="formatMediaUrl(rp.image_url)"
                  :alt="rp.title"
                  loading="lazy"
                />
                <div v-else class="related-media-placeholder">
                  <q-icon name="inventory_2" size="36px" color="grey-5" />
                </div>
              </div>

              <div class="related-card-content">
                <h3 class="related-card-title">{{ rp.title }}</h3>
                <p class="related-card-desc">{{ rp.short_description }}</p>
                <div class="related-card-footer">
                  <span class="related-view-link">مشاهده مشخصات سامانه</span>
                  <q-icon name="arrow_back" size="16px" />
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </section>

      <!-- 7. High-Impact Enterprise CTA Banner -->
      <CloudlandCTA :page-name="'محصول: ' + (product?.title || 'پروژه‌ها')" />
    </template>

    <!-- Image Lightbox Modal -->
    <teleport to="body">
      <Transition name="lightbox">
        <div v-if="lightboxOpen" class="luxury-lightbox-overlay" @click.self="closeLightbox">
          <button class="lb-close-btn" @click="closeLightbox" title="بستن">
            <q-icon name="close" size="22px" />
          </button>

          <button v-if="allLightboxImages.length > 1" class="lb-nav-btn lb-prev" @click="lightboxPrev" title="قبلی">
            <q-icon name="chevron_right" size="28px" />
          </button>

          <div class="lb-stage-wrap">
            <img
              :src="formatMediaUrl(allLightboxImages[lightboxIndex]?.url)"
              :alt="'نمای ' + (lightboxIndex + 1)"
              class="lb-main-image"
              decoding="async"
            />
          </div>

          <button v-if="allLightboxImages.length > 1" class="lb-nav-btn lb-next" @click="lightboxNext" title="بعدی">
            <q-icon name="chevron_left" size="28px" />
          </button>

          <div class="lb-counter-strip">
            <span>{{ lightboxIndex + 1 }} / {{ allLightboxImages.length }}</span>
          </div>
        </div>
      </Transition>
    </teleport>

    <!-- Video Theater Lightbox Modal -->
    <teleport to="body">
      <Transition name="lightbox">
        <div v-if="videoLightboxOpen" class="luxury-lightbox-overlay" @click.self="closeVideoLightbox">
          <button class="lb-close-btn" @click="closeVideoLightbox" title="بستن">
            <q-icon name="close" size="22px" />
          </button>

          <button v-if="videos.length > 1" class="lb-nav-btn lb-prev" @click="videoLbPrev" title="ویدیوی قبلی">
            <q-icon name="chevron_right" size="28px" />
          </button>

          <div class="lb-stage-wrap lb-video-stage">
            <video
              :key="videoLbIndex"
              :src="videos[videoLbIndex]?.video_url"
              :poster="videos[videoLbIndex]?.thumbnail_url"
              controls
              autoplay
              playsinline
              class="lb-theater-video"
            >
              مرورگر شما از پخش ویدیو پشتیبانی نمی‌کند.
            </video>
            <div class="lb-video-title-bar">
              <span>{{ videos[videoLbIndex]?.title || `ویدیو ${videoLbIndex + 1}` }}</span>
            </div>
          </div>

          <button v-if="videos.length > 1" class="lb-nav-btn lb-next" @click="videoLbNext" title="ویدیوی بعدی">
            <q-icon name="chevron_left" size="28px" />
          </button>

          <div class="lb-counter-strip">
            <span>ویدیو {{ videoLbIndex + 1 }} از {{ videos.length }}</span>
          </div>
        </div>
      </Transition>
    </teleport>

  </q-page>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import api from 'src/services/api'
import { usePageMeta, SITE_ORIGIN } from 'src/composables/usePageMeta'
import RichContent from 'src/components/common/RichContent.vue'
import CloudlandCTA from 'src/components/CTA/CloudlandCTA.vue'
import { useAuth } from 'src/composables/useAuth'
import { useCatalogContent } from 'src/composables/useCatalogContent'

const route = useRoute()
const { isAdmin } = useAuth()
const { settings, loadSettings } = useCatalogContent()

const product = ref(null)
const relatedProducts = ref([])
const catalogs = ref([])
const images = ref([])
const videos = ref([])
const loading = ref(true)

// Video player state
const activeVideoIndex = ref(0)
const mainVideoPlayer = ref(null)

const activeVideo = computed(() => {
  if (!videos.value.length) return null
  return videos.value[activeVideoIndex.value] || videos.value[0]
})

function selectVideo(index) {
  activeVideoIndex.value = index
  if (mainVideoPlayer.value) {
    mainVideoPlayer.value.load()
  }
}

// Key metrics parsed from metrics_json or product object
const productMetrics = computed(() => {
  const p = product.value
  if (!p) return []
  if (p.metrics_json) {
    try {
      const parsed = typeof p.metrics_json === 'string' ? JSON.parse(p.metrics_json) : p.metrics_json
      if (Array.isArray(parsed) && parsed.length > 0) return parsed
    } catch {}
  }
  // Fallback to explicit columns if available
  const fallback = []
  if (p.metric1_val && p.metric1_lbl) fallback.push({ val: p.metric1_val, lbl: p.metric1_lbl })
  if (p.metric2_val && p.metric2_lbl) fallback.push({ val: p.metric2_val, lbl: p.metric2_lbl })
  if (p.metric3_val && p.metric3_lbl) fallback.push({ val: p.metric3_val, lbl: p.metric3_lbl })
  if (fallback.length) return fallback
  return [
    { val: '۹۹.۹۹٪', lbl: 'تضمین پایداری SLA' },
    { val: '< ۲۰ms', lbl: 'لتنسی پردازش بلادرنگ' },
    { val: 'Zero-Trust', lbl: 'امنیت و ایزولاسیون' },
  ]
})

// Tech tags parsed from tags_json
const productTags = computed(() => {
  const p = product.value
  if (!p) return []
  if (p.tags_json) {
    try {
      const parsed = typeof p.tags_json === 'string' ? JSON.parse(p.tags_json) : p.tags_json
      if (Array.isArray(parsed) && parsed.length > 0) return parsed
    } catch {}
  }
  return ['معماری توزیع‌شده', 'زیرساخت ابری', 'میکروسرویس', 'داکر و کوبرنتیز']
})

// Lightbox state
const lightboxOpen = ref(false)
const lightboxIndex = ref(0)
const videoLightboxOpen = ref(false)
const videoLbIndex = ref(0)

const allLightboxImages = computed(() => {
  const list = []
  if (product.value?.image_url) {
    list.push({ url: product.value.image_url })
  }
  for (const img of images.value) {
    if (img.image_url) list.push({ url: img.image_url })
  }
  return list
})

function formatMediaUrl(url) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  if (url.startsWith('/')) return url
  return '/' + url
}

function scrollToSection(id) {
  const el = document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

usePageMeta(() => {
  const item = product.value
  if (!item) {
    return { title: 'محصول سازمانی | کهکشان هوشمند', path: '/projects' }
  }
  return {
    title: `${item.title} | کهکشان هوشمند`,
    description: item.short_description || item.description || '',
    path: `/products/${item.slug}`,
    image: item.image_url ? formatMediaUrl(item.image_url) : undefined,
    jsonLd: {
      '@type': 'Product',
      name: item.title,
      description: item.short_description || '',
      image: item.image_url ? `${SITE_ORIGIN}${formatMediaUrl(item.image_url)}` : undefined,
      url: `${SITE_ORIGIN}/products/${item.slug}`,
      ...(item.category_name ? { category: item.category_name } : {}),
    },
  }
})

async function fetchProduct(slug) {
  loading.value = true
  product.value = null
  relatedProducts.value = []
  catalogs.value = []
  images.value = []
  videos.value = []
  activeVideoIndex.value = 0

  try {
    const res = await api.get(`/api/products/${slug}`)
    product.value = res.data.data

    if (product.value?.category_slug) {
      fetchRelated(product.value.category_slug, product.value.id)
    }
    fetchCatalogs(slug)
    fetchImages(product.value.id)
    fetchVideos(product.value.id)
  } catch (err) {
    console.error('Failed to load product:', err)
    product.value = null
  } finally {
    loading.value = false
  }
}

async function fetchImages(productId) {
  try {
    const res = await api.get(`/api/products/${productId}/images`)
    images.value = res.data.data || []
  } catch (err) {
    console.error('Failed to load images:', err)
  }
}

async function fetchVideos(productId) {
  try {
    const res = await api.get(`/api/products/${productId}/videos`)
    const rawList = res.data.data || []
    videos.value = rawList.map(v => ({
      ...v,
      video_url: formatMediaUrl(v.video_url),
      thumbnail_url: v.thumbnail_url ? formatMediaUrl(v.thumbnail_url) : '',
    }))
  } catch (err) {
    console.error('Failed to load videos:', err)
  }
}

async function fetchCatalogs(slug) {
  try {
    const res = await api.get(`/api/catalogs/product/${slug}`)
    catalogs.value = res.data.data || []
  } catch (err) {
    console.error('Failed to load catalogs:', err)
  }
}

async function fetchRelated(categorySlug, excludeId) {
  try {
    const res = await api.get(`/api/products?category=${categorySlug}&limit=4`)
    relatedProducts.value = (res.data.data || []).filter(p => p.id !== excludeId).slice(0, 3)
  } catch (err) {
    console.error('Failed to load related products:', err)
  }
}

function getFileIcon(url) {
  if (!url) return 'insert_drive_file'
  const ext = url.split('.').pop()?.toLowerCase()
  const icons = {
    pdf: 'picture_as_pdf',
    doc: 'article',
    docx: 'article',
    xls: 'table_chart',
    xlsx: 'table_chart',
    ppt: 'slideshow',
    pptx: 'slideshow',
    csv: 'table_chart',
    zip: 'folder_zip',
    rar: 'folder_zip',
  }
  return icons[ext] || 'insert_drive_file'
}

function getFileExtension(url) {
  if (!url) return 'FILE'
  return url.split('.').pop()?.toUpperCase() || 'FILE'
}

// Lightbox triggers
function openMainImageLightbox() {
  if (!product.value?.image_url) return
  lightboxIndex.value = 0
  lightboxOpen.value = true
  document.body.style.overflow = 'hidden'
}

function openLightbox(index) {
  const hasMain = !!product.value?.image_url
  lightboxIndex.value = hasMain ? index + 1 : index
  lightboxOpen.value = true
  document.body.style.overflow = 'hidden'
}

function closeLightbox() {
  lightboxOpen.value = false
  document.body.style.overflow = ''
}

function lightboxPrev() {
  const total = allLightboxImages.value.length
  lightboxIndex.value = lightboxIndex.value <= 0 ? total - 1 : lightboxIndex.value - 1
}

function lightboxNext() {
  const total = allLightboxImages.value.length
  lightboxIndex.value = lightboxIndex.value >= total - 1 ? 0 : lightboxIndex.value + 1
}

function openVideoLightbox(index) {
  videoLbIndex.value = index
  videoLightboxOpen.value = true
  document.body.style.overflow = 'hidden'
}

function closeVideoLightbox() {
  videoLightboxOpen.value = false
  document.body.style.overflow = ''
}

function videoLbPrev() {
  const total = videos.value.length
  videoLbIndex.value = videoLbIndex.value <= 0 ? total - 1 : videoLbIndex.value - 1
}

function videoLbNext() {
  const total = videos.value.length
  videoLbIndex.value = videoLbIndex.value >= total - 1 ? 0 : videoLbIndex.value + 1
}

function onKeydown(e) {
  if (videoLightboxOpen.value) {
    if (e.key === 'Escape') closeVideoLightbox()
    if (e.key === 'ArrowLeft') videoLbPrev()
    if (e.key === 'ArrowRight') videoLbNext()
    return
  }
  if (!lightboxOpen.value) return
  if (e.key === 'Escape') closeLightbox()
  if (e.key === 'ArrowLeft') lightboxPrev()
  if (e.key === 'ArrowRight') lightboxNext()
}

watch(() => route.params.slug, (slug) => {
  if (slug) fetchProduct(slug)
})

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  loadSettings().catch(() => {})
  if (route.params.slug) fetchProduct(route.params.slug)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* ==========================================================================
   PRODUCT DETAILS PAGE (Luxury Tech Minimalist Bento Design)
   Matches new-design.css & ProductsPage / SolutionsPage aesthetic
   ========================================================================== */
.product-detail-page-new {
  background-color: var(--bg-canvas, #f7f7f7);
  color: var(--text-dark, #0a0a0a);
  direction: rtl;
  min-height: 100vh;
  overflow-x: hidden;
  padding-bottom: 60px;
}

.container {
  width: min(1340px, 94vw);
  margin: 0 auto;
  padding: 0 16px;
  box-sizing: border-box;
}

/* Loading & Not Found */
.detail-loading-state,
.detail-not-found-state {
  min-height: 70vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 120px 24px;
}

.luxury-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid rgba(255, 204, 0, 0.2);
  border-top-color: #ffcc00;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.not-found-icon-wrap {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  display: grid;
  place-items: center;
  margin-bottom: 24px;
}

/* 1. Hero Section */
.detail-hero-section {
  padding: 130px 0 40px 0;
  position: relative;
}

.detail-nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 28px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--border-light, #e5e5e5);
}

.back-nav-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  color: #0a0a0a;
  padding: 7px 16px;
  border-radius: 9999px;
  font-size: 0.82rem;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.back-nav-pill:hover {
  background: #0a0a0a;
  color: #ffcc00;
  border-color: #0a0a0a;
  transform: translateX(3px);
}

.detail-badges-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.category-tag-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 204, 0, 0.12);
  border: 1px solid rgba(255, 204, 0, 0.35);
  color: #946200;
  padding: 5px 14px;
  border-radius: 9999px;
  font-size: 0.78rem;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.2s;
}

.category-tag-pill:hover {
  background: #ffcc00;
  color: #000000;
}

.status-tag-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  color: #0a0a0a;
  padding: 5px 14px;
  border-radius: 9999px;
  font-size: 0.76rem;
  font-weight: 700;
}

.status-pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 8px #22c55e;
}

/* Overview Bento Split */
.overview-bento-grid {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 36px;
  align-items: start;
}

.overview-info-col {
  display: flex;
  flex-direction: column;
}

.product-main-title {
  font-size: clamp(1.85rem, 3.8vw, 2.85rem);
  font-weight: 900;
  line-height: 1.25;
  color: #0a0a0a;
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}

.product-slug-code {
  font-family: var(--font-en, 'Outfit', monospace);
  font-size: 0.82rem;
  font-weight: 600;
  color: #a1a1aa;
  direction: ltr;
  display: inline-block;
  margin-bottom: 18px;
}

.product-summary-text {
  font-size: 1.05rem;
  line-height: 1.85;
  color: #52525b;
  margin: 0 0 24px 0;
}

/* Metrics Bento Strip */
.metrics-bento-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 12px;
  margin-bottom: 22px;
}

.metric-bento-card {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: 18px;
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.02);
  transition: transform 0.2s, border-color 0.2s;
}

.metric-bento-card:hover {
  transform: translateY(-2px);
  border-color: #ffd54a;
}

.metric-val {
  font-family: var(--font-fa, 'Estedad', sans-serif);
  font-size: 1.45rem;
  font-weight: 900;
  color: #0a0a0a;
  line-height: 1.1;
}

.metric-lbl {
  font-size: 0.74rem;
  font-weight: 700;
  color: #71717a;
}

/* Tech Tags */
.tech-tags-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 28px;
}

.tech-tag-chip {
  background: #f4f4f5;
  color: #3f3f46;
  font-size: 0.76rem;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 9999px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

/* Actions */
.overview-actions-strip {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

/* Hero Media Card */
.hero-media-card {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: 28px;
  padding: 16px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.04);
}

.hero-media-frame {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 10;
  border-radius: 20px;
  overflow: hidden;
  background: #111116;
  cursor: pointer;
}

.hero-media-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.hero-media-frame:hover .hero-media-img {
  transform: scale(1.04);
}

.hero-media-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  background: #1c1c24;
}

.media-zoom-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: grid;
  place-items: center;
  opacity: 0;
  transition: opacity 0.25s ease;
}

.hero-media-frame:hover .media-zoom-overlay {
  opacity: 1;
}

.zoom-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(10, 10, 10, 0.85);
  backdrop-filter: blur(8px);
  color: #ffffff;
  padding: 8px 16px;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 700;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.hero-media-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-top: 14px;
}

.security-chip,
.sla-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.76rem;
  font-weight: 700;
  color: #52525b;
}

/* ==========================================================================
   2. PRODUCT VIDEO SHOWCASE (Cinematic Video Section)
   ========================================================================== */
.detail-video-section {
  padding: 60px 0;
}

.video-showcase-card {
  background: #0a0a0a;
  border: 1px solid #262626;
  border-radius: 28px;
  padding: 24px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.25);
  color: #ffffff;
}

.video-player-frame {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 20px;
  overflow: hidden;
  background: #000000;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.main-html5-video {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #000000;
}

.video-meta-top-strip {
  position: absolute;
  top: 14px;
  left: 14px;
  right: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  pointer-events: none;
}

.video-title-pill,
.btn-theater-mode {
  pointer-events: auto;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(10, 10, 10, 0.85);
  backdrop-filter: blur(10px);
  color: #ffffff;
  padding: 6px 14px;
  border-radius: 9999px;
  font-size: 0.78rem;
  font-weight: 700;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.btn-theater-mode {
  cursor: pointer;
  transition: all 0.2s;
}

.btn-theater-mode:hover {
  background: #ffcc00;
  color: #000000;
  border-color: #ffcc00;
}

/* Playlist Row */
.video-playlist-bar {
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.playlist-label {
  font-size: 0.84rem;
  font-weight: 700;
  color: #a1a1aa;
  margin-bottom: 12px;
}

.video-thumbnails-row {
  display: flex;
  align-items: center;
  gap: 14px;
  overflow-x: auto;
  padding-bottom: 8px;
  -webkit-overflow-scrolling: touch;
}

.video-thumb-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 8px 12px;
  cursor: pointer;
  transition: all 0.2s;
  color: #ffffff;
  text-align: right;
  min-width: 220px;
  flex-shrink: 0;
}

.video-thumb-card:hover,
.video-thumb-card.active {
  background: rgba(255, 204, 0, 0.12);
  border-color: #ffcc00;
  transform: translateY(-2px);
}

.thumb-mini-frame {
  position: relative;
  width: 64px;
  height: 42px;
  border-radius: 8px;
  overflow: hidden;
  background: #18181f;
  flex-shrink: 0;
}

.thumb-mini-frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mini-play-icon {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: grid;
  place-items: center;
  color: #ffcc00;
}

.thumb-mini-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.mini-title {
  font-size: 0.78rem;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mini-order {
  font-size: 0.68rem;
  color: #a1a1aa;
}

.admin-empty-video-card {
  background: #ffffff;
  border: 2px dashed #d4d4d8;
  border-radius: 24px;
  padding: 48px 24px;
  text-align: center;
  max-width: 680px;
  margin: 0 auto;
}

.admin-empty-video-card h3 {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0a0a0a;
  margin: 0 0 8px 0;
}

.admin-empty-video-card p {
  font-size: 0.88rem;
  line-height: 1.7;
  color: #71717a;
  margin: 0 0 20px 0;
}

/* ==========================================================================
   3. TECHNICAL SPECIFICATIONS & FULL DESCRIPTION
   ========================================================================== */
.detail-description-section {
  padding: 40px 0;
}

.description-bento-card {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: 28px;
  padding: 36px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02);
}

.desc-card-head {
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-light, #e5e5e5);
  margin-bottom: 28px;
}

.desc-body-content {
  font-size: 0.96rem;
  line-height: 1.95;
  color: #27272a;
}

/* ==========================================================================
   4. IMAGE GALLERY
   ========================================================================== */
.detail-gallery-section {
  padding: 50px 0;
}

.gallery-bento-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 18px;
}

@media (max-width: 1200px) {
  .gallery-bento-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .gallery-bento-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.gallery-bento-item {
  position: relative;
  aspect-ratio: 16 / 10;
  border-radius: 20px;
  overflow: hidden;
  background: #111116;
  cursor: pointer;
  border: 1px solid var(--border-light, #e5e5e5);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.03);
}

.gallery-bento-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.gallery-bento-item:hover img {
  transform: scale(1.05);
}

.gallery-hover-veil {
  position: absolute;
  inset: 0;
  background: rgba(10, 10, 10, 0.45);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.25s ease;
  color: #ffffff;
}

.gallery-bento-item:hover .gallery-hover-veil {
  opacity: 1;
}

.zoom-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 204, 0, 0.95);
  color: #000000;
  display: grid;
  place-items: center;
}

.gallery-item-index {
  font-size: 0.74rem;
  font-weight: 700;
}

/* ==========================================================================
   5. CATALOGS & DOWNLOADS
   ========================================================================== */
.detail-catalogs-section {
  padding: 50px 0;
}

.catalogs-bento-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.catalog-bento-card {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: 20px;
  padding: 22px;
  display: flex;
  align-items: center;
  gap: 16px;
  text-decoration: none;
  color: inherit;
  transition: all 0.25s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
}

.catalog-bento-card:hover {
  transform: translateY(-3px);
  border-color: #ffd54a;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.06);
}

.catalog-icon-box {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: rgba(255, 204, 0, 0.12);
  color: #946200;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.catalog-info-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.catalog-title {
  font-size: 0.96rem;
  font-weight: 800;
  color: #0a0a0a;
  margin: 0;
}

.catalog-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.catalog-ext-badge {
  background: #0a0a0a;
  color: #ffd54a;
  font-size: 0.68rem;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 6px;
  font-family: var(--font-en, 'Outfit', monospace);
}

.catalog-hint {
  font-size: 0.72rem;
  color: #71717a;
}

.catalog-download-circle {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #f4f4f5;
  color: #0a0a0a;
  display: grid;
  place-items: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.catalog-bento-card:hover .catalog-download-circle {
  background: #ffcc00;
  color: #000000;
  transform: translateY(2px);
}

/* ==========================================================================
   6. RELATED PRODUCTS
   ========================================================================== */
.detail-related-section {
  padding: 50px 0;
}

.related-bento-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
  gap: 24px;
}

.related-project-card {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: 22px;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
}

.related-project-card:hover {
  transform: translateY(-5px);
  border-color: #0a0a0a;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.07);
}

.related-card-media {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #111116;
  overflow: hidden;
}

.related-card-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.related-project-card:hover .related-card-media img {
  transform: scale(1.05);
}

.related-media-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
}

.related-card-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.related-card-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0a0a0a;
  margin: 0 0 8px 0;
}

.related-card-desc {
  font-size: 0.82rem;
  line-height: 1.65;
  color: #71717a;
  margin: 0 0 16px 0;
  flex: 1;
}

.related-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid var(--border-light, #e5e5e5);
  font-size: 0.78rem;
  font-weight: 700;
  color: #946200;
}

/* ==========================================================================
   7. CTA BANNER
   ========================================================================== */
.detail-cta-section {
  padding: 40px 0 20px 0;
}

.cta-bento-card {
  position: relative;
  background: #0a0a0a;
  border-radius: 32px;
  padding: 56px 40px;
  overflow: hidden;
  border: 1px solid #262626;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.25);
  color: #ffffff;
}

.cta-glow-effect {
  position: absolute;
  top: -120px;
  right: -100px;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 204, 0, 0.22) 0%, rgba(255, 204, 0, 0) 70%);
  pointer-events: none;
}

.cta-bento-content {
  position: relative;
  z-index: 2;
  max-width: 760px;
}

.section-tag-light {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #ffd54a;
}

.cta-bento-title {
  font-size: clamp(1.6rem, 3.2vw, 2.3rem);
  font-weight: 900;
  line-height: 1.35;
  color: #ffffff;
  margin: 12px 0 16px 0;
}

.cta-bento-desc {
  font-size: 0.95rem;
  line-height: 1.8;
  color: #a1a1aa;
  margin-bottom: 28px;
}

.cta-btns-row {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.btn-pill-ghost-light {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.16);
  color: #ffffff;
  padding: 10px 22px;
  border-radius: 9999px;
  font-size: 0.86rem;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-pill-ghost-light:hover {
  background: rgba(255, 255, 255, 0.16);
  color: #ffd54a;
}

/* ==========================================================================
   LIGHTBOX OVERLAYS
   ========================================================================== */
.luxury-lightbox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(5, 5, 8, 0.96);
  backdrop-filter: blur(24px);
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
  direction: rtl;
}

.lb-close-btn {
  position: absolute;
  top: 24px;
  left: 24px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 10;
}

.lb-close-btn:hover {
  background: #ffcc00;
  color: #000000;
}

.lb-nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 10;
}

.lb-nav-btn:hover {
  background: #ffcc00;
  color: #000000;
}

.lb-prev { right: 28px; }
.lb-next { left: 28px; }

.lb-stage-wrap {
  max-width: 90vw;
  max-height: 85vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lb-main-image {
  max-width: 88vw;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.lb-video-stage {
  width: min(1040px, 90vw);
  aspect-ratio: 16 / 9;
  flex-direction: column;
}

.lb-theater-video {
  width: 100%;
  height: 100%;
  border-radius: 16px;
  background: #000000;
}

.lb-video-title-bar {
  margin-top: 12px;
  color: #ffd54a;
  font-size: 0.9rem;
  font-weight: 800;
  text-align: center;
}

.lb-counter-strip {
  position: absolute;
  bottom: 24px;
  background: rgba(0, 0, 0, 0.6);
  padding: 6px 16px;
  border-radius: 9999px;
  color: #ffffff;
  font-size: 0.8rem;
  font-weight: 700;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

/* Lightbox Transition */
.lightbox-enter-active,
.lightbox-leave-active {
  transition: opacity 0.3s ease;
}

.lightbox-enter-from,
.lightbox-leave-to {
  opacity: 0;
}

/* ==========================================================================
   RESPONSIVE DESIGN (Requirement 6: کامل بهینه شده برای موبایل)
   ========================================================================== */
@media (max-width: 1024px) {
  .overview-bento-grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }
  .overview-visual-col {
    order: -1;
  }
}

@media (max-width: 768px) {
  .detail-hero-section {
    padding: 96px 0 24px 0;
  }
  .detail-nav-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .product-main-title {
    font-size: clamp(1.28rem, 5.2vw, 1.62rem);
    line-height: 1.32;
  }
  .product-summary-text {
    font-size: 0.84rem;
    line-height: 1.7;
  }
  .hero-media-card {
    padding: 12px;
    border-radius: 20px;
  }
  .hero-media-frame {
    border-radius: 14px;
  }
  .hero-media-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
    padding-top: 10px;
  }
  .metrics-bento-strip {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  .metric-bento-card {
    padding: 12px 14px;
    border-radius: 14px;
  }
  .metric-val {
    font-size: 1.25rem;
  }
  .metric-lbl {
    font-size: 0.68rem;
  }
  .overview-actions-strip {
    flex-direction: column;
    width: 100%;
  }
  .overview-actions-strip .btn-pill {
    width: 100%;
    justify-content: space-between;
    font-size: 0.8rem;
    min-height: 44px;
  }
  .description-bento-card {
    padding: 20px 16px;
    border-radius: 20px;
  }
  .section-title {
    font-size: clamp(1.22rem, 5vw, 1.48rem);
  }
  .section-desc {
    font-size: 0.82rem;
    line-height: 1.68;
  }
  .feature-item-title {
    font-size: 0.96rem;
  }
  .feature-item-desc {
    font-size: 0.78rem;
    line-height: 1.65;
  }
  .gallery-bento-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
  }
  .catalogs-bento-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .catalog-bento-card {
    padding: 16px 14px;
    border-radius: 16px;
  }
  .video-showcase-card {
    padding: 14px;
    border-radius: 20px;
  }
  .cta-bento-card {
    padding: 30px 18px;
    border-radius: 22px;
  }
  .cta-bento-title {
    font-size: clamp(1.25rem, 5vw, 1.55rem);
  }
  .cta-bento-desc {
    font-size: 0.82rem;
    line-height: 1.68;
  }
  .cta-btns-row {
    flex-direction: column;
    width: 100%;
  }
  .cta-btns-row .btn-pill,
  .cta-btns-row .btn-pill-ghost-light {
    width: 100%;
    justify-content: center;
    font-size: 0.8rem;
    min-height: 44px;
  }
  .lb-prev { right: 8px; }
  .lb-next { left: 8px; }
  .lb-nav-btn {
    width: 38px;
    height: 38px;
  }
}

@media (max-width: 480px) {
  .metrics-bento-strip {
    grid-template-columns: 1fr;
  }
  .product-main-title {
    font-size: clamp(1.18rem, 4.8vw, 1.38rem);
  }
  .product-summary-text {
    font-size: 0.78rem;
    line-height: 1.65;
  }
  .overview-actions-strip .btn-pill {
    font-size: 0.76rem;
    min-height: 42px;
  }
  .cta-bento-card {
    padding: 24px 14px;
    border-radius: 18px;
  }
  .cta-bento-title {
    font-size: clamp(1.15rem, 4.5vw, 1.35rem);
  }
}
</style>

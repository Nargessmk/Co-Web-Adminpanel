<template>
  <section
    id="products"
    class="products-section"
  >
    <!-- Architectural Ambient Lighting & Grid -->
    <div class="products-ambient-glow orb-1"></div>
    <div class="products-ambient-glow orb-2"></div>
    <div class="products-bg-grid"></div>

    <div class="products-container">

      <q-btn
        v-if="isAdmin && authorized"
        class="section-edit-btn"
        round
        dense
        size="sm"
        unelevated
        color="primary"
        icon="edit"
        @click="openProductsDialog"
      >
        <q-tooltip>ویرایش بخش محصولات</q-tooltip>
      </q-btn>

      <!-- Section Header -->
      <div class="section-header">
        <div class="eyebrow-pill">
          <span class="live-indicator"></span>
          <span>{{ settings.products_badge || 'سبد سامانه‌ها و محصولات' }}</span>
        </div>

        <h2 class="section-title">
          سامانه‌های نوآورانه و نرم‌افزارهای
          <span class="title-accent">مقیاس‌پذیر کلودلند</span>
        </h2>

        <RichContent
          class="section-description"
          :html="settings.products_description || 'مجموعه‌ای یکپارچه از راهکارهای نرم‌افزاری، اتوماسیون فرآیندها و پلتفرم‌های تحلیل داده که با بالاترین استانداردهای مهندسی تولید شده‌اند.'"
        />

        <!-- Category Filter Tabs -->
        <div class="category-tabs-bar">
          <button
            class="cat-tab-btn"
            :class="{ active: selectedCategory === 'all' }"
            @click="selectedCategory = 'all'"
          >
            <q-icon name="apps" size="16px" class="q-mr-xs" />
            <span>همه سامانه‌ها</span>
            <span class="tab-count">{{ products.length }}</span>
          </button>
          <button
            v-for="cat in availableCategories"
            :key="cat.slug"
            class="cat-tab-btn"
            :class="{ active: selectedCategory === cat.slug }"
            @click="selectedCategory = cat.slug"
          >
            <q-icon :name="cat.icon" size="16px" class="q-mr-xs" />
            <span>{{ cat.name }}</span>
          </button>
        </div>
      </div>

      <!-- High-End Bento Showcase Layout -->
      <div class="products-showcase-wrapper">

        <!-- 1. Featured Hero Product (Large Bento Card) -->
        <article
          v-if="featuredHeroProduct"
          class="hero-product-card double-bezel"
        >
          <div class="double-bezel-inner hero-card-inner">
            <div class="hero-product-grid">
              
              <!-- Content Side -->
              <div class="hero-product-info">
                <div class="hero-badge-row">
                  <span class="featured-spotlight-tag">
                    <q-icon name="stars" size="16px" />
                    سامانه برگزیده سازمانی
                  </span>
                  <span v-if="featuredHeroProduct.category" class="hero-category-tag">
                    {{ getCategoryName(featuredHeroProduct.category) }}
                  </span>
                </div>

                <router-link :to="`/products/${featuredHeroProduct.slug}`" class="hero-title-link">
                  <h3 class="hero-product-title">
                    {{ featuredHeroProduct.title }}
                  </h3>
                </router-link>

                <p class="hero-product-desc">
                  {{ previewText(featuredHeroProduct.description, 240) }}
                </p>

                <!-- Key Capabilities Grid -->
                <div class="hero-features-chips">
                  <div class="feature-chip">
                    <q-icon name="check_circle" size="16px" color="primary" />
                    <span>یکپارچگی چندمنبعی</span>
                  </div>
                  <div class="feature-chip">
                    <q-icon name="security" size="16px" color="primary" />
                    <span>امنیت سطح Enterprise</span>
                  </div>
                  <div class="feature-chip">
                    <q-icon name="bolt" size="16px" color="amber-8" />
                    <span>پردازش بلادرنگ</span>
                  </div>
                  <div class="feature-chip">
                    <q-icon name="verified" size="16px" color="positive" />
                    <span>گارانتی آپتایم ۹۹.۹۸٪</span>
                  </div>
                </div>

                <!-- Action Button -->
                <div class="hero-product-actions">
                  <router-link
                    :to="`/products/${featuredHeroProduct.slug}`"
                    class="hero-primary-btn"
                  >
                    <span>بررسی معماری و دمو</span>
                    <span class="btn-icon-capsule">
                      <q-icon name="arrow_back" size="16px" />
                    </span>
                  </router-link>
                  <router-link
                    to="/contact"
                    class="hero-secondary-btn"
                  >
                    <q-icon name="support_agent" size="18px" />
                    <span>درخواست جلسه مشاوره</span>
                  </router-link>
                </div>
              </div>

              <!-- Visual / Tech Canvas Side -->
              <router-link
                :to="`/products/${featuredHeroProduct.slug}`"
                class="hero-product-visual"
                aria-label="مشاهده تصویر سامانه برگزیده"
              >
                <img
                  v-if="featuredHeroProduct.image"
                  :src="featuredHeroProduct.image"
                  :alt="featuredHeroProduct.title"
                  class="hero-visual-img"
                  loading="lazy"
                />
                <div v-else class="hero-tech-canvas">
                  <div class="tech-canvas-grid"></div>
                  <div class="tech-canvas-glow"></div>
                  <div class="tech-interactive-hub">
                    <div class="hub-emblem">
                      <q-icon name="account_tree" size="54px" color="white" />
                    </div>
                    <div class="hub-rings ring-1"></div>
                    <div class="hub-rings ring-2"></div>
                  </div>
                  <div class="tech-metric-overlay">
                    <div class="metric-pill">
                      <span class="pulse-dot"></span>
                      <span>وضعیت: فعال و آماده پیاده‌سازی</span>
                    </div>
                  </div>
                </div>
                <div class="card-shine"></div>
              </router-link>

            </div>
          </div>
        </article>

        <!-- 2. Grid of Secondary Products -->
        <div class="products-grid">
          <ProductCard
            v-for="(product, index) in secondaryProducts"
            :key="product.id || product.slug"
            :product="product"
            class="product-enter"
            :style="{ animationDelay: `${index * 0.08}s` }"
          />
        </div>

      </div>

      <!-- All Products CTA & Catalog Download -->
      <div class="products-bottom-bar">
        <router-link
          to="/products"
          class="all-products-link"
        >
          <span class="link-label">{{ settings.products_all_label || 'مشاهده تمامی سامانه‌ها و محصولات' }}</span>
          <span class="btn-icon-capsule">
            <q-icon
              name="arrow_back"
              size="16px"
            />
          </span>
        </router-link>

        <router-link
          to="/contact"
          class="catalog-request-link"
        >
          <q-icon name="file_download" size="18px" />
          <span>درخواست کاتالوگ جامع محصولات</span>
        </router-link>
      </div>

    </div>

  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import ProductCard from './ProductCard.vue'
import RichContent from 'src/components/common/RichContent.vue'
import api from 'src/services/api'
import { useAuth } from 'src/composables/useAuth'
import { useHomeContent } from 'src/composables/useHomeContent'
import { useHomeAdmin } from 'src/composables/useHomeAdmin'
import { htmlToText } from 'src/utils/sanitize'

const { isAdmin } = useAuth()
const { settings } = useHomeContent()
const { authorized, openProductsDialog } = useHomeAdmin()

const selectedCategory = ref('all')

const previewText = (html, max = 180) => htmlToText(html, max)

const fallbackProducts = [
  {
    id: 1,
    title: 'سامانه یکپارچه مدیریت فرآیندهای کسب‌وکار (BPMS)',
    slug: 'cloudland-bpms',
    description: 'اتوماسیون هوشمند فرآیندها، موتور گردش کار پیشرفته بدون نیاز به کدنویسی، یکپارچه‌ساز فرم‌ها، امضای دیجیتال و کنترل دسترسی سازمانی.',
    image: null,
    url: null,
    is_featured: true,
    category: { name: 'اتوماسیون سازمانی', slug: 'automation' }
  },
  {
    id: 2,
    title: 'پلتفرم تحلیل کلان‌داده و هوش تجاری (BI & Analytics)',
    slug: 'cloudland-bi',
    description: 'تجمیع داده‌های چندمنبعی سازمانی، داشبوردهای مدیریتی بلادرنگ، پیش‌بینی شاخص‌های کلیدی با الگوریتم‌های هوش مصنوعی و گزارش‌ساز پویا.',
    image: null,
    url: null,
    is_featured: true,
    category: { name: 'تحلیل داده و هوش تجاری', slug: 'bi' }
  },
  {
    id: 3,
    title: 'زیرساخت ابری توزیع‌شده و مش میکروسرویس (Cloud Mesh)',
    slug: 'cloudland-mesh',
    description: 'اورکستریشن خودکار کانتینرها، مقیاس‌پذیری هوشمند بر اساس بار ترافیکی، مانیتورینگ کارایی و امنیت چندلایه‌ای سرویس‌های حیاتی.',
    image: null,
    url: null,
    is_featured: false,
    category: { name: 'زیرساخت ابری', slug: 'cloud' }
  },
  {
    id: 4,
    title: 'سامانه احراز هویت متمرکز و کنترل دسترسی (SSO & IAM)',
    slug: 'cloudland-sso',
    description: 'ورود یکپارچه امن، احراز هویت دو مرحله‌ای سخت‌افزاری و نرم‌افزاری، پیاده‌سازی متدولوژی Zero-Trust و لاگ‌گیری امنیتی لحظه‌ای.',
    image: null,
    url: null,
    is_featured: false,
    category: { name: 'امنیت داده', slug: 'security' }
  }
]

// Initialized with fallback so it renders instantly
const products = ref([...fallbackProducts])
const loading = ref(false)

function getCategoryName(category) {
  if (typeof category === 'string') return category
  return category?.name || ''
}

const availableCategories = computed(() => {
  const map = new Map()
  products.value.forEach(p => {
    if (p.category && p.category.slug) {
      if (!map.has(p.category.slug)) {
        let icon = 'dashboard'
        if (p.category.slug.includes('auto')) icon = 'smart_toy'
        else if (p.category.slug.includes('bi') || p.category.slug.includes('data')) icon = 'analytics'
        else if (p.category.slug.includes('cloud')) icon = 'cloud'
        else if (p.category.slug.includes('sec')) icon = 'shield'
        map.set(p.category.slug, {
          name: p.category.name,
          slug: p.category.slug,
          icon
        })
      }
    }
  })
  return Array.from(map.values())
})

const filteredProducts = computed(() => {
  if (selectedCategory.value === 'all') return products.value
  return products.value.filter(p => p.category?.slug === selectedCategory.value)
})

// Highlight the most featured product as hero
const featuredHeroProduct = computed(() => {
  if (!filteredProducts.value.length) return null
  return filteredProducts.value.find(p => p.is_featured) || filteredProducts.value[0]
})

// Remaining products for the lower grid
const secondaryProducts = computed(() => {
  if (!featuredHeroProduct.value) return []
  return filteredProducts.value.filter(p => p.id !== featuredHeroProduct.value.id)
})

async function fetchProducts() {
  try {
    const response = await api.get('/api/products', {
      params: { page: 1, limit: 6 },
      timeout: 2500
    })

    const rows = response.data?.data || []

    if (rows.length > 0) {
      products.value = rows.map((row) => ({
        id: row.id,
        title: row.title,
        slug: row.slug,
        description: row.short_description,
        image: row.image_url,
        url: row.url,
        is_featured: row.is_featured,
        category: row.category_name
          ? { name: row.category_name, slug: row.category_slug }
          : null,
      }))
    }
  } catch (error) {
    console.warn('Backend unavailable, using local products cache:', error?.message)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
/* =========================================
   PRODUCTS SECTION ROOT
========================================== */
.products-section {
  position: relative;
  padding: var(--section-pad-y) 0;
  background: var(--cl-surface);
  direction: rtl;
  overflow: hidden;
  border-top: 1px solid var(--cl-border);
  border-bottom: 1px solid var(--cl-border);
}

/* Ambient Backdrops */
.products-ambient-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(140px);
  pointer-events: none;
  opacity: 0.35;
}

.orb-1 {
  width: 550px;
  height: 550px;
  top: 15%;
  right: -100px;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.18) 0%, transparent 70%);
}

.orb-2 {
  width: 500px;
  height: 500px;
  bottom: 10%;
  left: -80px;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.14) 0%, transparent 70%);
}

.products-bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(to right, rgba(226, 232, 240, 0.3) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(226, 232, 240, 0.3) 1px, transparent 1px);
  background-size: 56px 56px;
  opacity: 0.55;
  pointer-events: none;
  -webkit-mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, #000 40%, transparent 100%);
  mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, #000 40%, transparent 100%);
}

.products-container {
  position: relative;
  z-index: 1;
  width: min(var(--container-max-w), calc(100% - 48px));
  margin: 0 auto;
}

/* Admin-only edit button */
.section-edit-btn {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 5;
  width: 32px;
  height: 32px;
}

/* =========================================
   Section Header & Category Tabs
========================================== */
.section-header {
  max-width: 760px;
  margin: 0 auto 46px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.section-title {
  margin: 14px 0 12px;
  color: var(--cl-text-dark);
  font-size: clamp(26px, 3.4vw, 36px);
  line-height: 1.32;
  font-weight: 800;
  letter-spacing: -0.025em;
}

.title-accent {
  color: var(--cl-primary);
  display: inline-block;
  position: relative;
}

.title-accent::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, var(--cl-primary), var(--cl-accent));
  border-radius: var(--radius-pill);
  opacity: 0.85;
}

.section-description {
  margin: 0 0 24px;
  color: var(--cl-text-muted);
  font-size: 15.5px;
  line-height: 1.85;
  max-width: 640px;
}

/* Category Filter Tabs */
.category-tabs-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
  padding: 6px;
  background: var(--cl-bg-subtle);
  border: 1px solid rgba(226, 232, 240, 0.85);
  border-radius: var(--radius-pill);
  box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.04);
}

.cat-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border-radius: var(--radius-pill);
  border: none;
  background: transparent;
  color: var(--cl-text-muted);
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s var(--cl-ease);
}

.cat-tab-btn:hover {
  color: var(--cl-primary);
  background: rgba(255, 255, 255, 0.6);
}

.cat-tab-btn.active {
  background: #ffffff;
  color: var(--cl-primary);
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
}

.tab-count {
  font-size: 11px;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: var(--radius-pill);
  background: var(--cl-primary-light);
  color: var(--cl-primary);
}

/* =========================================
   Hero Featured Product Card (Bento Star)
========================================== */
.hero-product-card {
  margin-bottom: 32px;
  transition: transform 0.35s var(--cl-ease), box-shadow 0.35s var(--cl-ease);
}

.hero-product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 48px -10px rgba(15, 23, 42, 0.12), 0 0 30px rgba(37, 99, 235, 0.1);
}

.hero-card-inner {
  padding: 38px 40px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
}

.hero-product-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr);
  gap: 40px;
  align-items: center;
}

.hero-badge-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

.featured-spotlight-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: var(--radius-pill);
  font-size: 12px;
  font-weight: 800;
  color: #78350F;
  background: linear-gradient(135deg, #FEF3C7, #FDE68A);
  border: 1px solid #FCD34D;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.18);
}

.hero-category-tag {
  font-size: 12px;
  font-weight: 700;
  color: var(--cl-primary);
  background: var(--cl-primary-light);
  padding: 5px 12px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(37, 99, 235, 0.15);
}

.hero-title-link {
  text-decoration: none;
  display: block;
}

.hero-product-title {
  font-size: clamp(24px, 2.6vw, 32px);
  font-weight: 800;
  color: var(--cl-text-dark);
  line-height: 1.35;
  margin: 0 0 16px;
  transition: color 0.25s var(--cl-ease);
}

.hero-product-card:hover .hero-product-title {
  color: var(--cl-primary);
}

.hero-product-desc {
  color: var(--cl-text);
  font-size: 15.5px;
  line-height: 1.85;
  margin: 0 0 26px;
}

/* Feature Chips */
.hero-features-chips {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 32px;
}

.feature-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 600;
  color: var(--cl-text-dark);
}

/* Action Buttons */
.hero-product-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.hero-primary-btn {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px 10px 24px;
  background: var(--cl-primary);
  color: #ffffff;
  font-weight: 700;
  font-size: 14.5px;
  border-radius: var(--radius-pill);
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.3);
  text-decoration: none;
  transition: all 0.3s var(--cl-ease);
}

.hero-primary-btn:hover {
  background: var(--cl-primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.4);
}

.hero-primary-btn:hover .btn-icon-capsule {
  transform: translateX(-4px);
  background: rgba(255, 255, 255, 0.35);
}

.hero-secondary-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--cl-surface);
  color: var(--cl-text-dark);
  border: 1px solid rgba(226, 232, 240, 0.9);
  font-weight: 700;
  font-size: 14px;
  border-radius: var(--radius-pill);
  text-decoration: none;
  transition: all 0.25s var(--cl-ease);
}

.hero-secondary-btn:hover {
  border-color: var(--cl-primary);
  color: var(--cl-primary);
  background: var(--cl-primary-light);
}

/* Hero Tech Canvas Visual */
.hero-product-visual {
  position: relative;
  height: 380px;
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: #0B132B;
  display: block;
  text-decoration: none;
  box-shadow: inset 0 0 40px rgba(0, 0, 0, 0.4);
}

.hero-visual-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s var(--cl-ease);
}

.hero-product-card:hover .hero-visual-img {
  transform: scale(1.05);
}

.hero-tech-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at 50% 50%, #172554 0%, #0B132B 85%);
}

.tech-canvas-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(to right, rgba(255, 255, 255, 0.08) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(255, 255, 255, 0.08) 1px, transparent 1px);
  background-size: 30px 30px;
}

.tech-canvas-glow {
  position: absolute;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.4) 0%, transparent 70%);
  filter: blur(40px);
}

.tech-interactive-hub {
  position: relative;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hub-emblem {
  width: 100px;
  height: 100px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.25);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.5s var(--cl-ease);
}

.hero-product-card:hover .hub-emblem {
  transform: scale(1.1);
}

.hub-rings {
  position: absolute;
  border-radius: 50%;
  border: 1px dashed rgba(255, 255, 255, 0.15);
  pointer-events: none;
}

.ring-1 {
  width: 170px;
  height: 170px;
  animation: rotateClockwise 25s linear infinite;
}

.ring-2 {
  width: 240px;
  height: 240px;
  animation: rotateCounterClockwise 35s linear infinite;
}

@keyframes rotateClockwise {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes rotateCounterClockwise {
  from { transform: rotate(0deg); }
  to { transform: rotate(-360deg); }
}

.tech-metric-overlay {
  position: absolute;
  bottom: 16px;
  left: 16px;
  right: 16px;
  display: flex;
  justify-content: center;
  z-index: 4;
}

.metric-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: var(--radius-pill);
  color: #ffffff;
  font-size: 11.5px;
  font-weight: 700;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  animation: pulse-ring 2s infinite;
}

/* =========================================
   Secondary Products Grid
========================================== */
.products-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
}

.product-enter {
  animation: fadeInUp 0.6s var(--cl-ease) both;
}

/* =========================================
   Bottom Bar
========================================== */
.products-bottom-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-top: 55px;
  flex-wrap: wrap;
}

.all-products-link {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px 12px 28px;
  background: var(--cl-primary);
  color: #ffffff;
  font-weight: 700;
  font-size: 14.5px;
  border-radius: var(--radius-pill);
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.3);
  text-decoration: none;
  transition: all 0.3s var(--cl-ease);
}

.all-products-link:hover {
  background: var(--cl-primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.4);
}

.all-products-link:hover .btn-icon-capsule {
  transform: translateX(-4px);
  background: rgba(255, 255, 255, 0.35);
}

.catalog-request-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 22px;
  background: #ffffff;
  color: var(--cl-text-dark);
  font-weight: 700;
  font-size: 14px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(226, 232, 240, 0.9);
  box-shadow: var(--shadow-xs);
  text-decoration: none;
  transition: all 0.25s var(--cl-ease);
}

.catalog-request-link:hover {
  border-color: var(--cl-primary);
  color: var(--cl-primary);
  background: var(--cl-primary-light);
  transform: translateY(-2px);
}

/* =========================================
   Responsive Breakpoints
========================================== */
@media (max-width: 1080px) {
  .hero-product-grid {
    grid-template-columns: 1fr;
    gap: 30px;
  }

  .hero-product-visual {
    height: 300px;
  }

  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .products-section {
    padding: 70px 0 80px;
  }

  .hero-card-inner {
    padding: 24px 20px;
  }

  .hero-features-chips {
    grid-template-columns: 1fr;
  }

  .products-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .products-bottom-bar {
    flex-direction: column;
    gap: 12px;
    width: 100%;
  }

  .all-products-link,
  .catalog-request-link {
    width: 100%;
    justify-content: center;
  }
}
</style>

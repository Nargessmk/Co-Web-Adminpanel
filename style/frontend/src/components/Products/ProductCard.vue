<template>
  <article
    class="product-card double-bezel"
    ref="cardRef"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
  >
    <div class="product-card-inner double-bezel-inner">

      <!-- Product Image or Architectural Tech Illustration (SEO Link) -->
      <router-link
        :to="`/products/${product.slug}`"
        class="product-image-wrapper"
        :aria-label="product.title"
      >
        <img
          v-if="product.image"
          :src="product.image"
          :alt="product.title"
          class="product-image"
          loading="lazy"
        />

        <!-- High-End Dynamic Tech Art when no image uploaded -->
        <div
          v-else
          class="product-graphic"
          :class="getCategoryTheme(product)"
        >
          <!-- Geometric Matrix Layer -->
          <div class="graphic-grid"></div>

          <!-- Luminous Ambient Core -->
          <div class="graphic-core"></div>

          <!-- Themed Architectural Emblem -->
          <div class="graphic-emblem">
            <q-icon
              :name="getCategoryIcon(product)"
              size="40px"
              class="emblem-icon"
            />
          </div>

          <!-- Tech Floating Signals -->
          <div class="graphic-nodes">
            <span class="tech-node node-1"></span>
            <span class="tech-node node-2"></span>
            <span class="tech-node node-3"></span>
          </div>

          <div class="graphic-watermark">
            {{ getWatermark(product) }}
          </div>
        </div>

        <!-- Badges Bar -->
        <div class="badges-row">
          <!-- Category -->
          <span
            v-if="product.category"
            class="product-category-badge"
          >
            {{ getCategoryName(product.category) }}
          </span>

          <!-- Featured Tag -->
          <span
            v-if="product.is_featured"
            class="featured-badge"
          >
            <q-icon name="star" size="13px" class="q-mr-xs" />
            ویژه
          </span>
        </div>

        <!-- External URL badge -->
        <a
          v-if="product.url"
          :href="product.url"
          target="_blank"
          rel="noopener"
          class="product-url-badge"
          @click.stop
          aria-label="پیوند خارجی"
        >
          <q-icon name="open_in_new" size="15px" />
        </a>

        <!-- Shine overlay on hover -->
        <div class="card-shine"></div>

      </router-link>

      <!-- Content -->
      <div class="product-content">

        <router-link
          :to="`/products/${product.slug}`"
          class="product-title-link"
        >
          <h3 class="product-title">
            {{ product.title }}
          </h3>
        </router-link>

        <p class="product-desc">
          {{ previewText(product.description) }}
        </p>

        <div class="product-footer">
          <router-link
            :to="`/products/${product.slug}`"
            class="product-cta-btn"
          >
            <span class="cta-label">مشاهده جزئیات</span>
            <span class="btn-icon-capsule">
              <q-icon
                name="arrow_back"
                size="15px"
              />
            </span>
          </router-link>
        </div>

      </div>

    </div>
  </article>
</template>

<script setup>
import { ref } from 'vue'
import { htmlToText } from 'src/utils/sanitize'

const previewText = (html) => htmlToText(html, 130)

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const cardRef = ref(null)

function getCategoryName(category) {
  if (typeof category === 'string') return category
  return category?.name || ''
}

function getCategorySlug(product) {
  const cat = product.category
  if (!cat) return ''
  return (typeof cat === 'object' ? cat.slug : cat) || ''
}

function getCategoryTheme(product) {
  const slug = getCategorySlug(product).toLowerCase()
  const title = (product.title || '').toLowerCase()
  if (slug.includes('software') || title.includes('erp') || title.includes('pipeline')) return 'theme-software'
  if (slug.includes('cloud') || title.includes('cloud') || title.includes('migration')) return 'theme-cloud'
  if (slug.includes('ai') || slug.includes('machine') || title.includes('bot') || title.includes('analytics')) return 'theme-ai'
  if (slug.includes('consulting') || slug.includes('security') || title.includes('security')) return 'theme-security'
  return 'theme-default'
}

function getCategoryIcon(product) {
  const slug = getCategorySlug(product).toLowerCase()
  const title = (product.title || '').toLowerCase()
  if (title.includes('security')) return 'shield'
  if (title.includes('analytics')) return 'analytics'
  if (title.includes('bot') || slug.includes('ai')) return 'smart_toy'
  if (title.includes('migration') || slug.includes('cloud')) return 'cloud_sync'
  if (title.includes('pipeline')) return 'terminal'
  if (title.includes('erp') || slug.includes('software')) return 'layers'
  return 'hub'
}

function getWatermark(product) {
  const title = (product.title || '').toUpperCase()
  if (title.includes('ERP')) return 'ENTERPRISE ERP'
  if (title.includes('DEVOPS')) return 'CI / CD PIPELINE'
  if (title.includes('MIGRATION')) return 'CLOUD ARCHITECTURE'
  if (title.includes('ANALYTICS')) return 'BIG DATA & BI'
  if (title.includes('BOT')) return 'NEURAL AI MODEL'
  if (title.includes('SECURITY')) return 'CYBER DEFENSE'
  return 'CLOUDLAND SUITE'
}

function handleMouseMove(e) {
  const card = cardRef.value
  if (!card) return

  const rect = card.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  const centerX = rect.width / 2
  const centerY = rect.height / 2

  const rotateX = ((y - centerY) / centerY) * -3.5
  const rotateY = ((x - centerX) / centerX) * 3.5

  card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-6px)`
}

function handleMouseLeave() {
  const card = cardRef.value
  if (!card) return
  card.style.transform = 'perspective(900px) rotateX(0deg) rotateY(0deg) translateY(0px)'
}
</script>

<style scoped>
.product-card {
  position: relative;
  border-radius: var(--nx-radius-card, 22px);
  padding: 6px;
  background: #FFFFFF;
  border: 1.5px solid var(--nx-ink, #111113);
  box-shadow: var(--nx-shadow-hard, -4px 5px 0 #111113);
  transition: border-color 0.35s var(--cl-ease), box-shadow 0.35s var(--cl-ease), transform 0.35s var(--cl-ease);
  will-change: transform;
}

.product-card-inner {
  border-radius: calc(var(--nx-radius-card, 22px) - 6px);
  overflow: hidden;
  background: #FFFFFF;
  border: 1.5px solid var(--nx-ink, #111113);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.product-card:hover {
  border-color: var(--nx-gold-ink, #8A6100);
  box-shadow: var(--nx-shadow-hard-lg, -7px 8px 0 #111113);
}

/* =========================
   Image / Visual Canvas
========================= */

.product-image-wrapper {
  position: relative;
  height: 220px;
  overflow: hidden;
  background: #EFEFEF;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s var(--cl-ease);
}

.product-card:hover .product-image {
  transform: scale(1.06);
}

/* =========================
   Dynamic Tech Art Illustration
========================= */

.product-graphic {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: transform 0.6s var(--cl-ease);
}

.product-card:hover .product-graphic {
  transform: scale(1.03);
}

.graphic-grid {
  position: absolute;
  inset: 0;
  background-size: 24px 24px;
  background-image:
    linear-gradient(to right, rgba(17, 17, 19, 0.07) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(17, 17, 19, 0.07) 1px, transparent 1px);
}

.graphic-core {
  position: absolute;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.5;
}

.graphic-emblem {
  position: relative;
  z-index: 3;
  width: 76px;
  height: 76px;
  border-radius: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFFFFF;
  border: 1.5px solid var(--nx-ink, #111113);
  box-shadow: -4px 5px 0 var(--nx-ink, #111113);
  transition: transform 0.4s var(--cl-ease);
}

.product-card:hover .graphic-emblem {
  transform: scale(1.1);
}

.emblem-icon {
  color: var(--nx-ink, #111113);
}

.graphic-watermark {
  position: absolute;
  bottom: 12px;
  left: 14px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.12em;
  color: rgba(17, 17, 19, 0.35);
  pointer-events: none;
}

/* Tech Nodes */
.graphic-nodes {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.tech-node {
  position: absolute;
  border-radius: 50%;
}

.node-1 {
  width: 6px;
  height: 6px;
  top: 35px;
  left: 45px;
  background: #2563EB;
}

.node-2 {
  width: 5px;
  height: 5px;
  bottom: 40px;
  right: 50px;
  background: #F59E0B;
}

.node-3 {
  width: 4px;
  height: 4px;
  top: 45px;
  right: 40px;
  background: #10B981;
}

/* Category Themes */
.theme-software {
  background: linear-gradient(135deg, #FFF7D6 0%, #FFE9A8 60%, #FFD54A 100%);
}
.theme-software .graphic-core {
  background: #F5C21B;
}

.theme-cloud {
  background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 60%, #BAE6FD 100%);
}
.theme-cloud .graphic-core {
  background: #38BDF8;
}

.theme-ai {
  background: linear-gradient(135deg, #FAF5FF 0%, #F3E8FF 60%, #E9D5FF 100%);
}
.theme-ai .graphic-core {
  background: #A855F7;
}

.theme-security {
  background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 60%, #A7F3D0 100%);
}
.theme-security .graphic-core {
  background: #10B981;
}

.theme-default {
  background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
}
.theme-default .graphic-core {
  background: #60A5FA;
}

/* =========================
   Badges
========================= */

.badges-row {
  position: absolute;
  top: 14px;
  right: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 5;
}

.product-category-badge {
  padding: 5px 12px;
  border-radius: 999px;
  color: var(--nx-ink, #111113);
  background: #FFFFFF;
  border: 1.5px solid var(--nx-ink, #111113);
  font-size: 11px;
  font-weight: 800;
  box-shadow: -2px 3px 0 var(--nx-ink, #111113);
}

.featured-badge {
  padding: 5px 11px;
  border-radius: 999px;
  color: #111113;
  background: var(--nx-yellow);
  border: 1.5px solid var(--nx-ink, #111113);
  font-size: 11px;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  box-shadow: -2px 3px 0 var(--nx-ink, #111113);
}

.product-url-badge {
  position: absolute;
  top: 14px;
  left: 14px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: var(--nx-ink, #111113);
  background: #FFFFFF;
  border: 1.5px solid var(--nx-ink, #111113);
  box-shadow: -2px 3px 0 var(--nx-ink, #111113);
  text-decoration: none;
  z-index: 5;
  transition: transform 0.25s var(--cl-ease), background 0.25s var(--cl-ease);
}

.product-url-badge:hover {
  background: var(--nx-yellow);
  transform: scale(1.1);
}

/* Shine */
.card-shine {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    105deg,
    transparent 20%,
    rgba(255, 255, 255, 0.5) 50%,
    transparent 80%
  );
  transform: translateX(-100%);
  transition: transform 0.75s var(--cl-ease);
  pointer-events: none;
}

.product-card:hover .card-shine {
  transform: translateX(100%);
}

/* =========================
   Card Body
========================= */

.product-content {
  padding: 22px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  background: #FFFFFF;
}

.product-title-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.product-title {
  margin: 0 0 10px;
  color: var(--nx-ink, #111113);
  font-size: 17.5px;
  font-weight: 800;
  line-height: 1.5;
  letter-spacing: -0.01em;
  transition: color 0.25s var(--cl-ease);
}

.product-card:hover .product-title {
  color: var(--nx-gold-ink, #8A6100);
}

.product-desc {
  min-height: 44px;
  margin: 0 0 20px;
  color: #52525B;
  font-size: 13.5px;
  line-height: 1.8;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-footer {
  margin-top: auto;
  padding-top: 14px;
  border-top: 1px solid rgba(17, 17, 19, 0.12);
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.product-cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  font-family: inherit;
  font-size: 13.5px;
  font-weight: 800;
  color: var(--nx-ink, #111113);
  transition: all 0.25s var(--cl-ease);
}

.product-cta-btn .btn-icon-capsule {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--nx-yellow, #FFD54A);
  color: var(--nx-ink, #111113);
  border: 1.5px solid var(--nx-ink, #111113);
  box-shadow: -2px 3px 0 var(--nx-ink, #111113);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.25s var(--cl-ease), background 0.25s var(--cl-ease), color 0.25s var(--cl-ease);
}

.product-card:hover .product-cta-btn .btn-icon-capsule {
  background: var(--nx-ink, #111113);
  color: var(--nx-yellow, #FFD54A);
  transform: translateX(-4px);
}

/* =========================
   Mobile Optimization
========================= */

@media (max-width: 600px) {
  .product-image-wrapper {
    height: 170px;
  }

  .product-content {
    padding: 16px;
  }

  .product-title {
    font-size: 16px;
  }

  .product-desc {
    font-size: 12.5px;
    line-height: 1.7;
    margin-bottom: 14px;
  }

  .graphic-emblem {
    width: 60px;
    height: 60px;
    border-radius: 18px;
  }

  .emblem-icon {
    font-size: 30px !important;
  }
}
</style>

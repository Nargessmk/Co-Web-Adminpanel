<template>
  <section class="customers-section">
    <div class="customers-container">

      <q-btn
        v-if="isAdmin && authorized"
        class="section-edit-btn"
        round
        dense
        size="sm"
        unelevated
        color="primary"
        icon="edit"
        @click="openCustomersDialog"
      >
        <q-tooltip>ویرایش بخش مشتریان</q-tooltip>
      </q-btn>

      <!-- Section Header -->
      <div class="section-header">

        <div class="eyebrow-pill">
          <span class="live-indicator"></span>
          <span>{{ settings.customers_badge }}</span>
        </div>

        <h2 class="section-title">
          {{ settings.customers_title }}
          <span class="title-accent">{{ settings.customers_title_accent }}</span>
        </h2>

        <RichContent
          class="section-description"
          :html="settings.customers_description"
        />

      </div>

      <!-- Customer Logos Marquee Ticker -->
      <div v-if="customers.length" class="customers-marquee">
        <!-- Forward Arrow (Right in RTL) -->
        <q-btn
          class="marquee-arrow marquee-arrow-next"
          round
          dense
          unelevated
          icon="chevron_right"
          aria-label="مشتری بعدی"
          @click="nudge(1)"
        >
          <q-tooltip>بعدی</q-tooltip>
        </q-btn>

        <div class="marquee-viewport">
          <div ref="trackEl" class="marquee-track">
            <div
              v-for="(customer, index) in doubledCustomers"
              :key="`${customer.id ?? customer.name}-${index}`"
              class="marquee-item"
              :aria-hidden="index >= customers.length ? 'true' : undefined"
            >
              <div class="customer-card double-bezel">
                <div class="customer-card-inner double-bezel-inner">
                  <div class="customer-logo">
                    <img
                      v-if="customer.logo_url"
                      :src="customer.logo_url"
                      :alt="customer.name"
                      class="customer-logo-img"
                      loading="lazy"
                      decoding="async"
                    />
                    <div v-else class="customer-monogram" :class="getMonogramTheme(customer)">
                      <div class="monogram-icon-box">
                        <q-icon name="business" size="20px" />
                      </div>
                      <span class="customer-logo-text">{{ customer.logo }}</span>
                    </div>
                  </div>
                  <span class="customer-name">{{ customer.name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Backward Arrow (Left in RTL) -->
        <q-btn
          class="marquee-arrow marquee-arrow-prev"
          round
          dense
          unelevated
          icon="chevron_left"
          aria-label="مشتری قبلی"
          @click="nudge(-1)"
        >
          <q-tooltip>قبلی</q-tooltip>
        </q-btn>
      </div>

      <!-- Executive Trust Message -->
      <div class="trust-message double-bezel">
        <div class="trust-inner double-bezel-inner">

          <div class="trust-icon-box">
            <q-icon
              name="verified"
              size="32px"
            />
          </div>

          <div class="trust-content">
            <div class="trust-headline-row">
              <strong class="trust-title">
                {{ settings.trust_title }}
              </strong>
              <div class="trust-stars">
                <q-icon v-for="s in 5" :key="s" name="star" size="14px" class="star-icon" />
              </div>
            </div>

            <RichContent
              class="trust-desc"
              :html="settings.trust_description"
            />
          </div>

        </div>
      </div>

    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import RichContent from 'src/components/common/RichContent.vue'
import { useAuth } from 'src/composables/useAuth'
import { useHomeContent } from 'src/composables/useHomeContent'
import { useHomeAdmin } from 'src/composables/useHomeAdmin'

const { isAdmin } = useAuth()
const { settings, customers: homeCustomers } = useHomeContent()
const { authorized, openCustomersDialog } = useHomeAdmin()

const customers = computed(() => homeCustomers.value || [])
const doubledCustomers = computed(() => [...customers.value, ...customers.value])

const trackEl = ref(null)

const SPEED = 50
let position = 0
let frame = null
let lastTime = 0
let loopDistance = 0
let stepDistance = 0
let probe = 0

function getMonogramTheme(customer) {
  const code = String(customer.logo || customer.name || '').toLowerCase()
  if (code.includes('digi')) return 'mono-red'
  if (code.includes('mci')) return 'mono-teal'
  if (code.includes('snapp')) return 'mono-green'
  if (code.includes('tapsi')) return 'mono-amber'
  if (code.includes('iran')) return 'mono-blue'
  return 'mono-primary'
}

function measure () {
  const el = trackEl.value
  if (!el) {
    loopDistance = 0
    stepDistance = 0
    return
  }

  const items = el.querySelectorAll('.marquee-item')
  const count = items.length / 2
  if (!count || items.length < 2) {
    loopDistance = 0
    stepDistance = 0
    return
  }

  loopDistance = Math.abs(items[count].offsetLeft - items[0].offsetLeft)
  const gap = parseFloat(window.getComputedStyle(el).columnGap) || 0
  stepDistance = items[0].offsetWidth + gap
}

function applyPosition () {
  const el = trackEl.value
  if (el) el.style.transform = `translateX(${position}px)`
}

function normalise () {
  if (!loopDistance) return
  position = ((position % loopDistance) + loopDistance) % loopDistance
  applyPosition()
}

function prefersReducedMotion () {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

function tick (time) {
  if (!lastTime) lastTime = time
  const delta = (time - lastTime) / 1000
  lastTime = time

  if (!document.hidden && !prefersReducedMotion()) {
    if (!loopDistance && ++probe % 30 === 0) {
      measure()
    }
    if (loopDistance) {
      position -= SPEED * delta
      if (position <= -loopDistance) position += loopDistance
      applyPosition()
    }
  }

  frame = requestAnimationFrame(tick)
}

function start () {
  if (frame !== null) return
  lastTime = 0
  frame = requestAnimationFrame(tick)
}

function stop () {
  if (frame === null) return
  cancelAnimationFrame(frame)
  frame = null
}

function nudge (direction) {
  if (!stepDistance) {
    measure()
    if (!stepDistance) return
  }
  position -= direction * stepDistance
  normalise()
}

function onResize () {
  measure()
  normalise()
}

onMounted(() => {
  measure()
  normalise()
  start()
  window.addEventListener('resize', onResize)
})

watch(() => customers.value.length, () => {
  nextTick(() => {
    measure()
    normalise()
  })
})

onBeforeUnmount(() => {
  stop()
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.customers-section {
  position: relative;
  padding: 110px 0;
  background: var(--cl-surface);
  direction: rtl;
  overflow: hidden;
}

.customers-container {
  position: relative;
  z-index: 1;
  width: min(1440px, calc(100% - 48px));
  margin: 0 auto;
}

.section-edit-btn {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 5;
  width: 32px;
  height: 32px;
}

/* =========================
   Section Header
========================= */

.section-header {
  max-width: 700px;
  margin: 0 auto 55px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.section-title {
  margin: 16px 0 12px;
  color: var(--cl-text-dark);
  font-size: clamp(28px, 3.8vw, 40px);
  line-height: 1.3;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.title-accent {
  color: var(--cl-primary);
}

.section-description {
  margin: 0;
  color: var(--cl-text-muted);
  font-size: 16px;
  line-height: 1.8;
  max-width: 580px;
}

/* =========================
   Marquee Ticker
========================= */

.customers-marquee {
  display: flex;
  align-items: center;
  gap: 16px;
}

.marquee-viewport {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  -webkit-mask-image: linear-gradient(to right, transparent, #000 8%, #000 92%, transparent);
  mask-image: linear-gradient(to right, transparent, #000 8%, #000 92%, transparent);
  padding: 10px 0;
}

.marquee-track {
  display: flex;
  align-items: stretch;
  column-gap: 20px;
  width: max-content;
  will-change: transform;
}

.marquee-arrow {
  flex: 0 0 auto;
  width: 44px;
  height: 44px;
  color: var(--cl-text-dark);
  background: var(--cl-surface);
  border: 1px solid var(--cl-border);
  box-shadow: var(--shadow-sm);
  transition: all 0.25s var(--cl-ease);
}

.marquee-arrow:hover {
  background: var(--cl-primary);
  border-color: var(--cl-primary);
  color: #ffffff;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.marquee-arrow:active {
  transform: scale(0.95);
}

/* =========================
   Customer Double-Bezel Card
========================= */

.marquee-item {
  flex: 0 0 auto;
  width: 210px;
}

.customer-card {
  padding: 5px;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(226, 232, 240, 0.85);
  box-shadow: var(--shadow-xs);
  transition: transform 0.3s var(--cl-ease), border-color 0.3s var(--cl-ease), box-shadow 0.3s var(--cl-ease);
}

.customer-card-inner {
  padding: 20px 16px;
  min-height: 140px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border-radius: calc(var(--radius-lg) - 5px);
  background: var(--cl-surface);
}

.customer-card:hover {
  transform: translateY(-4px);
  border-color: rgba(37, 99, 235, 0.3);
  box-shadow: var(--shadow-md), 0 0 16px rgba(37, 99, 235, 0.08);
}

.customer-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 52px;
  width: 100%;
}

.customer-logo-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  filter: grayscale(100%);
  opacity: 0.7;
  transition: all 0.35s var(--cl-ease);
}

.customer-card:hover .customer-logo-img {
  filter: grayscale(0%);
  opacity: 1;
  transform: scale(1.05);
}

/* High-End Typographic Monogram */
.customer-monogram {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: var(--radius-pill);
  background: var(--cl-bg);
  border: 1px solid var(--cl-border);
  transition: all 0.3s var(--cl-ease);
}

.monogram-icon-box {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(37, 99, 235, 0.1);
  color: var(--cl-primary);
}

.customer-logo-text {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14.5px;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: var(--cl-text-dark);
}

.customer-card:hover .customer-monogram {
  background: var(--cl-primary-light);
  border-color: rgba(37, 99, 235, 0.3);
}

.customer-card:hover .customer-logo-text {
  color: var(--cl-primary);
}

.customer-name {
  color: var(--cl-text-muted);
  font-size: 13px;
  font-weight: 600;
  text-align: center;
  line-height: 1.4;
  white-space: nowrap;
}

/* =========================
   Executive Trust Banner
========================= */

.trust-message {
  max-width: 860px;
  margin: 60px auto 0;
  padding: 6px;
  border-radius: var(--radius-xl);
  background: rgba(255, 255, 255, 0.8);
  box-shadow: var(--shadow-sm);
}

.trust-inner {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 24px 32px;
  border-radius: calc(var(--radius-xl) - 6px);
  background: var(--cl-bg);
  border: 1px solid rgba(226, 232, 240, 0.7);
  position: relative;
  overflow: hidden;
}

.trust-inner::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, var(--cl-primary), var(--cl-accent));
}

.trust-icon-box {
  flex-shrink: 0;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
  background: var(--cl-primary);
  color: #ffffff;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25);
  transition: transform 0.3s var(--cl-ease);
}

.trust-message:hover .trust-icon-box {
  transform: scale(1.06);
}

.trust-content {
  flex: 1;
  text-align: right;
}

.trust-headline-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}

.trust-title {
  color: var(--cl-text-dark);
  font-size: 17px;
  font-weight: 800;
}

.trust-stars {
  display: inline-flex;
  gap: 2px;
}

.star-icon {
  color: var(--cl-accent);
}

.trust-desc {
  color: var(--cl-text-muted);
  font-size: 13.5px;
  line-height: 1.8;
}

/* =========================
   Responsive Breakpoints
========================= */

@media (max-width: 650px) {
  .customers-section {
    padding: 60px 0 70px;
  }

  .customers-container {
    width: calc(100% - 24px);
  }

  .marquee-item {
    width: 165px;
  }

  .customer-card-inner {
    padding: 16px 10px;
    min-height: 120px;
  }

  .customer-logo-text {
    font-size: 12.5px;
  }

  .customer-name {
    font-size: 11.5px;
  }

  .marquee-arrow {
    width: 36px;
    height: 36px;
  }

  .trust-inner {
    flex-direction: column;
    text-align: center;
    padding: 20px 16px;
  }

  .trust-inner::after {
    top: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: 3px;
  }

  .trust-content {
    text-align: center;
  }

  .trust-headline-row {
    flex-direction: column;
    gap: 6px;
  }
}
</style>

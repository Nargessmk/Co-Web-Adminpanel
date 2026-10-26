<template>
  <section class="hero-section" id="sec-hero">
    <div class="hero-container">
      <div class="hero-split-grid">
        <!-- Visual Column (Right in RTL) -->
        <div class="hero-visual-col">
          <div class="hero-dashboard-frame">
            <video
              v-if="isVideo"
              ref="heroVideoRef"
              class="hero-dashboard-video"
              autoplay
              loop
              muted
              playsinline
              webkit-playsinline
              disablePictureInPicture
              preload="auto"
              poster="/Modern 3D Tech Dashboard Illustration(1).png"
              @loadeddata="onHeroMediaLoad"
              @loadedmetadata="onHeroMediaLoad"
            >
              <source :src="heroMediaSrc" type="video/mp4" />
              <source src="/images/herosection-video.mp4" type="video/mp4" />
              <source src="/images/herosection-video.mp4" type="video/mp4" />
            </video>
            <img 
              v-else
              :src="heroMediaSrc" 
              alt="داشبورد و معماری ابری هوشمند کهکشان" 
              class="hero-dashboard-img"
              loading="eager"
              @load="onHeroMediaLoad"
            />
            
            <q-btn
              v-if="isAdmin"
              class="orbit-edit-btn"
              round
              dense
              size="sm"
              unelevated
              color="dark"
              icon="edit"
              @click="openMasterEditor('hero')"
              style="position: absolute; top: -12px; left: -12px; z-index: 5;"
            >
              <q-tooltip>ویرایش جامع تصویر و محتوای هیرو</q-tooltip>
            </q-btn>
          </div>
        </div>

        <!-- Content Column (Left in RTL) -->
        <div class="hero-content-col">
          <div class="hero-tag-badge">
            <span class="hero-badge-pulse"></span>
            <span>{{ heroBadgeText }}</span>
            <q-btn
              v-if="isAdmin"
              class="admin-edit-btn"
              round
              dense
              size="sm"
              unelevated
              color="dark"
              icon="edit"
              @click="openMasterEditor('hero')"
              style="margin-right: 10px; width: 24px; height: 24px;"
            >
              <q-tooltip>ویرایش جامع هدر و محتوای هیرو</q-tooltip>
            </q-btn>
          </div>

          <h1 class="hero-heading">
            {{ heroTitleText }}
          </h1>

          <div class="hero-subtext">
            <RichContent :html="heroDescText" />
          </div>

          <div class="hero-actions-group">
            <component
              :is="btnBindings(button.link).to ? 'router-link' : 'a'"
              v-for="(button, index) in heroButtonsList"
              :key="`${button.label}-${index}`"
              v-bind="btnBindings(button.link)"
              :class="['btn-pill', button.variant === 'primary' ? 'btn-pill-yellow' : 'btn-pill-dark']"
            >
              <span class="btn-text">{{ button.label }}</span>
              <span class="btn-icon-bubble">
                <svg v-if="button.variant === 'primary'" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
              </span>
            </component>
          </div>
          
          <!-- Metrics Strip -->
          <div v-if="heroStatRows.length" class="hero-metrics-strip">
             <div
              v-for="(stat, index) in heroStatRows"
              :key="`${stat.key}-${index}`"
              class="hero-metric-tile"
            >
              <strong class="hero-metric-number">{{ stat.display }}</strong>
              <span class="hero-metric-desc">{{ stat.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import RichContent from 'src/components/common/RichContent.vue'
import { useAuth } from 'src/composables/useAuth'
import { useHomeContent } from 'src/composables/useHomeContent'
import { useStatValues } from 'src/composables/useStatValues'
import { useMasterEditor } from 'src/composables/useMasterEditor'

const { isAdmin } = useAuth()
const { settings, buttons, heroStats } = useHomeContent()
const { loadValues, animate, displayFor } = useStatValues()
const { openMasterEditor } = useMasterEditor()

const heroVideoRef = ref(null)

const heroBadgeText = computed(() => {
  return settings.value.hero_badge || 'استودیو هوشمند معماری ابری و مهندسی نرم‌افزار'
})

const heroTitleText = computed(() => {
  return settings.value.hero_title || 'خلق پلتفرم‌های مقیاس‌پذیر، مهندسی سیستم‌های ابری پایدار'
})

const heroDescText = computed(() => {
  return settings.value.hero_description || 'طراحی و پیاده‌سازی سیستم‌های ابری توزیع‌شده با لتنسی زیر ۱۵ میلی‌ثانیه، امنیت Zero-Trust و پایداری ۹۹.۹۹۹٪ برای سازمان‌ها و پلتفرم‌های پرترافیک.'
})

const heroMediaSrc = computed(() => {
  const url = settings.value.hero_image_url
  if (!url || url.includes('hero-programming') || url.includes('hero-portrait') || url.includes('Modern 3D Tech Dashboard Illustration')) {
    return '/images/herosection-video.mp4'
  }
  return url
})

const heroImageSrc = heroMediaSrc

const isVideo = computed(() => {
  const src = (heroMediaSrc.value || '').toLowerCase()
  return (
    src.endsWith('.mp4') ||
    src.endsWith('.webm') ||
    src.endsWith('.ogg') ||
    src.includes('gemini_generated_video') ||
    src.includes('herosection-video')
  )
})

const heroButtonsList = computed(() => {
  const raw = (buttons.value || []).filter((b) => String(b.label || '').trim())
  if (raw.length) return raw
  return [
    { label: 'مشاوره و شروع همکاری', link: '#sec-contact', variant: 'primary' },
    { label: 'بررسی توانمندی‌های مهندسی', link: '#sec-services', variant: 'secondary' }
  ]
})

const heroStatRows = computed(() => (heroStats.value || []).map((stat) => ({
  ...stat,
  display: displayFor(stat.key),
})))

function btnBindings (link) {
  const target = String(link || '').trim()
  if (!target) return {}
  if (target.startsWith('#')) return { href: target }
  if (target.startsWith('/')) return { to: target }
  return { href: target, target: '_blank', rel: 'noopener' }
}

function onHeroMediaLoad () {
  if (typeof window !== 'undefined' && window.ScrollTrigger) {
    window.ScrollTrigger.refresh()
  }
}
const onHeroImageLoad = onHeroMediaLoad

const playHeroVideo = () => {
  if (heroVideoRef.value) {
    heroVideoRef.value.muted = true
    const p = heroVideoRef.value.play()
    if (p && typeof p.catch === 'function') {
      p.catch(() => {})
    }
  }
}

onMounted(async () => {
  await loadValues()
  setTimeout(() => {
    animate(heroStatRows.value)
  }, 650)
  playHeroVideo()
})
</script>

<style scoped>
/* ==========================================================================
   HERO SECTION (Design from index.html)
   ========================================================================== */
.hero-section {
  padding-top: 148px;
  padding-bottom: 70px;
  position: relative;
  z-index: 1;
  background: var(--bg-canvas, #f7f7f7);
  direction: rtl;
  width: 100%;
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-sizing: border-box;
}

.hero-container {
  width: min(1340px, 94vw);
  margin: 0 auto;
  padding: 0 16px;
  box-sizing: border-box;
}

.hero-split-grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 48px;
  align-items: center;
}

/* Right column in RTL: Visual Image Display */
.hero-visual-col {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.hero-dashboard-frame {
  width: 100%;
  background: transparent;
  border: none;
  box-shadow: none;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.hero-dashboard-img {
  width: 100%;
  max-width: 580px;
  height: auto;
  display: block;
  object-fit: contain;
  filter: drop-shadow(0 20px 40px rgba(0, 0, 0, 0.08));
  transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), filter 0.5s ease;
}

.hero-dashboard-video {
  width: 100%;
  max-width: 580px;
  height: auto;
  aspect-ratio: 16 / 9;
  display: block;
  object-fit: cover;
  border-radius: var(--radius-lg, 24px);
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.1), 0 4px 16px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.85);
  outline: none;
  transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.5s ease;
  overflow: hidden;
}

.hero-dashboard-frame:hover .hero-dashboard-img {
  transform: translateY(-6px) scale(1.02);
  filter: drop-shadow(0 28px 50px rgba(0, 0, 0, 0.12));
}

.hero-dashboard-frame:hover .hero-dashboard-video {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 28px 60px rgba(0, 0, 0, 0.14), 0 8px 24px rgba(0, 0, 0, 0.06);
}

/* Left column in RTL: Content & CTAs */
.hero-content-col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: right;
}

.hero-tag-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 6px 18px;
  border-radius: var(--radius-pill, 9999px);
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-dark, #0a0a0a);
  margin-bottom: 22px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
}

.hero-badge-pulse {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--yellow, #ffcc00);
  box-shadow: 0 0 0 3px rgba(255, 204, 0, 0.25);
}

.hero-heading {
  font-size: clamp(2rem, 3.4vw, 3.1rem);
  font-weight: 900;
  line-height: 1.35;
  color: var(--text-dark, #0a0a0a);
  margin-bottom: 20px;
  letter-spacing: -0.025em;
  white-space: pre-line;
}

.hero-subtext {
  font-size: 1.02rem;
  color: var(--text-dark-dim, #4a4a4a);
  line-height: 1.9;
  margin-bottom: 30px;
  max-width: 580px;
}

.hero-subtext :deep(p) {
  margin: 0;
  display: inline;
}

.hero-actions-group {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 32px;
}

/* ==========================================================================
   BUTTONS: Pill with Separate Icon Bubble
   ========================================================================== */
.btn-pill {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 6px 22px 6px 6px;
  border-radius: var(--radius-pill, 9999px);
  font-weight: 700;
  font-size: 0.88rem;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
}

.btn-pill .btn-text {
  line-height: 1;
}

.btn-pill .btn-icon-bubble {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  transition: transform 0.25s ease, background 0.25s ease, color 0.25s ease;
}

/* Primary Yellow Pill Button */
.btn-pill-yellow {
  background: var(--yellow, #ffcc00);
  color: #000000;
  box-shadow: 0 4px 18px rgba(255, 204, 0, 0.3);
  border: 1px solid var(--yellow, #ffcc00);
}

.btn-pill-yellow .btn-icon-bubble {
  background: #000000;
  color: var(--yellow, #ffcc00);
}

.btn-pill-yellow:hover {
  background: var(--yellow-hover, #ffd633);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 204, 0, 0.42);
}

.btn-pill-yellow:hover .btn-icon-bubble {
  transform: scale(1.1) rotate(-8deg);
  background: #1f1f1f;
}

/* Dark Pill Button */
.btn-pill-dark {
  background: #0a0a0a;
  color: #ffffff;
  border: 1px solid #262626;
}

.btn-pill-dark .btn-icon-bubble {
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
}

.btn-pill-dark:hover {
  border-color: var(--yellow, #ffcc00);
  transform: translateY(-2px);
}

.btn-pill-dark:hover .btn-icon-bubble {
  background: var(--yellow, #ffcc00);
  color: #000000;
  transform: scale(1.1);
}

/* Metrics Strip */
.hero-metrics-strip {
  width: 100%;
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: var(--radius-md, 20px);
  padding: 18px 24px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 16px;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.02);
  box-sizing: border-box;
}

.hero-metric-tile {
  display: flex;
  flex-direction: column;
  gap: 4px;
  position: relative;
}

.hero-metric-tile:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 0;
  top: 15%;
  height: 70%;
  width: 1px;
  background: var(--border-light, #e5e5e5);
}

.hero-metric-number {
  font-family: var(--font-fa, 'Estedad', sans-serif);
  font-size: 1.55rem;
  font-weight: 900;
  color: #0a0a0a;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.hero-metric-desc {
  font-size: 0.74rem;
  font-weight: 700;
  color: var(--text-dark-muted, #737373);
  line-height: 1.4;
}

/* Responsive Adaptations */
@media (max-width: 1024px) {
  .hero-split-grid {
    grid-template-columns: 1fr;
    gap: 36px;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding-top: 86px;
    padding-bottom: 24px;
    min-height: 100vh;
    min-height: 100dvh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-sizing: border-box;
  }

  .hero-tag-badge {
    font-size: 0.7rem;
    padding: 5px 13px;
    margin-bottom: 12px;
  }

  .hero-heading {
    font-size: clamp(1.3rem, 5.2vw, 1.7rem);
    line-height: 1.32;
    margin-bottom: 10px;
  }

  .hero-subtext {
    font-size: 0.84rem;
    line-height: 1.68;
    margin-bottom: 16px;
  }

  .hero-actions-group {
    flex-direction: column;
    width: 100%;
    gap: 8px;
    margin-bottom: 18px;
  }

  .hero-actions-group .btn-pill {
    width: 100%;
    justify-content: space-between;
    font-size: 0.78rem;
  }

  .hero-visual-col {
    order: -1;
    width: 100%;
    margin-bottom: 6px;
  }

  .hero-dashboard-frame {
    min-height: 180px;
  }

  .hero-dashboard-img {
    max-width: 290px;
    margin: 0 auto;
    aspect-ratio: 16 / 10;
  }

  .hero-dashboard-video {
    max-width: 320px;
    margin: 0 auto;
    aspect-ratio: 16 / 9;
    border-radius: 16px;
  }

  .hero-metrics-strip {
    grid-template-columns: repeat(2, 1fr);
    padding: 12px 14px;
    gap: 8px;
    text-align: right;
  }

  .hero-metric-tile:not(:last-child)::after {
    display: none;
  }

  .hero-metric-tile {
    padding: 4px 6px;
  }

  .hero-metric-number {
    font-size: 1.15rem;
  }

  .hero-metric-desc {
    font-size: 0.65rem;
  }
}

@media (max-width: 480px) {
  .hero-heading {
    font-size: clamp(1.22rem, 5vw, 1.45rem);
  }

  .hero-subtext {
    font-size: 0.8rem;
    line-height: 1.68;
  }

  .hero-actions-group .btn-pill {
    font-size: 0.76rem;
  }
}
</style>

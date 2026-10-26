<template>
  <section class="section-spacing section-layer-sheet" id="sec-services">
    <div class="sheet-layer-indicator" aria-hidden="true">
      <div class="sheet-layer-pill"></div>
    </div>
    <div class="container">
      <!-- Section Head -->
      <div class="section-head">
        <div class="section-tag">
          <span class="tag-dot"></span>
          <span>{{ settings.why_badge || 'خدمات ما' }}</span>
        </div>
        <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
          <h2 class="section-title">{{ settings.why_title || 'راهکارهای تخصصی مهندسی' }}</h2>
          <q-btn
            v-if="isAdmin"
            class="section-edit-btn"
            round
            dense
            size="sm"
            unelevated
            color="dark"
            icon="edit"
            @click="openMasterEditor('services')"
          >
            <q-tooltip>ویرایش جامع خدمات</q-tooltip>
          </q-btn>
        </div>
        <p class="section-desc">
          {{ settings.why_description || 'مجموعه‌ای از سرویس‌های نرم‌افزاری و زیرساخت‌های ابری مدرن که بر پایه پایداری، سرعت و امنیت پایدار طراحی شده‌اند.' }}
        </p>
      </div>

      <!-- Services Grid -->
      <div class="services-grid">
        <div
          v-for="(service, index) in serviceItems"
          :key="`${service.title}-${index}`"
          class="service-card"
        >
          <div>
            <div class="service-3d-wrap">
              <img
                :src="formatIconUrl(service.iconSrc, index)"
                :alt="service.title"
                class="service-3d-img"
                loading="lazy"
                @error="onIconError($event, index)"
              />
            </div>
            <h3 class="service-title">{{ service.title }}</h3>
            <p class="service-text">{{ service.text }}</p>
          </div>
          <ul v-if="service.features && service.features.length" class="service-features-list">
            <li v-for="(feat, fIdx) in service.features" :key="fIdx">{{ feat }}</li>
          </ul>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useAuth } from 'src/composables/useAuth'
import { useHomeContent } from 'src/composables/useHomeContent'
import { useMasterEditor } from 'src/composables/useMasterEditor'

const { isAdmin } = useAuth()
const { settings } = useHomeContent()
const { servicesState, openMasterEditor } = useMasterEditor()

const DEFAULT_ICONS = [
  '/assets/icons3d/cloud.svg',
  '/assets/icons3d/microservices.svg',
  '/assets/icons3d/ai.svg',
  '/assets/icons3d/ux.svg',
  '/assets/icons3d/security.svg',
  '/assets/icons3d/bigdata.svg',
]

function formatIconUrl (url, index) {
  if (!url) return DEFAULT_ICONS[index % DEFAULT_ICONS.length]
  if (url.startsWith('uploads/')) return '/' + url
  return url
}

function onIconError (event, index) {
  event.target.src = DEFAULT_ICONS[index % DEFAULT_ICONS.length]
}

const serviceItems = computed(() => {
  return servicesState.value || []
})
</script>

<style scoped>
/* ==========================================================================
   SECTION 2: SERVICES (Design from index.html)
   ========================================================================== */
.section-spacing {
  padding: 60px 0;
  position: relative;
  direction: rtl;
}

.section-layer-sheet {
  position: relative;
  z-index: 20;
  background: #ffffff;
  border-top-left-radius: 48px;
  border-top-right-radius: 48px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 -28px 70px rgba(0, 0, 0, 0.09), 0 -6px 20px rgba(0, 0, 0, 0.03);
  padding-top: 48px;
}

.sheet-layer-indicator {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.sheet-layer-pill {
  width: 44px;
  height: 4px;
  border-radius: var(--radius-pill, 9999px);
  background: rgba(0, 0, 0, 0.12);
  transition: width 0.35s cubic-bezier(0.16, 1, 0.3, 1), background 0.3s ease;
}

.section-layer-sheet:hover .sheet-layer-pill {
  width: 58px;
  background: var(--yellow, #ffcc00);
}

.container {
  width: min(1340px, 94vw);
  margin: 0 auto;
  padding: 0 16px;
  box-sizing: border-box;
}

.section-head {
  margin-bottom: 36px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.section-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  border-radius: var(--radius-pill, 9999px);
  font-size: 0.78rem;
  font-weight: 700;
  margin-bottom: 16px;
  background: var(--yellow-dim, rgba(255, 204, 0, 0.12));
  border: 1px solid var(--yellow-border, rgba(255, 204, 0, 0.35));
  color: #946200;
}

.tag-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--yellow, #ffcc00);
}

.section-title {
  font-size: clamp(1.9rem, 3.2vw, 2.7rem);
  font-weight: 900;
  letter-spacing: -0.5px;
  line-height: 1.3;
  margin-bottom: 12px;
  color: var(--text-dark, #0a0a0a);
}

.section-desc {
  font-size: 1rem;
  color: var(--text-dark-dim, #4a4a4a);
  max-width: 620px;
  line-height: 1.75;
}

.section-edit-btn {
  width: 26px;
  height: 26px;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.service-card {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: var(--radius-bento, 28px);
  padding: 34px 28px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow: hidden;
}

.service-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  height: 3px;
  background: transparent;
  transition: background 0.3s ease;
}

.service-card:hover {
  transform: translateY(-5px);
  border-color: #000000;
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.06);
}

.service-card:hover::before {
  background: var(--yellow, #ffcc00);
}

.service-3d-wrap {
  width: 72px;
  height: 72px;
  margin-bottom: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.service-3d-img {
  width: 68px;
  height: 68px;
  object-fit: contain;
  filter: drop-shadow(0 6px 12px rgba(0, 0, 0, 0.08));
  transition: transform 0.4s ease;
}

.service-card:hover .service-3d-img {
  transform: scale(1.1) rotate(-3deg);
}

.service-title {
  font-size: 1.22rem;
  font-weight: 800;
  margin-bottom: 10px;
  color: var(--text-dark, #0a0a0a);
}

.service-text {
  font-size: 0.88rem;
  color: var(--text-dark-dim, #4a4a4a);
  line-height: 1.8;
  margin-bottom: 24px;
}

.service-features-list {
  list-style: none;
  padding: 0;
  margin: 0;
  border-top: 1px solid var(--border-light, #e5e5e5);
  padding-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.service-features-list li {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-dark-muted, #737373);
  display: flex;
  align-items: center;
  gap: 8px;
}

.service-features-list li::before {
  content: '';
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--yellow, #ffcc00);
  flex-shrink: 0;
}

@media (max-width: 1024px) {
  .services-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .section-layer-sheet {
    margin-top: 0;
    border-top-left-radius: 36px;
    border-top-right-radius: 36px;
    padding-top: 36px;
  }

  .section-tag {
    font-size: 0.72rem;
    padding: 5px 13px;
    margin-bottom: 12px;
  }

  .section-title {
    font-size: clamp(1.35rem, 5vw, 1.7rem);
    line-height: 1.3;
    margin-bottom: 10px;
  }

  .section-desc {
    font-size: 0.86rem;
    line-height: 1.68;
  }

  .services-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .service-card {
    padding: 24px 20px;
    border-radius: 22px;
  }

  .service-title {
    font-size: 1.05rem;
    margin-bottom: 8px;
  }

  .service-text {
    font-size: 0.8rem;
    line-height: 1.68;
    margin-bottom: 18px;
  }

  .service-features-list li {
    font-size: 0.72rem;
  }
}

@media (max-width: 480px) {
  .section-title {
    font-size: clamp(1.18rem, 4.8vw, 1.4rem);
  }

  .section-desc {
    font-size: 0.8rem;
    line-height: 1.65;
  }

  .service-title {
    font-size: 0.96rem;
  }

  .service-text {
    font-size: 0.76rem;
  }
}
</style>

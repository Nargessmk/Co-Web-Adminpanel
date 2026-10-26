<template>
  <section class="section-spacing about-split-section" id="sec-about">
    <div class="container">
      <q-card class="about-grid-wrapper about-single-card" flat>
        
        <!-- RIGHT COLUMN (محتوای متنی سمت راست: فقط لیبل، عنوان، متن و دکمه) - 50% عرض -->
        <q-card-section class="about-content-col q-pa-none">
          <!-- 1. Label (لیبل) -->
          <div class="section-tag">
            <span class="tag-dot"></span>
            <span>{{ aboutData.badge || 'درباره کهکشان هوشمند' }}</span>
          </div>

          <!-- 2. Title (عنوان) & Admin Edit -->
          <div class="title-row">
            <h2 class="about-main-title">
              {{ aboutData.title || 'اصالت مهندسی، انضباط سازمانی' }}
            </h2>
            <q-btn
              v-if="isAdmin"
              class="section-edit-btn"
              round
              dense
              size="sm"
              unelevated
              color="dark"
              icon="edit"
              @click="openMasterEditor('about')"
            >
              <q-tooltip>ویرایش درباره ما در Master Editor</q-tooltip>
            </q-btn>
          </div>

          <!-- 3. Text (متن) -->
          <div
            v-if="hasHtmlDesc"
            class="about-main-desc richtext-content"
            v-html="aboutText"
          ></div>
          <p v-else class="about-main-desc">
            {{ aboutText }}
          </p>

          <!-- 4. Button (دکمه) -->
          <q-card-actions class="about-action-wrap q-pa-none" align="left">
            <router-link
              v-if="isInternalLink(buttonLink)"
              :to="buttonLink"
              class="btn-pill btn-pill-dark"
            >
              <span class="btn-text">{{ buttonText }}</span>
              <span class="btn-icon-bubble">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
              </span>
            </router-link>
            <a
              v-else
              :href="buttonLink"
              class="btn-pill btn-pill-dark"
            >
              <span class="btn-text">{{ buttonText }}</span>
              <span class="btn-icon-bubble">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
              </span>
            </a>
          </q-card-actions>
        </q-card-section>

        <!-- LEFT COLUMN (بخش تصویر و نمودار دایره‌ای - تم کاملاً لایت، نمودار دایره‌ای و تصویر بزرگتر) - 50% عرض -->
        <q-card-section class="about-visual-col q-pa-none">
          <div class="about-media-frame">
            <!-- Dot Matrix Grid Backdrop (Light Theme) -->
            <div class="motion-grid-pattern" aria-hidden="true"></div>

            <!-- Ambient Radiant Glow (Light warm amber & soft sky blue) -->
            <div class="motion-ambient-glow glow-amber" aria-hidden="true"></div>
            <div class="motion-ambient-glow glow-blue" aria-hidden="true"></div>

            <!-- Large Circular Chart & Tech Orbits (نمودار دایره‌ای بزرگ مهندسی) -->
            <div class="circular-chart-wrapper" aria-hidden="true">
              <!-- High-Tech SVG Radar / Circular Gauge / Degree Scale -->
              <svg class="tech-radar-svg" viewBox="0 0 600 600" fill="none" xmlns="http://www.w3.org/2000/svg">
                <!-- Precision calibrated outer ticks ring -->
                <circle cx="300" cy="300" r="275" stroke="rgba(0,0,0,0.06)" stroke-width="1.5" stroke-dasharray="3 7" />
                <circle cx="300" cy="300" r="260" stroke="rgba(255, 204, 0, 0.35)" stroke-width="2" stroke-dasharray="80 180 40 180" />
                <!-- Telemetry Arc 1 (Gold) -->
                <path d="M 300 40 A 260 260 0 0 1 540 200" stroke="#ffcc00" stroke-width="3" stroke-linecap="round" />
                <!-- Telemetry Arc 2 (Blue) -->
                <path d="M 60 300 A 240 240 0 0 1 200 80" stroke="#2563eb" stroke-width="2.5" stroke-linecap="round" opacity="0.75" />
                <!-- Concentric Guide Rings -->
                <circle cx="300" cy="300" r="215" stroke="rgba(0,0,0,0.05)" stroke-width="1" />
                <circle cx="300" cy="300" r="155" stroke="rgba(0,0,0,0.06)" stroke-width="1" stroke-dasharray="4 8" />
                <circle cx="300" cy="300" r="95" stroke="rgba(255, 204, 0, 0.22)" stroke-width="1.2" />
                <!-- Axis crosshair dashed lines -->
                <line x1="300" y1="20" x2="300" y2="580" stroke="rgba(0,0,0,0.04)" stroke-width="1" stroke-dasharray="4 6" />
                <line x1="20" y1="300" x2="580" y2="300" stroke="rgba(0,0,0,0.04)" stroke-width="1" stroke-dasharray="4 6" />
                <!-- Precision Degree Markers -->
                <text x="300" y="32" fill="#94a3b8" font-size="10" font-family="monospace" text-anchor="middle" font-weight="700">000°</text>
                <text x="572" y="304" fill="#94a3b8" font-size="10" font-family="monospace" text-anchor="middle" font-weight="700">090°</text>
                <text x="300" y="574" fill="#94a3b8" font-size="10" font-family="monospace" text-anchor="middle" font-weight="700">180°</text>
                <text x="28" y="304" fill="#94a3b8" font-size="10" font-family="monospace" text-anchor="middle" font-weight="700">270°</text>
              </svg>

              <!-- Outer Orbital Ring (550px) -->
              <div class="orbital-ring outer-ring">
                <div class="satellite-node sat-gold"></div>
                <div class="satellite-node sat-accent"></div>
              </div>

              <!-- Mid Ring (420px) -->
              <div class="orbital-ring mid-ring">
                <div class="satellite-node sat-emerald"></div>
              </div>

              <!-- Inner Ring (300px) -->
              <div class="orbital-ring inner-ring"></div>
            </div>

            <!-- Central 3D Tech Core (Floating Motion - Large Scale) -->
            <div class="tech-core-wrapper">
              <div class="core-hologram-frame">
                <img
                  :src="motionGraphicSrc"
                  alt="معماری هوشمند سیستم‌های ابری"
                  class="tech-core-img"
                  loading="lazy"
                  @error="$event.target.src = '/Modern 3D Tech Dashboard Illustration(1).png'"
                />
              </div>
              <!-- Soft Floor Reflection Shadow -->
              <div class="core-floor-shadow" aria-hidden="true"></div>
            </div>

            <!-- Floating Motion Glassmorphism Status Chips (Light Theme) -->
            
            <!-- Chip 1: Zero-Trust Security -->
            <div class="floating-motion-chip chip-security">
              <div class="chip-icon-box chip-icon-gold">
                <q-icon name="shield" size="18px" />
              </div>
              <div class="chip-content">
                <span class="chip-label">{{ chip1Label }}</span>
                <span class="chip-val">{{ chip1Val }}</span>
              </div>
            </div>

            <!-- Chip 2: Edge Latency -->
            <div class="floating-motion-chip chip-latency">
              <span class="beacon-pulse-dot"></span>
              <div class="chip-content">
                <span class="chip-label">{{ chip2Label }}</span>
                <span class="chip-val">{{ chip2Val }}</span>
              </div>
            </div>

            <!-- Chip 3: High Availability SLA -->
            <div class="floating-motion-chip chip-sla">
              <div class="chip-icon-box chip-icon-blue">
                <q-icon name="verified" size="16px" />
              </div>
              <div class="chip-content">
                <span class="chip-label">{{ chip3Label }}</span>
                <span class="chip-val">{{ chip3Val }}</span>
              </div>
            </div>

          </div>
        </q-card-section>

      </q-card>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useAuth } from 'src/composables/useAuth'
import { useMasterEditor } from 'src/composables/useMasterEditor'

const { isAdmin } = useAuth()
const { aboutState, openMasterEditor } = useMasterEditor()

const aboutData = computed(() => {
  return aboutState.value || {}
})

const aboutText = computed(() => {
  return aboutData.value.desc || aboutData.value.statementP1 || 'ما یک استودیوی پیشرو در معماری نرم‌افزارهای تجاری و زیرساخت‌های ابری هستیم که دقت فنی را با استانداردهای بین‌المللی سازمانی تلفیق می‌کنیم. رویکرد ما در مهندسی نرم‌افزار متکی بر شفافیت کد منبع، کاهش ریسک‌های عملیاتی و ایزولاسیون امنیتی Zero-Trust بنا شده است.'
})

const hasHtmlDesc = computed(() => {
  return /<[a-z][\s\S]*>/i.test(aboutText.value)
})

const buttonText = computed(() => {
  return aboutData.value.button_text || 'آشنایی بیشتر با کهکشان هوشمند'
})

const buttonLink = computed(() => {
  return aboutData.value.button_link || '/about'
})

function isInternalLink (link) {
  return link && link.startsWith('/')
}

const motionGraphicSrc = computed(() => {
  return aboutData.value.image || '/Modern 3D Tech Dashboard Illustration(1).png'
})

const chip1Label = computed(() => aboutData.value.chip1_label || 'معماری امنیتی')
const chip1Val = computed(() => aboutData.value.chip1_val || 'Zero-Trust Isolated')
const chip2Label = computed(() => aboutData.value.chip2_label || 'لتنسی لبه شبکه')
const chip2Val = computed(() => aboutData.value.chip2_val || '< ۱۵ms Anycast')
const chip3Label = computed(() => aboutData.value.chip3_label || 'تضمین پایداری کتبی')
const chip3Val = computed(() => aboutData.value.chip3_val || 'SLA ۹۹.۹۹٪ رسمی')
</script>

<style scoped>
/* ==========================================================================
   ABOUT US SECTION: MINIMAL 50/50 SPLIT ARCHITECTURE
   - No dark theme on the left part
   - Circular chart and image scaled up (بزرگتر)
   - Equal 50/50 width for visual and text
   - Text section has ONLY: Label, Title, Text, Button
   - 100% editable with Master Editor
   ========================================================================== */
.about-split-section {
  padding: 80px 0;
  position: relative;
  direction: rtl;
  background-color: transparent;
}

.container {
  width: min(1340px, 94vw);
  margin: 0 auto;
  padding: 0 16px;
  box-sizing: border-box;
}

/* Master Grid: 50% - 50% Equal Split without White Box */
.about-grid-wrapper {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  border-radius: 0 !important;
  padding: 0 !important;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
  position: relative;
}

/* ==========================================================================
   RIGHT COLUMN: Content (50% Width) - Label, Title, Text, Button ONLY
   ========================================================================== */
.about-content-col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: right;
  width: 100%;
}

.section-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  border-radius: var(--radius-pill, 9999px);
  font-size: 0.82rem;
  font-weight: 700;
  margin-bottom: 20px;
  background: var(--yellow-dim, rgba(255, 204, 0, 0.12));
  border: 1px solid var(--yellow-border, rgba(255, 204, 0, 0.35));
  color: #946200;
}

.tag-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--yellow, #ffcc00);
  box-shadow: 0 0 8px rgba(255, 204, 0, 0.8);
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 22px;
}

.about-main-title {
  font-size: clamp(2rem, 3.2vw, 2.75rem);
  font-weight: 900;
  line-height: 1.32;
  letter-spacing: -0.025em;
  color: var(--text-dark, #0a0a0a);
  margin: 0;
}

.section-edit-btn {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
}

.about-main-desc {
  font-size: 1.08rem;
  font-weight: 500;
  color: var(--text-dark-dim, #404040);
  line-height: 1.95;
  margin: 0 0 36px 0;
  max-width: 580px;
}

.about-main-desc :deep(p) {
  margin: 0 0 16px 0;
  line-height: 1.95;
}

.about-action-wrap {
  display: flex;
  align-items: center;
  width: 100%;
}

.btn-pill {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  padding: 8px 24px 8px 8px;
  border-radius: var(--radius-pill, 9999px);
  font-weight: 800;
  font-size: 0.94rem;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
}

.btn-pill .btn-text {
  line-height: 1;
}

.btn-pill .btn-icon-bubble {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  transition: transform 0.25s ease, background 0.25s ease, color 0.25s ease;
}

.btn-pill-dark {
  background: #0a0a0a;
  color: #ffffff;
  border: 1.5px solid #0a0a0a;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.btn-pill-dark .btn-icon-bubble {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
}

.btn-pill-dark:hover {
  border-color: var(--yellow, #ffcc00);
  background: #000000;
  transform: translateY(-2px);
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.18);
}

.btn-pill-dark:hover .btn-icon-bubble {
  background: var(--yellow, #ffcc00);
  color: #000000;
  transform: scale(1.08);
}

/* ==========================================================================
   LEFT COLUMN: Visual & Circular Chart (Light Theme + Scaled Up)
   ========================================================================== */
.about-visual-col {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.about-media-frame {
  position: relative;
  width: 100%;
  min-height: 590px;
  border-radius: 36px;
  background: linear-gradient(145deg, #ffffff 0%, #f6f8fd 100%);
  border: 1px solid var(--border-light, #e5e5e5);
  box-shadow: 0 16px 44px rgba(0, 0, 0, 0.035);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 24px;
}

/* Tech Dot Grid Pattern (Light theme) */
.motion-grid-pattern {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(0, 0, 0, 0.045) 1.2px, transparent 1.2px);
  background-size: 22px 22px;
  pointer-events: none;
  opacity: 0.85;
}

/* Radiant Ambient Glows (Light & Warm) */
.motion-ambient-glow {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  filter: blur(52px);
}

.glow-amber {
  width: 340px;
  height: 340px;
  background: radial-gradient(circle, rgba(255, 204, 0, 0.22) 0%, rgba(255, 204, 0, 0) 70%);
  animation: ambientPulse 7s ease-in-out infinite;
}

.glow-blue {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.08) 0%, rgba(37, 99, 235, 0) 70%);
  top: 10%;
  left: 10%;
}

/* ==========================================================================
   CIRCULAR CHART WRAPPER (نمودار دایره‌ای بزرگ)
   ========================================================================== */
.circular-chart-wrapper {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

/* High-Tech SVG Circular Compass / Gauge / Metrics Overlay */
.tech-radar-svg {
  position: absolute;
  width: 550px;
  height: 550px;
  pointer-events: none;
  animation: radarSvgRotate 90s linear infinite;
  opacity: 0.95;
}

/* Orbital Rings (Scaled Up) */
.orbital-ring {
  position: absolute;
  border-radius: 50%;
}

.outer-ring {
  width: 550px;
  height: 550px;
  border: 1.5px dashed rgba(0, 0, 0, 0.09);
  animation: orbitRotate 45s linear infinite;
}

.mid-ring {
  width: 420px;
  height: 420px;
  border: 1.5px solid rgba(255, 204, 0, 0.45);
  animation: orbitCounter 30s linear infinite;
}

.inner-ring {
  width: 300px;
  height: 300px;
  border: 1px dashed rgba(37, 99, 235, 0.25);
  animation: orbitRotate 22s linear infinite;
}

.satellite-node {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  position: absolute;
}

.sat-gold {
  top: -5px;
  left: 50%;
  margin-left: -5px;
  background: #ffcc00;
  box-shadow: 0 0 12px rgba(255, 204, 0, 0.95);
}

.sat-accent {
  bottom: -5px;
  right: 50%;
  margin-right: -5px;
  background: #2563eb;
  box-shadow: 0 0 10px rgba(37, 99, 235, 0.8);
}

.sat-emerald {
  top: 50%;
  right: -5px;
  margin-top: -5px;
  background: #10b981;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.85);
}

/* ==========================================================================
   CENTRAL 3D TECH CORE (تصویر بزرگتر)
   ========================================================================== */
.tech-core-wrapper {
  position: relative;
  z-index: 5;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  animation: floatLevitate 6s ease-in-out infinite;
}

.core-hologram-frame {
  display: flex;
  align-items: center;
  justify-content: center;
}

.tech-core-img {
  max-width: 460px;
  max-height: 440px;
  width: 100%;
  height: auto;
  object-fit: contain;
  filter: drop-shadow(0 22px 42px rgba(0, 0, 0, 0.09));
  transition: transform 0.4s ease;
}

.tech-core-wrapper:hover .tech-core-img {
  transform: scale(1.04);
}

.core-floor-shadow {
  width: 280px;
  height: 20px;
  border-radius: 50%;
  background: radial-gradient(ellipse at center, rgba(0, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0) 70%);
  margin-top: -10px;
  pointer-events: none;
  animation: shadowPulse 6s ease-in-out infinite;
}

/* ==========================================================================
   FLOATING GLASSMORPHISM CHIPS (LIGHT THEME)
   ========================================================================== */
.floating-motion-chip {
  position: absolute;
  z-index: 10;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 18px;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.06);
  color: #0f172a;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  white-space: nowrap;
}

.floating-motion-chip:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.1);
  border-color: rgba(255, 204, 0, 0.5);
}

.chip-icon-box {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.chip-icon-gold {
  background: rgba(255, 204, 0, 0.2);
  color: #946200;
}

.chip-icon-blue {
  background: rgba(37, 99, 235, 0.12);
  color: #2563eb;
}

.chip-content {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}

.chip-label {
  font-size: 0.68rem;
  color: #64748b;
  font-weight: 700;
}

.chip-val {
  font-size: 0.84rem;
  color: #0f172a;
  font-weight: 900;
}

.chip-security {
  top: 24px;
  right: 20px;
  animation: floatBadge1 5.8s ease-in-out infinite;
}

.chip-latency {
  top: 50%;
  left: 18px;
  transform: translateY(-50%);
  animation: floatBadge2 5.2s ease-in-out infinite 0.6s;
}

.chip-sla {
  bottom: 22px;
  left: 50%;
  transform: translateX(-50%);
  animation: floatBadge3 6.4s ease-in-out infinite 1.2s;
}

.beacon-pulse-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #16a34a;
  box-shadow: 0 0 0 2px rgba(22, 163, 74, 0.25);
  animation: beaconPulse 2s infinite;
  flex-shrink: 0;
}

/* Keyframes */
@keyframes floatLevitate {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-12px); }
}

@keyframes shadowPulse {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(0.85); opacity: 0.45; }
}

@keyframes orbitRotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes orbitCounter {
  0% { transform: rotate(360deg); }
  100% { transform: rotate(0deg); }
}

@keyframes radarSvgRotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes floatBadge1 {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-7px); }
}

@keyframes floatBadge2 {
  0%, 100% { transform: translateY(-50%) translateY(0px); }
  50% { transform: translateY(-50%) translateY(7px); }
}

@keyframes floatBadge3 {
  0%, 100% { transform: translateX(-50%) translateY(0px); }
  50% { transform: translateX(-50%) translateY(-8px); }
}

@keyframes ambientPulse {
  0%, 100% { transform: scale(0.95); opacity: 0.65; }
  50% { transform: scale(1.08); opacity: 0.95; }
}

@keyframes beaconPulse {
  0%, 100% { box-shadow: 0 0 0 2px rgba(22, 163, 74, 0.25); }
  50% { box-shadow: 0 0 0 7px rgba(34, 197, 94, 0); }
}

/* ==========================================================================
   RESPONSIVE DESIGN (TABLET & MOBILE)
   ========================================================================== */
@media (max-width: 1200px) {
  .tech-radar-svg {
    width: 460px;
    height: 460px;
  }
  .outer-ring {
    width: 460px;
    height: 460px;
  }
  .mid-ring {
    width: 360px;
    height: 360px;
  }
  .inner-ring {
    width: 260px;
    height: 260px;
  }
  .tech-core-img {
    max-width: 380px;
    max-height: 370px;
  }
}

@media (max-width: 1024px) {
  .about-grid-wrapper {
    grid-template-columns: 1fr;
    gap: 40px;
  }

  .about-visual-col {
    order: 1;
    width: 100%;
  }

  .about-content-col {
    order: 2;
    width: 100%;
  }

  .about-media-frame {
    min-height: 480px;
  }

  .tech-radar-svg {
    width: 410px;
    height: 410px;
  }
  .outer-ring {
    width: 410px;
    height: 410px;
  }
  .mid-ring {
    width: 320px;
    height: 320px;
  }
  .inner-ring {
    width: 230px;
    height: 230px;
  }
  .tech-core-img {
    max-width: 340px;
  }
}

@media (max-width: 768px) {
  .about-split-section {
    padding: 44px 0;
  }

  .about-grid-wrapper {
    gap: 24px;
  }

  .section-tag {
    font-size: 0.72rem;
    padding: 5px 14px;
    margin-bottom: 12px;
  }

  .about-media-frame {
    min-height: 350px;
    padding: 16px;
    border-radius: 20px;
  }

  .about-main-title {
    font-size: clamp(1.28rem, 5.2vw, 1.65rem);
    line-height: 1.34;
    margin-bottom: 12px;
  }

  .about-main-desc {
    font-size: 0.86rem;
    line-height: 1.72;
    margin-bottom: 22px;
  }

  .about-action-wrap .btn-pill {
    width: 100%;
    justify-content: space-between;
    font-size: 0.82rem;
    padding: 6px 18px 6px 6px;
    min-height: 44px;
  }

  .tech-radar-svg {
    width: 300px;
    height: 300px;
  }
  .outer-ring {
    width: 300px;
    height: 300px;
  }
  .mid-ring {
    width: 230px;
    height: 230px;
  }
  .inner-ring {
    width: 160px;
    height: 160px;
  }

  .tech-core-img {
    max-width: 230px;
  }

  .floating-motion-chip {
    padding: 6px 12px;
    font-size: 0.72rem;
  }

  .chip-security {
    top: 12px;
    right: 12px;
  }

  .chip-latency {
    top: 55%;
    left: 10px;
  }

  .chip-sla {
    bottom: 12px;
  }
}

@media (max-width: 480px) {
  .about-split-section {
    padding: 32px 0;
  }

  .about-grid-wrapper {
    gap: 20px;
  }

  .section-tag {
    font-size: 0.68rem;
    padding: 4px 12px;
    margin-bottom: 10px;
  }

  .about-media-frame {
    min-height: 290px;
    padding: 12px;
    border-radius: 18px;
  }

  .about-main-title {
    font-size: clamp(1.18rem, 4.8vw, 1.4rem);
    line-height: 1.35;
    margin-bottom: 10px;
  }

  .about-main-desc {
    font-size: 0.8rem;
    line-height: 1.68;
    margin-bottom: 18px;
  }

  .about-action-wrap .btn-pill {
    font-size: 0.78rem;
    min-height: 42px;
  }

  .tech-radar-svg {
    width: 250px;
    height: 250px;
  }
  .outer-ring {
    width: 250px;
    height: 250px;
  }
  .mid-ring {
    width: 190px;
    height: 190px;
  }
  .inner-ring {
    width: 130px;
    height: 130px;
  }

  .tech-core-img {
    max-width: 180px;
    max-height: 170px;
  }

  .floating-motion-chip {
    padding: 4px 10px;
    gap: 6px;
  }

  .chip-icon-box {
    width: 22px;
    height: 22px;
  }

  .chip-label {
    font-size: 0.6rem;
  }

  .chip-val {
    font-size: 0.72rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .tech-core-wrapper,
  .outer-ring,
  .mid-ring,
  .inner-ring,
  .tech-radar-svg,
  .floating-motion-chip,
  .motion-ambient-glow,
  .beacon-pulse-dot,
  .core-floor-shadow {
    animation: none !important;
  }
}
</style>

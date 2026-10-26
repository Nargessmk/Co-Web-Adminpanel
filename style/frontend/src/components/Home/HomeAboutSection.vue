<template>
  <section id="about" class="home-about-section">
    <!-- Ambient Background Elements -->
    <div class="about-ambient-glow orb-left"></div>
    <div class="about-ambient-glow orb-right"></div>
    <div class="about-grid-lines"></div>

    <div class="about-container">
      <!-- Section Header -->
      <div class="section-header">
        <div class="eyebrow-pill">
          <span class="live-indicator"></span>
          <span>{{ displayBadge }}</span>
        </div>

        <h2 class="section-title">
          {{ displayTitle }}
          <span class="title-accent">{{ displayTitleAccent }}</span>
        </h2>

        <p class="section-description">
          {{ displayDescription }}
        </p>
      </div>

      <!-- Bento Grid Layout -->
      <div class="about-bento-grid">
        <!-- Main Story Card (Large) -->
        <div class="bento-card bento-card-main double-bezel">
          <div class="double-bezel-inner bento-card-inner">
            <div class="main-card-header">
              <div class="icon-capsule primary-gradient">
                <q-icon name="auto_awesome" size="26px" />
              </div>
              <span class="pill-tag">معماری سازمانی</span>
            </div>

            <h3 class="main-card-title">
              خلق ارزش پایدار با راهکارهای نرم‌افزاری نسل جدید
            </h3>

            <p class="main-card-text">
              در سرزمین ابری (CloudLand)، ما سامانه‌های نرم‌افزاری را تنها به عنوان یک کد پیاده‌سازی نمی‌کنیم؛ بلکه به عنوان ستون فقرات پایدار کسب‌وکار شما مهندسی می‌کنیم. تیم ما متشکل از نخبگان معماری ابر، امنیت داده و هوش تجاری است که مأموریت خود را توانمندسازی سازمان‌ها برای تحول دیجیتال مطمئن قرار داده‌اند.
            </p>

            <div class="key-points-grid">
              <div class="key-point-item">
                <div class="point-icon-box">
                  <q-icon name="verified_user" size="18px" />
                </div>
                <div class="point-info">
                  <span class="point-title">امنیت لایه‌ای</span>
                  <span class="point-desc">مطابق استانداردهای جهانی Zero Trust</span>
                </div>
              </div>

              <div class="key-point-item">
                <div class="point-icon-box">
                  <q-icon name="speed" size="18px" />
                </div>
                <div class="point-info">
                  <span class="point-title">کارایی فوق‌العاده</span>
                  <span class="point-desc">پاسخگویی آنی با معماری مقیاس‌پذیر ابری</span>
                </div>
              </div>

              <div class="key-point-item">
                <div class="point-icon-box">
                  <q-icon name="hub" size="18px" />
                </div>
                <div class="point-info">
                  <span class="point-title">یکپارچگی هوشمند</span>
                  <span class="point-desc">اتصال بی‌نقص سامانه‌های سازمانی و فرآیندها</span>
                </div>
              </div>

              <div class="key-point-item">
                <div class="point-icon-box">
                  <q-icon name="support_agent" size="18px" />
                </div>
                <div class="point-info">
                  <span class="point-title">همراهی ۲۴/۷</span>
                  <span class="point-desc">پشتیبانی اختصاصی و پایش مدام سیستم‌ها</span>
                </div>
              </div>
            </div>

            <div class="main-card-footer">
              <router-link to="/about" class="about-more-btn">
                <span class="btn-label">آشنایی بیشتر با تاریخچه و تیم ما</span>
                <span class="btn-icon-capsule">
                  <q-icon name="arrow_back" size="15px" />
                </span>
              </router-link>
            </div>
          </div>
        </div>

        <!-- Side Cards Stack -->
        <div class="bento-side-stack">
          <!-- Card 1: Mission -->
          <div class="bento-card bento-card-side double-bezel theme-blue">
            <div class="double-bezel-inner bento-card-inner">
              <div class="side-card-top">
                <div class="icon-capsule blue-gradient">
                  <q-icon name="flag" size="22px" />
                </div>
                <span class="badge-subtle">مأموریت ما</span>
              </div>
              <h4 class="side-card-title">ساده‌سازی پیچیدگی‌های سازمانی</h4>
              <p class="side-card-desc">
                تبدیل چالش‌های پیچیده سازمانی به راهکارهای دیجیتال روان، چابک و با کاربری آسان برای مدیران و تیم‌ها.
              </p>
            </div>
          </div>

          <!-- Card 2: Vision -->
          <div class="bento-card bento-card-side double-bezel theme-amber">
            <div class="double-bezel-inner bento-card-inner">
              <div class="side-card-top">
                <div class="icon-capsule amber-gradient">
                  <q-icon name="visibility" size="22px" />
                </div>
                <span class="badge-subtle">چشم‌انداز آینده</span>
              </div>
              <h4 class="side-card-title">مرجع راهکارهای ابری پیشرفته</h4>
              <p class="side-card-desc">
                شکل‌دهی به اکوسیستم نرم‌افزارهای یکپارچه‌ای که تصمیم‌گیری داده‌محور را در دسترس هر کسب‌وکاری قرار می‌دهد.
              </p>
            </div>
          </div>

          <!-- Card 3: Values -->
          <div class="bento-card bento-card-side double-bezel theme-emerald">
            <div class="double-bezel-inner bento-card-inner">
              <div class="side-card-top">
                <div class="icon-capsule emerald-gradient">
                  <q-icon name="handshake" size="22px" />
                </div>
                <span class="badge-subtle">ارزش‌های کلیدی</span>
              </div>
              <h4 class="side-card-title">شفافیت، کیفیت و تعهد بی‌پایان</h4>
              <p class="side-card-desc">
                موفقیت مشتریان، معیار سنجش دستاوردهای ماست؛ خلق نرم‌افزارهایی که سال‌ها با وقار به کسب‌وکارها خدمت می‌کنند.
              </p>
            </div>
          </div>
        </div>
      </div>

    </div>
  </section>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAboutContent } from 'src/composables/useAboutContent'

const { settings, stats, load: loadAbout } = useAboutContent()

onMounted(async () => {
  try {
    if (!settings.value.hero_title) {
      await loadAbout()
    }
  } catch (err) {
    // Non-fatal: default fallbacks will display beautifully
  }
})

const displayBadge = computed(() => {
  return settings.value.hero_badge || 'درباره سرزمین ابری'
})

const displayTitle = computed(() => {
  return settings.value.hero_title || 'مهندسی راهکارهای نرم‌افزاری برای'
})

const displayTitleAccent = computed(() => {
  return settings.value.hero_title_accent || 'تحول دیجیتال پایدار'
})

const displayDescription = computed(() => {
  return settings.value.hero_description
    ? settings.value.hero_description.replace(/<[^>]*>/g, '')
    : 'ما در CloudLand با تلفیق فناوری‌های نوین ابری، استانداردهای روز نرم‌افزاری و تفکر داده‌محور، سازمان‌ها را برای فتح قله‌های رقابتی مجهز می‌کنیم.'
})
</script>

<style scoped>
/* =========================================
   HOME ABOUT SECTION
========================================== */
.home-about-section {
  position: relative;
  padding: var(--section-pad-y) 0;
  background: var(--cl-surface);
  direction: rtl;
  overflow: hidden;
  border-top: 1px solid var(--cl-border);
  border-bottom: 1px solid var(--cl-border);
}

/* Ambient Backdrops */
.about-ambient-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  pointer-events: none;
  opacity: 0.45;
  z-index: 0;
}

.orb-left {
  width: 500px;
  height: 500px;
  top: 10%;
  left: -120px;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.15) 0%, rgba(37, 99, 235, 0) 70%);
}

.orb-right {
  width: 480px;
  height: 480px;
  bottom: 5%;
  right: -100px;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.12) 0%, rgba(245, 158, 11, 0) 70%);
}

.about-grid-lines {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(to right, rgba(226, 232, 240, 0.3) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(226, 232, 240, 0.3) 1px, transparent 1px);
  background-size: 56px 56px;
  pointer-events: none;
  opacity: 0.6;
  -webkit-mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, #000 40%, transparent 100%);
  mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, #000 40%, transparent 100%);
}

.about-container {
  position: relative;
  z-index: 1;
  width: min(var(--container-max-w), calc(100% - 48px));
  margin: 0 auto;
}

/* =========================================
   Section Header
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
  opacity: 0.8;
}

.section-description {
  margin: 0;
  color: var(--cl-text-muted);
  font-size: 16px;
  line-height: 1.85;
  max-width: 620px;
}

/* =========================================
   Bento Grid
========================================== */
.about-bento-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(0, 0.9fr);
  gap: 24px;
  margin-bottom: 36px;
}

.bento-card {
  transition: transform 0.35s var(--cl-ease), box-shadow 0.35s var(--cl-ease), border-color 0.35s var(--cl-ease);
}

.bento-card-inner {
  padding: 36px 32px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Main Bento Card */
.bento-card-main .bento-card-inner {
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
}

.main-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22px;
}

.icon-capsule {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  box-shadow: 0 8px 16px -4px rgba(37, 99, 235, 0.3);
}

.primary-gradient {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
}

.blue-gradient {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.amber-gradient {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.emerald-gradient {
  background: linear-gradient(135deg, #10b981, #059669);
}

.pill-tag {
  font-size: 12px;
  font-weight: 700;
  color: var(--cl-primary);
  background: var(--cl-primary-light);
  padding: 6px 14px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(37, 99, 235, 0.15);
}

.main-card-title {
  font-size: clamp(20px, 2.2vw, 26px);
  font-weight: 800;
  color: var(--cl-text-dark);
  line-height: 1.4;
  margin: 0 0 16px;
}

.main-card-text {
  color: var(--cl-text);
  font-size: 15px;
  line-height: 1.85;
  margin: 0 0 28px;
}

.key-points-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18px;
  margin-bottom: 32px;
  padding: 20px;
  background: rgba(248, 250, 252, 0.85);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: var(--radius-lg);
}

.key-point-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.point-icon-box {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: #ffffff;
  color: var(--cl-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.06);
  flex-shrink: 0;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.point-info {
  display: flex;
  flex-direction: column;
}

.point-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--cl-text-dark);
  line-height: 1.3;
}

.point-desc {
  font-size: 12px;
  color: var(--cl-text-muted);
  line-height: 1.5;
  margin-top: 2px;
}

.main-card-footer {
  margin-top: auto;
}

.about-more-btn {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 10px 10px 10px 22px;
  background: var(--cl-primary);
  color: #ffffff;
  font-weight: 700;
  font-size: 14px;
  border-radius: var(--radius-pill);
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.28);
  transition: all 0.3s var(--cl-ease);
}

.about-more-btn:hover {
  background: var(--cl-primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 8px 22px rgba(37, 99, 235, 0.36);
}

.about-more-btn:hover .btn-icon-capsule {
  transform: translateX(-4px);
  background: rgba(255, 255, 255, 0.35);
}

/* Side Bento Stack */
.bento-side-stack {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.bento-card-side .bento-card-inner {
  padding: 24px 22px;
}

.side-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.badge-subtle {
  font-size: 11px;
  font-weight: 700;
  color: var(--cl-text-muted);
  background: rgba(241, 245, 249, 0.9);
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(226, 232, 240, 0.7);
}

.side-card-title {
  font-size: 16px;
  font-weight: 800;
  color: var(--cl-text-dark);
  line-height: 1.4;
  margin: 0 0 8px;
}

.side-card-desc {
  font-size: 13px;
  color: var(--cl-text-muted);
  line-height: 1.7;
  margin: 0;
}

/* Hover Accent Colors on Side Cards */
.theme-blue:hover {
  border-color: rgba(37, 99, 235, 0.35);
}
.theme-amber:hover {
  border-color: rgba(245, 158, 11, 0.35);
}
.theme-emerald:hover {
  border-color: rgba(16, 185, 129, 0.35);
}

/* =========================================
   Responsive Breakpoints
========================================== */
@media (max-width: 1024px) {
  .about-bento-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .home-about-section {
    padding: 70px 0 80px;
  }

  .bento-card-inner {
    padding: 24px 18px;
  }

  .key-points-grid {
    grid-template-columns: 1fr;
    padding: 14px;
    gap: 14px;
  }
}
</style>

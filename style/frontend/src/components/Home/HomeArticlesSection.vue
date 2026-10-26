<template>
  <section id="articles" class="home-articles-section">
    <!-- Ambient Background Lighting -->
    <div class="articles-ambient-mesh">
      <div class="articles-glow-orb orb-primary"></div>
      <div class="articles-glow-orb orb-accent"></div>
      <div class="articles-grid-pattern"></div>
    </div>

    <div class="articles-container">
      <!-- Section Header -->
      <div class="section-header">
        <div class="eyebrow-pill">
          <span class="live-indicator"></span>
          <span>دانش و راهکارها</span>
        </div>

        <h2 class="section-title">
          آخرین مقالات و بینش‌های
          <span class="title-accent">تخصصی نرم‌افزار</span>
        </h2>

        <p class="section-description">
          راهکارهای فنی، تحلیل‌های مهندسی و تجربیات معماری تیم CloudLand برای ساخت سیستم‌های مقیاس‌پذیر، امن و نسل آینده.
        </p>
      </div>

      <!-- Loading State: Skeletons -->
      <div v-if="loading" class="articles-grid">
        <div
          v-for="n in 3"
          :key="n"
          class="skeleton-card double-bezel"
        >
          <div class="skeleton-inner double-bezel-inner">
            <div class="skeleton-image"></div>
            <div class="skeleton-content">
              <div class="skeleton-pill"></div>
              <div class="skeleton-title"></div>
              <div class="skeleton-text"></div>
              <div class="skeleton-text short"></div>
              <div class="skeleton-footer"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Real or Curated Articles Grid -->
      <div v-else class="articles-grid">
        <article
          v-for="(article, index) in displayArticles"
          :key="article.id || article.slug || index"
          class="article-card double-bezel"
        >
          <div class="double-bezel-inner article-card-inner">
            <!-- Article Cover -->
            <router-link
              :to="article.slug ? `/solutions/${article.slug}` : '/solutions'"
              class="article-image-wrapper"
            >
              <img
                v-if="article.image_url"
                :src="article.image_url"
                :alt="article.title"
                class="article-image"
                loading="lazy"
              />
              <div
                v-else
                class="article-graphic-placeholder"
                :class="`theme-${(index % 3) + 1}`"
              >
                <div class="graphic-pattern"></div>
                <div class="graphic-icon-wrap">
                  <q-icon :name="getArticleIcon(index)" size="36px" />
                </div>
                <span class="graphic-watermark">CLOUDLAND INSIGHTS</span>
              </div>

              <!-- Shine effect -->
              <div class="card-shine"></div>

              <!-- Top badges inside image -->
              <div class="image-top-badges">
                <span class="category-badge">
                  {{ article.category_name || getArticleCategory(index) }}
                </span>
                <span class="read-time-badge">
                  <q-icon name="schedule" size="13px" />
                  {{ article.read_time || getArticleReadTime(index) }}
                </span>
              </div>
            </router-link>

            <!-- Card Body Content -->
            <div class="article-body">
              <!-- Meta: Date & Author -->
              <div class="article-meta-row">
                <span class="meta-date">
                  <q-icon name="event" size="14px" />
                  {{ formatDate(article.created_at) }}
                </span>

                <span class="meta-author">
                  <img
                    v-if="article.author_image_url"
                    :src="article.author_image_url"
                    :alt="article.author_name || 'نویسنده'"
                    class="author-avatar"
                  />
                  <q-icon v-else name="account_circle" size="16px" class="author-icon" />
                  <span class="author-name">{{ article.author_name || 'تیم مهندسی کلودلند' }}</span>
                </span>
              </div>

              <!-- Title -->
              <router-link
                :to="article.slug ? `/solutions/${article.slug}` : '/solutions'"
                class="article-title-link"
              >
                <h3 class="article-title">
                  {{ article.title }}
                </h3>
              </router-link>

              <!-- Summary Excerpt -->
              <p class="article-summary">
                {{ cleanExcerpt(article.summary || article.content) }}
              </p>

              <!-- Footer Read Link -->
              <div class="article-card-footer">
                <router-link
                  :to="article.slug ? `/solutions/${article.slug}` : '/solutions'"
                  class="read-more-link"
                >
                  <span class="read-text">مطالعه کامل راهکار</span>
                  <span class="btn-icon-capsule">
                    <q-icon name="arrow_back" size="14px" />
                  </span>
                </router-link>
              </div>
            </div>
          </div>
        </article>
      </div>

      <!-- Section CTA: View All Articles -->
      <div class="all-articles-wrapper">
        <router-link to="/solutions" class="all-articles-btn">
          <span class="btn-label">مشاهده همه راهکارها و مقالات</span>
          <span class="btn-icon-capsule">
            <q-icon name="arrow_back" size="16px" />
          </span>
        </router-link>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import moment from 'moment-jalaali'
import api from 'src/services/api'

const articles = ref([])
const loading = ref(true)

// High-grade fallback articles for when the API is empty or in mock mode
const curatedFallbacks = [
  {
    id: 'art-1',
    slug: 'distributed-microservices-architecture',
    title: 'معماری میکروسرویس‌های توزیع‌شده: اصول مقیاس‌پذیری سیستم‌های پرتراکنش',
    summary: 'بررسی الگوهای طراحی مقیاس‌پذیر، مدیریت کانسیستنسی داده‌ها در پایگاه‌های داده توزیع‌شده و نحوه کاهش Latency در سامانه‌های سازمانی ابری.',
    created_at: new Date(Date.now() - 3 * 24 * 3600 * 1000).toISOString(),
    author_name: 'مهندس معماری ابری',
    category_name: 'معماری ابری',
    read_time: '۶ دقیقه'
  },
  {
    id: 'art-2',
    slug: 'zero-trust-enterprise-security',
    title: 'امنیت لایه‌ای و رویکرد Zero Trust در نرم‌افزارهای یکپارچه سازمانی',
    summary: 'چگونه با اعمال مکانیزم‌های احراز هویت تطبیقی، رمزنگاری End-to-End و جداسازی کانتینرها، نفوذناپذیری داده‌های حیاتی کسب‌وکار را تضمین کنیم.',
    created_at: new Date(Date.now() - 7 * 24 * 3600 * 1000).toISOString(),
    author_name: 'متخصص امنیت داده',
    category_name: 'امنیت سیستم‌ها',
    read_time: '۸ دقیقه'
  },
  {
    id: 'art-3',
    slug: 'ai-workflow-automation',
    title: 'یکپارچه‌سازی مدل‌های هوش مصنوعی با اتوماسیون فرآیندهای کسب‌وکار (RPA)',
    summary: 'راهنمای عملی ارتقای فرآیندهای سازمانی با هوش مصنوعی مولد؛ تصمیم‌گیری خودکار، پیش‌بینی رفتار مشتریان و حذف اتلاف وقت عملیاتی.',
    created_at: new Date(Date.now() - 14 * 24 * 3600 * 1000).toISOString(),
    author_name: 'تیم هوش تجاری',
    category_name: 'هوش مصنوعی',
    read_time: '۵ دقیقه'
  }
]

onMounted(async () => {
  loading.value = true
  try {
    const res = await api.get('/api/solutions', {
      params: { page: 1, limit: 3 }
    })
    const data = (res.data && res.data.data) || []
    if (Array.isArray(data) && data.length > 0) {
      articles.value = data
    } else {
      articles.value = curatedFallbacks
    }
  } catch (error) {
    // Graceful fallback: render rich curated articles
    articles.value = curatedFallbacks
  } finally {
    loading.value = false
  }
})

const displayArticles = computed(() => {
  if (articles.value && articles.value.length > 0) {
    return articles.value.slice(0, 3)
  }
  return curatedFallbacks
})

function formatDate(dateStr) {
  if (!dateStr) return 'به‌تازگی'
  try {
    return moment(dateStr).format('jD jMMMM jYYYY')
  } catch (e) {
    return 'به‌تازگی'
  }
}

function cleanExcerpt(text) {
  if (!text) return ''
  const stripped = String(text).replace(/<[^>]*>/g, '').trim()
  if (stripped.length > 130) {
    return stripped.slice(0, 130) + '…'
  }
  return stripped
}

function getArticleIcon(index) {
  const icons = ['cloud_queue', 'security', 'psychology']
  return icons[index % icons.length]
}

function getArticleCategory(index) {
  const cats = ['معماری ابری', 'امنیت داده', 'هوش تجاری']
  return cats[index % cats.length]
}

function getArticleReadTime(index) {
  const times = ['۵ دقیقه', '۷ دقیقه', '۶ دقیقه']
  return times[index % times.length]
}
</script>

<style scoped>
/* =========================================
   HOME ARTICLES SECTION
========================================== */
.home-articles-section {
  position: relative;
  padding: var(--section-pad-y) 0;
  background: var(--cl-bg);
  direction: rtl;
  overflow: hidden;
}

/* Ambient Backdrops */
.articles-ambient-mesh {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.articles-glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(130px);
  opacity: 0.4;
}

.orb-primary {
  width: 520px;
  height: 520px;
  top: 15%;
  right: -80px;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.16) 0%, rgba(37, 99, 235, 0) 70%);
}

.orb-accent {
  width: 460px;
  height: 460px;
  bottom: 10%;
  left: -60px;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.12) 0%, rgba(245, 158, 11, 0) 70%);
}

.articles-grid-pattern {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(to right, rgba(226, 232, 240, 0.35) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(226, 232, 240, 0.35) 1px, transparent 1px);
  background-size: 52px 52px;
  opacity: 0.55;
  -webkit-mask-image: radial-gradient(ellipse 75% 65% at 50% 50%, #000 45%, transparent 100%);
  mask-image: radial-gradient(ellipse 75% 65% at 50% 50%, #000 45%, transparent 100%);
}

.articles-container {
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
  font-size: 15.5px;
  line-height: 1.85;
  max-width: 640px;
}

/* =========================================
   Articles Grid & Cards
========================================== */
.articles-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
  margin-bottom: 50px;
}

.article-card {
  transition: transform 0.4s var(--cl-ease), border-color 0.4s var(--cl-ease), box-shadow 0.4s var(--cl-ease);
}

.article-card:hover {
  transform: translateY(-6px);
  border-color: rgba(37, 99, 235, 0.32);
  box-shadow: 0 20px 40px -8px rgba(15, 23, 42, 0.1), 0 0 25px rgba(37, 99, 235, 0.1);
}

.article-card-inner {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Image Cover */
.article-image-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9.5;
  overflow: hidden;
  background: #0f172a;
  display: block;
}

.article-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s var(--cl-ease);
}

.article-card:hover .article-image {
  transform: scale(1.06);
}

/* Graphic Placeholder */
.article-graphic-placeholder {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.theme-1 {
  background: linear-gradient(135deg, #0b132b 0%, #1e3a8a 100%);
}
.theme-2 {
  background: linear-gradient(135deg, #0b132b 0%, #1e293b 50%, #0f766e 100%);
}
.theme-3 {
  background: linear-gradient(135deg, #0b132b 0%, #312e81 60%, #b45309 100%);
}

.graphic-pattern {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(255, 255, 255, 0.12) 1px, transparent 1px);
  background-size: 16px 16px;
  opacity: 0.6;
}

.graphic-icon-wrap {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-xl);
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  transition: transform 0.5s var(--cl-ease);
  z-index: 2;
}

.article-card:hover .graphic-icon-wrap {
  transform: scale(1.12);
}

.graphic-watermark {
  position: absolute;
  bottom: 10px;
  left: 12px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.15em;
  color: rgba(255, 255, 255, 0.25);
  font-family: monospace;
}

/* Card Shine */
.card-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  transform: skewX(-20deg);
  transition: left 0.75s ease;
  pointer-events: none;
}

.article-card:hover .card-shine {
  left: 200%;
}

/* Top Badges inside image */
.image-top-badges {
  position: absolute;
  top: 12px;
  right: 12px;
  left: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 3;
  pointer-events: none;
}

.category-badge {
  font-size: 11px;
  font-weight: 700;
  color: #ffffff;
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.25);
  padding: 4px 12px;
  border-radius: var(--radius-pill);
}

.read-time-badge {
  font-size: 11px;
  font-weight: 600;
  color: #ffffff;
  background: rgba(37, 99, 235, 0.85);
  backdrop-filter: blur(8px);
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  display: flex;
  align-items: center;
  gap: 5px;
}

/* Body */
.article-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.article-meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: var(--cl-text-muted);
  margin-bottom: 14px;
}

.meta-date {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.meta-author {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.author-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  object-fit: cover;
}

.author-icon {
  color: var(--cl-primary);
}

.article-title-link {
  text-decoration: none;
  display: block;
}

.article-title {
  font-size: 17px;
  font-weight: 800;
  color: var(--cl-text-dark);
  line-height: 1.5;
  margin: 0 0 10px;
  transition: color 0.3s var(--cl-ease);
}

.article-card:hover .article-title {
  color: var(--cl-primary);
}

.article-summary {
  font-size: 13px;
  color: var(--cl-text);
  line-height: 1.7;
  margin: 0 0 20px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-card-footer {
  margin-top: auto;
  padding-top: 14px;
  border-top: 1px solid rgba(226, 232, 240, 0.7);
}

.read-more-link {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  font-size: 13px;
  font-weight: 700;
  color: var(--cl-primary);
  text-decoration: none;
  transition: all 0.3s var(--cl-ease);
}

.read-more-link .btn-icon-capsule {
  background: var(--cl-primary-light);
  color: var(--cl-primary);
}

.article-card:hover .read-more-link {
  color: var(--cl-primary-hover);
}

.article-card:hover .read-more-link .btn-icon-capsule {
  background: var(--cl-primary);
  color: #ffffff;
  transform: translateX(-4px);
}

/* =========================================
   Section Footer CTA
========================================== */
.all-articles-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.all-articles-btn {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px 12px 26px;
  background: var(--cl-surface);
  color: var(--cl-text-dark);
  font-weight: 700;
  font-size: 14px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(226, 232, 240, 0.9);
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
  transition: all 0.3s var(--cl-ease);
}

.all-articles-btn .btn-icon-capsule {
  background: var(--cl-bg-subtle);
  color: var(--cl-text-dark);
}

.all-articles-btn:hover {
  background: var(--cl-primary);
  color: #ffffff;
  border-color: var(--cl-primary);
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.28);
}

.all-articles-btn:hover .btn-icon-capsule {
  background: rgba(255, 255, 255, 0.25);
  color: #ffffff;
  transform: translateX(-4px);
}

/* =========================================
   Skeletons
========================================== */
.skeleton-card {
  height: 380px;
}

.skeleton-inner {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.skeleton-image {
  height: 180px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

.skeleton-pill {
  width: 70px;
  height: 18px;
  border-radius: var(--radius-pill);
  background: #e2e8f0;
}

.skeleton-title {
  width: 90%;
  height: 20px;
  border-radius: 6px;
  background: #e2e8f0;
}

.skeleton-text {
  width: 100%;
  height: 14px;
  border-radius: 4px;
  background: #f1f5f9;
}

.skeleton-text.short {
  width: 65%;
}

.skeleton-footer {
  margin-top: auto;
  width: 40%;
  height: 16px;
  border-radius: 4px;
  background: #e2e8f0;
}

/* =========================================
   Responsive Breakpoints
========================================== */
@media (max-width: 1024px) {
  .articles-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .home-articles-section {
    padding: 70px 0 80px;
  }

  .articles-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .article-body {
    padding: 18px;
  }
}
</style>

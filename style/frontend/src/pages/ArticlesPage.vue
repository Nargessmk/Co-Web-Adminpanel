<template>
  <q-page class="articles-page-root">
    <!-- 1. Header & Hero Section -->
    <section class="articles-hero">
      <div class="container">
        <div class="hero-center-head">
          <div class="section-tag">
            <span class="tag-dot"></span>
            <span>{{ articlesData.badge || 'پایگاه دانش و مقالات مهندسی' }}</span>
          </div>

          <div class="title-with-admin">
            <h1 class="articles-main-title">
              {{ articlesData.title || 'تحلیل‌های تخصصی معماری، زیرساخت ابری و هوش مصنوعی' }}
            </h1>
            <div class="hero-admin-actions" v-if="isAdmin">
              <button
                type="button"
                class="btn-pill btn-pill-dark btn-pill-sm mr-2"
                @click="openMasterEditor('articles')"
              >
                <q-icon name="edit" size="14px" />
                <span>ویرایش محتوای مقالات</span>
              </button>
              <router-link
                to="/admin/solutions"
                class="btn-pill btn-pill-dark btn-pill-sm mr-2"
              >
                <q-icon name="settings" size="14px" />
                <span>مدیریت راهکارهای ابری (مقالات)</span>
              </router-link>
            </div>
          </div>

          <p class="articles-subtext">
            {{ articlesData.desc || 'دیدگاه‌ها، درس‌آموخته‌ها و مقالات فنی تیم مهندسی کهکشان هوشمند در حوزه‌های معماری ابری، امنیت، طراحی محصول و هوش مصنوعی.' }}
          </p>

          <!-- Search & Filter Controls -->
          <div class="filter-controls-wrap">
            <div class="category-pills">
              <button
                v-for="cat in categories"
                :key="cat"
                type="button"
                class="cat-pill"
                :class="{ active: selectedCategory === cat }"
                @click="selectedCategory = cat"
              >
                {{ cat }}
              </button>
            </div>

            <div class="search-input-wrap">
              <q-icon name="search" size="18px" class="search-icon" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="جستجو در عناوین و مفاهیم مقالات..."
                class="search-input"
              />
              <button v-if="searchQuery" class="clear-search" @click="searchQuery = ''">✕</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 2. Featured Article Spotlight (Hero Bento Card) -->
    <section v-if="featuredArticle && !searchQuery && selectedCategory === 'همه'" class="featured-article-section">
      <div class="container">
        <div class="featured-card" @click="navigateToArticle(featuredArticle)">
          <div class="featured-media">
            <img :src="featuredArticle.image || '/uploads/articles/edge-computing.jpg'" :alt="featuredArticle.title" @error="e => handleImageError(e)" />
            <div class="featured-badge">مقاله برگزیده مهندسی</div>
          </div>
          <div class="featured-content">
            <div class="article-meta-row">
              <span class="category-tag">{{ featuredArticle.category }}</span>
              <span class="meta-dot">•</span>
              <span class="read-time">{{ featuredArticle.readTime }}</span>
              <span class="meta-dot">•</span>
              <span class="pub-date">{{ featuredArticle.date || 'شهریور ۱۴۰۵' }}</span>
            </div>

            <h2 class="featured-title">{{ featuredArticle.title }}</h2>
            <div class="featured-excerpt" v-html="featuredArticle.excerpt"></div>

            <div class="featured-footer">
              <div class="author-box" v-if="featuredArticle && featuredArticle.author">
                <img :src="featuredArticle.author.avatar || '/Modern 3D Tech Dashboard Illustration(1).png'" class="author-avatar" alt="" />
                <div>
                  <div class="author-name">{{ featuredArticle.author?.name || 'تیم مهندسی' }}</div>
                  <div class="author-role">{{ featuredArticle.author?.role || 'کهکشان هوشمند' }}</div>
                </div>
              </div>

              <button type="button" class="btn-pill btn-pill-yellow btn-pill-sm" @click.stop="navigateToArticle(featuredArticle)">
                <span class="btn-text">مطالعه مقاله کامل</span>
                <span class="btn-icon-bubble">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"></path><path d="M12 5l7 7-7 7"></path></svg>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 3. Articles Grid -->
    <section class="articles-grid-section">
      <div class="container">
        <div class="grid-section-head">
          <span class="count-badge">{{ filteredArticles.length }} مقاله فنی</span>
          <router-link
            v-if="isAdmin"
            to="/admin/solutions"
            class="btn-pill btn-pill-yellow btn-pill-sm"
          >
            <q-icon name="add" size="14px" />
            <span>مقاله جدید در پنل ادمین</span>
          </router-link>
        </div>

        <div v-if="filteredArticles.length === 0" class="empty-results">
          <q-icon name="article" size="48px" color="grey-6" />
          <h3>مقاله‌ای با این مشخصات یافت نشد</h3>
          <p>لطفاً عبارت دیگری را جستجو کنید یا فیلتر دسته‌بندی را تغییر دهید.</p>
          <button class="btn-pill btn-pill-dark btn-pill-sm" @click="resetFilters">پاک کردن فیلترها</button>
        </div>

        <div v-else class="articles-cards-grid">
          <article
            v-for="(art, idx) in filteredArticles"
            :key="art.id || idx"
            class="article-card"
            @click="navigateToArticle(art)"
          >
            <div class="card-thumb-wrap">
              <img :src="art.image || '/uploads/articles/microservices.jpg'" :alt="art.title" loading="lazy" @error="e => handleImageError(e)" />
              <span class="card-cat-pill">{{ art.category }}</span>
            </div>

            <div class="card-body">
              <div class="card-meta">
                <span class="read-pill">{{ art.readTime }}</span>
                <span class="dot-sep">•</span>
                <span>{{ art.topic || art.category }}</span>
              </div>

              <h3 class="card-title">{{ art.title }}</h3>
              <p class="card-excerpt" v-html="art.excerpt"></p>
            </div>

            <div class="card-footer">
              <div class="author-mini">
                <img :src="art.author?.avatar || '/Modern 3D Tech Dashboard Illustration(1).png'" class="mini-avatar" alt="" />
                <span class="mini-name">{{ art.author?.name || 'تیم مهندسی' }}</span>
              </div>
              <div class="read-action" @click.stop="navigateToArticle(art)">
                <span>مطالعه مقاله</span>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"></path><path d="M12 5l7 7-7 7"></path></svg>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- 4. High-Impact Unified Consultation CTA -->
    <CloudlandCTA page-name="مقالات" />

  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { usePageMeta } from 'src/composables/usePageMeta'
import { useAuth } from 'src/composables/useAuth'
import { useMasterEditor, loadMasterContent } from 'src/composables/useMasterEditor'
import CloudlandCTA from 'src/components/CTA/CloudlandCTA.vue'
import { formatMediaUrl, handleImageError, DEFAULT_ARTICLE_IMAGE } from 'src/utils/media'
import api from 'src/services/api'

const router = useRouter()

usePageMeta({
  title: 'پایگاه دانش و مقالات فنی | کهکشان هوشمند',
  description: 'مقالات تخصصی و مستندات فنی در زمینه‌های رایانش ابری، معماری میکروسرویس، امنیت Zero-Trust و هوش مصنوعی در لبه شبکه.',
  path: '/articles',
})

const $q = useQuasar()
const { isAdmin } = useAuth()
const { openMasterEditor, articlesState } = useMasterEditor()

const searchQuery = ref('')
const selectedCategory = ref('همه')
const newsletterEmail = ref('')

const articlesData = computed(() => {
  return {
    badge: articlesState.value?.badge || 'پایگاه دانش و مقالات مهندسی',
    title: articlesState.value?.title || 'تحلیل‌های تخصصی معماری، زیرساخت ابری و هوش مصنوعی',
    desc: articlesState.value?.desc || 'دیدگاه‌ها، درس‌آموخته‌ها و مقالات فنی تیم مهندسی کهکشان هوشمند در حوزه‌های معماری ابری، امنیت، طراحی محصول و هوش مصنوعی.',
    categories: ['همه', 'رایانش ابری', 'معماری میکروسرویس', 'هوش مصنوعی', 'امنیت ابری', 'دیزاین سیستم'],
  }
})

const backendArticles = ref([])

const categories = computed(() => {
  return articlesData.value.categories || ['همه', 'رایانش ابری', 'معماری میکروسرویس', 'هوش مصنوعی', 'امنیت ابری', 'دیزاین سیستم']
})

const allItems = computed(() => {
  return backendArticles.value
})

const featuredArticle = computed(() => {
  return allItems.value[0] || null
})

const filteredArticles = computed(() => {
  let list = allItems.value
  if (selectedCategory.value !== 'همه') {
    list = list.filter((a) => a.category === selectedCategory.value)
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    list = list.filter((a) => {
      return (
        (a.title && a.title.toLowerCase().includes(q)) ||
        (a.excerpt && a.excerpt.toLowerCase().includes(q)) ||
        (a.topic && a.topic.toLowerCase().includes(q)) ||
        (a.category && a.category.toLowerCase().includes(q))
      )
    })
  }
  return list
})

function navigateToArticle (art) {
  if (!art) return
  const identifier = art.slug || art.id
  router.push(`/articles/${encodeURIComponent(identifier)}`)
}

function resetFilters () {
  searchQuery.value = ''
  selectedCategory.value = 'همه'
}

function handleSubscribe () {
  $q.notify({
    type: 'positive',
    message: 'ایمیل شما با موفقیت در خبرنامه فنی کهکشان هوشمند ثبت شد.',
    position: 'top',
  })
  newsletterEmail.value = ''
}

async function loadArticles () {
  try {
    const res = await api.get('/api/articles', { params: { limit: 50 } })
    if (res?.data?.data && Array.isArray(res.data.data) && res.data.data.length) {
      backendArticles.value = res.data.data.map(art => ({
        id: art.id,
        title: art.title,
        excerpt: art.excerpt || art.summary || '',
        content: art.content || '',
        category: art.category || 'رایانش ابری',
        readTime: art.readTime || art.read_time || '۵ دقیقه مطالعه',
        topic: art.topic || 'معماری سیستم',
        image: formatMediaUrl(art.image || art.image_url, DEFAULT_ARTICLE_IMAGE),
        date: art.date || 'شهریور ۱۴۰۵',
        author: art.author ? {
          ...art.author,
          avatar: formatMediaUrl(art.author.avatar, '/Modern 3D Tech Dashboard Illustration(1).png')
        } : {
          name: art.author_name || 'تیم مهندسی',
          role: art.author_role || 'کهکشان هوشمند',
          avatar: formatMediaUrl(art.author_image_url, '/Modern 3D Tech Dashboard Illustration(1).png'),
        },
        tags: Array.isArray(art.tags) ? art.tags : (art.tags ? [art.tags] : []),
        slug: art.slug,
      }))
    }
  } catch (e) {
    console.error('Failed to load articles:', e)
  }
}

onMounted(() => {
  loadMasterContent().catch(() => {})
  loadArticles()
})
</script>

<style scoped>
/* ==========================================================================
   ARTICLES PAGE (Luxury Tech Design)
   ========================================================================== */
.articles-page-root {
  background-color: var(--bg-canvas, #f7f7f7);
  color: var(--text-dark, #0a0a0a);
  direction: rtl;
  min-height: 100vh;
}

.container {
  width: min(1340px, 94vw);
  margin: 0 auto;
  padding: 0 16px;
  box-sizing: border-box;
}

/* Hero */
.articles-hero {
  padding: 148px 0 60px 0;
  text-align: center;
  position: relative;
}

.hero-center-head {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 880px;
  margin: 0 auto;
}

.section-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 18px;
  border-radius: var(--radius-pill, 9999px);
  font-size: 0.82rem;
  font-weight: 700;
  background: var(--yellow-dim, rgba(255, 204, 0, 0.12));
  border: 1px solid var(--yellow-border, rgba(255, 204, 0, 0.35));
  color: #946200;
  box-shadow: 0 2px 10px rgba(255, 204, 0, 0.08);
  margin-bottom: 20px;
}

.tag-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ffd54a;
  box-shadow: 0 0 8px #ffd54a;
}

.title-with-admin {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
  margin: 0 0 16px 0;
}

.articles-main-title {
  font-size: clamp(2.1rem, 4vw, 3.1rem);
  font-weight: 900;
  line-height: 1.3;
  margin: 0;
  color: var(--text-dark, #0a0a0a);
  letter-spacing: -0.025em;
}

.articles-subtext {
  font-size: 1.08rem;
  line-height: 1.9;
  color: var(--text-dark-muted, #52525b);
  margin: 0 auto 36px auto;
  max-width: 760px;
}

/* Filter Controls */
.filter-controls-wrap {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}

.category-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.cat-pill {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  color: var(--text-dark, #0a0a0a);
  padding: 8px 18px;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.cat-pill:hover {
  border-color: #0a0a0a;
}

.cat-pill.active {
  background: #0a0a0a;
  color: #ffffff;
  border-color: #0a0a0a;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.search-input-wrap {
  position: relative;
  width: 100%;
  max-width: 480px;
}

.search-icon {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #a1a1aa;
}

.search-input {
  width: 100%;
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  padding: 12px 42px 12px 36px;
  border-radius: 9999px;
  font-size: 0.88rem;
  font-family: inherit;
  color: var(--text-dark, #0a0a0a);
  outline: none;
  box-sizing: border-box;
  transition: all 0.2s;
}

.search-input:focus {
  border-color: #0a0a0a;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.05);
}

.clear-search {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: #71717a;
  cursor: pointer;
  font-size: 0.85rem;
}

/* Featured Article Spotlight */
.featured-article-section {
  padding: 20px 0 50px 0;
}

.featured-card {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: 28px;
  overflow: hidden;
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  cursor: pointer;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.featured-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.08);
  border-color: #d4d4d8;
}

.featured-media {
  position: relative;
  min-height: 380px;
  background: #0a0a0a;
}

.featured-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.featured-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(10, 10, 10, 0.85);
  backdrop-filter: blur(8px);
  color: #ffd54a;
  font-size: 0.78rem;
  font-weight: 800;
  padding: 6px 14px;
  border-radius: 9999px;
  border: 1px solid rgba(255, 213, 74, 0.3);
}

.featured-content {
  padding: 44px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.article-meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: var(--text-dark-muted, #737373);
  font-weight: 600;
}

.category-tag {
  background: rgba(255, 204, 0, 0.15);
  color: #946c00;
  padding: 3px 10px;
  border-radius: 6px;
  font-weight: 800;
}

.meta-dot {
  opacity: 0.5;
}

.featured-title {
  font-size: 1.6rem;
  font-weight: 900;
  line-height: 1.35;
  margin: 14px 0;
  color: var(--text-dark, #0a0a0a);
}

.featured-excerpt {
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--text-dark-muted, #737373);
  margin-bottom: 24px;
}

.featured-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 20px;
  border-top: 1px solid var(--border-light, #e5e5e5);
}

.author-box {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: cover;
  background: #e5e5e5;
}

.author-name {
  font-weight: 800;
  font-size: 0.88rem;
  color: var(--text-dark, #0a0a0a);
}

.author-role {
  font-size: 0.75rem;
  color: var(--text-dark-muted, #737373);
}

/* Articles Grid */
.articles-grid-section {
  padding: 40px 0 80px 0;
}

.grid-section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}

.count-badge {
  font-size: 0.85rem;
  font-weight: 800;
  color: var(--text-dark-muted, #737373);
}

.articles-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 28px;
}

.article-card {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: 22px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}

.article-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.07);
  border-color: #0a0a0a;
}

.card-thumb-wrap {
  position: relative;
  height: 220px;
  background: #111116;
  overflow: hidden;
}

.card-thumb-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.article-card:hover .card-thumb-wrap img {
  transform: scale(1.04);
}

.card-cat-pill {
  position: absolute;
  top: 14px;
  right: 14px;
  background: rgba(13, 13, 15, 0.8);
  backdrop-filter: blur(8px);
  color: #ffd54a;
  font-size: 0.74rem;
  font-weight: 800;
  padding: 4px 12px;
  border-radius: 9999px;
  border: 1px solid rgba(255, 213, 74, 0.25);
}

.card-body {
  padding: 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  color: var(--text-dark-muted, #737373);
  margin-bottom: 10px;
}

.dot-sep {
  opacity: 0.4;
}

.card-title {
  font-size: 1.15rem;
  font-weight: 800;
  line-height: 1.4;
  margin: 0 0 10px 0;
  color: var(--text-dark, #0a0a0a);
}

.card-excerpt {
  font-size: 0.86rem;
  line-height: 1.65;
  color: var(--text-dark-muted, #737373);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border-light, #e5e5e5);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fafafa;
}

.author-mini {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mini-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
}

.mini-name {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-dark, #0a0a0a);
}

.read-action {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  font-weight: 800;
  color: var(--text-dark, #0a0a0a);
  transition: gap 0.2s;
}

.article-card:hover .read-action {
  gap: 9px;
  color: #946c00;
}

.empty-results {
  text-align: center;
  padding: 60px 20px;
  background: #ffffff;
  border-radius: 20px;
  border: 1px dashed var(--border-light, #e5e5e5);
}

.empty-results h3 {
  margin: 14px 0 6px 0;
  font-size: 1.2rem;
  font-weight: 800;
}

.empty-results p {
  color: var(--text-dark-muted, #737373);
  margin-bottom: 20px;
}

/* Newsletter Section */
.newsletter-section {
  padding: 40px 0 80px 0;
}

.newsletter-bento-card {
  position: relative;
  background: #0a0a0a;
  color: #ffffff;
  border-radius: 32px;
  padding: 60px 48px;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}

.bento-glow {
  position: absolute;
  top: -100px;
  left: -100px;
  width: 350px;
  height: 350px;
  background: radial-gradient(circle, rgba(255, 213, 74, 0.2) 0%, transparent 70%);
  pointer-events: none;
}

.newsletter-content {
  position: relative;
  z-index: 2;
  max-width: 680px;
  margin: 0 auto;
  text-align: center;
}

.section-tag-light {
  background: rgba(255, 255, 255, 0.1);
  color: #ffd54a;
  border-color: rgba(255, 213, 74, 0.3);
  margin: 0 auto 16px auto;
}

.newsletter-title {
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  font-weight: 900;
  margin: 0 0 14px 0;
  line-height: 1.3;
}

.newsletter-desc {
  font-size: 0.95rem;
  line-height: 1.7;
  color: #a1a1aa;
  margin: 0 0 32px 0;
}

.newsletter-form {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.newsletter-input {
  flex: 1;
  max-width: 360px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 9999px;
  padding: 12px 24px;
  color: #ffffff;
  font-family: inherit;
  font-size: 0.9rem;
  outline: none;
}

.newsletter-input:focus {
  border-color: #ffd54a;
}

/* Reader Modal */
.reader-modal-root {
  background: #ffffff;
  color: #0a0a0a;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  direction: rtl;
  overflow-y: auto;
}

.reader-header {
  height: 64px;
  background: #ffffff;
  border-bottom: 1px solid var(--border-light, #e5e5e5);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.reader-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.82rem;
  color: var(--text-dark-muted, #737373);
}

.btn-close-modal {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f4f4f5;
  border: none;
  padding: 8px 16px;
  border-radius: 9999px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
}

.reader-body {
  flex: 1;
  padding: 48px 24px 80px 24px;
}

.reader-container {
  max-width: 800px;
  margin: 0 auto;
}

.reader-title {
  font-size: clamp(1.8rem, 3.5vw, 2.6rem);
  font-weight: 900;
  line-height: 1.3;
  margin: 0 0 24px 0;
}

.reader-author-strip {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-light, #e5e5e5);
}

.reader-cover-wrap {
  width: 100%;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 36px;
}

.reader-cover-wrap img {
  width: 100%;
  max-height: 480px;
  object-fit: cover;
  display: block;
}

.reader-callout {
  background: #fdf6d8;
  border-right: 4px solid #f59e0b;
  padding: 20px 24px;
  border-radius: 12px;
  font-size: 1.05rem;
  line-height: 1.8;
  color: #78350f;
  margin-bottom: 36px;
  font-weight: 600;
}

.reader-content {
  font-size: 1.05rem;
  line-height: 2;
  color: #27272a;
}

.reader-content :deep(h3) {
  font-size: 1.45rem;
  font-weight: 900;
  margin: 36px 0 16px 0;
  color: #09090b;
}

.reader-content :deep(h4) {
  font-size: 1.2rem;
  font-weight: 800;
  margin: 28px 0 12px 0;
  color: #18181b;
}

.reader-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 40px 0;
}

.tag-pill {
  background: #f4f4f5;
  color: #71717a;
  padding: 6px 14px;
  border-radius: 9999px;
  font-size: 0.82rem;
  font-weight: 700;
}

.reader-cta-box {
  background: #0a0a0a;
  color: #ffffff;
  border-radius: 20px;
  padding: 36px;
  text-align: center;
  margin-top: 50px;
}

.reader-cta-box h3 {
  margin: 0 0 10px 0;
  font-size: 1.25rem;
  font-weight: 800;
}

.reader-cta-box p {
  color: #a1a1aa;
  margin: 0 0 20px 0;
  font-size: 0.9rem;
}

@media (max-width: 900px) {
  .articles-hero {
    padding: 100px 0 32px 0;
  }

  .articles-main-title {
    font-size: clamp(1.4rem, 5.5vw, 1.85rem);
    line-height: 1.32;
  }

  .articles-subtext {
    font-size: 0.85rem;
    line-height: 1.72;
  }

  .featured-card {
    grid-template-columns: 1fr;
  }

  .featured-content {
    padding: 24px 20px;
  }

  .featured-title {
    font-size: 1.18rem;
    line-height: 1.4;
  }

  .featured-excerpt {
    font-size: 0.82rem;
    line-height: 1.7;
  }

  .articles-cards-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .card-title {
    font-size: 1.02rem;
    line-height: 1.42;
  }

  .card-excerpt {
    font-size: 0.8rem;
    line-height: 1.68;
  }

  .newsletter-form {
    flex-direction: column;
  }

  .newsletter-input {
    max-width: 100%;
  }
}

@media (max-width: 640px) {
  .articles-hero {
    padding: 92px 0 24px 0;
  }

  .articles-main-title {
    font-size: clamp(1.22rem, 5vw, 1.48rem);
  }

  .articles-subtext {
    font-size: 0.8rem;
    line-height: 1.68;
  }

  .featured-media {
    min-height: 200px;
  }

  .featured-content {
    padding: 20px 16px;
  }

  .featured-title {
    font-size: 1.08rem;
  }

  .featured-excerpt {
    font-size: 0.78rem;
  }

  .article-card {
    padding: 16px 14px;
    border-radius: 18px;
  }

  .card-title {
    font-size: 0.96rem;
  }

  .card-excerpt {
    font-size: 0.76rem;
  }

  .reader-body-wrap {
    padding: 18px 14px;
    font-size: 0.88rem;
  }

  .reader-header {
    padding: 20px 16px 16px;
  }

  .reader-title {
    font-size: 1.18rem;
    line-height: 1.35;
  }

  .search-input-wrap {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .articles-hero {
    padding: 88px 0 20px 0;
  }

  .articles-main-title {
    font-size: clamp(1.18rem, 4.8vw, 1.4rem);
  }

  .articles-subtext {
    font-size: 0.78rem;
    line-height: 1.65;
  }

  .featured-media {
    min-height: 170px;
  }

  .featured-content {
    padding: 16px 12px;
  }

  .featured-title {
    font-size: 1.02rem;
  }

  .article-card {
    padding: 14px 12px;
    border-radius: 16px;
  }

  .card-title {
    font-size: 0.92rem;
  }

  .card-excerpt {
    font-size: 0.74rem;
  }

  .reader-title {
    font-size: 1.1rem;
  }

  .reader-body-wrap {
    padding: 14px 10px;
  }
}
</style>

<template>
  <section class="section-spacing articles-minimal-section" id="sec-articles">
    <div class="container">
      <!-- Minimalist Clean Header -->
      <div class="section-head-minimal">
        <div class="section-tag">
          <span class="tag-motion-dot"></span>
          <span>{{ sectionBadge }}</span>
        </div>

        <div class="title-action-row">
          <h2 class="section-title-minimal">{{ sectionTitle }}</h2>
          <div class="admin-quick-btns" v-if="isAdmin">
            <q-btn
              class="section-edit-btn"
              round
              dense
              size="sm"
              unelevated
              color="dark"
              icon="edit"
              @click="openMasterEditor('articles')"
            >
              <q-tooltip>ویرایش عنوان و توضیحات مقالات</q-tooltip>
            </q-btn>
            <q-btn
              class="section-edit-btn"
              round
              dense
              size="sm"
              unelevated
              color="dark"
              icon="settings"
              to="/admin/solutions"
            >
              <q-tooltip>مدیریت مقالات در پنل ادمین</q-tooltip>
            </q-btn>
          </div>
        </div>

        <p class="section-desc-minimal">
          {{ sectionDesc }}
        </p>
      </div>

      <!-- Minimalist Motion Cards Grid (3 Featured Articles) -->
      <div class="minimal-articles-grid">
        <router-link
          v-for="(article, index) in displayArticles"
          :key="article.id || index"
          :to="article.link || '/articles'"
          class="minimal-article-card"
          :style="{ animationDelay: `${index * 120}ms` }"
        >
          <!-- Thumbnail with Zoom Motion -->
          <div class="card-thumb-frame">
            <img
              :src="article.image"
              :alt="article.title"
              loading="lazy"
              class="card-img-motion"
              @error="e => handleImageError(e)"
            />
            <span class="category-chip">{{ article.category }}</span>
          </div>

          <!-- Content Minimal -->
          <div class="card-body-minimal">
            <div class="meta-row-minimal">
              <span class="read-time">{{ article.readTime }}</span>
              <span class="dot-sep">•</span>
              <span class="topic-tag">{{ article.topic }}</span>
            </div>

            <h3 class="card-title-minimal">{{ article.title }}</h3>

            <div class="card-footer-motion">
              <span class="read-link-text">مطالعه مقاله</span>
              <span class="arrow-motion-bubble">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"></path><path d="M12 5l7 7-7 7"></path></svg>
              </span>
            </div>
          </div>
        </router-link>
      </div>

      <!-- Minimal Bottom Link with Smooth Motion -->
      <div class="articles-bottom-action">
        <router-link to="/articles" class="btn-explore-articles">
          <span>مشاهده تمامی مقالات و تحلیل‌های مهندسی</span>
          <q-icon name="arrow_back" size="16px" class="arrow-glide" />
        </router-link>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from 'src/composables/useAuth'
import { useHomeContent } from 'src/composables/useHomeContent'
import { useMasterEditor } from 'src/composables/useMasterEditor'
import { formatMediaUrl, handleImageError, DEFAULT_ARTICLE_IMAGE } from 'src/utils/media'
import api from 'src/services/api'

const { isAdmin } = useAuth()
const { settings } = useHomeContent()
const { articlesState, openMasterEditor } = useMasterEditor()

const sectionBadge = computed(() => settings.value?.articles_badge || articlesState.value?.badge || 'دانش و وبلاگ')
const sectionTitle = computed(() => settings.value?.articles_title || articlesState.value?.title || 'تازه‌ترین مقالات مهندسی')
const sectionDesc = computed(() => settings.value?.articles_description || articlesState.value?.desc || 'دیدگاه‌ها و مقالات فنی تیم مهندسی در حوزه‌های معماری ابری، امنیت، طراحی محصول و هوش مصنوعی.')

const backendArticles = ref([])

const FALLBACK_ARTICLES = [
  {
    id: 1,
    title: 'معماری مایکروسرویس با لتنسی زیر ۱۰ میلی‌ثانیه بر بستر کوبرنتیز',
    category: 'رایانش ابری',
    readTime: '۵ دقیقه مطالعه',
    topic: 'معماری سیستم',
    image: '/uploads/home/contact-programming.jpg',
    link: '/articles',
  },
  {
    id: 2,
    title: 'پیاده‌سازی استراتژی امنیت Zero-Trust در کلاسترهای ابری سازمانی',
    category: 'امنیت ابری',
    readTime: '۷ دقیقه مطالعه',
    topic: 'امنیت شبکه',
    image: '/uploads/general/Modern 3D Tech Dashboard Illustration(1).png',
    link: '/articles',
  },
  {
    id: 3,
    title: 'بهینه‌سازی مدل‌های زبانی بزرگ (LLM) و پایگاه‌داده‌های برداری در لبه شبکه',
    category: 'هوش مصنوعی',
    readTime: '۶ دقیقه مطالعه',
    topic: 'پردازش داده',
    image: '/assets/icons3d/ai.svg',
    link: '/articles',
  },
]

async function loadArticlesFromBackend () {
  try {
    const res = await api.get('/api/articles', { params: { limit: 3 } })
    const items = res?.data?.data || []
    if (items.length) {
      backendArticles.value = items.slice(0, 3).map((art) => ({
        id: art.id,
        title: art.title,
        category: art.category || 'رایانش ابری',
        readTime: art.readTime || art.read_time || '۵ دقیقه مطالعه',
        topic: art.topic || 'معماری سیستم',
        image: formatMediaUrl(art.image || art.image_url, DEFAULT_ARTICLE_IMAGE),
        link: `/articles/${art.slug || art.id}`,
      }))
    }
  } catch (err) {
    console.warn('Backend articles not reachable, using featured defaults:', err)
  }
}

onMounted(() => {
  loadArticlesFromBackend()
})

const displayArticles = computed(() => {
  if (backendArticles.value && backendArticles.value.length > 0) {
    return backendArticles.value.slice(0, 3)
  }
  return FALLBACK_ARTICLES
})
</script>

<style scoped>
/* ==========================================================================
   MINIMALIST MOTION ARTICLES SECTION
   ========================================================================== */
.articles-minimal-section {
  padding: 70px 0;
  position: relative;
  direction: rtl;
}

.container {
  width: min(1340px, 94vw);
  margin: 0 auto;
  padding: 0 16px;
  box-sizing: border-box;
}

.section-head-minimal {
  margin-bottom: 40px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.section-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  border-radius: 9999px;
  font-size: 0.76rem;
  font-weight: 700;
  margin-bottom: 14px;
  background: rgba(255, 204, 0, 0.12);
  border: 1px solid rgba(255, 204, 0, 0.35);
  color: #946200;
}

.tag-motion-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ffcc00;
  box-shadow: 0 0 8px #ffcc00;
  animation: pulseDot 2s infinite ease-in-out;
}

@keyframes pulseDot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(1.3); }
}

.title-action-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 10px;
}

.section-title-minimal {
  font-size: clamp(1.6rem, 2.8vw, 2.2rem);
  font-weight: 900;
  letter-spacing: -0.5px;
  line-height: 1.3;
  margin: 0;
  color: #0a0a0a;
}

.admin-quick-btns {
  display: inline-flex;
  gap: 6px;
}

.section-desc-minimal {
  font-size: 0.92rem;
  color: #52525b;
  max-width: 580px;
  line-height: 1.7;
  margin: 0;
}

/* Minimal Motion Grid */
.minimal-articles-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.minimal-article-card {
  background: #ffffff;
  border: 1px solid #e4e4e7;
  border-radius: 20px;
  overflow: hidden;
  text-decoration: none;
  display: flex;
  flex-direction: column;
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  animation: fadeSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) backwards;
  position: relative;
}

@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.minimal-article-card:hover {
  transform: translateY(-8px);
  border-color: #09090b;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.08);
}

.card-thumb-frame {
  width: 100%;
  height: 200px;
  overflow: hidden;
  position: relative;
  background: #09090b;
}

.card-img-motion {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.minimal-article-card:hover .card-img-motion {
  transform: scale(1.08);
}

.category-chip {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(9, 9, 11, 0.85);
  backdrop-filter: blur(8px);
  color: #ffd54a;
  padding: 3px 10px;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 700;
  border: 1px solid rgba(255, 213, 74, 0.25);
}

.card-body-minimal {
  padding: 20px 20px 18px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.meta-row-minimal {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.74rem;
  color: #71717a;
  font-weight: 600;
  margin-bottom: 8px;
}

.dot-sep {
  color: #d4d4d8;
}

.card-title-minimal {
  font-size: 1.05rem;
  font-weight: 800;
  line-height: 1.5;
  color: #09090b;
  margin: 0 0 16px 0;
  transition: color 0.2s ease;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.minimal-article-card:hover .card-title-minimal {
  color: #b45309;
}

.card-footer-motion {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 14px;
  border-top: 1px solid #f4f4f5;
  color: #09090b;
  font-size: 0.8rem;
  font-weight: 700;
}

.arrow-motion-bubble {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #f4f4f5;
  display: grid;
  place-items: center;
  transition: all 0.25s ease;
}

.minimal-article-card:hover .arrow-motion-bubble {
  background: #09090b;
  color: #ffd54a;
  transform: translateX(-4px);
}

/* Bottom Action Link */
.articles-bottom-action {
  text-align: center;
  margin-top: 36px;
}

.btn-explore-articles {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: #ffffff;
  color: #09090b;
  border: 1px solid #e4e4e7;
  padding: 10px 24px;
  border-radius: 9999px;
  font-size: 0.86rem;
  font-weight: 700;
  text-decoration: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
  transition: all 0.25s ease;
}

.arrow-glide {
  transition: transform 0.25s ease;
}

.btn-explore-articles:hover {
  background: #09090b;
  color: #ffd54a;
  border-color: #09090b;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.btn-explore-articles:hover .arrow-glide {
  transform: translateX(-4px);
}

/* Responsive */
@media (max-width: 1024px) {
  .minimal-articles-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .articles-minimal-section {
    padding: 44px 0;
  }

  .minimal-articles-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .card-thumb-frame {
    height: 180px;
  }

  .card-body-minimal {
    padding: 16px 16px 14px;
  }

  .section-title-minimal {
    font-size: clamp(1.28rem, 5.2vw, 1.65rem);
    line-height: 1.34;
  }

  .section-desc-minimal {
    font-size: 0.86rem;
    line-height: 1.7;
  }

  .card-title-minimal {
    font-size: 1.02rem;
  }

  .btn-explore-articles {
    width: 100%;
    justify-content: space-between;
    font-size: 0.82rem;
    padding: 8px 18px;
    min-height: 44px;
  }
}

@media (max-width: 480px) {
  .articles-minimal-section {
    padding: 32px 0;
  }

  .card-thumb-frame {
    height: 160px;
  }

  .section-title-minimal {
    font-size: clamp(1.18rem, 4.8vw, 1.4rem);
  }

  .section-desc-minimal {
    font-size: 0.8rem;
    line-height: 1.65;
  }

  .card-title-minimal {
    font-size: 0.96rem;
  }

  .btn-explore-articles {
    font-size: 0.78rem;
    min-height: 42px;
  }
}
</style>

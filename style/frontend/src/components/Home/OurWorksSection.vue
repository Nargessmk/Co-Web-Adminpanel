<template>
  <section class="section-spacing" id="sec-projects">
    <div class="container">
      <!-- Section Head -->
      <div class="section-head">
        <div class="section-tag">
          <span class="tag-dot"></span>
          <span>{{ settings.works_eyebrow || 'پروژه‌های شاخص' }}</span>
        </div>
        <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
          <h2 class="section-title">{{ settings.works_title || 'معماری سیستم‌های پرترافیک و مقیاس‌پذیر' }}</h2>
          <q-btn
            v-if="isAdmin"
            class="section-edit-btn"
            round
            dense
            size="sm"
            unelevated
            color="dark"
            icon="edit"
            @click="openMasterEditor('projects')"
          >
            <q-tooltip>ویرایش عنوان و توضیحات پروژه‌ها</q-tooltip>
          </q-btn>
          <q-btn
            v-if="isAdmin"
            class="section-edit-btn"
            round
            dense
            size="sm"
            unelevated
            color="dark"
            icon="settings"
            to="/admin/products"
          >
            <q-tooltip>مدیریت پروژه‌ها (محصولات سازمانی) در پنل ادمین</q-tooltip>
          </q-btn>
        </div>
        <p class="section-desc">
          {{ settings.works_description || 'سامانه‌های استراتژیک ملی و سازمانی که با تکیه بر پایداری، سرعت و بالاترین استانداردهای مهندسی نرم‌افزار خلق شده‌اند.' }}
        </p>
      </div>

      <!-- Editorial List -->
      <div class="projects-editorial-list">
        <article
          v-for="(item, index) in displayProjects"
          :key="`${item.title}-${index}`"
          class="project-showcase-item"
          :class="{ reverse: index % 2 === 1 }"
        >
          <!-- Info Column -->
          <div class="project-showcase-info">
            <div class="project-meta-top">
              <span class="project-category-tag">{{ item.category }}</span>
            </div>

            <h3 class="project-showcase-title">
              <router-link v-if="item.link && item.link.startsWith('/')" :to="item.link" class="project-title-link">
                {{ item.title }}
              </router-link>
              <a v-else-if="item.link" :href="item.link" class="project-title-link">
                {{ item.title }}
              </a>
              <span v-else>{{ item.title }}</span>
            </h3>

            <p class="project-showcase-desc">{{ item.description }}</p>

            <div v-if="item.metrics && item.metrics.length" class="project-metrics-row">
              <div
                v-for="(metric, mIdx) in item.metrics"
                :key="mIdx"
                class="project-metric-pill"
              >
                <span class="metric-accent-dot"></span>
                <span class="metric-pill-val">{{ metric.val }}</span>
                <span class="metric-pill-lbl">{{ metric.lbl }}</span>
              </div>
            </div>

            <div v-if="item.tags && item.tags.length" class="project-stack-tags">
              <span v-for="(tag, tIdx) in item.tags" :key="tIdx" class="stack-tag">{{ tag }}</span>
            </div>

            <div class="project-action-wrap">
              <router-link
                v-if="item.link && item.link.startsWith('/')"
                :to="item.link"
                class="btn-pill btn-pill-dark"
              >
                <span class="btn-text">بررسی معماری پروژه</span>
                <span class="btn-icon-bubble">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                </span>
              </router-link>
              <a
                v-else
                :href="item.link || '#sec-contact'"
                class="btn-pill btn-pill-dark"
              >
                <span class="btn-text">بررسی معماری پروژه</span>
                <span class="btn-icon-bubble">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                </span>
              </a>
            </div>
          </div>

          <!-- Media Column -->
          <div class="project-showcase-media">
            <div class="project-media-frame">
              <router-link v-if="item.link && item.link.startsWith('/')" :to="item.link" class="project-media-link">
                <img :src="item.image" :alt="item.title" loading="lazy" />
              </router-link>
              <a v-else-if="item.link" :href="item.link" class="project-media-link">
                <img :src="item.image" :alt="item.title" loading="lazy" />
              </a>
              <img v-else :src="item.image" :alt="item.title" loading="lazy" />
              <div v-if="item.badge" class="project-media-badge">
                <span class="badge-status-dot"></span>
                <span>{{ item.badge }}</span>
              </div>
            </div>
          </div>
        </article>
      </div>

      <!-- View All Projects CTA Link -->
      <div class="projects-view-all-wrap">
        <router-link to="/projects" class="btn-pill btn-pill-yellow btn-view-all-projects">
          <span class="btn-text">مشاهده همه پروژه‌ها</span>
          <span class="btn-icon-bubble">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
          </span>
        </router-link>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from 'src/composables/useAuth'
import { useHomeContent } from 'src/composables/useHomeContent'
import { useMasterEditor, DEFAULT_PROJECTS } from 'src/composables/useMasterEditor'
import api from 'src/services/api'

const { isAdmin } = useAuth()
const { settings } = useHomeContent()
const { openMasterEditor } = useMasterEditor()

const formatNum = (num) => {
  const f = ['۰۰', '۰۱', '۰۲', '۰۳', '۰۴', '۰۵', '۰۶', '۰۷', '۰۸', '۰۹']
  return f[num] || `۰${num}`
}

const backendProducts = ref([])

async function loadProductsFromBackend () {
  try {
    const res = await api.get('/api/products', { params: { limit: 12 } })
    const items = res?.data?.data || []
    if (items.length) {
      backendProducts.value = items.map((p, idx) => {
        let metrics = []
        if (p.metrics_json) {
          try {
            metrics = typeof p.metrics_json === 'string' ? JSON.parse(p.metrics_json) : p.metrics_json
          } catch {}
        }
        let tags = []
        if (p.tags_json) {
          try {
            tags = typeof p.tags_json === 'string' ? JSON.parse(p.tags_json) : p.tags_json
          } catch {}
        }

        return {
          id: p.id,
          num: formatNum(idx + 1),
          title: p.title,
          category: p.category_name || 'سامانه‌های ابری',
          description: p.short_description || p.description?.replace(/<[^>]+>/g, '') || '',
          metrics: Array.isArray(metrics) ? metrics : [],
          tags: Array.isArray(tags) ? tags : [],
          image: p.image_url || '/uploads/home/contact-datacenter.jpg',
          badge: p.badge || (p.is_featured ? 'پروژه شاخص ملی' : ''),
          link: p.url || `/products/${p.slug}`,
        }
      })
    }
  } catch (err) {
    console.error('Failed to load products from backend in OurWorksSection:', err)
  }
}

onMounted(() => {
  loadProductsFromBackend()
})

// Limit displayed projects to maximum 3 on the home page
const displayProjects = computed(() => {
  const source = backendProducts.value.length ? backendProducts.value : DEFAULT_PROJECTS
  return source.slice(0, 3)
})
</script>

<style scoped>
/* ==========================================================================
   SECTION 3: PROJECTS (Design from index.html)
   ========================================================================== */
.section-spacing {
  padding: 60px 0;
  position: relative;
  direction: rtl;
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

.projects-editorial-list {
  display: flex;
  flex-direction: column;
  gap: 36px;
}

.project-showcase-item {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: var(--radius-bento, 28px);
  padding: 42px 48px;
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 48px;
  align-items: center;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease, border-color 0.3s ease;
}

.project-showcase-item:hover {
  transform: translateY(-4px);
  border-color: #000000;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.05);
}

.project-showcase-item.reverse {
  grid-template-columns: 0.85fr 1.15fr;
}

.project-showcase-item.reverse .project-showcase-info {
  order: 2;
}

.project-showcase-item.reverse .project-showcase-media {
  order: 1;
}

.project-showcase-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: right;
}

.project-meta-top {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}

.project-num {
  font-family: var(--font-fa, 'Estedad', sans-serif);
  font-size: 2.2rem;
  font-weight: 900;
  color: #0a0a0a;
  line-height: 1;
  letter-spacing: -0.04em;
}

.project-category-tag {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-dark-muted, #737373);
  padding: 4px 12px;
  background: var(--bg-light, #f7f7f7);
  border-radius: var(--radius-pill, 9999px);
  border: 1px solid var(--border-light, #e5e5e5);
}

.project-showcase-title {
  font-size: 1.45rem;
  font-weight: 900;
  line-height: 1.4;
  margin-bottom: 14px;
  color: var(--text-dark, #0a0a0a);
}

.project-showcase-desc {
  font-size: 0.94rem;
  color: var(--text-dark-dim, #4a4a4a);
  line-height: 1.85;
  margin-bottom: 24px;
}

.project-metrics-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.project-metric-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: var(--radius-pill, 9999px);
  font-size: 0.82rem;
}

.metric-accent-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--yellow, #ffcc00);
}

.metric-pill-val {
  font-weight: 900;
  color: #0a0a0a;
}

.metric-pill-lbl {
  color: var(--text-dark-muted, #737373);
  font-weight: 600;
}

.project-stack-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 28px;
}

.stack-tag {
  font-family: var(--font-en, 'Outfit', sans-serif);
  font-size: 0.74rem;
  font-weight: 700;
  padding: 4px 12px;
  background: #f2f2f2;
  border-radius: 6px;
  color: #2b2b2b;
}

.project-action-wrap {
  margin-top: 4px;
}

.project-showcase-media {
  position: relative;
  width: 100%;
}

.project-media-frame {
  width: 100%;
  height: 330px;
  border-radius: 22px;
  overflow: hidden;
  position: relative;
  background: #0a0a0a;
  border: 1px solid var(--border-light, #e5e5e5);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.06);
}

.project-media-link {
  display: block;
  width: 100%;
  height: 100%;
  text-decoration: none;
}

.project-media-frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.project-showcase-item:hover .project-media-frame img {
  transform: scale(1.05);
}

.project-media-badge {
  position: absolute;
  bottom: 16px;
  right: 16px;
  background: rgba(10, 10, 10, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #ffffff;
  padding: 6px 14px;
  border-radius: var(--radius-pill, 9999px);
  font-size: 0.76rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.badge-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.3);
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

.project-title-link {
  color: inherit;
  text-decoration: none;
  transition: color 0.2s ease;
}

.project-title-link:hover {
  color: var(--yellow, #ffcc00);
}

.projects-view-all-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 48px;
}

.btn-view-all-projects {
  padding: 8px 26px 8px 10px;
  font-size: 0.94rem;
  font-weight: 800;
  box-shadow: 0 4px 20px rgba(255, 204, 0, 0.32);
}

@media (max-width: 1024px) {
  .project-showcase-item {
    grid-template-columns: 1fr;
    gap: 32px;
    padding: 34px 28px;
  }
  .project-showcase-item.reverse {
    grid-template-columns: 1fr;
  }
  .project-showcase-item .project-showcase-info,
  .project-showcase-item.reverse .project-showcase-info {
    order: 2;
  }
  .project-showcase-item .project-showcase-media,
  .project-showcase-item.reverse .project-showcase-media {
    order: 1;
  }
  .project-media-frame {
    height: 280px;
  }
}

@media (max-width: 768px) {
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

  .projects-editorial-list {
    gap: 20px;
  }

  /* Refined, modern mobile card architecture */
  .project-showcase-item,
  .project-showcase-item.reverse {
    display: flex;
    flex-direction: column;
    padding: 16px;
    border-radius: 22px;
    gap: 16px;
    border: 1px solid var(--border-light, #e5e5e5);
    background: #ffffff;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03);
    overflow: hidden;
  }

  .project-showcase-item .project-showcase-media,
  .project-showcase-item.reverse .project-showcase-media {
    order: 1;
    width: 100%;
  }

  .project-showcase-item .project-showcase-info,
  .project-showcase-item.reverse .project-showcase-info {
    order: 2;
    width: 100%;
    padding: 0 4px;
    align-items: stretch;
  }

  .project-media-frame {
    width: 100%;
    height: auto;
    aspect-ratio: 16 / 9.5;
    min-height: 180px;
    max-height: 240px;
    border-radius: 16px;
    border: 1px solid rgba(0, 0, 0, 0.06);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
    display: block;
    position: relative;
    overflow: hidden;
  }

  .project-media-frame img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .project-media-badge {
    bottom: 10px;
    right: 10px;
    padding: 4px 10px;
    font-size: 0.68rem;
    border-radius: var(--radius-pill, 9999px);
    background: rgba(10, 10, 10, 0.82);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
  }

  .badge-status-dot {
    width: 5px;
    height: 5px;
  }

  .project-meta-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    margin-bottom: 10px;
  }

  .project-num {
    font-size: 1.35rem;
    color: #94a3b8;
    line-height: 1;
  }

  .project-category-tag {
    font-size: 0.72rem;
    padding: 3px 10px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    color: #475569;
  }

  .project-showcase-title {
    font-size: 1.12rem;
    line-height: 1.42;
    margin-bottom: 8px;
    color: var(--text-dark, #0a0a0a);
  }

  .project-showcase-desc {
    font-size: 0.82rem;
    line-height: 1.7;
    margin-bottom: 14px;
    color: var(--text-dark-dim, #4b5563);
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .project-metrics-row {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 12px;
    width: 100%;
  }

  .project-metric-pill {
    padding: 4px 10px;
    font-size: 0.72rem;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: var(--radius-pill, 9999px);
  }

  .metric-accent-dot {
    width: 5px;
    height: 5px;
  }

  .project-stack-tags {
    display: flex;
    align-items: center;
    gap: 5px;
    flex-wrap: wrap;
    margin-bottom: 18px;
    width: 100%;
  }

  .stack-tag {
    font-size: 0.66rem;
    padding: 3px 8px;
    border-radius: 6px;
    background: #f1f5f9;
    color: #334155;
  }

  .project-action-wrap {
    width: 100%;
    margin-top: 4px;
  }

  .project-action-wrap .btn-pill {
    width: 100%;
    justify-content: space-between;
    font-size: 0.82rem;
    padding: 6px 18px 6px 6px;
    min-height: 44px;
  }

  .projects-view-all-wrap {
    margin-top: 28px;
    width: 100%;
  }

  .btn-view-all-projects {
    width: 100%;
    justify-content: space-between;
    font-size: 0.85rem;
    padding: 8px 20px 8px 8px;
    min-height: 46px;
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

  .projects-editorial-list {
    gap: 16px;
  }

  .project-showcase-item,
  .project-showcase-item.reverse {
    padding: 14px;
    border-radius: 20px;
    gap: 12px;
  }

  .project-media-frame {
    border-radius: 14px;
    min-height: 160px;
  }

  .project-num {
    font-size: 1.2rem;
  }

  .project-showcase-title {
    font-size: 1.05rem;
  }

  .project-showcase-desc {
    font-size: 0.78rem;
    line-height: 1.65;
    -webkit-line-clamp: 2;
  }

  .project-action-wrap .btn-pill {
    font-size: 0.78rem;
    padding: 5px 14px 5px 5px;
    min-height: 42px;
  }

  .btn-view-all-projects {
    font-size: 0.8rem;
    min-height: 44px;
  }
}
</style>

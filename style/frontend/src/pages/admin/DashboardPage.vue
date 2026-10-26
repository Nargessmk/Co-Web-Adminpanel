<template>
  <div class="tech-dashboard-view">
    <!-- Top Stats Bento Grid -->
    <div class="stats-bento-grid">
      <div
        v-for="(stat, i) in stats"
        :key="stat.label"
        class="stat-bento-card"
        :style="{ animationDelay: i * 0.08 + 's' }"
      >
        <div class="stat-top-row">
          <div class="stat-icon-bubble" :class="stat.theme">
            <q-icon :name="stat.icon" size="22px" />
          </div>
          <span class="stat-status-pill">
            <span class="pill-dot"></span>
            <span>فعال</span>
          </span>
        </div>

        <div class="stat-main-figure">
          <span class="stat-big-number">{{ stat.value }}</span>
          <span class="stat-card-label">{{ stat.label }}</span>
        </div>
      </div>
    </div>

    <!-- Main Content Dual Bento Grid -->
    <div class="bento-two-col-grid">
      <!-- Recent Consultations Card -->
      <div class="bento-section-card">
        <div class="bento-card-header">
          <div class="header-title-box">
            <span class="header-indicator-dot"></span>
            <h3>درخواست‌های اخیر مشاوره</h3>
          </div>
          <router-link to="/admin/consultations" class="view-all-pill-link">
            <span>مشاهده همه</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </router-link>
        </div>

        <div class="bento-card-body">
          <div v-if="consultations.length === 0" class="tech-empty-state">
            <div class="empty-icon-wrap">
              <q-icon name="support_agent" size="36px" />
            </div>
            <span>هنوز درخواست مشاوره‌ای ثبت نشده است</span>
          </div>

          <TransitionGroup name="list-fade" tag="div" class="tech-items-stack">
            <div v-for="c in consultations" :key="c.id" class="tech-list-row">
              <div class="user-avatar-initial-box">
                <q-icon name="person" size="18px" />
              </div>
              <div class="row-text-info">
                <strong class="row-primary-title">{{ c.full_name }}</strong>
                <span class="row-subtitle-text">{{ c.subject || c.message?.substring(0, 45) || 'بدون موضوع' }}</span>
              </div>
              <span class="tech-status-pill" :class="c.status">
                {{ statusLabel(c.status) }}
              </span>
            </div>
          </TransitionGroup>
        </div>
      </div>

      <!-- Recent Products Card -->
      <div class="bento-section-card">
        <div class="bento-card-header">
          <div class="header-title-box">
            <span class="header-indicator-dot"></span>
            <h3>محصولات و پروژه‌های ثبت‌شده</h3>
          </div>
          <router-link to="/admin/products" class="view-all-pill-link">
            <span>مشاهده همه</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </router-link>
        </div>

        <div class="bento-card-body">
          <div v-if="products.length === 0" class="tech-empty-state">
            <div class="empty-icon-wrap">
              <q-icon name="inventory_2" size="36px" />
            </div>
            <span>هیچ محصولی در سیستم ثبت نشده است</span>
          </div>

          <TransitionGroup name="list-fade" tag="div" class="tech-items-stack">
            <div v-for="p in products" :key="p.id" class="tech-list-row">
              <img v-if="p.image_url" :src="p.image_url" class="product-thumb-img" loading="lazy" decoding="async" />
              <div v-else class="product-thumb-placeholder">
                <q-icon name="image" size="18px" />
              </div>
              <div class="row-text-info">
                <strong class="row-primary-title">{{ p.title }}</strong>
                <span class="row-subtitle-text">{{ p.category_name || 'بدون دسته‌بندی' }}</span>
              </div>
              <span class="product-active-pill" :class="{ active: p.is_active }">
                <span class="pill-dot"></span>
                <span>{{ p.is_active ? 'فعال' : 'غیرفعال' }}</span>
              </span>
            </div>
          </TransitionGroup>
        </div>
      </div>
    </div>

    <!-- Quick Actions Card -->
    <div class="quick-actions-bento">
      <div class="quick-actions-header">
        <div class="header-title-box">
          <span class="header-indicator-dot"></span>
          <h3>دسترسی سریع به ماژول‌های سیستم</h3>
        </div>
        <span class="quick-subtitle">میانبرهای کاربردی جهت مدیریت محتوا و اسناد</span>
      </div>

      <div class="quick-actions-grid">
        <router-link to="/admin/products" class="quick-bento-btn">
          <div class="btn-icon-circle">
            <q-icon name="add_box" size="22px" />
          </div>
          <span>افزودن محصول</span>
        </router-link>

        <router-link to="/admin/categories" class="quick-bento-btn">
          <div class="btn-icon-circle">
            <q-icon name="create_new_folder" size="22px" />
          </div>
          <span>افزودن دسته</span>
        </router-link>

        <router-link to="/admin/catalogs" class="quick-bento-btn">
          <div class="btn-icon-circle">
            <q-icon name="folder_open" size="22px" />
          </div>
          <span>کاتالوگ‌ها</span>
        </router-link>

        <router-link to="/admin/consultations" class="quick-bento-btn">
          <div class="btn-icon-circle">
            <q-icon name="support_agent" size="22px" />
          </div>
          <span>درخواست‌ها</span>
        </router-link>

        <router-link to="/admin/team" class="quick-bento-btn">
          <div class="btn-icon-circle">
            <q-icon name="groups" size="22px" />
          </div>
          <span>تیم کهکشان</span>
        </router-link>

        <router-link to="/admin/solutions" class="quick-bento-btn">
          <div class="btn-icon-circle">
            <q-icon name="menu_book" size="22px" />
          </div>
          <span>راهکارها</span>
        </router-link>

        <router-link to="/admin/settings" class="quick-bento-btn">
          <div class="btn-icon-circle">
            <q-icon name="settings" size="22px" />
          </div>
          <span>تنظیمات</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from 'src/services/api'

const stats = ref([
  { label: 'محصولات و پروژه‌ها', value: 0, icon: 'inventory_2', theme: 'theme-yellow' },
  { label: 'دسته‌بندی‌های فعال', value: 0, icon: 'category', theme: 'theme-dark' },
  { label: 'درخواست‌های مشاوره', value: 0, icon: 'support_agent', theme: 'theme-neutral' },
])

const products = ref([])
const consultations = ref([])

function statusLabel (s) {
  const map = {
    new: 'جدید',
    reviewed: 'بررسی شده',
    contacted: 'تماس گرفته شده',
    closed: 'بسته شده'
  }
  return map[s] || s
}

onMounted(async () => {
  try {
    const [pRes, cRes, catRes] = await Promise.all([
      api.get('/api/products/admin/all?limit=5'),
      api.get('/api/consultations/admin?limit=5'),
      api.get('/api/categories'),
    ])
    products.value = pRes.data.data || []
    consultations.value = cRes.data.data || []
    stats.value[0].value = pRes.data.pagination?.total || 0
    stats.value[1].value = catRes.data.data?.length || 0
    stats.value[2].value = cRes.data.pagination?.total || 0
  } catch (e) {
    if (e.response?.status !== 401) {
      console.error('Dashboard load error:', e)
    }
  }
})
</script>

<style scoped>
/* ==========================================================================
   DASHBOARD (Matching New Tech Aesthetic)
   ========================================================================== */
.tech-dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 28px;
  animation: dashboardFadeIn 0.5s ease both;
}

@keyframes dashboardFadeIn {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

/* --------------------------------------------------------------------------
   Stats Bento Grid
   -------------------------------------------------------------------------- */
.stats-bento-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-bento-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 24px;
  padding: 26px 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-bento-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.07);
}

.stat-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-icon-bubble {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-bubble.theme-yellow {
  background: var(--yellow, #fed72b);
  color: #0a0a0a;
  box-shadow: 0 4px 14px rgba(254, 215, 43, 0.35);
}

.stat-icon-bubble.theme-dark {
  background: #0a0a0a;
  color: #ffffff;
}

.stat-icon-bubble.theme-neutral {
  background: rgba(0, 0, 0, 0.06);
  color: #0a0a0a;
}

.stat-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: var(--radius-pill, 9999px);
  background: rgba(0, 0, 0, 0.04);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted, #71717a);
}

.pill-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
}

.stat-main-figure {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-big-number {
  font-family: 'Outfit', 'Estedad', sans-serif;
  font-size: 38px;
  font-weight: 800;
  color: var(--text-dark, #0a0a0a);
  line-height: 1.1;
  letter-spacing: -1px;
}

.stat-card-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted, #71717a);
}

/* --------------------------------------------------------------------------
   Dual Column Grid (Consultations + Products)
   -------------------------------------------------------------------------- */
.bento-two-col-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.bento-section-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.bento-card-header {
  padding: 22px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-title-box {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--yellow, #fed72b);
}

.header-title-box h3 {
  font-size: 15px;
  font-weight: 800;
  color: var(--text-dark, #0a0a0a);
  margin: 0;
}

.view-all-pill-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: var(--radius-pill, 9999px);
  background: rgba(0, 0, 0, 0.04);
  font-size: 12px;
  font-weight: 700;
  color: var(--text-dark, #0a0a0a);
  text-decoration: none;
  transition: all 0.2s ease;
}

.view-all-pill-link:hover {
  background: var(--yellow, #fed72b);
}

.bento-card-body {
  padding: 12px 16px;
  flex: 1;
}

.tech-empty-state {
  padding: 48px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #a1a1aa;
  font-size: 13px;
  font-weight: 600;
}

.empty-icon-wrap {
  width: 60px;
  height: 60px;
  border-radius: 18px;
  background: rgba(0, 0, 0, 0.03);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #d4d4d8;
}

.tech-items-stack {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tech-list-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  border-radius: 16px;
  background: #fbfbfb;
  border: 1px solid rgba(0, 0, 0, 0.04);
  transition: all 0.25s ease;
}

.tech-list-row:hover {
  background: #ffffff;
  border-color: rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.user-avatar-initial-box {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: #0a0a0a;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.product-thumb-img {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  object-fit: cover;
  flex-shrink: 0;
}

.product-thumb-placeholder {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a1a1aa;
  flex-shrink: 0;
}

.row-text-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.row-primary-title {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text-dark, #0a0a0a);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-subtitle-text {
  font-size: 11.5px;
  color: var(--text-muted, #71717a);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tech-status-pill {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: var(--radius-pill, 9999px);
  font-weight: 700;
  white-space: nowrap;
}

.tech-status-pill.new { background: #fef08a; color: #854d0e; }
.tech-status-pill.reviewed { background: #e0e7ff; color: #4338ca; }
.tech-status-pill.contacted { background: #dcfce7; color: #15803d; }
.tech-status-pill.closed { background: #f4f4f5; color: #71717a; }

.product-active-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  padding: 4px 10px;
  border-radius: var(--radius-pill, 9999px);
  background: #fee2e2;
  color: #b91c1c;
  font-weight: 700;
}

.product-active-pill .pill-dot {
  background: #ef4444;
}

.product-active-pill.active {
  background: #dcfce7;
  color: #15803d;
}

.product-active-pill.active .pill-dot {
  background: #22c55e;
}

/* --------------------------------------------------------------------------
   Quick Actions Bento
   -------------------------------------------------------------------------- */
.quick-actions-bento {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 24px;
  padding: 26px 28px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.quick-actions-header {
  margin-bottom: 20px;
}

.quick-subtitle {
  font-size: 12.5px;
  color: var(--text-muted, #71717a);
  margin-top: 4px;
  display: block;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 14px;
}

.quick-bento-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 18px 12px;
  border-radius: 18px;
  background: #fbfbfb;
  border: 1px solid rgba(0, 0, 0, 0.06);
  color: var(--text-dark, #0a0a0a);
  text-decoration: none;
  font-size: 12.5px;
  font-weight: 700;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  text-align: center;
}

.btn-icon-circle {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.04);
  color: #0a0a0a;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s ease;
}

.quick-bento-btn:hover {
  background: #0a0a0a;
  color: #ffffff;
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #0a0a0a;
}

.quick-bento-btn:hover .btn-icon-circle {
  background: var(--yellow, #fed72b);
  color: #0a0a0a;
}

/* List Transitions */
.list-fade-enter-active,
.list-fade-leave-active {
  transition: all 0.3s ease;
}

.list-fade-enter-from {
  opacity: 0;
  transform: translateX(12px);
}

.list-fade-leave-to {
  opacity: 0;
  transform: translateX(-12px);
}

/* Responsive */
@media (max-width: 1100px) {
  .quick-actions-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 900px) {
  .tech-dashboard-view {
    gap: 20px;
  }
  .stats-bento-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }
  .bento-two-col-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }
  .quick-actions-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 600px) {
  .quick-actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .stat-bento-card {
    padding: 18px 16px;
  }
  .quick-actions-bento {
    padding: 18px 16px;
  }
}

@media (max-width: 480px) {
  .tech-dashboard-view {
    gap: 14px;
  }
  .stat-bento-card {
    padding: 14px 14px;
    border-radius: 16px;
    gap: 10px;
  }
  .stat-big-number {
    font-size: 28px;
  }
  .stat-card-label {
    font-size: 12px;
  }
  .stat-icon-bubble {
    width: 40px;
    height: 40px;
    border-radius: 10px;
  }
  .bento-section-card {
    border-radius: 16px;
  }
  .bento-card-header {
    padding: 14px 14px;
  }
  .header-title-box h3 {
    font-size: 13.5px;
  }
  .tech-list-row {
    padding: 10px 10px;
    gap: 10px;
  }
  .quick-actions-bento {
    padding: 16px 14px;
    border-radius: 16px;
  }
  .quick-actions-header {
    margin-bottom: 14px;
  }
  .quick-bento-btn {
    padding: 14px 8px;
    font-size: 11.5px;
    gap: 8px;
  }
  .btn-icon-circle {
    width: 38px;
    height: 38px;
    border-radius: 10px;
  }
}

@media (max-width: 320px) {
  .tech-dashboard-view {
    gap: 10px;
  }
  .stat-bento-card {
    padding: 12px 10px;
    border-radius: 14px;
  }
  .stat-big-number {
    font-size: 24px;
  }
  .bento-card-header {
    padding: 10px 10px;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .tech-list-row {
    padding: 8px 8px;
    gap: 8px;
  }
  .user-avatar-initial-box,
  .product-thumb-img,
  .product-thumb-placeholder {
    width: 32px;
    height: 32px;
    border-radius: 8px;
  }
  .row-primary-title {
    font-size: 12px;
  }
  .row-subtitle-text {
    font-size: 10.5px;
  }
  .tech-status-pill,
  .product-active-pill {
    font-size: 9.5px;
    padding: 2px 5px;
  }
  .quick-actions-bento {
    padding: 12px 8px;
  }
  .quick-actions-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
  }
  .quick-bento-btn {
    padding: 10px 4px;
    font-size: 10.5px;
    gap: 6px;
    border-radius: 10px;
  }
  .btn-icon-circle {
    width: 32px;
    height: 32px;
  }
}
</style>

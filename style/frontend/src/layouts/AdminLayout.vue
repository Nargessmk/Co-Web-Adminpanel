<template>
  <div class="admin-layout-root">
    <!-- Mobile overlay -->
    <div class="mobile-overlay" v-if="mobileOpen" @click="mobileOpen = false"></div>

    <!-- Tech Sidebar -->
    <aside class="tech-sidebar" :class="{ collapsed: sidebarCollapsed, 'mobile-open': mobileOpen }">
      <!-- Logo & Brand Area -->
      <div class="sidebar-brand-strip">
        <div class="brand-logo-badge">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
          </svg>
        </div>
        <transition name="fade">
          <div v-if="!sidebarCollapsed" class="brand-title-wrap">
            <span class="brand-name">کهکشان هوشمند</span>
            <div class="brand-sub-badge">
              <span class="status-live-dot"></span>
              <span>پنل مدیریت ابری</span>
            </div>
          </div>
        </transition>
        <button
          class="sidebar-collapse-btn"
          @click="sidebarCollapsed = !sidebarCollapsed"
          :title="sidebarCollapsed ? 'باز کردن منو' : 'جمع کردن منو'"
        >
          <q-icon :name="sidebarCollapsed ? 'chevron_left' : 'chevron_right'" size="18px" />
        </button>
        <button
          class="sidebar-mobile-close-btn"
          @click="mobileOpen = false"
          title="بستن منو"
          aria-label="بستن منوی ناوبری"
        >
          <q-icon name="close" size="18px" />
        </button>
      </div>

      <!-- Navigation Links -->
      <nav class="sidebar-nav-list">
        <div class="nav-section-group">
          <span v-if="!sidebarCollapsed" class="nav-section-title">مدیریت محتوا و داده‌ها</span>
          <router-link
            v-for="(item, i) in mainNav"
            :key="item.path"
            :to="item.path"
            class="tech-nav-item"
            :class="{ active: isActive(item.path) }"
            :style="{ animationDelay: i * 0.04 + 's' }"
            @click="mobileOpen = false"
          >
            <div class="nav-icon-bubble" :class="{ active: isActive(item.path) }">
              <q-icon :name="item.icon" size="18px" />
            </div>
            <transition name="fade">
              <span v-if="!sidebarCollapsed" class="nav-item-label">{{ item.label }}</span>
            </transition>
            <transition name="fade">
              <span v-if="!sidebarCollapsed && item.badge" class="nav-item-badge">{{ item.badge }}</span>
            </transition>
          </router-link>
        </div>

        <div class="nav-section-group">
          <span v-if="!sidebarCollapsed" class="nav-section-title">تنظیمات و ابزارها</span>
          <router-link
            v-for="(item, i) in systemNav"
            :key="item.path"
            :to="item.path"
            class="tech-nav-item"
            :class="{ active: isActive(item.path) }"
            @click="mobileOpen = false"
          >
            <div class="nav-icon-bubble" :class="{ active: isActive(item.path) }">
              <q-icon :name="item.icon" size="18px" />
            </div>
            <transition name="fade">
              <span v-if="!sidebarCollapsed" class="nav-item-label">{{ item.label }}</span>
            </transition>
          </router-link>
        </div>
      </nav>

      <!-- User Profile Card -->
      <div class="sidebar-user-footer">
        <div class="user-pill-card" v-if="!sidebarCollapsed" @click="goToProfile" style="cursor: pointer;" title="مشاهده و ویرایش مشخصات حساب کاربری">
          <div class="user-avatar-frame">
            <img v-if="admin?.avatar" :src="admin.avatar" alt="Avatar" />
            <q-icon v-else name="person" size="20px" class="user-avatar-icon" />
          </div>
          <div class="user-meta-info">
            <span class="user-display-name">{{ admin?.full_name || admin?.username || 'مدیر سیستم' }}</span>
            <span class="user-role-label">دسترسی سطح اول</span>
          </div>
          <button class="user-logout-action" @click.stop="handleLogout" title="خروج از حساب">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
          </button>
        </div>
        <button v-else class="user-logout-collapsed" @click="handleLogout" title="خروج">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
        </button>
      </div>
    </aside>

    <!-- Main Workspace -->
    <main class="tech-main-workspace" :style="{ marginRight: sidebarCollapsed ? '82px' : '280px' }">
      <!-- Minimalist Top Bar -->
      <header class="workspace-topbar">
        <div class="topbar-right-block">
          <button class="mobile-menu-trigger" @click="mobileOpen = !mobileOpen" aria-label="منو">
            <q-icon name="menu" size="20px" />
          </button>
          <div class="page-title-badge">
            <span class="page-title-dot"></span>
            <h1 class="current-page-heading">{{ currentPageTitle }}</h1>
          </div>
        </div>

        <div class="topbar-left-block">
          <!-- View Site Button -->
          <router-link to="/" target="_blank" class="topbar-pill-btn">
            <span>مشاهده وب‌سایت</span>
            <span class="topbar-pill-bubble">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="7" y1="17" x2="17" y2="7"></line>
                <polyline points="7 7 17 7 17 17"></polyline>
              </svg>
            </span>
          </router-link>

          <!-- Profile Badge with Interactive Submenu -->
          <div class="profile-trigger-wrap">
            <button
              type="button"
              class="profile-topbar-btn"
              aria-label="پروفایل و منوی حساب کاربری"
              title="پروفایل و تنظیمات کاربری"
            >
              <div class="topbar-avatar-bubble">
                <img v-if="admin?.avatar" :src="admin.avatar" alt="Avatar" />
                <q-icon v-else name="person" size="20px" class="user-avatar-icon" />
              </div>
              <span class="profile-online-dot"></span>
              <q-icon name="expand_more" size="14px" class="profile-expand-icon" />

              <q-menu
                anchor="bottom left"
                self="top left"
                :offset="[0, 10]"
                class="admin-profile-menu-card"
                transition-show="jump-down"
                transition-hide="jump-up"
              >
                <!-- Profile Header: Clickable directly to Profile Settings -->
                <div class="menu-user-hero" @click="goToProfile" role="button" tabindex="0" title="مشاهده و ویرایش مشخصات حساب کاربری">
                  <div class="menu-avatar-wrap">
                    <img v-if="admin?.avatar" :src="admin.avatar" alt="Avatar" />
                    <q-icon v-else name="person" size="24px" class="user-avatar-icon" />
                  </div>
                  <div class="menu-user-details">
                    <div class="menu-name-row">
                      <span class="menu-user-name">{{ admin?.full_name || admin?.username || 'مدیر سیستم' }}</span>
                      <span class="menu-role-chip">{{ (admin?.roles || []).includes('admin') ? 'مدیر ارشد' : 'ادمین' }}</span>
                    </div>
                    <span class="menu-user-handle">@{{ admin?.username || 'admin' }}</span>
                  </div>
                  <q-icon name="arrow_back_ios_new" size="12px" class="menu-hero-arrow" />
                </div>

                <div class="menu-items-group">
                  <!-- 1. Profile & Account Settings -->
                  <q-item clickable v-close-popup @click="goToProfile" class="profile-sub-item">
                    <q-item-section avatar class="item-icon-box">
                      <div class="icon-bubble">
                        <q-icon name="account_circle" size="17px" />
                      </div>
                    </q-item-section>
                    <q-item-section>
                      <q-item-label class="sub-item-title">پروفایل و حساب کاربری</q-item-label>
                      <q-item-label caption class="sub-item-sub">مشخصات، نام و تصویر نمایه</q-item-label>
                    </q-item-section>
                  </q-item>

                  <!-- 2. Security & Password -->
                  <q-item clickable v-close-popup @click="goToSecurity" class="profile-sub-item">
                    <q-item-section avatar class="item-icon-box">
                      <div class="icon-bubble">
                        <q-icon name="lock" size="17px" />
                      </div>
                    </q-item-section>
                    <q-item-section>
                      <q-item-label class="sub-item-title">تغییر رمز عبور</q-item-label>
                      <q-item-label caption class="sub-item-sub">بروزرسانی گذرواژه و امنیت</q-item-label>
                    </q-item-section>
                  </q-item>

                  <!-- 3. General Settings -->
                  <q-item clickable v-close-popup @click="goToSettings" class="profile-sub-item">
                    <q-item-section avatar class="item-icon-box">
                      <div class="icon-bubble">
                        <q-icon name="tune" size="17px" />
                      </div>
                    </q-item-section>
                    <q-item-section>
                      <q-item-label class="sub-item-title">تنظیمات کلی وب‌سایت</q-item-label>
                      <q-item-label caption class="sub-item-sub">هویت سایت، فوتر و ویجت سریع</q-item-label>
                    </q-item-section>
                  </q-item>

                  <!-- 4. View Website -->
                  <q-item clickable v-close-popup to="/" target="_blank" class="profile-sub-item">
                    <q-item-section avatar class="item-icon-box">
                      <div class="icon-bubble">
                        <q-icon name="open_in_new" size="17px" />
                      </div>
                    </q-item-section>
                    <q-item-section>
                      <q-item-label class="sub-item-title">مشاهده وب‌سایت</q-item-label>
                      <q-item-label caption class="sub-item-sub">باز کردن سایت در برگه جدید</q-item-label>
                    </q-item-section>
                  </q-item>
                </div>

                <div class="menu-divider-line"></div>

                <!-- 5. Logout -->
                <div class="menu-footer-action">
                  <q-item clickable v-close-popup @click="handleLogout" class="profile-sub-item logout-item">
                    <q-item-section avatar class="item-icon-box">
                      <div class="icon-bubble logout">
                        <q-icon name="logout" size="17px" />
                      </div>
                    </q-item-section>
                    <q-item-section>
                      <q-item-label class="sub-item-title logout-label">خروج از حساب کاربری</q-item-label>
                    </q-item-section>
                  </q-item>
                </div>
              </q-menu>
            </button>
          </div>
        </div>
      </header>

      <!-- Dynamic Page Container -->
      <div class="workspace-body-container">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from 'src/composables/useAuth'

const router = useRouter()
const route = useRoute()
const { admin, logout } = useAuth()

const sidebarCollapsed = ref(false)
const mobileOpen = ref(false)

watch(() => route.path, () => {
  mobileOpen.value = false
})

const mainNav = [
  { path: '/admin', icon: 'dashboard', label: 'داشبورد مدیریت' },
  { path: '/admin/products', icon: 'inventory_2', label: 'محصولات سازمانی' },
  { path: '/admin/categories', icon: 'category', label: 'دسته‌بندی‌ها' },
  { path: '/admin/catalogs', icon: 'folder_open', label: 'کاتالوگ‌ها و اسناد' },
  { path: '/admin/consultations', icon: 'support_agent', label: 'درخواست‌های مشاوره' },
  { path: '/admin/team', icon: 'groups', label: 'تیم و متخصصین' },
  { path: '/admin/solutions', icon: 'menu_book', label: 'راهکارهای ابری' },
  { path: '/admin/media', icon: 'perm_media', label: 'مدیریت رسانه' },
]

const systemNav = [
  { path: '/admin/settings', icon: 'settings', label: 'تنظیمات کلی وب‌سایت' },
]

const currentPageTitle = computed(() => {
  const all = [...mainNav, ...systemNav]
  const item = all.find((n) => n.path === route.path)
  return item?.label || 'داشبورد'
})

function isActive (path) {
  if (path === '/admin') return route.path === '/admin'
  return route.path.startsWith(path)
}

function handleLogout () {
  logout()
  router.push('/')
}

function goToProfile () {
  router.push({ path: '/admin/settings', query: { tab: 'security' } })
}

function goToSecurity () {
  router.push({ path: '/admin/settings', query: { tab: 'security' } })
}

function goToSettings () {
  router.push({ path: '/admin/settings', query: { tab: 'identity' } })
}
</script>

<style scoped>
/* ==========================================================================
   ADMIN LAYOUT (Matching New Cloudland Aesthetic)
   ========================================================================== */
.admin-layout-root {
  display: flex;
  min-height: 100vh;
  font-family: 'Estedad', sans-serif;
  direction: rtl;
  background-color: var(--bg-canvas, #f7f7f7);
  color: var(--text-dark, #0a0a0a);
}

/* --------------------------------------------------------------------------
   Tech Sidebar
   -------------------------------------------------------------------------- */
.tech-sidebar {
  width: 280px;
  background: #0d0d0f;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  z-index: 100;
  border-left: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.25);
  transition: width 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.tech-sidebar.collapsed {
  width: 82px;
}

/* Sidebar Brand Strip */
.sidebar-brand-strip {
  padding: 22px 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  position: relative;
}

.brand-logo-badge {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: var(--yellow, #fed72b);
  color: #0a0a0a;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 14px rgba(254, 215, 43, 0.35);
}

.brand-title-wrap {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-name {
  font-size: 15px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.3px;
  white-space: nowrap;
}

.brand-sub-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #a1a1aa;
  margin-top: 2px;
  white-space: nowrap;
}

.status-live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--yellow, #fed72b);
  box-shadow: 0 0 6px rgba(254, 215, 43, 0.8);
}

.sidebar-collapse-btn {
  margin-right: auto;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: #a1a1aa;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.sidebar-collapse-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
}

/* Sidebar Navigation */
.sidebar-nav-list {
  flex: 1;
  padding: 18px 12px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
}

.sidebar-nav-list::-webkit-scrollbar {
  width: 3px;
}

.sidebar-nav-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.nav-section-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-section-title {
  font-size: 11px;
  font-weight: 700;
  color: #71717a;
  padding: 0 12px 6px;
  white-space: nowrap;
  letter-spacing: -0.2px;
}

.tech-nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 14px;
  color: #a1a1aa;
  text-decoration: none;
  font-size: 13.5px;
  font-weight: 600;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  white-space: nowrap;
  position: relative;
}

.tech-nav-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #ffffff;
}

.tech-nav-item.active {
  background: rgba(254, 215, 43, 0.1);
  color: #ffffff;
}

.tech-nav-item.active::before {
  content: '';
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 24px;
  border-radius: 4px 0 0 4px;
  background: var(--yellow, #fed72b);
  box-shadow: 0 0 10px rgba(254, 215, 43, 0.6);
}

.nav-icon-bubble {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.04);
  color: #a1a1aa;
  transition: all 0.25s ease;
}

.tech-nav-item:hover .nav-icon-bubble {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.tech-nav-item.active .nav-icon-bubble {
  background: var(--yellow, #fed72b);
  color: #0a0a0a;
  box-shadow: 0 2px 10px rgba(254, 215, 43, 0.35);
}

.nav-item-label {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-item-badge {
  background: var(--yellow, #fed72b);
  color: #0a0a0a;
  font-size: 10px;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: var(--radius-pill, 9999px);
}

/* Sidebar User Footer */
.sidebar-user-footer {
  padding: 14px 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.user-pill-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.user-avatar-frame {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--yellow, #fed72b);
  color: #0a0a0a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 800;
  overflow: hidden;
  flex-shrink: 0;
}

.user-avatar-frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-meta-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.user-display-name {
  font-size: 13px;
  font-weight: 700;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role-label {
  font-size: 11px;
  color: #71717a;
}

.user-logout-action {
  background: none;
  border: none;
  color: #71717a;
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.user-logout-action:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.user-logout-collapsed {
  width: 40px;
  height: 40px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: #71717a;
  cursor: pointer;
  transition: all 0.2s;
}

.user-logout-collapsed:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.15);
}

/* --------------------------------------------------------------------------
   Workspace & Topbar
   -------------------------------------------------------------------------- */
.tech-main-workspace {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-right 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.workspace-topbar {
  height: 72px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.07);
  padding: 0 36px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 50;
}

.topbar-right-block {
  display: flex;
  align-items: center;
  gap: 16px;
}

.mobile-menu-trigger {
  display: none;
  background: none;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  width: 36px;
  height: 36px;
  align-items: center;
  justify-content: center;
  color: var(--text-dark, #0a0a0a);
  cursor: pointer;
}

.page-title-badge {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-title-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--yellow, #fed72b);
}

.current-page-heading {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-dark, #0a0a0a);
  margin: 0;
  letter-spacing: -0.4px;
}

.topbar-left-block {
  display: flex;
  align-items: center;
  gap: 14px;
}

.topbar-pill-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 7px 14px 7px 8px;
  border-radius: var(--radius-pill, 9999px);
  background: #ffffff;
  color: var(--text-dark, #0a0a0a);
  border: 1px solid rgba(0, 0, 0, 0.12);
  text-decoration: none;
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.topbar-pill-btn:hover {
  background: #fed72b;
  color: #0a0a0b;
  border-color: #eab308;
  transform: translateY(-1px);
}

.topbar-pill-bubble {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--yellow, #fed72b);
  color: #0a0a0a;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.topbar-pill-btn:hover .topbar-pill-bubble {
  transform: rotate(-45deg);
}

.profile-trigger-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.profile-topbar-btn {
  background: transparent;
  border: none;
  padding: 2px 4px 2px 2px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  border-radius: 9999px;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
}

.profile-topbar-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.topbar-avatar-bubble {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #0a0a0a;
  color: #fed72b;
  border: 2px solid rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 14px;
  overflow: hidden;
  transition: all 0.2s ease;
  position: relative;
}

.profile-topbar-btn:hover .topbar-avatar-bubble {
  border-color: var(--yellow, #fed72b);
  box-shadow: 0 0 0 3px rgba(254, 215, 43, 0.25);
}

.topbar-avatar-bubble img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-online-dot {
  position: absolute;
  bottom: 3px;
  right: 4px;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #10b981;
  border: 2px solid #ffffff;
}

.profile-expand-icon {
  color: #71717a;
  transition: transform 0.2s ease, color 0.2s ease;
}

.profile-topbar-btn:hover .profile-expand-icon {
  color: #0a0a0a;
  transform: translateY(1px);
}

/* Workspace Container */
.workspace-body-container {
  padding: 32px 36px;
  flex: 1;
}

/* Page transitions */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.sidebar-mobile-close-btn {
  display: none;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  cursor: pointer;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  margin-right: auto;
}

.sidebar-mobile-close-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.4);
}

/* --------------------------------------------------------------------------
   Responsive Adaptations
   -------------------------------------------------------------------------- */
@media (max-width: 900px) {
  .tech-sidebar {
    transform: translateX(100%);
    width: min(280px, 86vw) !important;
    max-width: 100vw;
  }

  .tech-sidebar.mobile-open {
    transform: translateX(0);
  }

  .tech-main-workspace {
    margin-right: 0 !important;
    width: 100%;
    max-width: 100vw;
    overflow-x: hidden;
  }

  .mobile-menu-trigger {
    display: flex;
  }

  .sidebar-collapse-btn {
    display: none;
  }

  .sidebar-mobile-close-btn {
    display: flex;
  }

  .workspace-topbar {
    padding: 0 16px;
  }

  .workspace-body-container {
    padding: 18px 14px;
    width: 100%;
    max-width: 100vw;
    box-sizing: border-box;
  }

  .mobile-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    z-index: 90;
  }
}

@media (max-width: 480px) {
  .workspace-topbar {
    height: 58px;
    padding: 0 10px;
  }

  .topbar-right-block {
    gap: 8px;
    min-width: 0;
  }

  .mobile-menu-trigger {
    width: 34px;
    height: 34px;
    flex-shrink: 0;
  }

  .page-title-badge {
    gap: 6px;
    min-width: 0;
  }

  .current-page-heading {
    font-size: 13.5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 130px;
  }

  .topbar-left-block {
    gap: 8px;
    flex-shrink: 0;
  }

  .topbar-pill-btn {
    padding: 5px;
    width: 34px;
    height: 34px;
    justify-content: center;
  }

  .topbar-pill-btn span:first-child {
    display: none;
  }

  .topbar-avatar-bubble {
    width: 34px;
    height: 34px;
  }

  .workspace-body-container {
    padding: 14px 8px;
  }

  .admin-profile-menu-card {
    width: 270px !important;
    max-width: 94vw !important;
  }
}

@media (max-width: 320px) {
  .workspace-topbar {
    height: 52px;
    padding: 0 6px;
  }

  .topbar-right-block {
    gap: 6px;
  }

  .mobile-menu-trigger {
    width: 30px;
    height: 30px;
  }

  .current-page-heading {
    font-size: 12px;
    max-width: 95px;
  }

  .topbar-left-block {
    gap: 5px;
  }

  .topbar-pill-btn {
    width: 30px;
    height: 30px;
  }

  .topbar-pill-bubble {
    width: 20px;
    height: 20px;
  }

  .topbar-avatar-bubble {
    width: 30px;
    height: 30px;
  }

  .profile-expand-icon {
    display: none;
  }

  .workspace-body-container {
    padding: 10px 4px;
  }

  .admin-profile-menu-card {
    width: 250px !important;
    max-width: 96vw !important;
  }
}
</style>

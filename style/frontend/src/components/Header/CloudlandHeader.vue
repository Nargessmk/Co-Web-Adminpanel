<template>
  <!-- Backdrop for Mobile Drawer -->
  <transition name="fade">
    <div
      v-if="mobileOpen"
      class="mobile-nav-backdrop"
      @click="mobileOpen = false"
      aria-hidden="true"
    ></div>
  </transition>

  <header class="floating-header" id="main-nav">
    <router-link to="/" class="nav-brand" @click="mobileOpen = false">
      <div class="brand-mark">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
      </div>
      <span>{{ settings.site_name || 'کهکشان هوشمند' }}</span>
    </router-link>

    <nav class="desktop-nav">
      <ul class="nav-links">
        <li v-for="item in navLinks" :key="item.path">
          <component
            :is="isExternal(item.path) ? 'a' : 'router-link'"
            v-bind="linkBindings(item.path)"
            :class="{ active: isLinkActive(item.path) }"
          >
            {{ item.label }}
          </component>
        </li>
      </ul>
    </nav>

    <div class="header-cta">
      <q-btn
        v-if="isAdmin"
        round
        dense
        unelevated
        size="sm"
        icon="edit"
        color="dark"
        class="site-edit-btn"
        @click="openMasterEditor('brand')"
      >
        <q-tooltip>ویرایش هدر و برند</q-tooltip>
      </q-btn>

      <component
        :is="isExternal(button.link) ? 'a' : 'router-link'"
        v-for="button in actionButtons"
        :key="button.key"
        v-bind="linkBindings(button.link)"
        :class="['btn-pill', button.key === 'cta' ? 'btn-pill-yellow btn-pill-sm' : 'btn-pill-dark btn-pill-sm']"
      >
        <span class="btn-text">{{ button.label }}</span>
        <span class="btn-icon-bubble">
          <svg v-if="button.key === 'cta'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="M12 5l7 7-7 7"></path></svg>
          <svg v-else-if="isAdmin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path><polyline points="10 17 15 12 10 7"></polyline><line x1="15" y1="12" x2="3" y2="12"></line></svg>
        </span>
      </component>
    </div>

    <button
      class="mobile-menu-btn"
      id="mobile-menu-toggle"
      :aria-label="mobileOpen ? 'بستن منو' : 'منوی موبایل'"
      type="button"
      @click="mobileOpen = !mobileOpen"
    >
      <svg v-if="!mobileOpen" id="hamburger-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
      <svg v-else id="close-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
    </button>
  </header>

  <!-- Mobile Drawer Menu -->
  <div class="mobile-nav-drawer" :class="{ open: mobileOpen }" id="mobile-nav-drawer">
    <div class="mobile-drawer-header">
      <div class="brand-mark-sm">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
      </div>
      <span class="mobile-drawer-title">{{ settings.site_name || 'کهکشان هوشمند' }}</span>
    </div>

    <ul class="mobile-nav-links">
      <li v-for="item in navLinks" :key="item.path">
        <component
          :is="isExternal(item.path) ? 'a' : 'router-link'"
          v-bind="linkBindings(item.path)"
          class="mobile-nav-link"
          :class="{ active: isLinkActive(item.path) }"
          @click="mobileOpen = false"
        >
          <span>{{ item.label }}</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"></polyline></svg>
        </component>
      </li>
    </ul>

    <div class="mobile-drawer-actions">
      <component
        :is="isExternal(button.link) ? 'a' : 'router-link'"
        v-for="button in actionButtons"
        :key="button.key"
        v-bind="linkBindings(button.link)"
        :class="['btn-pill', button.key === 'cta' ? 'btn-pill-yellow' : 'btn-pill-dark']"
        style="width: 100%; justify-content: space-between;"
        @click="mobileOpen = false"
      >
        <span class="btn-text">{{ button.label }}</span>
        <span class="btn-icon-bubble">
          <svg v-if="button.key === 'cta'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"></path><path d="M12 5l7 7-7 7"></path></svg>
          <svg v-else-if="isAdmin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path><polyline points="10 17 15 12 10 7"></polyline><line x1="15" y1="12" x2="3" y2="12"></line></svg>
        </span>
      </component>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from 'src/composables/useAuth'
import { useSiteContent } from 'src/composables/useSiteContent'
import { useMasterEditor } from 'src/composables/useMasterEditor'

const mobileOpen = ref(false)
const route = useRoute()

const { isAdmin } = useAuth()
const { settings, navItems } = useSiteContent()
const { openMasterEditor } = useMasterEditor()

// Auto close mobile drawer on route change
watch(() => route.fullPath, () => {
  mobileOpen.value = false
})

const navLinks = computed(() => {
  const items = (navItems.value || []).filter((item) => item.is_active !== false && item.label && item.path)
  if (items.length) {
    // Ensure labels and links are correctly aligned if user customized
    return items
  }
  return [
    { label: 'خانه', path: '/' },
    { label: 'خدمات', path: '/services' },
    { label: 'پروژه‌ها', path: '/projects' },
    { label: 'مقالات', path: '/articles' },
    { label: 'درباره ما', path: '/about' },
    { label: 'تماس با ما', path: '/contact' },
  ]
})

const BUTTONS = {
  login: {
    label: 'header_login_label',
    link: 'header_login_link',
    defaultLabel: 'ورود',
    defaultLink: '/admin/login',
  },
  cta: {
    label: 'header_cta_label',
    link: 'header_cta_link',
    defaultLabel: 'شروع همکاری',
    defaultLink: '#sec-contact',
  },
}

const DEFAULT_BUTTON_ORDER = ['login', 'cta']

const actionButtons = computed(() => {
  const stored = String(settings.value.header_buttons_order || '')
    .split(',')
    .map((key) => key.trim())
    .filter((key) => key in BUTTONS)

  const keys = stored.length ? [...stored] : [...DEFAULT_BUTTON_ORDER]

  // Ensure login is present if not explicitly configured
  if (!keys.includes('login')) {
    keys.unshift('login')
  }

  return keys.map((key) => {
    let label = settings.value[BUTTONS[key].label] || BUTTONS[key].defaultLabel
    let link = settings.value[BUTTONS[key].link] || BUTTONS[key].defaultLink

    if (key === 'login' && isAdmin.value) {
      label = 'پنل مدیریت'
      link = '/admin'
    }

    return {
      key,
      label,
      link,
    }
  })
})

const isExternal = (path) => {
  const p = String(path || '').trim()
  return p.startsWith('#') || !p.startsWith('/')
}

function linkBindings (path) {
  const target = String(path || '').trim()
  if (target.startsWith('#')) {
    return { href: target }
  }
  if (!isExternal(target)) {
    return { to: target }
  }
  return /^(https?:)?\/\//i.test(target)
    ? { href: target, target: '_blank', rel: 'noopener' }
    : { href: target }
}

function isLinkActive (path) {
  const p = String(path || '').trim()
  if (p === '#sec-hero' || p === '/') {
    return route.path === '/' && (!route.hash || route.hash === '#sec-hero')
  }
  if (p.startsWith('#')) {
    return route.hash === p
  }
  return route.path === p
}
</script>

<style scoped>
/* ==========================================================================
   FLOATING NAVBAR
   ========================================================================== */
.floating-header {
  position: fixed;
  top: 18px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 8px 16px 8px 10px;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(226, 232, 240, 0.95);
  border-radius: var(--radius-pill, 9999px);
  width: min(1340px, 94vw);
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.03);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-sizing: border-box;
  direction: rtl;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-fa, 'Estedad', sans-serif);
  font-weight: 800;
  font-size: 0.98rem;
  color: var(--text-dark, #0a0a0a);
  white-space: nowrap;
  text-decoration: none;
  flex-shrink: 0;
}

.brand-mark {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #0a0a0a;
  display: grid;
  place-items: center;
  color: var(--yellow, #ffcc00);
  font-weight: 900;
  font-size: 0.9rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
}

.brand-mark-sm {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #0a0a0a;
  display: grid;
  place-items: center;
  color: var(--yellow, #ffcc00);
  font-weight: 900;
  font-size: 0.8rem;
  flex-shrink: 0;
}

.desktop-nav {
  display: flex;
  align-items: center;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 22px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-links a {
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text-dark-dim, #4a4a4a);
  transition: color 0.2s;
  white-space: nowrap;
  position: relative;
  text-decoration: none;
  padding: 4px 0;
}

.nav-links a:hover,
.nav-links a.active {
  color: #000000;
  font-weight: 700;
}

.nav-links a::after {
  content: '';
  position: absolute;
  bottom: -2px;
  right: 0;
  width: 0;
  height: 2px;
  background: var(--yellow, #ffcc00);
  transition: width 0.2s;
  border-radius: var(--radius-pill, 9999px);
}

.nav-links a:hover::after,
.nav-links a.active::after {
  width: 100%;
}

.header-cta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.site-edit-btn {
  width: 28px;
  height: 28px;
}

/* ==========================================================================
   BUTTONS: Pill with Separate Icon Bubble
   ========================================================================== */
.btn-pill {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 6px 20px 6px 6px;
  border-radius: var(--radius-pill, 9999px);
  font-weight: 700;
  font-size: 0.86rem;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
}

.btn-pill .btn-text {
  line-height: 1;
}

.btn-pill .btn-icon-bubble {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  transition: transform 0.25s ease, background 0.25s ease, color 0.25s ease;
}

.btn-pill-yellow {
  background: var(--yellow, #ffcc00);
  color: #000000;
  box-shadow: 0 4px 16px rgba(255, 204, 0, 0.32);
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

.btn-pill-sm {
  padding: 5px 16px 5px 5px;
  font-size: 0.82rem;
}

.btn-pill-sm .btn-icon-bubble {
  width: 28px;
  height: 28px;
}

/* Mobile Nav Toggle */
.mobile-menu-btn {
  display: none;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--bg-light, #f4f4f5);
  border: 1px solid var(--border-light, #e4e4e7);
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-dark, #0a0a0a);
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.mobile-menu-btn:hover {
  background: #000000;
  color: #ffffff;
  border-color: #000000;
}

/* Mobile Nav Backdrop */
.mobile-nav-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  z-index: 998;
}

/* Mobile Nav Drawer */
.mobile-nav-drawer {
  position: fixed;
  top: 76px;
  left: 12px;
  right: 12px;
  z-index: 999;
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
  border: 1px solid rgba(226, 232, 240, 0.95);
  border-radius: 26px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.18), 0 4px 16px rgba(0, 0, 0, 0.06);
  padding: 20px 18px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-16px) scale(0.98);
  transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
  display: none;
  direction: rtl;
}

.mobile-nav-drawer.open {
  opacity: 1;
  visibility: visible;
  transform: translateY(0) scale(1);
}

.mobile-drawer-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 14px;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--border-light, #f1f5f9);
}

.mobile-drawer-title {
  font-weight: 800;
  font-size: 0.95rem;
  color: var(--text-dark, #0a0a0a);
}

.mobile-nav-links {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 0;
  padding: 0;
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-radius: 14px;
  font-size: 0.94rem;
  font-weight: 700;
  color: var(--text-dark, #0a0a0a);
  transition: all 0.2s;
  text-decoration: none;
}

.mobile-nav-link svg {
  color: #a1a1aa;
  transition: transform 0.2s;
}

.mobile-nav-link:hover,
.mobile-nav-link.active {
  background: var(--yellow-dim, rgba(255, 204, 0, 0.14));
  color: #946200;
}

.mobile-nav-link:hover svg,
.mobile-nav-link.active svg {
  color: #946200;
  transform: translateX(-4px);
}

.mobile-drawer-actions {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid var(--border-light, #f1f5f9);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive Adaptations */
@media (max-width: 1080px) {
  .nav-links {
    gap: 14px;
  }
}

@media (max-width: 900px) {
  .floating-header {
    width: calc(100% - 24px);
    top: 12px;
    padding: 7px 14px;
    justify-content: space-between;
  }

  .nav-brand {
    font-size: 0.88rem;
  }

  .brand-mark {
    width: 28px;
    height: 28px;
    font-size: 0.8rem;
  }

  .desktop-nav,
  .floating-header .header-cta {
    display: none;
  }

  .mobile-menu-btn {
    display: flex;
    width: 38px;
    height: 38px;
  }

  .mobile-nav-drawer {
    display: block;
    top: 68px;
    padding: 16px 14px;
    max-height: calc(100vh - 84px);
    overflow-y: auto;
  }

  .mobile-drawer-title {
    font-size: 0.86rem;
  }

  .mobile-nav-link {
    font-size: 0.84rem;
    padding: 10px 12px;
  }

  .mobile-drawer-actions .btn-pill {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .nav-brand {
    font-size: 0.84rem;
  }

  .mobile-nav-link {
    font-size: 0.8rem;
  }

  .mobile-drawer-actions .btn-pill {
    font-size: 0.76rem;
  }
}
</style>

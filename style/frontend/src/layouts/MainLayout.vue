<template>
  <q-layout view="hHh lpR fFf">

    <!-- Universal Master Editor: lazily loaded for admins -->
    <HomeMasterEditor v-if="isAdmin" />

    <!-- Floating Admin Quick Dock (Available across all pages for admins) -->
    <aside v-if="isAdmin" class="admin-live-dock" aria-label="ابزارهای مدیریت محتوا">
      <button type="button" class="btn-live-dock-primary" @click="handleOpenEditorForCurrentRoute">
        <q-icon name="edit_note" size="20px" />
        <span>ویرایش محتوای این صفحه</span>
      </button>
      <router-link to="/admin" class="btn-live-dock-secondary" title="ورود به داشبورد پنل ادمین">
        <q-icon name="dashboard" size="18px" />
        <span>پنل ادمین</span>
      </router-link>
    </aside>

    <CloudlandHeader />

    <q-page-container>
      <router-view />
    </q-page-container>

    <CloudlandFooter />

    <!-- Global Floating Quick Access Widget on all public pages -->
    <QuickAccessWidget />

    <!-- Minimal Sleek Custom Cursor -->
    <CustomCursor />

  </q-layout>
</template>

<script setup>
import { defineAsyncComponent, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import CloudlandHeader from 'src/components/Header/CloudlandHeader.vue'
import CloudlandFooter from 'src/components/Footer/CloudlandFooter.vue'
import QuickAccessWidget from 'src/components/common/QuickAccessWidget.vue'
import CustomCursor from 'src/components/common/CustomCursor.vue'
import { useAuth } from 'src/composables/useAuth'
import { useSiteContent } from 'src/composables/useSiteContent'
import { useMasterEditor } from 'src/composables/useMasterEditor'

// Universal Master Editor
const HomeMasterEditor = defineAsyncComponent(() => import('src/components/Home/HomeMasterEditor.vue'))

const route = useRoute()
const { isAdmin } = useAuth()
const { loadSite } = useSiteContent()
const { openMasterEditor } = useMasterEditor()

function handleOpenEditorForCurrentRoute () {
  const path = route.path.toLowerCase()
  if (path.includes('about')) {
    openMasterEditor('about')
  } else if (path.includes('contact')) {
    openMasterEditor('contact')
  } else if (path.includes('article') || path.includes('blog')) {
    openMasterEditor('articles')
  } else if (path.includes('service') || path.includes('solution')) {
    openMasterEditor('services')
  } else if (path.includes('project') || path.includes('product')) {
    openMasterEditor('projects')
  } else {
    openMasterEditor('hero')
  }
}

onMounted(() => {
  loadSite().catch((e) => { console.error('Failed to load site content:', e) })
})
</script>

<style scoped>
.admin-live-dock {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 999;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(13, 13, 15, 0.92);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  padding: 6px 8px;
  border-radius: 9999px;
  border: 1px solid rgba(255, 213, 74, 0.35);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(255, 213, 74, 0.2);
  direction: rtl;
}

.btn-live-dock-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #ffd54a 0%, #f59e0b 100%);
  color: #000000;
  border: none;
  padding: 8px 16px;
  border-radius: 9999px;
  font-size: 0.82rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-live-dock-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(255, 213, 74, 0.4);
}

.btn-live-dock-secondary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.08);
  color: #e4e4e7;
  text-decoration: none;
  padding: 8px 14px;
  border-radius: 9999px;
  font-size: 0.78rem;
  font-weight: 700;
  transition: all 0.2s;
}

.btn-live-dock-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
}

@media (max-width: 600px) {
  .admin-live-dock {
    bottom: 12px;
    right: 12px;
    left: 12px;
    justify-content: space-between;
  }
}
</style>

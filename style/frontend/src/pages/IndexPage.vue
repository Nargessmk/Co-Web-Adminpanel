<template>
  <q-page class="home-page-root">

    <!-- 1. Hero: Modern Minimal Split Architecture -->
    <CloudlandHero />

    <!-- 2. Services Section: Cinematic Rising Sheet Layer & 6 3D Cards -->
    <WhyCloudlandSection />

    <!-- 3. Projects Section: Editorial Showcase -->
    <OurWorksSection />

    <!-- 4. About Us Section: Single Corporate Unified Section with SLAs -->
    <CloudlandAboutSection />

    <!-- 5. Articles Section: 3 Technical Articles -->
    <ArticlesSection />

    <!-- 6. High-Impact Contact Section: Dark Contrast Bento Card with Form -->
    <CloudlandCTA />
  </q-page>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'

import CloudlandHero from 'src/components/Hero/CloudlandHero.vue'
import WhyCloudlandSection from 'src/components/WhyCloudland/WhyCloudlandSection.vue'
import OurWorksSection from 'src/components/Home/OurWorksSection.vue'
import CloudlandAboutSection from 'src/components/About/CloudlandAboutSection.vue'
import ArticlesSection from 'src/components/Home/ArticlesSection.vue'
import CloudlandCTA from 'src/components/CTA/CloudlandCTA.vue'

import { useHomeContent } from 'src/composables/useHomeContent'
import { usePageMeta } from 'src/composables/usePageMeta'
import { useCinematicMotion } from 'src/composables/useCinematicMotion'

// Professional SEO metadata matching index.html
usePageMeta({
  title: 'سرزمین کهکشان هوشمند | پلتفرم ابری و مهندسی نرم‌افزار',
  description: 'توسعه نرم‌افزارهای سازمانی مقیاس‌پذیر، زیرساخت ابری و مدل‌های پردازش هوش مصنوعی توسط سرزمین کهکشان هوشمند.',
  path: '/',
})

const { loadHome } = useHomeContent()
const { initMotion, destroyMotion } = useCinematicMotion()

onMounted(async () => {
  if (typeof window !== 'undefined' && !window.location.hash) {
    window.scrollTo({ top: 0, behavior: 'instant' })
  }
  try {
    await loadHome()
  } catch (error) {
    console.error('Failed to load home content:', error)
  }
  initMotion()
})

onBeforeUnmount(() => {
  destroyMotion()
})
</script>

<style scoped>
.home-page-root {
  background-color: var(--bg-canvas, #f7f7f7);
  min-height: 100vh;
  overflow-x: hidden;
  color: var(--text-dark, #0a0a0a);
}
</style>

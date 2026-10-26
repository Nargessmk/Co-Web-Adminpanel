<template>
  <q-page class="projects-page">
    <!-- 1. Page Hero & Filter Controls -->
    <ProjectsHero />

    <!-- 2. Projects Grid, Cards & Pagination -->
    <ProjectsGrid />

    <!-- 3. High-Impact CTA Banner -->
    <CloudlandCTA page-name="پروژه‌ها" />
  </q-page>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { usePageMeta } from 'src/composables/usePageMeta'
import { useProductsStore } from 'src/stores/products'
import ProjectsHero from 'src/components/Products/ProjectsHero.vue'
import ProjectsGrid from 'src/components/Products/ProjectsGrid.vue'
import CloudlandCTA from 'src/components/CTA/CloudlandCTA.vue'

// Static SEO metadata
usePageMeta({
  title: 'پروژه‌ها و سامانه‌ها | کهکشان هوشمند',
  description: 'سبد پروژه‌های شاخص، سامانه‌های استراتژیک سازمانی و پلتفرم‌های ابری مقیاس‌پذیر کهکشان هوشمند.',
  path: '/projects',
})

const route = useRoute()
const productsStore = useProductsStore()

onMounted(() => {
  productsStore.initFromQuery(route.query)
})
</script>

<template>
  <q-page class="solutions-page">
    <!-- 1. Page Hero -->
    <SolutionsHero />

    <!-- 2. Services Grid (6 Core Cards from Master State) -->
    <ServicesGrid />

    <!-- 3. Engineering Process (4 Stages) -->
    <EngineeringProcess />

    <!-- 4. High-Impact CTA Bento Box -->
    <CloudlandCTA page-name="خدمات" />
  </q-page>
</template>

<script setup>
import { onMounted } from 'vue'
import { usePageMeta } from 'src/composables/usePageMeta'
import { useSolutionsStore } from 'src/stores/solutions'
import SolutionsHero from 'src/components/Solutions/SolutionsHero.vue'
import ServicesGrid from 'src/components/Solutions/ServicesGrid.vue'
import EngineeringProcess from 'src/components/Solutions/EngineeringProcess.vue'
import CloudlandCTA from 'src/components/CTA/CloudlandCTA.vue'

// Static page metadata
usePageMeta({
  title: 'خدمات و راهکارهای تخصصی | کهکشان هوشمند',
  description: 'خدمات مهندسی نرم‌افزار، معماری ابری توزیع‌شده، هوش مصنوعی و امنیت سازمانی Zero-Trust توسط کهکشان هوشمند.',
  path: '/services',
})

const solutionsStore = useSolutionsStore()

onMounted(() => {
  solutionsStore.init()
})
</script>

<template>
  <section class="services-hero">
    <div class="container">
      <div class="hero-center-head">
        <div class="section-tag">
          <span class="tag-dot"></span>
          <span>{{ solutionsStore.settings.page_badge || 'سبد جامع راهکارها و خدمات تخصصی' }}</span>
        </div>

        <div class="hero-title-wrap">
          <h1 class="services-main-title">
            {{ solutionsStore.settings.page_title || 'معماری سیستم‌های مدرن، رایانش ابری و هوش مصنوعی سازمانی' }}
          </h1>
          <button
            v-if="isAdmin"
            type="button"
            class="btn-pill btn-pill-dark btn-pill-sm mr-2"
            @click="openMasterEditor('services')"
          >
            <q-icon name="edit" size="14px" />
            <span>ویرایش خدمات</span>
          </button>
        </div>

        <p class="services-subtext">
          {{ solutionsStore.settings.page_description || 'ارائه طیف وسیعی از خدمات مهندسی نرم‌افزار، طراحی زیرساخت‌های توزیع‌شده با لتنسی میلی‌ثانیه‌ای، پیاده‌سازی مدل‌های هوش مصنوعی و امنیت چندسطحی Zero-Trust برای سازمان‌های پیشرو.' }}
        </p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useSolutionsStore } from 'src/stores/solutions'
import { useAuth } from 'src/composables/useAuth'
import { useMasterEditor } from 'src/composables/useMasterEditor'

const solutionsStore = useSolutionsStore()
const { isAdmin } = useAuth()
const { openMasterEditor } = useMasterEditor()
</script>

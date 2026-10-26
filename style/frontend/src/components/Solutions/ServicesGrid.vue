<template>
  <section class="services-catalog-section">
    <div class="container">
      <div class="section-head-mini row items-center justify-between">
        <div>
          <span class="sub-label">توانمندی‌های اصلی</span>
          <h2 class="sub-title">سرویس‌های تخصصی کهکشان هوشمند</h2>
        </div>
        <button
          v-if="isAdmin"
          type="button"
          class="btn-pill btn-pill-dark btn-pill-sm row items-center"
          @click="openMasterEditor('services')"
        >
          <q-icon name="edit" size="14px" class="q-ml-xs" />
          <span>ویرایش خدمات</span>
        </button>
      </div>

      <!-- Services Grid using Quasar Responsive Classes -->
      <div class="row q-col-gutter-lg">
        <div
          v-for="(service, index) in serviceItems"
          :key="`${service.title}-${index}`"
          class="col-12 col-sm-6 col-md-4"
        >
          <ServiceCard :service="service" :index="index" />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useAuth } from 'src/composables/useAuth'
import { useMasterEditor } from 'src/composables/useMasterEditor'
import { useSolutionsStore } from 'src/stores/solutions'
import ServiceCard from './ServiceCard.vue'

const { isAdmin } = useAuth()
const { servicesState, openMasterEditor } = useMasterEditor()
const solutionsStore = useSolutionsStore()

const serviceItems = computed(() => {
  if (servicesState.value && servicesState.value.length) {
    return servicesState.value
  }
  return solutionsStore.services
})
</script>

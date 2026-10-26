<template>
  <q-card flat class="service-card column justify-between full-height">
    <!-- Card Content (q-card-section) -->
    <q-card-section class="q-pa-none">
      <div class="service-3d-wrap">
        <img
          :src="iconUrl"
          :alt="service.title"
          class="service-3d-img"
          loading="lazy"
          @error="onIconError"
        />
      </div>
      <h3 class="service-title">{{ service.title }}</h3>
      <p class="service-text">{{ service.desc || service.description }}</p>
    </q-card-section>

    <!-- Card Features List (q-card-actions) -->
    <q-card-actions v-if="service.features && service.features.length" class="q-pa-none">
      <ul class="service-features-list full-width">
        <li v-for="(feat, fIdx) in service.features" :key="fIdx">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
          <span>{{ feat }}</span>
        </li>
      </ul>
    </q-card-actions>
  </q-card>
</template>

<script setup>
import { computed } from 'vue'
import { useSolutionsStore } from 'src/stores/solutions'

const props = defineProps({
  service: {
    type: Object,
    required: true,
  },
  index: {
    type: Number,
    default: 0,
  },
})

const solutionsStore = useSolutionsStore()

const iconUrl = computed(() => {
  return solutionsStore.formatIconUrl(props.service.icon, props.index)
})

function onIconError(event) {
  const fallback = solutionsStore.defaultIcons[props.index % solutionsStore.defaultIcons.length]
  event.target.src = fallback
}
</script>

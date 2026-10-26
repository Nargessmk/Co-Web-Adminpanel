<template>
  <div v-if="productsStore.pagination.totalPages > 1" class="pagination-wrap row items-center justify-center">
    <button
      class="btn-page-nav"
      :disabled="productsStore.pagination.page <= 1"
      aria-label="صفحه قبل"
      @click="productsStore.goToPage(productsStore.pagination.page - 1, router)"
    >
      <q-icon name="chevron_right" size="18px" />
    </button>

    <template v-for="pageNum in productsStore.visiblePages" :key="pageNum">
      <span v-if="pageNum === '...'" class="page-dots">...</span>
      <button
        v-else
        :class="['btn-page-num', { active: pageNum === productsStore.pagination.page }]"
        @click="productsStore.goToPage(pageNum, router)"
      >
        {{ pageNum }}
      </button>
    </template>

    <button
      class="btn-page-nav"
      :disabled="productsStore.pagination.page >= productsStore.pagination.totalPages"
      aria-label="صفحه بعد"
      @click="productsStore.goToPage(productsStore.pagination.page + 1, router)"
    >
      <q-icon name="chevron_left" size="18px" />
    </button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useProductsStore } from 'src/stores/products'

const router = useRouter()
const productsStore = useProductsStore()
</script>

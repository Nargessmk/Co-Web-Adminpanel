<template>
  <section class="projects-grid-section">
    <div class="container">
      <!-- Section Header -->
      <div class="section-head-mini">
        <div>
          <span class="sub-label">پروژه‌ها و سامانه‌های فعال</span>
          <h2 class="sub-title">سامانه‌های استراتژیک و پلتفرم‌های ابری</h2>
        </div>
        <div class="head-actions">
          <span class="count-badge">
            {{ productsStore.filteredProjects.length }} پروژه و محصول سازمانی
          </span>
          <router-link
            v-if="isAdmin"
            to="/admin/products"
            class="btn-pill btn-pill-yellow btn-pill-sm row items-center"
          >
            <q-icon name="add" size="14px" class="q-ml-xs" />
            <span>محصول سازمانی جدید</span>
          </router-link>
        </div>
      </div>

      <!-- Skeleton Loading State using Quasar q-card -->
      <div v-if="productsStore.loading" class="row q-col-gutter-lg">
        <div v-for="n in 6" :key="n" class="col-12 col-sm-6 col-md-4">
          <q-card flat class="skeleton-card full-height">
            <div class="skeleton-media"></div>
            <q-card-section class="skeleton-body">
              <div class="skeleton-line w-30"></div>
              <div class="skeleton-line w-80 h-title"></div>
              <div class="skeleton-line w-100"></div>
              <div class="skeleton-line w-70"></div>
            </q-card-section>
            <q-card-actions class="skeleton-footer"></q-card-actions>
          </q-card>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="productsStore.filteredProjects.length === 0" class="empty-results-box">
        <q-icon name="inventory_2" size="48px" color="grey-5" />
        <h3>هیچ پروژه‌ای با این مشخصات یافت نشد</h3>
        <p>لطفاً عبارت دیگری را جستجو کنید یا فیلتر دسته‌بندی را تغییر دهید.</p>
        <button
          class="btn-pill btn-pill-dark btn-pill-sm"
          @click="productsStore.resetFilters(router)"
        >
          پاک کردن فیلترها
        </button>
      </div>

      <!-- Clean Dynamic Grid using Quasar Responsive Classes -->
      <div v-else class="row q-col-gutter-lg">
        <div
          v-for="(item, index) in productsStore.filteredProjects"
          :key="item.id || `${item.title}-${index}`"
          class="col-12 col-sm-6 col-md-4"
        >
          <ProjectGridCard :item="item" />
        </div>
      </div>

      <!-- Pagination Component -->
      <ProjectsPagination />
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useProductsStore } from 'src/stores/products'
import { useAuth } from 'src/composables/useAuth'
import ProjectGridCard from './ProjectGridCard.vue'
import ProjectsPagination from './ProjectsPagination.vue'

const router = useRouter()
const productsStore = useProductsStore()
const { isAdmin } = useAuth()
</script>

<template>
  <section class="projects-hero">
    <div class="container">
      <div class="hero-center-head">
        <!-- Section Tag Badge -->
        <div class="section-tag">
          <span class="tag-dot"></span>
          <span>{{ productsStore.settings.page_badge || 'سبد پروژه‌ها و سامانه‌های ابری' }}</span>
        </div>

        <!-- Hero Title & Admin Actions -->
        <div class="hero-title-wrap">
          <h1 class="projects-main-title">
            {{ productsStore.settings.page_title || 'پروژه‌های شاخص، سامانه‌های استراتژیک و پلتفرم‌های توزیع‌شده' }}
          </h1>
          <div class="hero-admin-actions row items-center q-gutter-sm" v-if="isAdmin">
            <button
              type="button"
              class="btn-pill btn-pill-dark btn-pill-sm"
              @click="openMasterEditor('projects')"
            >
              <q-icon name="edit" size="14px" />
              <span>ویرایش محتوای پروژه‌ها</span>
            </button>
            <router-link
              to="/admin/products"
              class="btn-pill btn-pill-dark btn-pill-sm"
            >
              <q-icon name="settings" size="14px" />
              <span>مدیریت محصولات سازمانی</span>
            </router-link>
          </div>
        </div>

        <p class="projects-subtext">
          {{ productsStore.settings.page_description || 'بررسی معماری سیستم‌های ملی و تجاری با پایداری ۹۹.۹۹۹٪، مقیاس‌پذیری بالا و پردازش میلیون‌ها تراکنش بلادرنگ که توسط مهندسان کهکشان هوشمند خلق شده‌اند.' }}
        </p>

        <!-- Search & Filter Controls -->
        <div class="filter-controls-wrap">
          <div class="category-pills">
            <button
              type="button"
              class="cat-pill"
              :class="{ active: !productsStore.activeCategory }"
              @click="productsStore.setCategory(null, router)"
            >
              {{ productsStore.settings.all_category_label || 'همه پروژه‌ها' }}
            </button>

            <button
              v-for="cat in productsStore.categories"
              :key="cat.id"
              type="button"
              class="cat-pill"
              :class="{ active: productsStore.activeCategory === cat.slug }"
              @click="productsStore.setCategory(cat.slug, router)"
            >
              {{ cat.name }}
            </button>
          </div>

          <div class="search-input-wrap">
            <q-icon name="search" size="18px" class="search-icon" />
            <input
              v-model="productsStore.searchQuery"
              type="text"
              placeholder="جستجو در عناوین، فناوری‌ها و مشخصات پروژه‌ها..."
              class="search-input"
            />
            <button
              v-if="productsStore.searchQuery"
              class="clear-search"
              aria-label="پاک کردن جستجو"
              @click="productsStore.searchQuery = ''"
            >
              ✕
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useProductsStore } from 'src/stores/products'
import { useAuth } from 'src/composables/useAuth'
import { useMasterEditor } from 'src/composables/useMasterEditor'

const router = useRouter()
const productsStore = useProductsStore()
const { isAdmin } = useAuth()
const { openMasterEditor } = useMasterEditor()
</script>

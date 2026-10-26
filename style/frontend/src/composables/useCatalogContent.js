import { ref } from 'vue'
import api from 'src/services/api'

// Fallbacks keep the header readable even if the API is unreachable. The
// detail_* fields are the headings and button labels of a product's own page.
const emptySettings = () => ({
  page_badge: 'محصولات و سامانه‌های ابری',
  page_title: 'کاتالوگ محصولات',
  page_description: 'تمامی نرم‌افزارهای CloudLand را در یک نگاه مشاهده کنید.',
  all_category_label: 'همه',
  empty_title: 'محصولی یافت نشد',
  empty_text: 'در این دسته‌بندی محصولی ثبت نشده است.',
  detail_catalogs_title: 'کاتالوگ‌ها و فایل‌ها',
  detail_videos_title: 'ویدیوهای محصول',
  detail_gallery_title: 'گالری تصاویر',
  detail_description_title: 'توضیحات محصول',
  detail_related_title: 'محصولات مرتبط',
  detail_site_label: 'مشاهده سایت',
  detail_consult_label: 'درخواست مشاوره',
  detail_products_label: 'سایر محصولات'
})

// A cleared field falls back to the default text instead of showing an empty
// spot, exactly like a field the server stores as NULL.
const cleanSettings = (raw) => {
  const cleaned = {}
  Object.entries(raw || {}).forEach(([key, value]) => {
    if (value !== null && value !== undefined && String(value) !== '') cleaned[key] = value
  })
  return cleaned
}

// Module singleton shared by the page (rendering) and the admin widgets
// (editing), exactly like the About / Contact composables.
const settings = ref(emptySettings())
const categories = ref([])
const loading = ref(false)

/** Public products-page header: GET /api/catalog-page */
async function loadSettings () {
  loading.value = true
  try {
    const res = await api.get('/api/catalog-page')
    const data = (res.data && res.data.data) || {}
    settings.value = { ...emptySettings(), ...cleanSettings(data.settings) }
  } finally {
    loading.value = false
  }
}

/** Public category chips: GET /api/categories (ordered by sort_order) */
async function loadCategories () {
  try {
    const res = await api.get('/api/categories')
    categories.value = res.data?.data || []
  } catch (error) {
    console.error('Failed to load categories:', error)
    categories.value = []
  }
}

export function useCatalogContent () {
  return {
    settings,
    categories,
    loading,
    loadSettings,
    loadCategories
  }
}

import { ref } from 'vue'
import api from 'src/services/api'

// Fallbacks keep the header readable even if the API is unreachable. The
// detail_* fields are the eyebrow, block labels and buttons of an article's
// own page.
const emptySettings = () => ({
  page_badge: 'راهکارها',
  page_title: 'راهکارهای CloudLand',
  page_description: 'یادداشت‌ها، تحلیل‌ها و راهنمای تخصصی تیم CloudLand درباره نرم‌افزار، زیرساخت ابری و هوش مصنوعی.',
  empty_title: 'مقاله‌ای منتشر نشده است',
  empty_text: 'به‌زودی راهکارهای تیم CloudLand در این بخش قرار می‌گیرد.',
  detail_eyebrow: 'راهکارها و مقالات تخصصی',
  detail_source_label: 'منبع',
  detail_related_label: 'محصول مرتبط',
  detail_author_label: 'نویسنده',
  detail_author_link_label: 'مشاهده در افراد تیم',
  detail_others_label: 'سایر راهکارها',
  detail_consult_label: 'درخواست مشاوره'
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
// (editing), exactly like the About / Contact / Catalog composables.
const settings = ref(emptySettings())
const loading = ref(false)

/** Public solutions-page header: GET /api/solutions-page */
export async function loadSettings () {
  loading.value = true
  try {
    const res = await api.get('/api/solutions-page')
    const data = (res.data && res.data.data) || {}
    settings.value = { ...emptySettings(), ...cleanSettings(data.settings) }
  } finally {
    loading.value = false
  }
}

export function useSolutionsContent () {
  return {
    settings,
    loading,
    loadSettings
  }
}

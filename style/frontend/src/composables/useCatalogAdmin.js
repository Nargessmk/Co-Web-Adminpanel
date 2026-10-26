import { ref } from 'vue'
import { useQuasar } from 'quasar'
import api from 'src/services/api'
import { useCatalogContent } from 'src/composables/useCatalogContent'

// Fields of the singleton header row.
const SETTINGS_FIELDS = [
  'page_badge', 'page_title', 'page_description',
  'all_category_label', 'empty_title', 'empty_text'
]

// Headings and button labels of a product's detail page (same singleton row).
const DETAIL_FIELDS = [
  'detail_catalogs_title', 'detail_videos_title', 'detail_gallery_title',
  'detail_description_title', 'detail_related_title',
  'detail_site_label', 'detail_consult_label', 'detail_products_label'
]

// Dialog + session state (module singleton — admin widgets only, lazy chunk).
const saving = ref(false)
// Turns false when the API rejects an admin call: every editing widget then
// hides itself instead of leaving a half-working editor on screen.
const authorized = ref(true)
const settingsDialog = ref(false)
const settingsForm = ref({})
const detailDialog = ref(false)
const detailForm = ref({})

/**
 * Products-page editing: the header dialog plus the category-chip reordering.
 * Only the admin widgets use it (imported lazily after login); category CRUD
 * itself lives in the admin panel pages (/admin/categories).
 */
export function useCatalogAdmin () {
  const $q = useQuasar()
  const content = useCatalogContent()

  // A rejected admin call also means the visitor has no valid admin session.
  function reportError (error, fallbackMessage) {
    const status = error?.response?.status
    if (status === 401 || status === 403) {
      authorized.value = false
      return
    }
    $q.notify({ type: 'negative', message: error?.response?.data?.message || fallbackMessage })
  }

  // Header dialog (title + description), opened by the pencil next to the title.
  function openSettingsDialog () {
    const settings = content.settings.value
    const form = {}
    SETTINGS_FIELDS.forEach((field) => { form[field] = settings[field] || '' })
    settingsForm.value = form
    settingsDialog.value = true
  }

  async function submitSettings () {
    saving.value = true
    try {
      await api.put('/api/catalog-page/admin/settings', { ...settingsForm.value })
      settingsDialog.value = false
      await content.loadSettings()
      $q.notify({ type: 'positive', message: 'سربرگ صفحه محصولات ذخیره شد' })
    } catch (e) {
      reportError(e, 'خطا در ذخیره اطلاعات')
    } finally {
      saving.value = false
    }
  }

  // Product detail dialog (section headings + button labels), opened by the
  // pencil on a product's own page.
  function openDetailDialog () {
    const settings = content.settings.value
    const form = {}
    DETAIL_FIELDS.forEach((field) => { form[field] = settings[field] || '' })
    detailForm.value = form
    detailDialog.value = true
  }

  async function submitDetail () {
    saving.value = true
    try {
      await api.put('/api/catalog-page/admin/settings', { ...detailForm.value })
      detailDialog.value = false
      await content.loadSettings()
      $q.notify({ type: 'positive', message: 'سربرگ‌های صفحه محصول ذخیره شد' })
    } catch (e) {
      reportError(e, 'خطا در ذخیره اطلاعات')
    } finally {
      saving.value = false
    }
  }

  // Swaps two neighbouring chips of the horizontal RTL filter row and stores
  // the new order in `sort_order`, which is what GET /api/categories orders by.
  async function moveCategory (index, direction) {
    const list = content.categories
    const target = index + direction
    if (!list || target < 0 || target >= list.value.length) return

    const reordered = [...list.value]
    const moved = reordered[index]
    reordered[index] = reordered[target]
    reordered[target] = moved
    list.value = reordered

    saving.value = true
    try {
      await Promise.all(reordered.map((cat, order) => (
        cat.id
          ? api.put(`/api/categories/admin/${cat.id}`, { ...cat, sort_order: order })
          : null
      )))
      await content.loadCategories()
    } catch (e) {
      // Put the previous order back when the API rejects the change.
      await content.loadCategories()
      reportError(e, 'خطا در تغییر ترتیب')
    } finally {
      saving.value = false
    }
  }

  return {
    authorized,
    saving,
    settingsDialog,
    settingsForm,
    detailDialog,
    detailForm,
    openSettingsDialog,
    submitSettings,
    openDetailDialog,
    submitDetail,
    moveCategory
  }
}
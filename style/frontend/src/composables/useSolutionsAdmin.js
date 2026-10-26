import { ref } from 'vue'
import { useQuasar } from 'quasar'
import api from 'src/services/api'
import { useSolutionsContent } from 'src/composables/useSolutionsContent'

// Fields of the singleton header row.
const SETTINGS_FIELDS = ['page_badge', 'page_title', 'page_description', 'empty_title', 'empty_text']

// Eyebrow, block labels and buttons of an article's detail page (same row).
const DETAIL_FIELDS = [
  'detail_eyebrow', 'detail_source_label', 'detail_related_label',
  'detail_author_label', 'detail_author_link_label',
  'detail_others_label', 'detail_consult_label'
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
 * Solutions-page editing: the header dialog (badge + title + description).
 * Article CRUD itself lives in the admin panel page (/admin/solutions);
 * this only touches the header texts, so a visitor never sees any editor.
 */
export function useSolutionsAdmin () {
  const $q = useQuasar()
  const content = useSolutionsContent()

  // A rejected admin call also means the visitor has no valid admin session.
  function reportError (error, fallbackMessage) {
    const status = error?.response?.status
    if (status === 401 || status === 403) {
      authorized.value = false
      return
    }
    $q.notify({ type: 'negative', message: error?.response?.data?.message || fallbackMessage })
  }

  // Header dialog (badge + title + description), opened by the pencil.
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
      await api.put('/api/solutions-page/admin/settings', { ...settingsForm.value })
      settingsDialog.value = false
      await content.loadSettings()
      $q.notify({ type: 'positive', message: 'سربرگ صفحه راهکارها ذخیره شد' })
    } catch (e) {
      reportError(e, 'خطا در ذخیره اطلاعات')
    } finally {
      saving.value = false
    }
  }

  // Article detail dialog (eyebrow + block labels + buttons), opened by the
  // pencil on an article's own page.
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
      await api.put('/api/solutions-page/admin/settings', { ...detailForm.value })
      detailDialog.value = false
      await content.loadSettings()
      $q.notify({ type: 'positive', message: 'سربرگ‌های صفحه مقاله ذخیره شد' })
    } catch (e) {
      reportError(e, 'خطا در ذخیره اطلاعات')
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
    submitDetail
  }
}

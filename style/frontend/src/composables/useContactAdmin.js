import { ref } from 'vue'
import { useQuasar } from 'quasar'
import api from 'src/services/api'
import { useContactContent } from 'src/composables/useContactContent'

// Fields of the singleton settings row (all dialogs save the whole row).
const SETTINGS_FIELDS = [
  'hero_badge', 'hero_title', 'hero_title_accent', 'hero_description',
  'aside_title', 'aside_description', 'aside_icon',
  'form_title', 'form_subtitle', 'form_submit_label'
]

// Dialog and form state is shared by the triggers (the buttons) and the dialogs
// themselves, so it lives in a module singleton — one editing session per page.
const saving = ref(false)
// Turns false when the API rejects an admin call: every editing widget then
// hides itself instead of leaving a half-working editor on screen.
const authorized = ref(true)

const heroDialog = ref(false)
const asideDialog = ref(false)
const formDialog = ref(false)
const infoCardDialog = ref(false)
const deleteDialog = ref(false)

const settingsForm = ref({})
const infoCardForm = ref({})
const deleteTarget = ref({ id: null, name: '' })

/**
 * Contact page editing: the admin CRUD calls plus the state of the edit dialogs.
 * Only the admin widgets use it (lazily imported after login); every mutation is
 * followed by a fresh `load()` so the page always shows the stored content.
 * The request form posts to /api/consultations and is not managed here.
 */
export function useContactAdmin () {
  const $q = useQuasar()
  const content = useContactContent()

  // A rejected admin call also means the visitor has no valid admin session.
  function reportError (error, fallbackMessage) {
    const status = error?.response?.status
    if (status === 401 || status === 403) {
      authorized.value = false
      return
    }
    $q.notify({ type: 'negative', message: error?.response?.data?.message || fallbackMessage })
  }

  // Fills the shared form with every settings field, so saving from either
  // dialog always submits the complete row (the backend record is replaced).
  function fillSettingsForm () {
    const settings = content.settings.value
    const form = {}
    SETTINGS_FIELDS.forEach((field) => { form[field] = settings[field] || '' })
    settingsForm.value = form
  }

  // Hero dialog, opened by the pencil next to the badge.
  function openHeroDialog () {
    fillSettingsForm()
    heroDialog.value = true
  }

  // Blue aside card dialog, opened by the pencil next to its title.
  function openAsideDialog () {
    fillSettingsForm()
    asideDialog.value = true
  }

  // Consultation form texts dialog, opened by the pencil next to form heading.
  function openFormDialog () {
    fillSettingsForm()
    formDialog.value = true
  }

  async function submitSettings () {
    saving.value = true
    try {
      await api.put('/api/contact/admin/settings', { ...settingsForm.value })
      heroDialog.value = false
      asideDialog.value = false
      formDialog.value = false
      await content.load()
      $q.notify({ type: 'positive', message: 'محتوای صفحه تماس ذخیره شد' })
    } catch (e) {
      reportError(e, 'خطا در ذخیره اطلاعات')
    } finally {
      saving.value = false
    }
  }

  // Create / edit of one info row (phone / email / location / …).
  function openInfoCardDialog (item = null) {
    infoCardForm.value = {
      id: item?.id || null,
      label: item?.label || '',
      value: item?.value || '',
      icon: item?.icon || 'info'
    }
    infoCardDialog.value = true
  }

  async function submitInfoCard () {
    const form = infoCardForm.value
    if (!String(form.label || '').trim() || !String(form.value || '').trim()) {
      $q.notify({ type: 'warning', message: 'لطفاً فیلدهای ستاره‌دار را پر کنید' })
      return
    }

    saving.value = true
    try {
      const { id, ...payload } = form
      if (id) {
        await api.put(`/api/contact/admin/info-cards/${id}`, payload)
      } else {
        await api.post('/api/contact/admin/info-cards', payload)
      }
      infoCardDialog.value = false
      await content.load()
      $q.notify({ type: 'positive', message: id ? 'راه ارتباطی ذخیره شد' : 'راه ارتباطی افزوده شد' })
    } catch (e) {
      reportError(e, 'خطا در ذخیره اطلاعات')
    } finally {
      saving.value = false
    }
  }

  function confirmRemove (item) {
    deleteTarget.value = { id: item?.id || null, name: item?.label || '' }
    deleteDialog.value = true
  }

  async function submitDelete () {
    const { id } = deleteTarget.value
    if (!id) return

    saving.value = true
    try {
      await api.delete(`/api/contact/admin/info-cards/${id}`)
      deleteDialog.value = false
      await content.load()
      $q.notify({ type: 'positive', message: 'مورد حذف شد' })
    } catch (e) {
      reportError(e, 'خطا در حذف مورد')
    } finally {
      saving.value = false
    }
  }

  // Swaps two neighbouring rows of the vertical list and stores the new order
  // in `sort_order`, which is what the public GET is ordered by.
  async function moveItem (index, direction) {
    const list = content.infoCards
    const target = index + direction
    if (!list || target < 0 || target >= list.value.length) return

    const reordered = [...list.value]
    const moved = reordered[index]
    reordered[index] = reordered[target]
    reordered[target] = moved
    list.value = reordered

    saving.value = true
    try {
      await Promise.all(reordered.map((item, order) => (
        item.id
          ? api.put(`/api/contact/admin/info-cards/${item.id}`, { ...item, sort_order: order })
          : null
      )))
      await content.load()
    } catch (e) {
      // Put the previous order back when the API rejects the change.
      await content.load()
      reportError(e, 'خطا در تغییر ترتیب')
    } finally {
      saving.value = false
    }
  }

  return {
    authorized,
    saving,
    heroDialog,
    asideDialog,
    formDialog,
    infoCardDialog,
    deleteDialog,
    settingsForm,
    infoCardForm,
    deleteTarget,
    openHeroDialog,
    openAsideDialog,
    openFormDialog,
    submitSettings,
    openInfoCardDialog,
    submitInfoCard,
    confirmRemove,
    submitDelete,
    moveItem
  }
}
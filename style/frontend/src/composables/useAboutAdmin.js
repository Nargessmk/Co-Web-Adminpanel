import { ref } from 'vue'
import { useQuasar } from 'quasar'
import api from 'src/services/api'
import { useAboutContent } from 'src/composables/useAboutContent'

// Admin CRUD endpoints of the editable About page sections.
// This whole module is only imported by the lazily loaded admin widgets, so a
// regular visitor never receives any of it (endpoints, wording or logic).
const SECTION_ENDPOINTS = {
  stats: '/api/about/admin/stats',
  mission_cards: '/api/about/admin/mission-cards',
  timeline: '/api/about/admin/timeline',
  perks: '/api/about/admin/perks'
}

// Name of the content ref that belongs to each editable section.
const SECTION_REFS = {
  stats: 'stats',
  mission_cards: 'missionCards',
  timeline: 'timeline',
  perks: 'ctaPerks'
}

// Fields of the singleton settings row, in the order they appear in the dialog.
const SETTINGS_FIELDS = [
  'hero_badge', 'hero_title', 'hero_title_accent', 'hero_description',
  'timeline_title', 'team_title', 'team_subtitle',
  'cta_icon', 'cta_eyebrow', 'cta_title', 'cta_description',
  'cta_primary_icon', 'cta_primary_label', 'cta_primary_link',
  'cta_secondary_icon', 'cta_secondary_label', 'cta_secondary_link'
]

// Dialog and form state is shared by the triggers (the buttons) and the dialogs
// themselves, so it lives in a module singleton — one editing session per page.
const saving = ref(false)
// Turns false when the API rejects an admin call: every editing widget then
// hides itself instead of leaving a half-working editor on screen.
const authorized = ref(true)

const settingsDialog = ref(false)
const pageDialog = ref(false)

// Which settings fields each section-title pencil edits, and its dialog wording.
const TITLE_DIALOGS = {
  timeline: {
    heading: 'ویرایش عنوان این بخش',
    fields: [{ key: 'timeline_title', label: 'عنوان بخش مسیر پیشرفت' }]
  },
  team: {
    heading: 'ویرایش عنوان‌های بخش تیم',
    fields: [
      { key: 'team_title', label: 'عنوان بخش تیم' },
      { key: 'team_subtitle', label: 'زیرعنوان بخش تیم' }
    ]
  }
}
const titleDialog = ref(false)
const titleConfig = ref(TITLE_DIALOGS.timeline)

const statDialog = ref(false)
const missionDialog = ref(false)
const timelineDialog = ref(false)
const perkDialog = ref(false)
const deleteDialog = ref(false)

const settingsForm = ref({})
const statForm = ref({})
const missionForm = ref({})
const timelineForm = ref({})
const perkForm = ref({})
const deleteTarget = ref({ section: '', id: null, name: '' })

/**
 * About page editing: the admin CRUD calls plus the state of the edit dialogs.
 * Only the admin widgets use it; every mutation is followed by a fresh
 * `load()` so the page always shows exactly what is stored in the database.
 */
export function useAboutAdmin () {
  const $q = useQuasar()
  const content = useAboutContent()

  const endpoint = (section) => {
    const url = SECTION_ENDPOINTS[section]
    if (!url) throw new Error(`Unknown about section: ${section}`)
    return url
  }

  const saveSettings = (payload) => api.put('/api/about/admin/settings', payload)
  const createItem = (section, payload) => api.post(endpoint(section), payload)
  const updateItem = (section, id, payload) => api.put(`${endpoint(section)}/${id}`, payload)
  const deleteItem = (section, id) => api.delete(`${endpoint(section)}/${id}`)

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

  // Hero-only dialog, opened by the pencil next to the hero badge.
  function openSettingsDialog () {
    fillSettingsForm()
    settingsDialog.value = true
  }

  // Call-to-action section only (icon, texts, two buttons) — pencil in that block.
  function openPageDialog () {
    fillSettingsForm()
    pageDialog.value = true
  }

  // Section-title pencil (timeline heading, or team heading + subtitle):
  // renders only the fields listed for that section — nothing else on the page.
  function openTitleDialog (section = 'timeline') {
    const config = TITLE_DIALOGS[section]
    if (!config) return
    fillSettingsForm()
    titleConfig.value = config
    titleDialog.value = true
  }

  function openStatDialog (stat = null) {
    statForm.value = {
      id: stat?.id || null,
      value: stat?.value || '',
      label: stat?.label || '',
      icon: stat?.icon || 'task_alt',
    }
    statDialog.value = true
  }

  function openMissionDialog (card = null) {
    missionForm.value = {
      id: card?.id || null,
      title: card?.title || '',
      description: card?.description || '',
      icon: card?.icon || 'emoji_objects',
      is_highlight: Boolean(card?.is_highlight),
    }
    missionDialog.value = true
  }

  function openPerkDialog (perk = null) {
    perkForm.value = {
      id: perk?.id || null,
      label: perk?.label || '',
      icon: perk?.icon || 'check_circle',
    }
    perkDialog.value = true
  }

  function openTimelineDialog (item = null) {
    timelineForm.value = {
      id: item?.id || null,
      year: item?.year || '',
      title: item?.title || '',
      description: item?.description || '',
      icon: item?.icon || 'star',
    }
    timelineDialog.value = true
  }
  async function submitSettings () {
    saving.value = true
    try {
      await saveSettings({ ...settingsForm.value })
      settingsDialog.value = false
      pageDialog.value = false
      titleDialog.value = false
      await content.load()
      $q.notify({ type: 'positive', message: 'محتوای صفحه ذخیره شد' })
    } catch (e) {
      reportError(e, 'خطا در ذخیره اطلاعات')
    } finally {
      saving.value = false
    }
  }

  // Shared create/update flow of the list sections.
  async function persistItem (section, form, dialog, successMessage, requiredFields) {
    const missing = requiredFields.some((field) => !String(form[field] || '').trim())
    if (missing) {
      $q.notify({ type: 'warning', message: 'لطفاً فیلدهای ستاره‌دار را پر کنید' })
      return
    }

    saving.value = true
    try {
      const { id, ...payload } = form
      if (id) await updateItem(section, id, payload)
      else await createItem(section, payload)
      dialog.value = false
      await content.load()
      $q.notify({ type: 'positive', message: successMessage })
    } catch (e) {
      reportError(e, 'خطا در ذخیره اطلاعات')
    } finally {
      saving.value = false
    }
  }

  const submitStat = () => persistItem('stats', statForm.value, statDialog, 'آماره ذخیره شد', ['value', 'label'])
  const submitMission = () => persistItem('mission_cards', missionForm.value, missionDialog, 'کارت ذخیره شد', ['title'])
  const submitTimeline = () => persistItem('timeline', timelineForm.value, timelineDialog, 'رخداد ذخیره شد', ['year', 'title'])
  const submitPerk = () => persistItem('perks', perkForm.value, perkDialog, 'مزیت ذخیره شد', ['label'])

  function confirmRemove (section, item, name) {
    deleteTarget.value = { section, id: item?.id || null, name: name || '' }
    deleteDialog.value = true
  }

  async function submitDelete () {
    const { section, id } = deleteTarget.value
    if (!id) return

    saving.value = true
    try {
      await deleteItem(section, id)
      deleteDialog.value = false
      await content.load()
      $q.notify({ type: 'positive', message: 'مورد حذف شد' })
    } catch (e) {
      reportError(e, 'خطا در حذف مورد')
    } finally {
      saving.value = false
    }
  }

  // Swaps two neighbouring items and stores the new order in `sort_order`, which
  // is what every GET is ordered by.
  async function moveItem (section, index, direction) {
    const list = content[SECTION_REFS[section]]
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
        item.id ? updateItem(section, item.id, { ...item, sort_order: order }) : null
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
    settingsDialog,
    pageDialog,
    titleDialog,
    titleConfig,
    statDialog,
    missionDialog,
    timelineDialog,
    perkDialog,
    deleteDialog,
    settingsForm,
    statForm,
    missionForm,
    timelineForm,
    perkForm,
    deleteTarget,
    openSettingsDialog,
    openPageDialog,
    openTitleDialog,
    openStatDialog,
    openMissionDialog,
    openTimelineDialog,
    openPerkDialog,
    submitSettings,
    submitStat,
    submitMission,
    submitTimeline,
    submitPerk,
    confirmRemove,
    submitDelete,
    moveItem
  }
}



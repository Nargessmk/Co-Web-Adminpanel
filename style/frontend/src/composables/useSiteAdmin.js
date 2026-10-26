import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import api from 'src/services/api'
import { useSiteContent } from 'src/composables/useSiteContent'
import { moveRowTo, useRowDrag } from 'src/composables/useRowDrag'

// Fields of the singleton settings row, split by the dialog that edits them.
// The logo is not among them: it is uploaded / removed on its own endpoint.
const HEADER_FIELDS = [
  'site_name',
  'header_login_label', 'header_login_link', 'header_cta_label', 'header_cta_link'
]

// The two header action buttons. Their order is not a field of its own on the
// form — it is the single `header_buttons_order` the header reads.
const HEADER_BUTTONS = {
  login: { label: 'header_login_label', link: 'header_login_link', name: 'ورود' },
  cta: { label: 'header_cta_label', link: 'header_cta_link', name: 'دکمه اصلی' },
}
const DEFAULT_BUTTON_ORDER = ['login', 'cta']

const FOOTER_FIELDS = [
  'footer_description', 'footer_products_title', 'footer_all_products_label',
  'footer_company_title', 'footer_contact_title', 'footer_contact_address',
  'footer_contact_phone', 'footer_contact_email', 'footer_cta_label', 'footer_cta_link',
  'footer_copyright', 'footer_privacy_label', 'footer_privacy_url',
  'footer_terms_label', 'footer_terms_url'
]

// Dialog and form state is shared by the triggers (the pencils) and the dialogs
// themselves, so it lives in a module singleton — one editing session at a time.
const saving = ref(false)
// Turns false when the API rejects an admin call: every editing widget then
// hides itself instead of leaving a half-working editor on screen.
const authorized = ref(true)

const headerDialog = ref(false)
const footerDialog = ref(false)

const headerForm = ref({})
const footerForm = ref({})
const navRows = ref([])
const footerLinkRows = ref([])
const socialRows = ref([])

// Dragging the menu titles: the arrow buttons are gone, the handle is the
// only way to pick a row up.
const navDrag = useRowDrag()
// Same, for the two action buttons of the header.
const headerDrag = useRowDrag()

// Which of the two buttons comes first, e.g. ['cta', 'login'].
const headerButtonOrder = ref([...DEFAULT_BUTTON_ORDER])

// A stored order that is empty or half-written still has to offer both
// buttons to drag, so the missing ones are appended.
function readButtonOrder (stored) {
  const keys = String(stored || '')
    .split(',')
    .map((key) => key.trim())
    .filter((key) => key in HEADER_BUTTONS)
  DEFAULT_BUTTON_ORDER.forEach((key) => {
    if (!keys.includes(key)) keys.push(key)
  })
  return keys
}

const MAX_LOGO_SIZE = 10 * 1024 * 1024 // 10MB

const emptyRow = (fields) => {
  const row = {}
  fields.forEach((field) => { row[field] = '' })
  return row
}

// Keeps rows where everything is filled, drops rows left completely empty and
// rejects half-filled ones (a link without a label would render broken).
const cleanRows = (rows, fields) => {
  const items = []
  for (const row of rows) {
    const values = fields.map((field) => String(row[field] || '').trim())
    if (values.every((value) => !value)) continue
    if (values.some((value) => !value)) return null

    const item = {}
    fields.forEach((field, index) => { item[field] = values[index] })
    items.push(item)
  }
  return items
}

/**
 * Header / footer editing: the two dialogs plus the row lists they manage.
 * Only the admin widgets use it (lazily imported after login); every save is
 * followed by a fresh `loadSite()` so both bars show the stored content.
 */
export function useSiteAdmin () {
  const $q = useQuasar()
  const content = useSiteContent()

  function reportError (error, fallbackMessage) {
    const status = error?.response?.status
    if (status === 401 || status === 403) {
      authorized.value = false
      // Hiding the widgets without a word leaves the admin pressing a button
      // that can no longer work — say why instead.
      $q.notify({
        type: 'negative',
        message: 'نشست شما منقضی شده است؛ لطفاً دوباره وارد شوید',
      })
      return
    }
    $q.notify({ type: 'negative', message: error?.response?.data?.message || fallbackMessage })
  }

  // The logo is edited on its own endpoints, so its preview follows the stored
  // value: an empty string means the admin deleted it (name is shown instead).
  const logoPreview = computed(() => content.settings.value.logo_url || '')

  // Both endpoints answer with the stored settings, so the bars are updated
  // from the response instead of waiting for another round trip.
  const applyResponse = (response) => {
    const data = response && response.data && response.data.data
    if (data) content.applyServerData(data)
  }

  async function uploadLogo (file) {
    if (!file) return false
    if (file.size > MAX_LOGO_SIZE) {
      $q.notify({ type: 'negative', message: 'حجم تصویر نباید بیشتر از ۱۰ مگابایت باشد' })
      return false
    }

    saving.value = true
    try {
      const form = new FormData()
      form.append('image', file)
      const res = await api.post('/api/site/admin/logo', form, { headers: { 'Content-Type': 'multipart/form-data' } })
      applyResponse(res)
      $q.notify({ type: 'positive', message: 'لوگوی سایت به‌روزرسانی شد' })
      return true
    } catch (error) {
      reportError(error, 'خطا در آپلود لوگو')
      content.loadSite().catch(() => {})
      return false
    } finally {
      saving.value = false
    }
  }

  function deleteLogo () {
    $q.dialog({
      title: 'حذف لوگوی سایت',
      message: 'آیا از حذف لوگو اطمینان دارید؟ پس از حذف، نام سایت به جای لوگو نمایش داده می‌شود.',
      cancel: 'انصراف',
      ok: { label: 'حذف', color: 'negative' },
      persistent: true,
    }).onOk(async () => {
      saving.value = true
      try {
        const res = await api.delete('/api/site/admin/logo')
        applyResponse(res)
        $q.notify({ type: 'positive', message: 'لوگوی سایت حذف شد' })
      } catch (error) {
        reportError(error, 'خطا در حذف لوگو')
        content.loadSite().catch(() => {})
      } finally {
        saving.value = false
      }
    })
  }

  function openHeaderDialog () {
    const settings = content.settings.value
    const form = {}
    HEADER_FIELDS.forEach((field) => { form[field] = settings[field] || '' })
    headerForm.value = form
    headerButtonOrder.value = readButtonOrder(settings.header_buttons_order)
    navRows.value = (content.navItems.value || []).map((item) => ({
      label: item.label || '',
      path: item.path || '',
    }))
    headerDialog.value = true
  }

  function openFooterDialog () {
    const settings = content.settings.value
    const form = {}
    FOOTER_FIELDS.forEach((field) => { form[field] = settings[field] || '' })
    footerForm.value = form
    footerLinkRows.value = (content.footerLinks.value || []).map((item) => ({
      label: item.label || '',
      url: item.url || '',
    }))
    socialRows.value = (content.socialLinks.value || []).map((item) => ({
      label: item.label || '',
      url: item.url || '',
      icon: item.icon || 'link',
    }))
    footerDialog.value = true
  }

  function addNavRow () { navRows.value.push(emptyRow(['label', 'path'])) }
  function removeNavRow (index) { navRows.value.splice(index, 1) }

  function addFooterLinkRow () { footerLinkRows.value.push(emptyRow(['label', 'url'])) }
  function removeFooterLinkRow (index) { footerLinkRows.value.splice(index, 1) }

  function addSocialRow () { socialRows.value.push({ label: '', url: '', icon: 'link' }) }
  function removeSocialRow (index) { socialRows.value.splice(index, 1) }

  // Arrow buttons: `delta` -1 moves a row towards the start of the list
  // (visually right, because the dialog is RTL), +1 towards its end.
  function moveRow (rows, index, delta) {
    const target = index + delta
    if (!rows.value || target < 0 || target >= rows.value.length) return
    const next = rows.value.slice()
    const [moved] = next.splice(index, 1)
    next.splice(target, 0, moved)
    rows.value = next
  }

  /** Puts the carried menu title where it was dropped. */
  function dropNavRow (index) {
    const from = navDrag.takeDrag()
    if (from === null || from === index) return
    moveRowTo(navRows, from, index)
  }

  /** Swaps the carried header button with the one it was dropped on. */
  function dropHeaderButton (key) {
    const from = headerDrag.takeDrag()
    if (from === null) return
    const to = headerButtonOrder.value.indexOf(key)
    if (to === -1 || to === from) return
    const next = headerButtonOrder.value.slice()
    const [moved] = next.splice(from, 1)
    next.splice(to, 0, moved)
    headerButtonOrder.value = next
  }

  /**
   * The stored content is applied as soon as the dialog is confirmed — both
   * bars update without waiting — and the PUT response (the server's own
   * answer) confirms it, so a save is one round trip instead of two.
   */
  async function save (payload, dialog, successMessage) {
    saving.value = true
    content.applyLocal(payload)
    try {
      const res = await api.put('/api/site/admin/settings', payload)
      const data = res.data && res.data.data
      if (data) content.applyServerData(data)
      dialog.value = false
      $q.notify({ type: 'positive', message: successMessage })
    } catch (e) {
      reportError(e, 'خطا در ذخیره اطلاعات')
      // The optimistic content may differ from what is stored: show the truth.
      content.loadSite().catch(() => {})
    } finally {
      saving.value = false
    }
  }

  async function submitHeader () {
    const navItems = cleanRows(navRows.value, ['label', 'path'])
    if (navItems === null) {
      $q.notify({ type: 'warning', message: 'هر آیتم منو باید هم متن و هم مسیر داشته باشد' })
      return
    }
    await save(
      { ...headerForm.value, header_buttons_order: headerButtonOrder.value.join(','), nav_items: navItems },
      headerDialog,
      'هدر سایت ذخیره شد'
    )
  }

  async function submitFooter () {
    const footerLinks = cleanRows(footerLinkRows.value, ['label', 'url'])
    const socialLinks = cleanRows(socialRows.value, ['label', 'url'])
    if (footerLinks === null || socialLinks === null) {
      $q.notify({ type: 'warning', message: 'هر لینک باید هم متن و هم آدرس داشته باشد' })
      return
    }
    await save(
      { ...footerForm.value, footer_links: footerLinks, social_links: socialLinks },
      footerDialog,
      'فوتر سایت ذخیره شد'
    )
  }

  return {
    authorized,
    saving,
    headerDialog,
    footerDialog,
    headerForm,
    footerForm,
    headerButtonOrder,
    headerButtonFields: HEADER_BUTTONS,
    headerButtonLabels: Object.fromEntries(
      Object.keys(HEADER_BUTTONS).map((key) => [key, HEADER_BUTTONS[key].name])
    ),
    navRows,
    footerLinkRows,
    socialRows,
    logoPreview,
    navDrag,
    headerDrag,
    openHeaderDialog,
    openFooterDialog,
    uploadLogo,
    deleteLogo,
    addNavRow,
    removeNavRow,
    addFooterLinkRow,
    removeFooterLinkRow,
    addSocialRow,
    removeSocialRow,
    moveRow,
    dropNavRow,
    dropHeaderButton,
    submitHeader,
    submitFooter,
  }
}

import { computed, ref } from 'vue'
import { useQuasar } from 'quasar'
import api from 'src/services/api'
import { useHomeContent } from 'src/composables/useHomeContent'
import { moveRowTo, useRowDrag } from 'src/composables/useRowDrag'

// Fields of the singleton settings row, split by the dialog that edits them.
// The buttons and the statistics are lists (they travel with their own rows),
// so they are not part of these field groups.
const HERO_FIELDS = [
  'hero_badge', 'hero_title', 'hero_title_color', 'hero_description', 'hero_scroll_label', 'hero_image_url'
]

// The four colours the headline may take. The hero draws the same list, so a
// colour the server does not know never reaches the page.
// The four headline colours. The hex codes are the contract: the server
// replaces anything outside this list with the first one, and the hero falls
// back the same way, so all three must agree.
const TITLE_COLORS = [
  { label: 'سرمه‌ای', value: '#0d1b5e' },
  { label: 'طلایی', value: '#f5a300' },
  { label: 'مشکی', value: '#000000' },
  { label: 'سفید', value: '#ffffff' },
]

const ORBIT_FIELDS = ['orbit_caption']

const PRODUCTS_FIELDS = [
  'products_badge', 'products_title', 'products_description',
  'products_all_label', 'products_empty_title', 'products_empty_text'
]

const WHY_FIELDS = [
  'why_badge', 'why_title', 'why_title_accent', 'why_description'
]

const CUSTOMERS_FIELDS = [
  'customers_badge', 'customers_title', 'customers_title_accent', 'customers_description',
  'trust_title', 'trust_description'
]

// The CTA section is the contact form: header, buttons, images and tab labels.
const CTA_FIELDS = [
  'cta_icon', 'cta_title', 'cta_title_accent', 'cta_description',
  'cta_primary_label', 'cta_primary_link', 'cta_secondary_label', 'cta_secondary_link',
  'cta_image_url', 'cta_tab_hi_label', 'cta_tab_quote_label', 'cta_submit_label'
]

const WORKS_FIELDS = [
  'works_eyebrow', 'works_title', 'works_all_label', 'works_details_label',
  'works_tech_label', 'works_team_label', 'works_cta_label',
  'works_category_label', 'works_duration_label'
]

const REVIEWS_FIELDS = ['reviews_eyebrow', 'reviews_title']

// Fields of one showcase card (everything except its id and sort_order).
const WORK_ROW_FIELDS = [
  'badge', 'badge_icon', 'details_link', 'meta_category', 'meta_duration',
  'description', 'tech', 'team', 'team_more', 'cta_label', 'cta_link',
  'image_url', 'mockup'
]

// Fields of one testimonial.
const REVIEW_ROW_FIELDS = ['name', 'role', 'initials', 'text']

// Dialog and form state is shared by the triggers (the pencils) and the dialogs
// themselves, so it lives in a module singleton — one editing session at a time.
const saving = ref(false)
// Turns false when the API rejects an admin call: every editing widget then
// hides itself instead of leaving a half-working editor on screen.
const authorized = ref(true)

const heroDialog = ref(false)
const orbitDialog = ref(false)
const productsDialog = ref(false)
const whyDialog = ref(false)
const customersDialog = ref(false)
const ctaDialog = ref(false)
const worksDialog = ref(false)
const reviewsDialog = ref(false)

const heroForm = ref({})
const orbitForm = ref({})
const productsForm = ref({})
const whyForm = ref({})
const customersForm = ref({})
const ctaForm = ref({})
const worksForm = ref({})
const reviewsForm = ref({})

const buttonRows = ref([])
const orbitRows = ref([])
const featureRows = ref([])
const customerRows = ref([])
// Index of the customer's logo / a showcase card's picture that is mid-upload,
// so only that row shows a spinner. Null when nothing is uploading.
const uploadingLogo = ref(null)
const uploadingImage = ref(null)
const uploadingHeroImage = ref(false)
const uploadingCtaImage = ref(false)

const workRows = ref([])
const reviewRows = ref([])

// Same ceiling the site logo uses.
const MAX_LOGO_SIZE = 10 * 1024 * 1024 // 10MB
const heroStatRows = ref([])
const whyStatRows = ref([])

// Two independent drags: the buttons and the statistics are separate lists, so
// carrying a row never marks one of another.
const buttonDrag = useRowDrag()
const statDrag = useRowDrag()

// The colour the dialog shows and the one it saves are the same field; an
// unknown value falls back to the hero's own navy, as the hero does when it
// draws the headline.
const heroTitleColor = computed({
  get: () => {
    const current = String(heroForm.value.hero_title_color || '').toLowerCase()
    const known = TITLE_COLORS.some((option) => option.value === current)
    return known ? current : TITLE_COLORS[0].value
  },
  set: (value) => { heroForm.value = { ...heroForm.value, hero_title_color: value } },
})

// Shows the colour name next to its dot, not its hex code.
function colorLabel (value) {
  const found = TITLE_COLORS.find((option) => option.value === value)
  return found ? found.label : (value || TITLE_COLORS[0].label)
}

// Carrying an orbit icon from one ring to the other, or from one place in a
// ring to another.
const orbitDrag = useRowDrag()

// Anything that is not the outer ring belongs to the inner one — the same rule
// the hero uses when it places the icons on their circles.
const ringOf = (row) => (row && row.ring === 'outer' ? 'outer' : 'inner')

// The dialog shows the two rings one under the other, but the list they are
// edited in stays flat: the place of a row inside its ring is the place it has
// in the list, and `index` is what a drop refers to.
const ringEntries = (ring) => (orbitRows.value || [])
  .map((row, index) => ({ row, index }))
  .filter((entry) => ringOf(entry.row) === ring)

const innerOrbitRows = computed(() => ringEntries('inner'))
const outerOrbitRows = computed(() => ringEntries('outer'))

/** The icons of one ring, for the template to loop over. */
function ringRows (ring) {
  return ring === 'outer' ? outerOrbitRows.value : innerOrbitRows.value
}

// Keeps rows where every required field is filled, drops rows left empty.
const cleanRows = (rows, required) => {
  const items = []
  for (const row of rows) {
    const values = Object.keys(row).map((field) => String(row[field] || '').trim())
    if (!values.some(Boolean)) continue
    const item = {}
    Object.keys(row).forEach((field) => { item[field] = String(row[field] || '').trim() })
    if (!required.every((field) => item[field])) return null
    items.push(item)
  }
  return items
}

/**
 * Home page editing: the six section dialogs plus the lists they manage.
 * Only the admin widgets use it (lazily imported after login); every save is
 * followed by a fresh `loadHome()` so the page shows the stored content.
 */
export function useHomeAdmin () {
  const $q = useQuasar()
  const content = useHomeContent()

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

  function openDialog (dialog, fields, form, source) {
    const values = {}
    fields.forEach((field) => { values[field] = source[field] || '' })
    form.value = values
    dialog.value = true
  }

  function openHeroDialog () {
    openDialog(heroDialog, HERO_FIELDS, heroForm, content.settings.value)
    // A button without its text would render as a gap, so a variant the server
    // does not know falls back to the filled one here too.
    buttonRows.value = (content.buttons.value || []).map((item) => ({
      label: item.label || '',
      link: item.link || '',
      variant: item.variant === 'secondary' ? 'secondary' : 'primary',
    }))
    heroStatRows.value = (content.heroStats.value || []).map((item) => ({
      key: item.key || 'products',
      label: item.label || '',
    }))
  }

  function openOrbitDialog () {
    openDialog(orbitDialog, ORBIT_FIELDS, orbitForm, content.settings.value)
    orbitRows.value = (content.orbitItems.value || []).map((item) => ({
      ring: item.ring === 'outer' ? 'outer' : 'inner',
      label: item.label || '',
      icon: item.icon || '',
      color: item.color || '#1A2472',
    }))
  }

  function openProductsDialog () {
    openDialog(productsDialog, PRODUCTS_FIELDS, productsForm, content.settings.value)
  }

  function openWhyDialog () {
    openDialog(whyDialog, WHY_FIELDS, whyForm, content.settings.value)
    featureRows.value = (content.features.value || []).map((item) => ({
      title: item.title || '',
      description: item.description || '',
      icon: item.icon || '',
      color: item.color === 'orange' ? 'orange' : 'navy',
      link: item.link || '/solutions',
      link_label: item.link_label || 'بیشتر بدانید',
    }))
    whyStatRows.value = (content.whyStats.value || []).map((item) => ({
      key: item.key || 'products',
      label: item.label || '',
    }))
  }

  function openCustomersDialog () {
    openDialog(customersDialog, CUSTOMERS_FIELDS, customersForm, content.settings.value)
    customerRows.value = (content.customers.value || []).map((item) => ({
      name: item.name || '',
      logo: item.logo || '',
      logo_url: item.logo_url || '',
    }))
  }

  function openCtaDialog () {
    openDialog(ctaDialog, CTA_FIELDS, ctaForm, content.settings.value)
  }

  // The showcase cards: the section header plus one row per project.
  function openWorksDialog () {
    openDialog(worksDialog, WORKS_FIELDS, worksForm, content.settings.value)
    workRows.value = (content.works.value || []).map((item) => {
      const row = {}
      WORK_ROW_FIELDS.forEach((field) => { row[field] = item[field] || '' })
      return row
    })
  }

  // The testimonials: the section header plus one row per quote. The section
  // shows the first three rows, so the list can be reordered with the arrows.
  function openReviewsDialog () {
    openDialog(reviewsDialog, REVIEWS_FIELDS, reviewsForm, content.settings.value)
    reviewRows.value = (content.reviews.value || []).map((item) => {
      const row = {}
      REVIEW_ROW_FIELDS.forEach((field) => { row[field] = item[field] || '' })
      return row
    })
  }

  // The ring an icon is created in is the one whose button was pressed.
  function addOrbitRow (ring = 'inner') {
    orbitRows.value.push({ ring: ringOf({ ring }), label: '', icon: '', color: '#1A2472' })
  }
  function removeOrbitRow (index) { orbitRows.value.splice(index, 1) }

  function addFeatureRow () { featureRows.value.push({ title: '', description: '', icon: '', color: 'navy', link: '/solutions', link_label: 'بیشتر بدانید' }) }
  function removeFeatureRow (index) { featureRows.value.splice(index, 1) }

  function addCustomerRow () { customerRows.value.push({ name: '', logo: '', logo_url: '' }) }
  function removeCustomerRow (index) { customerRows.value.splice(index, 1) }

  function addWorkRow () {
    workRows.value.push({
      badge: '', badge_icon: 'star', details_link: '', meta_category: '',
      meta_duration: '', description: '', tech: '', team: '', team_more: '',
      cta_label: '', cta_link: '/contact', image_url: '', mockup: 'phones',
    })
  }
  function removeWorkRow (index) { workRows.value.splice(index, 1) }

  function addReviewRow () { reviewRows.value.push({ name: '', role: '', initials: '', text: '' }) }
  function removeReviewRow (index) { reviewRows.value.splice(index, 1) }

  function addHeroStatRow () { heroStatRows.value.push({ key: 'products', label: '' }) }
  function removeHeroStatRow (index) { heroStatRows.value.splice(index, 1) }

  // A new button is the filled one.
  function addButtonRow () { buttonRows.value.push({ label: '', link: '', variant: 'primary' }) }
  function removeButtonRow (index) { buttonRows.value.splice(index, 1) }

  // The two hero lists are plain lists: a drop just puts the carried row at
  // the index it was dropped on.
  function dropButtonRow (index) {
    const from = buttonDrag.takeDrag()
    if (from === null || from === index) return
    moveRowTo(buttonRows, from, index)
  }

  function dropHeroStatRow (index) {
    const from = statDrag.takeDrag()
    if (from === null || from === index) return
    moveRowTo(heroStatRows, from, index)
  }

  function addWhyStatRow () { whyStatRows.value.push({ key: 'products', label: '' }) }
  function removeWhyStatRow (index) { whyStatRows.value.splice(index, 1) }

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

  /* =========================================
     ORBIT DRAG AND DROP
     The two rings are shown one under the other, so a drop can mean three
     different things and the ring the icon was dropped on decides which.
     ========================================== */

  /**
   * An icon dropped on another one takes its place. When the two are on
   * different rings they simply exchange rings, which is how an icon is moved
   * from the inner to the outer ring and back.
   */
  function dropOrbitRow (target) {
    const from = orbitDrag.takeDrag()
    if (from === null || from === target) return
    if (ringOf(orbitRows.value[from]) === ringOf(orbitRows.value[target])) {
      moveRowTo(orbitRows, from, target)
      return
    }
    swapOrbitRings(from, target)
  }

  /**
   * An icon dropped on the empty part of a ring joins the end of that ring;
   * dropping it on the ring it is already on does nothing.
   */
  function dropOrbitOnRing (ring) {
    const from = orbitDrag.takeDrag()
    if (from === null) return
    const next = orbitRows.value.slice()
    const [moved] = next.splice(from, 1)
    if (ringOf(moved) === ring) {
      orbitRows.value = next
      return
    }
    moved.ring = ring
    // Straight after the last icon already on that ring; an empty ring takes
    // the icon at the end of the list, the way the rings are stored.
    let insertAt = next.length
    next.forEach((row, index) => {
      if (ringOf(row) === ring) insertAt = index + 1
    })
    next.splice(insertAt, 0, moved)
    orbitRows.value = next
  }

  // Two icons change places, each one keeping its own label, icon and colour.
  function swapOrbitRings (first, second) {
    const next = orbitRows.value.slice()
    const a = { ...next[first] }
    const b = { ...next[second] }
    next[first] = { ...a, ring: b.ring }
    next[second] = { ...b, ring: a.ring }
    orbitRows.value = next
  }

  /**
   * The stored content is applied as soon as the dialog is confirmed — the page
   * behind it updates without waiting — and the PUT response (the server's own
   * answer) confirms it, so a save is one round trip instead of two.
   */
  async function save (payload, dialog, successMessage) {
    saving.value = true
    content.applyLocal(payload)
    try {
      const res = await api.put('/api/home/admin/settings', payload)
      const data = res.data && res.data.data
      if (data) content.applyServerData(data)
      dialog.value = false
      $q.notify({ type: 'positive', message: successMessage })
    } catch (e) {
      reportError(e, 'خطا در ذخیره اطلاعات')
      // The optimistic content may differ from what is stored: show the truth.
      content.loadHome().catch(() => {})
    } finally {
      saving.value = false
    }
  }

  async function submitHero () {
    // The headline is one text in one box: without it the hero has no title at
    // all, so it is the one field that is refused rather than dropped.
    if (!String(heroForm.value.hero_title || '').trim()) {
      $q.notify({ type: 'warning', message: 'عنوان اصلی را وارد کنید' })
      return
    }
    // A button without a link is still a button: it simply goes nowhere, which
    // is what the hero does with an empty link today.
    const buttons = cleanRows(buttonRows.value, ['label'])
    if (buttons === null) {
      $q.notify({ type: 'warning', message: 'هر دکمه باید متن داشته باشد' })
      return
    }
    const heroStats = cleanRows(heroStatRows.value, ['key', 'label'])
    if (heroStats === null) {
      $q.notify({ type: 'warning', message: 'هر آمار باید برچسب داشته باشد' })
      return
    }
    await save({ ...heroForm.value, buttons, hero_stats: heroStats }, heroDialog, 'بخش هدر صفحه ذخیره شد')
  }

  async function submitOrbit () {
    const orbitItems = cleanRows(orbitRows.value, ['label', 'icon'])
    if (orbitItems === null) {
      $q.notify({ type: 'warning', message: 'هر آیتم مدار باید هم برچسب و هم آیکون داشته باشد' })
      return
    }
    await save({ ...orbitForm.value, orbit_items: orbitItems }, orbitDialog, 'مدار ذخیره شد')
  }

  async function submitProducts () {
    await save({ ...productsForm.value }, productsDialog, 'بخش محصولات ذخیره شد')
  }

  async function submitWhy () {
    const features = cleanRows(featureRows.value, ['title', 'icon'])
    if (features === null) {
      $q.notify({ type: 'warning', message: 'هر ویژگی باید هم عنوان و هم آیکون داشته باشد' })
      return
    }
    const whyStats = cleanRows(whyStatRows.value, ['key', 'label'])
    if (whyStats === null) {
      $q.notify({ type: 'warning', message: 'هر آمار باید برچسب داشته باشد' })
      return
    }
    await save(
      { ...whyForm.value, features, why_stats: whyStats },
      whyDialog,
      'بخش «چرا CloudLand» ذخیره شد'
    )
  }

  // Uploads a customer's mark and parks the returned URL on the row. The file
  // is sent on its own because the settings save carries JSON, not multipart;
  // the row is only persisted when the dialog is saved.
  async function uploadCustomerLogo (index, file) {
    if (!file) return
    if (file.size > MAX_LOGO_SIZE) {
      $q.notify({ type: 'negative', message: 'حجم تصویر نباید بیشتر از ۱۰ مگابایت باشد' })
      return
    }
    if (!/^image\//.test(file.type)) {
      $q.notify({ type: 'negative', message: 'فقط فایل تصویری مجاز است' })
      return
    }

    uploadingLogo.value = index
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await api.post('/api/home/admin/customers/logo', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      customerRows.value[index].logo_url = res.data.data.url
      $q.notify({ type: 'positive', message: 'لوگو بارگذاری شد. برای اعمال، «ذخیره» را بزنید.' })
    } catch (error) {
      $q.notify({ type: 'negative', message: error.response?.data?.message || 'خطا در بارگذاری لوگو' })
    } finally {
      uploadingLogo.value = null
    }
  }

  function clearCustomerLogo (index) {
    customerRows.value[index].logo_url = ''
  }

  // A showcase card's picture rides on its own for the same reason the logo
  // does: the settings save is JSON, and the row only keeps the returned URL.
  async function uploadWorkImage (index, file) {
    if (!file) return
    if (file.size > MAX_LOGO_SIZE) {
      $q.notify({ type: 'negative', message: 'حجم تصویر نباید بیشتر از ۱۰ مگابایت باشد' })
      return
    }
    if (!/^image\//.test(file.type)) {
      $q.notify({ type: 'negative', message: 'فقط فایل تصویری مجاز است' })
      return
    }

    uploadingImage.value = index
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await api.post('/api/home/admin/works/image', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      workRows.value[index].image_url = res.data.data.url
      $q.notify({ type: 'positive', message: 'تصویر بارگذاری شد. برای اعمال، «ذخیره» را بزنید.' })
    } catch (error) {
      $q.notify({ type: 'negative', message: error.response?.data?.message || 'خطا در بارگذاری تصویر' })
    } finally {
      uploadingImage.value = null
    }
  }

  function clearWorkImage (index) {
    workRows.value[index].image_url = ''
  }

  async function uploadHeroImage (file) {
    if (!file) return
    if (file.size > MAX_LOGO_SIZE) {
      $q.notify({ type: 'negative', message: 'حجم تصویر نباید بیشتر از ۱۰ مگابایت باشد' })
      return
    }
    if (!/^image\//.test(file.type)) {
      $q.notify({ type: 'negative', message: 'فقط فایل تصویری مجاز است' })
      return
    }

    uploadingHeroImage.value = true
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await api.post('/api/home/admin/hero/image', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      heroForm.value.hero_image_url = res.data.data.url
      $q.notify({ type: 'positive', message: 'تصویر هدر بارگذاری شد. برای اعمال، «ذخیره» را بزنید.' })
    } catch (error) {
      $q.notify({ type: 'negative', message: error.response?.data?.message || 'خطا در بارگذاری تصویر هدر' })
    } finally {
      uploadingHeroImage.value = false
    }
  }

  function clearHeroImage () {
    heroForm.value.hero_image_url = ''
  }

  async function uploadCtaImage (file) {
    if (!file) return
    if (file.size > MAX_LOGO_SIZE) {
      $q.notify({ type: 'negative', message: 'حجم تصویر نباید بیشتر از ۱۰ مگابایت باشد' })
      return
    }
    if (!/^image\//.test(file.type)) {
      $q.notify({ type: 'negative', message: 'فقط فایل تصویری مجاز است' })
      return
    }

    uploadingCtaImage.value = true
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await api.post('/api/home/admin/cta/image', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      ctaForm.value.cta_image_url = res.data.data.url
      $q.notify({ type: 'positive', message: 'تصویر بخش دعوت به همکاری بارگذاری شد. برای اعمال، «ذخیره» را بزنید.' })
    } catch (error) {
      $q.notify({ type: 'negative', message: error.response?.data?.message || 'خطا در بارگذاری تصویر' })
    } finally {
      uploadingCtaImage.value = false
    }
  }

  function clearCtaImage () {
    ctaForm.value.cta_image_url = ''
  }

  async function submitCustomers () {
    // Only the name is mandatory. A customer needs a mark of some sort, but it
    // can be the uploaded picture or the text fallback — requiring both would
    // force the admin to type a brand name for a row that already has a logo.
    const customers = cleanRows(customerRows.value, ['name'])
    if (customers === null) {
      $q.notify({ type: 'warning', message: 'نام هر مشتری را وارد کنید' })
      return
    }
    if (customers.some((row) => !row.logo_url && !row.logo)) {
      $q.notify({ type: 'warning', message: 'برای هر مشتری یا تصویر لوگو بارگذاری کنید یا متن لوگو بنویسید' })
      return
    }
    await save({ ...customersForm.value, customers }, customersDialog, 'بخش مشتریان ذخیره شد')
  }

  async function submitCta () {
    await save({ ...ctaForm.value }, ctaDialog, 'بخش دعوت به همکاری ذخیره شد')
  }

  async function submitWorks () {
    const works = cleanRows(workRows.value, ['badge'])
    if (works === null) {
      $q.notify({ type: 'warning', message: 'برچسب هر پروژه را وارد کنید' })
      return
    }
    await save({ ...worksForm.value, works }, worksDialog, 'بخش نمونه‌کارها ذخیره شد')
  }

  async function submitReviews () {
    const reviews = cleanRows(reviewRows.value, ['name', 'text'])
    if (reviews === null) {
      $q.notify({ type: 'warning', message: 'برای هر نظر، نام و متن را وارد کنید' })
      return
    }
    await save({ ...reviewsForm.value, reviews }, reviewsDialog, 'نظرات مشتریان ذخیره شد')
  }

  return {
    authorized,
    saving,
    heroDialog,
    orbitDialog,
    productsDialog,
    whyDialog,
    customersDialog,
    ctaDialog,
    worksDialog,
    reviewsDialog,
    heroForm,
    orbitForm,
    productsForm,
    whyForm,
    customersForm,
    ctaForm,
    worksForm,
    reviewsForm,
    heroTitleColor,
    TITLE_COLORS,
    colorLabel,
    buttonRows,
    orbitRows,
    orbitDrag,
    ringRows,
    buttonDrag,
    statDrag,
    featureRows,
    customerRows,
    workRows,
    reviewRows,
    heroStatRows,
    whyStatRows,
    openHeroDialog,
    openOrbitDialog,
    openProductsDialog,
    openWhyDialog,
    openCustomersDialog,
    openCtaDialog,
    openWorksDialog,
    openReviewsDialog,
    addOrbitRow,
    removeOrbitRow,
    dropOrbitRow,
    dropOrbitOnRing,
    addFeatureRow,
    removeFeatureRow,
    addCustomerRow,
    removeCustomerRow,
    addWorkRow,
    removeWorkRow,
    addReviewRow,
    removeReviewRow,
    uploadCustomerLogo,
    clearCustomerLogo,
    uploadingLogo,
    uploadWorkImage,
    clearWorkImage,
    uploadingImage,
    uploadHeroImage,
    clearHeroImage,
    uploadingHeroImage,
    uploadCtaImage,
    clearCtaImage,
    uploadingCtaImage,
    addButtonRow,
    removeButtonRow,
    dropButtonRow,
    addHeroStatRow,
    removeHeroStatRow,
    dropHeroStatRow,
    addWhyStatRow,
    removeWhyStatRow,
    moveRow,
    submitHero,
    submitOrbit,
    submitProducts,
    submitWhy,
    submitCustomers,
    submitCta,
    submitWorks,
    submitReviews,
  }
}

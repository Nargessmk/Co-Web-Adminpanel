import { ref } from 'vue'
import api from 'src/services/api'

// Shape of the single settings row, used as a fallback so the page always has
// something to render (same pattern as useAboutContent).
const emptySettings = () => ({
  hero_badge: '',
  hero_title: '',
  hero_title_accent: '',
  hero_description: '',
  aside_title: '',
  aside_description: '',
  aside_icon: 'support_agent',
  form_title: '',
  form_subtitle: '',
  form_submit_label: ''
})

// The page renders the content and the admin widgets edit it, so the refs live
// in a module singleton: both sides always share exactly the same data, and a
// mutation reloaded by the admin immediately shows up on the page.
const settings = ref(emptySettings())
const infoCards = ref([])
const phone = ref('')
const email = ref('')
const address = ref('')
const workingHours = ref('')
const emergencySupport = ref('')
const slaResponse = ref('')
const faqs = ref([])
const loading = ref(false)

/**
 * Public Contact content: the read-only `GET /api/contact`.
 * The admin CRUD calls live in `useContactAdmin` so that this module — which
 * the page loads for every visitor — contains nothing about editing.
 * The request form is static and never touches this content.
 */
async function load () {
  loading.value = true
  try {
    const res = await api.get('/api/contact')
    const data = (res.data && res.data.data) || {}
    settings.value = { ...emptySettings(), ...(data.settings || {}) }
    infoCards.value = data.info_cards || []
    phone.value = data.phone || ''
    email.value = data.email || ''
    address.value = data.address || ''
    workingHours.value = data.workingHours || ''
    emergencySupport.value = data.emergencySupport || ''
    slaResponse.value = data.slaResponse || ''
    faqs.value = data.faqs || []
  } finally {
    loading.value = false
  }
}

export function useContactContent () {
  return {
    settings,
    infoCards,
    phone,
    email,
    address,
    workingHours,
    emergencySupport,
    slaResponse,
    faqs,
    loading,
    load,
  }
}
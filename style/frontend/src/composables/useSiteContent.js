import { ref } from 'vue'
import api from 'src/services/api'

// Fallbacks keep both bars looking exactly like the hardcoded version until
// the API answers (or when it is unreachable). No default logo: showing the
// old file until GET /api/site resolves would flash the wrong brand.
const emptySettings = () => ({
  logo_url: '',
  site_name: 'کهکشان هوشمند',
  header_login_label: 'ورود',
  header_login_link: '/admin/login',
  header_cta_label: 'شروع همکاری',
  header_cta_link: '#sec-contact',
  // The order the two action buttons are rendered in; the admin swaps them
  // by dragging one over the other.
  header_buttons_order: 'cta',
  footer_description: 'راهکارهای نرم‌افزاری هوشمند برای کسب‌وکارهای مدرن. ما به شما کمک می‌کنیم سریع‌تر، هوشمندتر و مطمئن‌تر رشد کنید.',
  footer_products_title: 'محصولات',
  footer_all_products_label: 'همه محصولات',
  footer_company_title: 'شرکت',
  footer_contact_title: 'تماس با ما',
  footer_contact_address: 'ایران، اهواز',
  footer_contact_phone: '۰۶۱۳-۳۳۶۲۷۷۲',
  footer_contact_email: 'inform@gmail.com',
  footer_cta_label: 'شروع همکاری',
  footer_cta_link: '#sec-contact',
  footer_copyright: '© ۱۴۰۵ تمامی حقوق مادی و معنوی متعلق به سرزمین کهکشان هوشمند است.',
  footer_credit: 'Designed with precision & high standards.',
  social_github: 'https://github.com',
  social_linkedin: 'https://linkedin.com',
  social_telegram: 'https://t.me',
  social_twitter: 'https://x.com',
  quick_phone: '02188901234',
  quick_phone_label: 'تماس تلفنی مستقیم',
  quick_telegram: 'https://t.me',
  quick_telegram_label: 'پشتیبانی تلگرام',
  quick_cta_link: '/contact',
  quick_cta_label: 'درخواست مشاوره فوری',
  quick_whatsapp: '',
  quick_is_enabled: 'true',
})

const defaultNavItems = () => [
  { label: 'خانه', path: '/' },
  { label: 'خدمات', path: '/services' },
  { label: 'پروژه‌ها', path: '/projects' },
  { label: 'مقالات', path: '/articles' },
  { label: 'درباره ما', path: '/about' },
  { label: 'تماس با ما', path: '/contact' },
]

const defaultFooterLinks = () => [
  { label: 'خانه', path: '/', url: '/' },
  { label: 'راهکارها', path: '/solutions', url: '/solutions' },
  { label: 'درباره ما', path: '/about', url: '/about' },
  { label: 'تماس با ما', path: '/contact', url: '/contact' },
  { label: 'وبلاگ', path: '#', url: '#' },
]

const defaultSocialLinks = () => [
  { label: 'LinkedIn', url: '#', icon: 'business' },
  { label: 'Instagram', url: '#', icon: 'photo_camera' },
  { label: 'Telegram', url: '#', icon: 'send' },
]

const LIST_KEYS = ['nav_items', 'footer_links', 'social_links']

// Module singleton shared by the layout (rendering) and the admin dialog.
const settings = ref(emptySettings())
const navItems = ref(defaultNavItems())
const footerLinks = ref(defaultFooterLinks())
const socialLinks = ref(defaultSocialLinks())
const loading = ref(false)

// A cleared field falls back to the default text instead of showing an empty
// spot, exactly like a field the server stores as NULL.
const cleanSettings = (raw) => {
  const cleaned = {}
  Object.entries(raw || {}).forEach(([key, value]) => {
    if (value !== null && value !== undefined && String(value) !== '') cleaned[key] = value
  })
  return cleaned
}

const listRef = (key) => ({
  nav_items: navItems,
  footer_links: footerLinks,
  social_links: socialLinks,
})[key]

/** A full server answer (GET /api/site or the PUT / logo response). */
function applyServerData (data) {
  const payload = data || {}
  settings.value = { ...emptySettings(), ...cleanSettings(payload.settings) }

  LIST_KEYS.forEach((key) => {
    if (Array.isArray(payload[key])) listRef(key).value = payload[key]
  })
}

/**
 * The part of a save that is already known on the client: both bars show the
 * new content right away, the response then confirms it.
 */
function applyLocal (payload) {
  if (!payload) return

  const patch = {}
  Object.entries(payload).forEach(([key, value]) => {
    if (!LIST_KEYS.includes(key)) patch[key] = value
  })
  settings.value = { ...settings.value, ...cleanSettings(patch) }

  LIST_KEYS.forEach((key) => {
    if (Array.isArray(payload[key])) listRef(key).value = payload[key]
  })
}

/** Header + footer content: GET /api/site */
export async function loadSite () {
  loading.value = true
  try {
    const res = await api.get('/api/site')
    applyServerData((res.data && res.data.data) || {})
  } finally {
    loading.value = false
  }
}

export function useSiteContent () {
  return {
    settings,
    navItems,
    footerLinks,
    socialLinks,
    loading,
    loadSite,
    applyServerData,
    applyLocal,
  }
}

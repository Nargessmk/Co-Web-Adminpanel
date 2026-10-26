import { ref } from 'vue'
import api from 'src/services/api'

// Fallbacks keep the homepage looking exactly like the hardcoded version until
// the API answers (or when it is unreachable).
const emptySettings = () => ({
  hero_badge: 'استودیو هوشمند معماری ابری و مهندسی نرم‌افزار',
  hero_title: 'خلق پلتفرم‌های مقیاس‌پذیر،\nمهندسی سیستم‌های ابری پایدار',
  // High contrast ink colour for the white hero panel
  hero_title_color: '#0a0a0a',
  hero_description: 'طراحی و پیاده‌سازی سیستم‌های ابری توزیع‌شده با لتنسی زیر ۱۵ میلی‌ثانیه، امنیت Zero-Trust و پایداری ۹۹.۹۹۹٪ برای سازمان‌ها و پلتفرم‌های پرترافیک.',
  hero_scroll_label: 'بررسی توانمندی‌های مهندسی',
  hero_image_url: '/images/herosection-video.mp4',
  orbit_caption: 'سرزمین ابری',
  products_badge: 'سبد پروژه‌ها و سامانه‌ها',
  products_title: 'سامانه‌های نوآورانه و نرم‌افزارهای مقیاس‌پذیر',
  products_description: 'مجموعه‌ای یکپارچه از راهکارهای نرم‌افزاری، اتوماسیون فرآیندها و پلتفرم‌های تحلیل داده که با بالاترین استانداردهای مهندسی تولید شده‌اند.',
  products_all_label: 'مشاهده همه پروژه‌ها',
  products_empty_title: 'هنوز محصولی ثبت نشده است',
  products_empty_text: 'محصولات CloudLand به‌زودی در این بخش نمایش داده می‌شوند.',
  why_badge: 'سبد جامع خدمات و سامانه‌ها',
  why_title: 'خدمات جامع و تخصصی ما برای',
  why_title_accent: 'رشد و تحول کسب‌وکار شما',
  why_description: 'از طراحی معماری‌های پیچیده نرم‌افزاری تا پیاده‌سازی زیرساخت‌های ابری پایدار، طیف متنوعی از خدمات مهندسی متناسب با اهداف سازمانی شما.',
  customers_badge: 'اعتماد شما، سرمایه ماست',
  customers_title: 'مورد اعتماد',
  customers_title_accent: 'کسب‌وکارهای بزرگ',
  customers_description: 'مجموعه‌ای از سازمان‌ها و کسب‌وکارها به راهکارهای نرم‌افزاری CloudLand اعتماد کرده‌اند.',
  trust_title: 'همراه شما در مسیر رشد',
  trust_description: 'ما به ایجاد همکاری‌های بلندمدت و ارائه راهکارهای قابل اعتماد برای کسب‌وکارها متعهد هستیم.',
  cta_icon: 'support_agent',
  cta_title: 'آماده‌اید پروژه بعدی خود را با ما بسازید؟',
  cta_title_accent: 'همین حالا گفت‌وگو کنیم',
  cta_description: 'تیم مشاوره فنی و مهندسی ما آماده پاسخگویی به سوالات شما و ارائه بهترین برآورد زمانی و هزینه‌ای است.',
  cta_image_url: '/uploads/home/contact-programming.jpg',
  cta_tab_hi_label: 'ارسال پیام (Say Hi)',
  cta_tab_quote_label: 'درخواست پیش‌فاکتور (Get a Quote)',
  cta_submit_label: 'ارسال پیام (Send Message)',
  works_eyebrow: 'پروژه‌ها و نمونه‌کارها',
  works_title: 'OUR WORKS',
  works_all_label: 'مشاهده همه پروژه‌ها',
  works_details_label: 'جزئیات پروژه',
  works_tech_label: 'TECHNOLOGIES USED',
  works_team_label: 'TEAM MEMBERS',
  works_cta_label: 'رزرو جلسه و دمو',
  works_category_label: 'دسته‌بندی',
  works_duration_label: 'مدت زمان اجرا',
  reviews_eyebrow: 'نظرات مشتریان و همکاران',
  reviews_title: 'تجربه همکاری با سرزمین ابری',
})

const defaultOrbitItems = () => ([
  { ring: 'inner', label: 'معماری ابری', icon: 'cloud', color: '#111113' },
  { ring: 'inner', label: 'امنیت داده', icon: 'shield', color: '#FFD54A' },
  { ring: 'inner', label: 'هوش مصنوعی', icon: 'psychology', color: '#111113' },
  { ring: 'outer', label: 'اتوماسیون سازمانی', icon: 'auto_awesome', color: '#FFD54A' },
])

const defaultButtons = () => ([
  { label: 'مشاوره و شروع همکاری', link: '#sec-contact', variant: 'primary' },
  { label: 'بررسی توانمندی‌های مهندسی', link: '#sec-services', variant: 'secondary' },
])

const defaultFeatures = () => ([
  {
    title: 'توسعه نرم‌افزار سفارشی',
    description: 'راهکارهای منعطف و مقیاس‌پذیر سازمانی مهندسی‌شده با بالاترین کیفیت معماری کد.',
    icon: 'code',
    color: 'light',
    link: '/solutions',
    link_label: 'بیشتر بدانید',
  },
  {
    title: 'خدمات توسعه وب و پلتفرم',
    description: 'سامانه‌های تحت وب فوق‌سریع، تعاملی و ابری متناسب با نیازمندی‌های پرتراکنش.',
    icon: 'language',
    color: 'yellow',
    link: '/solutions',
    link_label: 'بیشتر بدانید',
  },
  {
    title: 'توسعه اپلیکیشن موبایل',
    description: 'اپلیکیشن‌های بومی و چندسکویی مدرن با رابط کاربری روان و تجربه کاربری شگفت‌انگیز.',
    icon: 'smartphone',
    color: 'dark',
    link: '/solutions',
    link_label: 'بیشتر بدانید',
  },
  {
    title: 'راهکارهای ابری و دوآپس',
    description: 'زیرساخت‌های توزیع‌شده، استقرار خودکار، مانیتورینگ بلادرنگ و امنیت چندلایه‌ای.',
    icon: 'cloud_sync',
    color: 'soft',
    link: '/solutions',
    link_label: 'بیشتر بدانید',
  },
])

const defaultCustomers = () => ([
  { name: 'دیجی‌کالا', logo: 'DIGIKALA' },
  { name: 'همراه اول', logo: 'MCI' },
  { name: 'اسنپ', logo: 'SNAPP' },
  { name: 'تپسی', logo: 'TAPSI' },
  { name: 'بیمه ایران', logo: 'IRAN' },
  { name: 'پارک علم و فناوری', logo: 'STP' },
])

// 4 stats matching the reference: 2000+ Company, 10+ Years Exp., 800+ Hours of Digital, 150M+ Revenue
const defaultHeroStats = () => ([
  { key: 'company', label: 'شرکت و سازمان همکار' },
  { key: 'experience', label: 'سال سابقه تخصصی' },
  { key: 'digital_hours', label: 'ساعت مشاوره و دیجیتال' },
  { key: 'revenue', label: 'ارزش خلق‌شده' },
])

const defaultWhyStats = () => ([
  { key: 'company', label: 'شرکت همکار' },
  { key: 'experience', label: 'سال سابقه' },
  { key: 'digital_hours', label: 'ساعت دیجیتال' },
  { key: 'revenue', label: 'ارزش پروژه‌ها' },
])

// The two showcase cards the "OUR WORKS" section drew before it was editable.
const defaultWorks = () => ([
  {
    badge: 'FITNESS APP',
    badge_icon: 'star',
    details_link: '/products/cloudland-bi',
    meta_category: 'توسعه اپلیکیشن موبایل',
    meta_duration: '۴ ماه',
    description: 'سامانه جامع و هوشمند سلامت و پایش تناسب اندام با برنامه‌ریزی خودکار تمرینات ورزشی، رژیم غذایی هوش مصنوعی و پردازش بلادرنگ شاخص‌های زیستی کاربران.',
    tech: 'React Native, Firebase, Redux, REST API, PostgreSQL',
    team: 'SA,MR,EM,FK',
    team_more: '+۳',
    cta_label: 'رزرو جلسه و دمو',
    cta_link: '/contact',
    image_url: '',
    mockup: 'phones',
  },
  {
    badge: 'E-COMMERCE ENTERPRISE',
    badge_icon: 'storefront',
    details_link: '/products/cloudland-bpms',
    meta_category: 'پلتفرم ابری سازمانی',
    meta_duration: '۵ ماه',
    description: 'سامانه چندفروشندگی و تجارت الکترونیک B2B با موتور پردازش سریع فاکتور، یکپارچه‌ساز انبارداری توزیع‌شده، گیت‌وی پرداخت بانکی مقیاس‌پذیر و داشبورد تحلیل رفتار مشتریان.',
    tech: 'Vue 3, FastAPI, Docker & K8s, Redis Cache, PostgreSQL',
    team: 'AS,ND,KH,BM',
    team_more: '+۴',
    cta_label: 'درخواست دمو آنلاین',
    cta_link: '/contact',
    image_url: '',
    mockup: 'browser',
  },
])

// The testimonials the section rendered before they were editable.
const defaultReviews = () => ([
  {
    name: 'مهندس آرش شریفی',
    role: 'مدیر ارشد فناوری (CTO) در نکست‌ژن',
    initials: 'آش',
    text: 'همکاری با تیم کلودلند یکی از بهترین تجربیات مهندسی سازمان ما بود. آن‌ها با درک دقیق دغدغه‌های پرتراکنش ما، معماری ابری قدرتمند و پایداری را پیاده کردند که فراتر از استانداردهای معمول بود.',
  },
  {
    name: 'دکتر علیرضا باقری',
    role: 'مدیرعامل هلدینگ رادمان تکنولوژی',
    initials: 'عب',
    text: 'تعهد کاری، سرعت اجرای بالا و طراحی رابط کاربری بسیار لوکس و مدرن باعث شد پلتفرم جدید ما تحسین همه سرمایه‌گذاران و مشتریان را برانگیزد. پشتیبانی ۲۴ ساعته آن‌ها واقعاً قوت قلب ماست.',
  },
  {
    name: 'سارا مهدی‌پور',
    role: 'مدیر محصول ارشد سامانه‌های مالی',
    initials: 'سم',
    text: 'دقت در جزییات UI/UX و هماهنگی فوق‌العاده با تیم بک‌اند، فرآیند اجرای پروژه را بدون کمترین تأخیر پیش برد. به هر شرکتی که به دنبال کار درجه‌یک سازمانی است توصیه می‌کنم.',
  },
  {
    name: 'کامران یزدانی',
    role: 'معمار نرم‌افزار و زیرساخت',
    initials: 'کی',
    text: 'امنیت داده و رعایت استانداردهای Zero-Trust در راهکارهای ابری کلودلند در بالاترین سطح ممکن قرار دارد. تجربه‌ای کاملاً متمایز نسبت به سایر پیمانکاران.',
  },
])

const LIST_KEYS = ['buttons', 'orbit_items', 'features', 'customers', 'hero_stats', 'why_stats', 'works', 'reviews']

// A list that the server sends back empty would leave the hero with no buttons,
// so the fallback stays until the admin has saved something real. The two
// showcase lists behave the same way: a migration only creates their table, and
// the page must keep showing the cards until the admin has replaced them.
const KEEP_DEFAULT_IF_EMPTY = ['buttons', 'works', 'reviews']

// Module singleton shared by the homepage sections (rendering) and the admin
// dialogs, so a pencil and the dialog it opens always see the same data.
const settings = ref(emptySettings())
const buttons = ref(defaultButtons())
const orbitItems = ref(defaultOrbitItems())
const features = ref(defaultFeatures())
const customers = ref(defaultCustomers())
const heroStats = ref(defaultHeroStats())
const whyStats = ref(defaultWhyStats())
const works = ref(defaultWorks())
const reviews = ref(defaultReviews())
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
  buttons,
  orbit_items: orbitItems,
  features,
  customers,
  hero_stats: heroStats,
  why_stats: whyStats,
  works,
  reviews,
})[key]

const applyLists = (payload) => {
  LIST_KEYS.forEach((key) => {
    if (!Array.isArray(payload[key])) return
    if (!payload[key].length && KEEP_DEFAULT_IF_EMPTY.includes(key)) return
    listRef(key).value = payload[key]
  })
}

/** A full server answer (GET /api/home or the PUT response). */
function applyServerData (data) {
  const payload = data || {}
  settings.value = { ...emptySettings(), ...cleanSettings(payload.settings) }
  applyLists(payload)
}

/**
 * The part of a save that is already known on the client. Applying it right
 * away means the page behind the dialog shows the new content without waiting
 * for a second round trip; the PUT response then confirms it.
 */
function applyLocal (payload) {
  if (!payload) return

  const patch = {}
  Object.entries(payload).forEach(([key, value]) => {
    if (!LIST_KEYS.includes(key)) patch[key] = value
  })
  settings.value = { ...settings.value, ...cleanSettings(patch) }

  applyLists(payload)
}

/** Home page content: GET /api/home */
export async function loadHome () {
  loading.value = true
  try {
    const res = await api.get('/api/home')
    applyServerData((res.data && res.data.data) || {})
  } finally {
    loading.value = false
  }
}

export function useHomeContent () {
  return {
    settings,
    buttons,
    orbitItems,
    features,
    customers,
    heroStats,
    whyStats,
    works,
    reviews,
    loading,
    loadHome,
    applyServerData,
    applyLocal,
  }
}

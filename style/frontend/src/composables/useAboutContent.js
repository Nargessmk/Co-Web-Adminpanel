import { ref } from 'vue'
import api from 'src/services/api'

// Shape of the single settings row, used as a fallback so the page always has
// something to render.
const emptySettings = () => ({
  hero_badge: '',
  hero_title: '',
  hero_title_accent: '',
  hero_description: '',
  timeline_title: '',
  team_title: '',
  team_subtitle: '',
  cta_icon: 'support_agent',
  cta_eyebrow: 'همکاری با سرزمین ابری',
  cta_title: '',
  cta_description: '',
  cta_primary_icon: 'mail',
  cta_primary_label: '',
  cta_primary_link: '',
  cta_secondary_icon: 'inventory_2',
  cta_secondary_label: '',
  cta_secondary_link: ''
})

// The page renders the content and the admin widgets edit it, so the refs live
// in a module singleton: both sides always share exactly the same data, and a
// mutation reloaded by the admin immediately shows up on the page.
const settings = ref(emptySettings())
const stats = ref([])
const missionCards = ref([])
const timeline = ref([])
const ctaPerks = ref([])
const statementTitle = ref('')
const statementP1 = ref('')
const statementP2 = ref('')
const metrics = ref([])
const values = ref([])
const team = ref([])
const loading = ref(false)

/**
 * Public About content: the read-only `GET /api/about`.
 * The admin CRUD calls live in `useAboutAdmin` so that this module — which the
 * page loads for every visitor — contains nothing about editing.
 */
async function load () {
  loading.value = true
  try {
    const res = await api.get('/api/about')
    const data = (res.data && res.data.data) || {}
    settings.value = { ...emptySettings(), ...(data.settings || {}) }
    statementTitle.value = data.statementTitle || ''
    statementP1.value = data.statementP1 || ''
    statementP2.value = data.statementP2 || ''
    metrics.value = data.metrics || []
    values.value = data.values || []
    team.value = data.team || []
    stats.value = data.stats || []
    missionCards.value = data.mission_cards || []
    timeline.value = sortTimeline(data.timeline || [])
    ctaPerks.value = data.cta_perks || []
  } finally {
    loading.value = false
  }
}

// The `year` column is free text (VARCHAR(50)) and seeded with Persian digits
// («۱۳۹۶»), so both digit scripts are normalised before numeric comparison.
const toLatinDigits = (value) => String(value ?? '')
  .replace(/[۰-۹]/g, (d) => String(d.charCodeAt(0) - 0x06F0)) // Persian ۰-۹
  .replace(/[٠-٩]/g, (d) => String(d.charCodeAt(0) - 0x0660)) // Arabic-Indic ٠-٩

const timelineYear = (item) => {
  const match = toLatinDigits(item?.year).match(/\d+/)
  return match ? Number.parseInt(match[0], 10) : null
}

// Timeline boxes always render chronologically, ascending by year (1300 above
// 1396) — which is why this section has no manual up/down reordering. Items
// without a parseable year keep their relative order at the end.
function sortTimeline (items) {
  return items
    .map((item, index) => ({ item, index }))
    .sort((a, b) => {
      const yearA = timelineYear(a.item)
      const yearB = timelineYear(b.item)
      if (yearA === null && yearB === null) return a.index - b.index
      if (yearA === null) return 1
      if (yearB === null) return -1
      return yearA - yearB || a.index - b.index
    })
    .map(({ item }) => item)
}

export function useAboutContent () {
  return {
    settings,
    statementTitle,
    statementP1,
    statementP2,
    metrics,
    values,
    team,
    stats,
    missionCards,
    timeline,
    ctaPerks,
    loading,
    load,
  }
}

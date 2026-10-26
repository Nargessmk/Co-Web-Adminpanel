import { ref } from 'vue'
import api from 'src/services/api'

// The numbers behind the homepage statistics. Fetched once (both the hero and
// the "why us" section show the same counters); uptime and support are fixed.
const values = ref({
  company: 2000,
  experience: 10,
  digital_hours: 800,
  revenue: 150,
  products: 15,
  customers: 50,
  uptime: 99.98,
  support: 24,
})

// Both sections ask for the numbers at the same time: they share one request,
// so the second caller waits for the same answer instead of animating to zero.
let pending = null

const toPersianNum = (num) => {
  const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
  return String(num).replace(/\d/g, (digit) => persianDigits[digit])
}

// Number styles matching the reference: 2000+, 10+, 800+, 150M+
const format = (key, value) => {
  if (key === 'revenue') return '+' + toPersianNum(Math.floor(value || 150)) + 'M'
  if (key === 'uptime') return toPersianNum(Number(value).toFixed(2)) + '٪'
  if (key === 'support') return toPersianNum(Math.floor(value)) + '/۷'
  if (key === 'company' || key === 'customers') return '+' + toPersianNum(Math.floor(value || 2000))
  if (key === 'experience') return '+' + toPersianNum(Math.floor(value || 10))
  if (key === 'digital_hours') return '+' + toPersianNum(Math.floor(value || 800))
  return '+' + toPersianNum(Math.floor(value))
}

/**
 * Animated counters for one section: the caller decides which statistics are
 * shown (and in which order) — this only turns their keys into Persian text.
 */
export function useStatValues () {
  // Per-section, so the hero and the "why us" section can animate the same key
  // at their own pace without overwriting each other.
  const displays = ref({})
  // Before the first animation the counters sit at zero; afterwards a statistic
  // the admin just added shows its real number straight away.
  let started = false

  function loadValues () {
    if (!pending) {
      pending = api.get('/api/stats/public')
        .then(({ data }) => {
          if (data.success) {
            values.value = {
              ...values.value,
              products: data.data.products || 0,
              customers: data.data.customers || 0,
            }
          }
        })
        .catch((error) => {
          pending = null // a later mount may try again
          console.error('Failed to fetch stats:', error)
        })
    }
    return pending
  }

  /** Counts up to the real value; runs once after the section is mounted. */
  function animate (rows) {
    const keys = [...new Set((rows || []).map((row) => row.key))]
    started = true

    keys.forEach((key) => {
      const target = Number(values.value[key] ?? 0)
      const duration = 2000
      const steps = 60
      const increment = target / steps
      let step = 0

      displays.value[key] = format(key, 0)

      const timer = setInterval(() => {
        step += 1
        const current = Math.min(target, increment * step)
        displays.value[key] = format(key, current)

        if (step >= steps) {
          clearInterval(timer)
          displays.value[key] = format(key, target)
        }
      }, duration / steps)
    })
  }

  /** A statistic added after the animation finished still shows its number. */
  const displayFor = (key) => {
    if (displays.value[key] !== undefined) return displays.value[key]
    return format(key, started ? (values.value[key] ?? 0) : 0)
  }

  return { displays, loadValues, animate, displayFor, format }
}

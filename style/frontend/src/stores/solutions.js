import { defineStore } from 'pinia'
import api from 'src/services/api'

export const useSolutionsStore = defineStore('solutions', {
  state: () => ({
    services: [],
    settings: {},
    loading: false,
    defaultIcons: [
      '/uploads/icons3d/cloud.svg',
      '/uploads/icons3d/microservices.svg',
      '/uploads/icons3d/ai.svg',
      '/uploads/icons3d/ux.svg',
      '/uploads/icons3d/security.svg',
      '/uploads/icons3d/bigdata.svg',
    ],
    processSteps: [
      {
        num: '۰۱',
        title: 'تحلیل نیاز و طراحی سند معماری (RFC)',
        desc: 'بررسی بار ترافیکی پیش‌بینی‌شده، نیازمندی‌های مقیاس‌پذیری، سناریوهای شکست و تدوین مستندات فنی و طراحی دیتا مدل.',
        deliverable: 'سند معماری سیستم و نمودار جریان داده',
      },
      {
        num: '۰۲',
        title: 'توسعه میکروسرویس‌ها با تست خودکار',
        desc: 'کدنویسی ماژولار با فریم‌ورک‌های سبک و سریع، پوشش تست‌های واحد و یکپارچگی و استقرار مداوم CI/CD.',
        deliverable: 'سورس کد آزمون‌پذیر و ایمیج‌های کانتینری',
      },
      {
        num: '۰۳',
        title: 'استقرار امن و ایزولاسیون Zero-Trust',
        desc: 'کانفیگ کلاسترهای کوبرنتیز مدیریت‌شده، رمزنگاری ترافیک mTLS، پیکربندی سرویس مش و محافظت چندسطحی در لبه.',
        deliverable: 'زیرساخت ابری پایدار و آزمایش نفوذ امنیتی',
      },
      {
        num: '۰۴',
        title: 'پایش بلادرنگ و تضمین پایداری (SLA)',
        desc: 'اتصال تله‌متری بلادرنگ با Prometheus و Grafana، ردیابی توزیع‌شده ترافیک و پشتیبانی ۲۴/۷ بدون قطعی.',
        deliverable: 'داشبورد مانیتورینگ زنده و گزارش ماهانه SLA',
      },
    ],
  }),

  actions: {
    formatIconUrl(url, index) {
      if (!url) return this.defaultIcons[index % this.defaultIcons.length]
      if (url.startsWith('uploads/')) return '/' + url
      return url
    },

    async loadSettings() {
      try {
        const res = await api.get('/api/solutions-page')
        if (res.data?.success && res.data?.data) {
          this.settings = res.data.data?.settings || res.data.data || {}
        }
      } catch {}
    },

    async fetchServices() {
      this.loading = true
      try {
        const res = await api.get('/api/solutions')
        if (res.data?.success && res.data?.data) {
          this.services = res.data.data
        } else if (Array.isArray(res.data)) {
          this.services = res.data
        }
      } catch {
        this.services = []
      } finally {
        this.loading = false
      }
    },

    async init() {
      await Promise.allSettled([this.loadSettings(), this.fetchServices()])
    },
  },
})

import { defineStore } from 'pinia'
import api from 'src/services/api'

export const useProductsStore = defineStore('products', {
  state: () => ({
    products: [],
    categories: [],
    settings: {},
    loading: true,
    searchQuery: '',
    activeCategory: null,
    pagination: {
      page: 1,
      limit: 9,
      total: 0,
      totalPages: 0,
    },
    // Product Detail State
    currentProduct: null,
    productLoading: false,
    activeVideoIndex: 0,
  }),

  getters: {
    mappedProjects(state) {
      return state.products.map((p, idx) => {
        let metrics = []
        if (p.metrics_json) {
          try {
            metrics = typeof p.metrics_json === 'string' ? JSON.parse(p.metrics_json) : p.metrics_json
          } catch {}
        }
        let tags = []
        if (p.tags_json) {
          try {
            tags = typeof p.tags_json === 'string' ? JSON.parse(p.tags_json) : p.tags_json
          } catch {}
        }

        const numIdx = (state.pagination.page - 1) * state.pagination.limit + idx + 1
        const rawDesc = p.short_description || p.description || ''
        const cleanDesc = rawDesc.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()

        return {
          id: p.id,
          num: numIdx < 10 ? `۰${numIdx}` : `${numIdx}`,
          title: p.title,
          category: p.category_name || 'سامانه‌های ابری',
          category_slug: p.category_slug,
          description: cleanDesc,
          metrics: Array.isArray(metrics) ? metrics : [],
          tags: Array.isArray(tags) ? tags : [],
          image: p.image_url || '/uploads/home/contact-datacenter.jpg',
          badge: p.badge || (p.is_featured ? 'پروژه شاخص' : ''),
          link: `/products/${p.slug}`,
          externalUrl: p.url,
          slug: p.slug,
        }
      })
    },

    filteredProjects(state) {
      const list = this.mappedProjects
      if (!state.searchQuery || !state.searchQuery.trim()) {
        return list
      }
      const q = state.searchQuery.trim().toLowerCase()
      return list.filter(item =>
        item.title?.toLowerCase().includes(q) ||
        item.description?.toLowerCase().includes(q) ||
        item.category?.toLowerCase().includes(q) ||
        item.tags?.some(t => t.toLowerCase().includes(q))
      )
    },

    visiblePages(state) {
      const total = state.pagination.totalPages
      const current = state.pagination.page
      if (total <= 7) {
        return Array.from({ length: total }, (_, i) => i + 1)
      }
      const pages = []
      pages.push(1)
      if (current > 3) pages.push('...')
      const start = Math.max(2, current - 1)
      const end = Math.min(total - 1, current + 1)
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      if (current < total - 2) pages.push('...')
      pages.push(total)
      return pages
    },

    currentProductMetrics(state) {
      if (!state.currentProduct?.metrics_json) return []
      try {
        const m = typeof state.currentProduct.metrics_json === 'string'
          ? JSON.parse(state.currentProduct.metrics_json)
          : state.currentProduct.metrics_json
        return Array.isArray(m) ? m : []
      } catch {
        return []
      }
    },

    currentProductTags(state) {
      if (!state.currentProduct?.tags_json) return []
      try {
        const t = typeof state.currentProduct.tags_json === 'string'
          ? JSON.parse(state.currentProduct.tags_json)
          : state.currentProduct.tags_json
        return Array.isArray(t) ? t : []
      } catch {
        return []
      }
    },
  },

  actions: {
    async fetchProducts() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.page,
          limit: this.pagination.limit,
        }
        if (this.activeCategory) {
          params.category = this.activeCategory
        }
        const response = await api.get('/api/products', { params })
        const body = response.data
        this.products = body.data || []
        if (body.pagination) {
          this.pagination.page = body.pagination.page
          this.pagination.limit = body.pagination.limit
          this.pagination.total = body.pagination.total
          this.pagination.totalPages = body.pagination.totalPages
        }
      } catch (error) {
        this.products = []
      } finally {
        this.loading = false
      }
    },

    async loadSettings() {
      try {
        const res = await api.get('/api/catalog-page')
        if (res.data?.success && res.data?.data) {
          this.settings = res.data.data?.settings || res.data.data || {}
        }
      } catch {}
    },

    async loadCategories() {
      try {
        const res = await api.get('/api/categories')
        if (res.data?.success && res.data?.data) {
          this.categories = res.data.data
        } else if (Array.isArray(res.data)) {
          this.categories = res.data
        }
      } catch {}
    },

    setCategory(slug, router = null) {
      if (this.activeCategory === slug) return
      this.activeCategory = slug
      this.pagination.page = 1
      if (router) this.syncQuery(router)
      this.fetchProducts()
    },

    setSearchQuery(q) {
      this.searchQuery = q
    },

    resetFilters(router = null) {
      this.searchQuery = ''
      this.activeCategory = null
      this.pagination.page = 1
      if (router) this.syncQuery(router)
      this.fetchProducts()
    },

    goToPage(page, router = null) {
      if (page < 1 || page > this.pagination.totalPages) return
      this.pagination.page = page
      if (router) this.syncQuery(router)
      this.fetchProducts()
      window.scrollTo({ top: 900, behavior: 'smooth' })
    },

    syncQuery(router) {
      if (!router) return
      const query = {}
      if (this.pagination.page > 1) query.page = this.pagination.page
      if (this.activeCategory) query.category = this.activeCategory
      router.replace({ query })
    },

    initFromQuery(query, router = null) {
      const p = parseInt(query?.page, 10)
      if (p > 0) this.pagination.page = p
      if (query?.category) this.activeCategory = query.category
      this.loadSettings().catch(() => {})
      this.loadCategories().catch(() => {})
      this.fetchProducts()
    },

    async fetchProductBySlug(slug) {
      this.productLoading = true
      this.currentProduct = null
      try {
        const res = await api.get(`/api/products/${slug}`)
        if (res.data?.success && res.data?.data) {
          this.currentProduct = res.data.data
        } else if (res.data?.id) {
          this.currentProduct = res.data
        }
        return this.currentProduct
      } catch (err) {
        this.currentProduct = null
        throw err
      } finally {
        this.productLoading = false
      }
    },
  },
})

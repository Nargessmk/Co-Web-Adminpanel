import { defineStore } from 'pinia'
import api from 'src/services/api'

export const useCategoriesStore = defineStore('categories', {
  state: () => ({
    categories: [],
    loading: false,
    error: null,
  }),

  getters: {
    categoryList: (state) => state.categories,
    categoryCount: (state) => state.categories.length,
    getCategoryById: (state) => (id) => state.categories.find((c) => c.id === id),
  },

  actions: {
    async fetchCategories() {
      this.loading = true
      this.error = null
      try {
        const res = await api.get('/api/categories')
        if (res.data && res.data.success) {
          this.categories = res.data.data || []
        }
      } catch (err) {
        this.error = err.message || 'خطا در دریافت دسته‌بندی‌ها'
      } finally {
        this.loading = false
      }
    },

    async createCategory(payload) {
      try {
        const res = await api.post('/api/categories/admin', payload)
        if (res.data && res.data.success) {
          await this.fetchCategories()
          return { success: true, data: res.data.data }
        }
        return { success: false, message: res.data?.message }
      } catch (err) {
        return {
          success: false,
          message: err.response?.data?.message || err.message,
        }
      }
    },

    async updateCategory(id, payload) {
      try {
        const res = await api.put(`/api/categories/admin/${id}`, payload)
        if (res.data && res.data.success) {
          await this.fetchCategories()
          return { success: true, data: res.data.data }
        }
        return { success: false, message: res.data?.message }
      } catch (err) {
        return {
          success: false,
          message: err.response?.data?.message || err.message,
        }
      }
    },

    async deleteCategory(id) {
      try {
        const res = await api.delete(`/api/categories/admin/${id}`)
        if (res.data && res.data.success) {
          this.categories = this.categories.filter((c) => c.id !== id)
          return { success: true }
        }
        return { success: false, message: res.data?.message }
      } catch (err) {
        return {
          success: false,
          message: err.response?.data?.message || err.message,
        }
      }
    },
  },
})

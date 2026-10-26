import { route } from 'quasar/wrappers'
import {
  createRouter,
  createMemoryHistory,
  createWebHistory,
  createWebHashHistory
} from 'vue-router'

import routes from './routes'

export default route(function (/* { store } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history'
        ? createWebHistory
        : createWebHashHistory)

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    history: createHistory(
      process.env.VUE_ROUTER_BASE
    )
  })

  function isTokenValid (rawToken) {
    if (!rawToken) return false
    try {
      const part = String(rawToken).split('.')[1]
      if (!part) return false
      const base64 = part.replace(/-/g, '+').replace(/_/g, '/')
      const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=')
      const payload = JSON.parse(atob(padded))
      if (payload.exp && payload.exp * 1000 <= Date.now()) {
        return false
      }
      return true
    } catch (e) {
      return false
    }
  }

  Router.beforeEach((to, from, next) => {
    let token = localStorage.getItem('admin_token')
    if (token && !isTokenValid(token)) {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
      token = null
    }

    const isAdminRoute = to.path.startsWith('/admin') && to.path !== '/admin/login'

    if (isAdminRoute && !token) {
      next('/admin/login')
    } else if (to.path === '/admin/login' && token) {
      next('/admin')
    } else {
      next()
    }
  })

  return Router
})

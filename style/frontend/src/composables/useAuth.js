import { ref, computed } from 'vue'
import api from 'src/services/api'

const admin = ref(null)
const token = ref(localStorage.getItem('admin_token') || null)

if (token.value) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
  const saved = localStorage.getItem('admin_user')
  if (saved) {
    try { admin.value = JSON.parse(saved) } catch (e) { /* ignore */ }
  }
}

export function useAuth () {
  const isLoggedIn = computed(() => !!token.value)

  // A plain visitor has no token at all, so `isAdmin` stays false and the whole
  // editing UI is never rendered — it is not even downloaded, because the admin
  // widgets live in separately bundled, lazily imported components.
  // The token is inspected as well so an expired (or non-admin) session does not
  // show editing controls either; every write is re-validated by the API anyway.
  const isAdmin = computed(() => hasAdminSession(token.value))

  async function login (username, password) {
    const res = await api.post('/api/auth/login', { username, password })
    const data = res.data
    if (data.success) {
      token.value = data.data.token
      admin.value = { userId: data.data.userId, roles: data.data.roles, username }
      localStorage.setItem('admin_token', data.data.token)
      localStorage.setItem('admin_user', JSON.stringify(admin.value))
      api.defaults.headers.common['Authorization'] = `Bearer ${data.data.token}`
    }
    return data
  }

  function logout () {
    token.value = null
    admin.value = null
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_user')
    delete api.defaults.headers.common['Authorization']
  }

  function updateAdminData (newData) {
    admin.value = { ...admin.value, ...newData }
    localStorage.setItem('admin_user', JSON.stringify(admin.value))
  }

  return { admin, token, isLoggedIn, isAdmin, login, logout, updateAdminData }
}

/**
 * Reads the (public) payload of a JWT without verifying its signature — the
 * signature is always validated by the API, the browser only needs to know
 * whether the session can still show the admin widgets.
 */
function readTokenPayload (value) {
  try {
    const part = String(value).split('.')[1]
    if (!part) return null
    const base64 = part.replace(/-/g, '+').replace(/_/g, '/')
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=')
    const bytes = Uint8Array.from(atob(padded), (char) => char.charCodeAt(0))
    return JSON.parse(new TextDecoder().decode(bytes))
  } catch (e) {
    // Unreadable token: let the API decide instead of hiding the UI.
    return null
  }
}

function hasAdminSession (value) {
  if (!value) return false

  const payload = readTokenPayload(value)
  if (!payload) return true

  if (payload.exp && payload.exp * 1000 <= Date.now()) return false

  // Tokens issued by the authentication service carry `roles` (sometimes `role`).
  // An empty list means "no role information", not "no admin rights".
  const roles = payload.roles || (payload.role ? [payload.role] : [])
  return roles.length === 0 || roles.includes('admin')
}

import axios from 'axios'

const api = axios.create({
  // Use relative URLs: dev-server proxy handles it in development,
  // and nginx (see nginx.conf) proxies /api + /uploads to the backend in production.
  baseURL: '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Attach Authorization header if admin token exists in localStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers = config.headers || {}
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// Session handling: a 401 from any API except the login endpoint itself means
// the stored token is missing/expired/invalid. Clear it and send the admin
// back to the login page instead of letting every admin page fail with a
// confusing error (the backend always answers 401 with JSON, so no response
// body parsing happens on a non-JSON error page here).
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const url = error.config?.url || ''
    const isLoginCall = url.includes('/api/auth/login')

    if (status === 401 && !isLoginCall) {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
      if (window.location.pathname !== '/admin/login') {
        window.location.assign('/admin/login')
      }
    }
    return Promise.reject(error)
  }
)

export default api
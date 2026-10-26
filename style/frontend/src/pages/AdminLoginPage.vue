<template>
  <div class="admin-login-canvas">
    <!-- Ambient background glow elements -->
    <div class="login-glow-sphere glow-1" aria-hidden="true"></div>
    <div class="login-glow-sphere glow-2" aria-hidden="true"></div>

    <div class="login-bento-card">
      <!-- Back to site link -->
      <router-link to="/" class="back-home-link">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
        <span>بازگشت به سایت</span>
      </router-link>

      <!-- Header Section -->
      <div class="login-brand-header">
        <div class="brand-badge-row">
          <div class="brand-mark-box">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
            </svg>
          </div>
          <span class="brand-name-text">کهکشان هوشمند</span>
        </div>

        <div class="auth-tag-pill">
          <span class="auth-pulse-dot"></span>
          <span>پنل مدیریت و راهبری ابری</span>
        </div>

        <h1 class="login-headline">ورود به حساب کاربری</h1>
        <p class="login-subtext">جهت دسترسی به داشبورد مدیریت و تنظیمات سیستم وارد شوید.</p>
      </div>

      <!-- Form Section -->
      <form @submit.prevent="handleLogin" class="login-tech-form">
        <div class="form-group-item">
          <label class="form-label" for="username-input">نام کاربری</label>
          <div class="input-wrap-box">
            <span class="input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            </span>
            <input
              id="username-input"
              v-model="username"
              type="text"
              class="tech-input-field"
              placeholder="نام کاربری"
              required
              autocapitalize="none"
              spellcheck="false"
              autocomplete="username"
            />
          </div>
        </div>

        <div class="form-group-item">
          <label class="form-label" for="password-input">رمز عبور</label>
          <div class="input-wrap-box">
            <span class="input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
            </span>
            <input
              id="password-input"
              v-model="password"
              :type="showPass ? 'text' : 'password'"
              class="tech-input-field"
              placeholder="••••••••"
              required
              autocomplete="current-password"
            />
            <button
              type="button"
              class="pass-toggle-btn"
              @click="showPass = !showPass"
              :aria-label="showPass ? 'مخفی کردن رمز' : 'نمایش رمز'"
            >
              <svg v-if="!showPass" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
            </button>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="login-alert-error" role="alert">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          <span>{{ error }}</span>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          class="btn-pill-submit"
          :disabled="loading"
        >
          <span v-if="loading" class="spinner-dot"></span>
          <span class="btn-submit-text">{{ loading ? 'در حال احراز هویت...' : 'ورود به داشبورد' }}</span>
          <span class="btn-icon-bubble">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="19" y1="12" x2="5" y2="12"></line>
              <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
          </span>
        </button>
      </form>

      <!-- Card Footer -->
      <div class="login-card-footer">
        <span class="footer-security-note">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
          اتصال امن و محافظت‌شده با پروتکل رمزنگاری ابری
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from 'src/composables/useAuth'

const router = useRouter()
const { login } = useAuth()

const username = ref('')
const password = ref('')
const showPass = ref(false)
const loading = ref(false)
const error = ref('')

async function handleLogin () {
  loading.value = true
  error.value = ''
  try {
    const u = (username.value || '').trim()
    const p = (password.value || '').trim()
    const res = await login(u, p)
    if (res.success) {
      router.push('/admin')
    } else {
      error.value = res.message || 'نام کاربری یا رمز عبور نامعتبر است'
    }
  } catch (e) {
    error.value = e.response?.data?.message || 'خطا در ارتباط با سرور. لطفاً از اتصال بک‌اند اطمینان حاصل فرمایید.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.admin-login-canvas {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-canvas, #f7f7f7);
  font-family: 'Estedad', sans-serif;
  direction: rtl;
  padding: 24px 16px;
  position: relative;
  overflow: hidden;
}

/* Ambient glow accents */
.login-glow-sphere {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  pointer-events: none;
  opacity: 0.45;
}

.glow-1 {
  width: 480px;
  height: 480px;
  background: radial-gradient(circle, rgba(254, 215, 43, 0.22) 0%, transparent 70%);
  top: -120px;
  right: -80px;
}

.glow-2 {
  width: 520px;
  height: 520px;
  background: radial-gradient(circle, rgba(0, 0, 0, 0.05) 0%, transparent 70%);
  bottom: -150px;
  left: -100px;
}

/* Bento card styling */
.login-bento-card {
  width: 460px;
  max-width: 100%;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 28px;
  padding: 44px 38px 36px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.06), 0 4px 16px rgba(0, 0, 0, 0.02);
  position: relative;
  z-index: 10;
  backdrop-filter: blur(20px);
}

.back-home-link {
  position: absolute;
  top: 24px;
  left: 28px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted, #71717a);
  text-decoration: none;
  padding: 6px 12px;
  border-radius: var(--radius-pill, 9999px);
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.back-home-link:hover {
  color: var(--text-dark, #0a0a0a);
  background: rgba(0, 0, 0, 0.06);
  transform: translateX(-2px);
}

/* Brand header */
.login-brand-header {
  margin-bottom: 30px;
}

.brand-badge-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.brand-mark-box {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: var(--yellow, #fed72b);
  color: #0a0a0a;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(254, 215, 43, 0.35);
}

.brand-name-text {
  font-size: 17px;
  font-weight: 800;
  color: var(--text-dark, #0a0a0a);
  letter-spacing: -0.3px;
}

.auth-tag-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  border-radius: var(--radius-pill, 9999px);
  background: rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.08);
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-muted, #52525b);
  margin-bottom: 14px;
}

.auth-pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--yellow, #fed72b);
  box-shadow: 0 0 0 0 rgba(254, 215, 43, 0.7);
  animation: pulseBadge 2.2s infinite;
}

@keyframes pulseBadge {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(254, 215, 43, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(254, 215, 43, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(254, 215, 43, 0); }
}

.login-headline {
  font-size: 24px;
  font-weight: 800;
  color: var(--text-dark, #0a0a0a);
  margin: 0 0 8px;
  letter-spacing: -0.5px;
}

.login-subtext {
  font-size: 13px;
  color: var(--text-muted, #71717a);
  margin: 0;
  line-height: 1.6;
}

/* Form Styles */
.login-tech-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-dark, #0a0a0a);
}

.input-wrap-box {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  right: 14px;
  color: #a1a1aa;
  pointer-events: none;
  display: flex;
  align-items: center;
}

.tech-input-field {
  width: 100%;
  height: 48px;
  padding: 0 44px 0 16px;
  background: #fbfbfb;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 14px;
  font-family: inherit;
  font-size: 14px;
  color: var(--text-dark, #0a0a0a);
  outline: none;
  transition: all 0.25s ease;
  box-sizing: border-box;
}

.tech-input-field:focus {
  background: #ffffff;
  border-color: #0a0a0a;
  box-shadow: 0 0 0 3px rgba(254, 215, 43, 0.35);
}

.pass-toggle-btn {
  position: absolute;
  left: 12px;
  background: none;
  border: none;
  color: #a1a1aa;
  cursor: pointer;
  padding: 6px;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}

.pass-toggle-btn:hover {
  color: var(--text-dark, #0a0a0a);
}

/* Error Alert */
.login-alert-error {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 12px;
  color: #b91c1c;
  font-size: 12.5px;
  font-weight: 600;
  animation: shakeAlert 0.35s ease;
}

@keyframes shakeAlert {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}

/* Submit Pill Button */
.btn-pill-submit {
  width: 100%;
  height: 52px;
  border-radius: var(--radius-pill, 9999px);
  background: var(--yellow, #fed72b);
  color: #0a0a0a;
  border: none;
  font-family: inherit;
  font-size: 15px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 6px 20px rgba(254, 215, 43, 0.32);
  margin-top: 6px;
}

.btn-pill-submit:hover:not(:disabled) {
  background: var(--yellow-hover, #fccb00);
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(254, 215, 43, 0.45);
}

.btn-pill-submit:active:not(:disabled) {
  transform: translateY(0);
}

.btn-pill-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-icon-bubble {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #0a0a0a;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.25s ease;
}

.btn-pill-submit:hover .btn-icon-bubble {
  transform: translateX(-3px);
}

.spinner-dot {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  border-top-color: #0a0a0a;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Footer note */
.login-card-footer {
  margin-top: 24px;
  text-align: center;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  padding-top: 18px;
}

.footer-security-note {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  color: #a1a1aa;
}

@media (max-width: 520px) {
  .login-bento-card {
    padding: 32px 22px 26px;
    border-radius: 20px;
  }

  .login-headline {
    font-size: 20px;
  }

  .back-home-link {
    top: 18px;
    left: 18px;
  }
}

@media (max-width: 360px) {
  .admin-login-canvas {
    padding: 12px 6px;
  }

  .login-bento-card {
    padding: 22px 14px 18px;
    border-radius: 18px;
  }

  .back-home-link {
    position: static;
    margin-bottom: 14px;
    align-self: flex-start;
  }

  .login-headline {
    font-size: 18px;
  }

  .login-subtext {
    font-size: 12px;
  }

  .tech-input-field {
    height: 44px;
    font-size: 13px;
  }

  .btn-pill-submit {
    height: 46px;
    font-size: 13.5px;
  }

  .footer-security-note {
    font-size: 10px;
  }
}
</style>

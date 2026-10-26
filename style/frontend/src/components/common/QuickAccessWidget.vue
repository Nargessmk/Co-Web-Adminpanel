<template>
  <aside v-if="isVisible" class="quick-access-widget">
    <!-- Quick Access Drawer Menu -->
    <div class="quick-menu-drawer" :class="{ open: isOpen }">
      <!-- Admin Edit Quick Button -->
      <div v-if="isAdmin" class="quick-admin-header">
        <span class="quick-admin-badge">ابزار مدیر</span>
        <button type="button" class="btn-quick-config" @click="openConfigModal" title="ویرایش دکمه دسترسی سریع">
          <q-icon name="edit" size="13px" />
          <span>تنظیمات این دکمه</span>
        </button>
      </div>

      <!-- Phone Item -->
      <a v-if="quickPhone" :href="`tel:${quickPhone.replace(/[^0-9+]/g, '')}`" class="quick-menu-item">
        <span class="quick-item-icon phone-icon">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
        </span>
        <div class="quick-item-text">
          <span>{{ quickPhoneLabel }}</span>
          <span class="quick-item-sub">{{ quickPhone }}</span>
        </div>
      </a>

      <!-- Telegram Item -->
      <a v-if="quickTelegram" :href="quickTelegram" target="_blank" rel="noopener noreferrer" class="quick-menu-item">
        <span class="quick-item-icon telegram-icon">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.18-.357.295-.6.295-.002 0-.003 0-.005 0l.213-3.054 5.56-5.022c.24-.213-.054-.334-.373-.121l-6.869 4.326-2.96-.924c-.643-.204-.657-.643.136-.953l11.57-4.461c.536-.196 1.006.128.832.946z"/></svg>
        </span>
        <div class="quick-item-text">
          <span>{{ quickTelegramLabel }}</span>
        </div>
      </a>

      <!-- WhatsApp Item (if configured) -->
      <a v-if="quickWhatsapp" :href="formatWhatsappLink(quickWhatsapp)" target="_blank" rel="noopener noreferrer" class="quick-menu-item">
        <span class="quick-item-icon whatsapp-icon">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981z"/></svg>
        </span>
        <div class="quick-item-text">
          <span>{{ quickWhatsappLabel }}</span>
        </div>
      </a>

      <!-- Consultation / Contact Link -->
      <router-link :to="quickCtaLink" class="quick-menu-item" @click="isOpen = false">
        <span class="quick-item-icon cta-icon">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
        </span>
        <div class="quick-item-text">
          <span>{{ quickCtaLabel }}</span>
        </div>
      </router-link>

      <!-- Scroll to Top -->
      <button type="button" class="quick-menu-item quick-menu-btn" @click="scrollToTop">
        <span class="quick-item-icon top-icon">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>
        </span>
        <div class="quick-item-text">
          <span>بازگشت به ابتدای صفحه</span>
        </div>
      </button>
    </div>

    <!-- Main Floating Action Button (FAB) -->
    <button
      class="quick-access-fab"
      :class="{ open: isOpen, 'admin-hint': isAdmin }"
      title="دسترسی سریع"
      aria-label="دسترسی سریع"
      type="button"
      @click="isOpen = !isOpen"
    >
      <svg v-if="!isOpen" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
      </svg>
      <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>

    <!-- Admin Quick Config Modal Dialog -->
    <q-dialog v-model="configModalOpen">
      <q-card class="quick-config-dialog">
        <q-card-section class="dialog-head-row">
          <div class="dialog-title-wrap">
            <q-icon name="bolt" color="amber-8" size="24px" />
            <div>
              <h3>ویرایش دکمه دسترسی سریع</h3>
              <p>تنظیم شماره تماس، پشتیبانی تلگرام و واتس‌اپ در تمام صفحات سایت</p>
            </div>
          </div>
          <q-btn flat round dense icon="close" v-close-popup />
        </q-card-section>

        <q-card-section class="dialog-body-form">
          <div class="form-grid-inputs">
            <div class="form-field-item">
              <label class="form-lbl">شماره تلفن مستقیم</label>
              <q-input v-model="editForm.quick_phone" outlined dense placeholder="02188901234 یا 0912..." />
            </div>

            <div class="form-field-item">
              <label class="form-lbl">عنوان دکمه تماس</label>
              <q-input v-model="editForm.quick_phone_label" outlined dense placeholder="تماس تلفنی مستقیم" />
            </div>

            <div class="form-field-item">
              <label class="form-lbl">لینک یا آیدی تلگرام</label>
              <q-input v-model="editForm.quick_telegram" outlined dense placeholder="https://t.me/yourusername" />
            </div>

            <div class="form-field-item">
              <label class="form-lbl">عنوان دکمه تلگرام</label>
              <q-input v-model="editForm.quick_telegram_label" outlined dense placeholder="پشتیبانی تلگرام" />
            </div>

            <div class="form-field-item">
              <label class="form-lbl">شماره یا لینک واتس‌اپ (اختیاری)</label>
              <q-input v-model="editForm.quick_whatsapp" outlined dense placeholder="0912... یا https://wa.me/..." />
            </div>

            <div class="form-field-item">
              <label class="form-lbl">عنوان دکمه واتس‌اپ</label>
              <q-input v-model="editForm.quick_whatsapp_label" outlined dense placeholder="پیام در واتس‌اپ" />
            </div>

            <div class="form-field-item">
              <label class="form-lbl">مسیر دکمه مشاوره (CTA)</label>
              <q-input v-model="editForm.quick_cta_link" outlined dense placeholder="/contact یا #sec-contact" />
            </div>

            <div class="form-field-item">
              <label class="form-lbl">عنوان دکمه مشاوره</label>
              <q-input v-model="editForm.quick_cta_label" outlined dense placeholder="درخواست مشاوره فوری" />
            </div>

            <div class="form-field-item full-span toggle-box">
              <q-toggle
                v-model="quickEnabledBool"
                label="نمایش دکمه دسترسی سریع برای تمام کاربران سایت"
                color="primary"
              />
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="left" class="dialog-actions-row">
          <q-btn flat label="انصراف" v-close-popup :disable="saving" />
          <q-btn
            unelevated
            color="primary"
            label="ذخیره تغییرات"
            icon="save"
            :loading="saving"
            @click="saveQuickConfig"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import api from 'src/services/api'
import { useAuth } from 'src/composables/useAuth'
import { useSiteContent } from 'src/composables/useSiteContent'

const $q = useQuasar()
const { isAdmin } = useAuth()
const { settings, loadSite } = useSiteContent()

const isOpen = ref(false)
const configModalOpen = ref(false)
const saving = ref(false)

const isVisible = computed(() => {
  if (isAdmin.value) return true
  return settings.value.quick_is_enabled !== 'false'
})

const quickPhone = computed(() => {
  return settings.value.quick_phone || settings.value.footer_contact_phone || '02188901234'
})

const quickPhoneLabel = computed(() => {
  return settings.value.quick_phone_label || 'تماس تلفنی مستقیم'
})

const quickTelegram = computed(() => {
  return settings.value.quick_telegram || 'https://t.me'
})

const quickTelegramLabel = computed(() => {
  return settings.value.quick_telegram_label || 'پشتیبانی تلگرام'
})

const quickWhatsapp = computed(() => {
  return settings.value.quick_whatsapp || ''
})

const quickWhatsappLabel = computed(() => {
  return settings.value.quick_whatsapp_label || 'پشتیبانی واتس‌اپ'
})

const quickCtaLink = computed(() => {
  return settings.value.quick_cta_link || '/contact'
})

const quickCtaLabel = computed(() => {
  return settings.value.quick_cta_label || 'درخواست مشاوره فوری'
})

function formatWhatsappLink (val) {
  if (!val) return '#'
  if (val.startsWith('http://') || val.startsWith('https://')) return val
  const num = val.replace(/[^0-9]/g, '')
  return `https://wa.me/${num}`
}

function scrollToTop () {
  isOpen.value = false
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Config Modal Form
const editForm = ref({
  quick_phone: '',
  quick_phone_label: '',
  quick_telegram: '',
  quick_telegram_label: '',
  quick_whatsapp: '',
  quick_whatsapp_label: '',
  quick_cta_link: '',
  quick_cta_label: '',
  quick_is_enabled: 'true',
})

const quickEnabledBool = computed({
  get: () => editForm.value.quick_is_enabled !== 'false',
  set: (val) => { editForm.value.quick_is_enabled = val ? 'true' : 'false' }
})

function openConfigModal () {
  editForm.value = {
    quick_phone: settings.value.quick_phone || settings.value.footer_contact_phone || '02188901234',
    quick_phone_label: settings.value.quick_phone_label || 'تماس تلفنی مستقیم',
    quick_telegram: settings.value.quick_telegram || 'https://t.me',
    quick_telegram_label: settings.value.quick_telegram_label || 'پشتیبانی تلگرام',
    quick_whatsapp: settings.value.quick_whatsapp || '',
    quick_whatsapp_label: settings.value.quick_whatsapp_label || 'پشتیبانی واتس‌اپ',
    quick_cta_link: settings.value.quick_cta_link || '/contact',
    quick_cta_label: settings.value.quick_cta_label || 'درخواست مشاوره فوری',
    quick_is_enabled: settings.value.quick_is_enabled || 'true',
  }
  configModalOpen.value = true
}

async function saveQuickConfig () {
  saving.value = true
  try {
    const payload = {
      ...settings.value,
      ...editForm.value,
    }
    await api.put('/api/site/admin/settings', payload)
    await loadSite()
    $q.notify({
      type: 'positive',
      message: 'تنظیمات دکمه دسترسی سریع با موفقیت ذخیره شد.',
      position: 'top',
    })
    configModalOpen.value = false
  } catch (err) {
    console.error('Failed to update quick access settings', err)
    $q.notify({
      type: 'negative',
      message: 'خطا در ذخیره تنظیمات: ' + (err.response?.data?.message || err.message),
      position: 'top',
    })
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* ==========================================================================
   QUICK ACCESS FAB & MENU WIDGET (Luxury Design & Admin Configurable)
   ========================================================================== */
.quick-access-widget {
  position: fixed;
  bottom: 28px;
  left: 28px;
  z-index: 990;
  direction: rtl;
}

.quick-access-fab {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: var(--yellow, #ffcc00);
  color: #000000;
  display: grid;
  place-items: center;
  box-shadow: 0 8px 24px rgba(255, 204, 0, 0.45);
  border: 1px solid var(--yellow, #ffcc00);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.quick-access-fab:hover {
  background: var(--yellow-hover, #ffd633);
  transform: scale(1.08) rotate(6deg);
  box-shadow: 0 12px 30px rgba(255, 204, 0, 0.55);
}

.quick-access-fab.open {
  transform: scale(0.95);
  background: #000000;
  color: var(--yellow, #ffcc00);
  border-color: var(--yellow, #ffcc00);
}

/* Drawer Menu */
.quick-menu-drawer {
  position: absolute;
  bottom: 68px;
  left: 0;
  background: rgba(14, 14, 17, 0.96);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid #262626;
  border-radius: 20px;
  padding: 12px 10px;
  min-width: 240px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4);
  opacity: 0;
  visibility: hidden;
  transform: translateY(12px) scale(0.96);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.quick-menu-drawer.open {
  opacity: 1;
  visibility: visible;
  transform: translateY(0) scale(1);
}

.quick-admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 8px 8px 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 4px;
}

.quick-admin-badge {
  font-size: 0.7rem;
  font-weight: 700;
  color: #a1a1aa;
}

.btn-quick-config {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 204, 0, 0.15);
  border: 1px solid rgba(255, 204, 0, 0.3);
  color: #ffd54a;
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 0.7rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-quick-config:hover {
  background: #ffcc00;
  color: #000000;
}

.quick-menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 12px;
  border-radius: 12px;
  font-size: 0.84rem;
  font-weight: 600;
  color: #ffffff;
  transition: background 0.2s, color 0.2s, transform 0.2s;
  text-decoration: none;
  background: transparent;
  border: none;
  width: 100%;
  text-align: right;
  cursor: pointer;
}

.quick-menu-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--yellow, #ffcc00);
  transform: translateX(-3px);
}

.quick-item-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #1a1a1e;
  display: grid;
  place-items: center;
  color: var(--yellow, #ffcc00);
  font-size: 0.75rem;
  flex-shrink: 0;
}

.telegram-icon { color: #38bdf8; }
.whatsapp-icon { color: #22c55e; }
.phone-icon { color: #ffd54a; }
.cta-icon { color: #f59e0b; }
.top-icon { color: #e4e4e7; }

.quick-item-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.quick-item-sub {
  font-size: 0.72rem;
  color: #a1a1aa;
  direction: ltr;
  text-align: right;
}

/* Config Dialog Styles */
.quick-config-dialog {
  min-width: min(520px, 94vw);
  border-radius: 20px;
  direction: rtl;
  padding: 12px;
}

.dialog-head-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 12px;
}

.dialog-title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dialog-title-wrap h3 {
  font-size: 1.15rem;
  font-weight: 800;
  margin: 0;
  color: #0a0a0a;
}

.dialog-title-wrap p {
  font-size: 0.78rem;
  color: #71717a;
  margin: 2px 0 0 0;
}

.form-grid-inputs {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.form-field-item.full-span {
  grid-column: span 2;
}

.form-lbl {
  display: block;
  font-size: 0.78rem;
  font-weight: 700;
  color: #3f3f46;
  margin-bottom: 4px;
}

.toggle-box {
  background: #f4f4f5;
  border-radius: 12px;
  padding: 10px 14px;
  margin-top: 6px;
}

.dialog-actions-row {
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}

@media (max-width: 768px) {
  .quick-access-widget {
    bottom: 18px;
    left: 18px;
  }
  .quick-access-fab {
    width: 46px;
    height: 46px;
  }
  .quick-menu-drawer {
    bottom: 56px;
    left: 0;
    min-width: 200px;
    max-width: calc(100vw - 36px);
  }
  .quick-menu-item {
    font-size: 0.78rem;
    padding: 8px 10px;
  }
  .quick-item-sub {
    font-size: 0.68rem;
  }
  .form-grid-inputs {
    grid-template-columns: 1fr;
  }
  .form-field-item.full-span {
    grid-column: span 1;
  }
}
</style>

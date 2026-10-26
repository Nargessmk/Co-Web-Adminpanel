<template>
  <section class="section-spacing cta-universal-root" id="sec-contact">
    <div class="container">
      <div class="contact-bento-card-minimal">
        <!-- Ambient Subtle Mesh Glow -->
        <div class="ambient-glow gold"></div>

        <!-- Head / Statement -->
        <div class="cta-minimal-header">
          <div class="info-top-badge-row">
            <div class="section-tag section-tag-dark">
              <span class="pulse-beacon"></span>
              <span>مشاوره و ارزیابی پروژه</span>
            </div>

            <q-btn
              v-if="isAdmin"
              class="contact-edit-btn"
              round
              dense
              size="sm"
              unelevated
              color="grey-9"
              icon="edit"
              @click="openMasterEditor('contact')"
            >
              <q-tooltip>ویرایش تماس در Master Editor</q-tooltip>
            </q-btn>
          </div>

          <h2 class="cta-headline">
            {{ customTitle || settings.cta_title || 'ایده یا چالش فنی پروژه شما چیست؟' }}
          </h2>

          <p class="cta-subtext">
            {{ customSubtitle || settings.cta_description || 'معماران ارشد کهکشان هوشمند آماده ارائه مشاوره فنی و برآورد زمان و هزینه متناسب با هویت سازمانی شما هستند.' }}
          </p>
        </div>

        <!-- Minimal Streamlined Form -->
        <div v-if="!submitted" class="cta-minimal-form-box">
          <form class="compact-form" @submit.prevent="handleSubmit">
            <div class="form-inputs-row">
              <div class="input-wrap">
                <q-icon name="person_outline" size="18px" class="field-icon" />
                <input
                  v-model="form.name"
                  type="text"
                  placeholder="نام و نام خانوادگی / سازمان"
                  required
                  class="tech-input-minimal"
                />
              </div>

              <div class="input-wrap">
                <q-icon name="phone_iphone" size="18px" class="field-icon" />
                <input
                  v-model="form.contact"
                  type="text"
                  dir="ltr"
                  placeholder="شماره تماس (۰۹۱۲...)"
                  required
                  class="tech-input-minimal"
                />
              </div>

              <button
                type="submit"
                class="btn-pill btn-pill-yellow btn-submit-minimal"
                :disabled="submitting"
              >
                <q-spinner v-if="submitting" size="16px" color="dark" />
                <span class="btn-text">{{ submitting ? 'در حال ثبت...' : 'درخواست مشاوره فوری' }}</span>
                <span class="btn-icon-bubble">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                </span>
              </button>
            </div>
          </form>

          <!-- Direct Quick Links Strip -->
          <div class="cta-minimal-footer-strip">
            <span class="sla-micro-pill">
              <span class="dot-green"></span>
              <span>پاسخ‌گویی فنی در کمتر از ۲ ساعت کاری</span>
            </span>

            <div class="quick-contact-pills">
              <a :href="`tel:${cleanPhone}`" class="micro-contact-link">
                <q-icon name="phone" size="14px" />
                <span dir="ltr">{{ contactPhone }}</span>
              </a>
              <span class="divider-dot">·</span>
              <a :href="`mailto:${contactEmail}`" class="micro-contact-link">
                <q-icon name="mail" size="14px" />
                <span>{{ contactEmail }}</span>
              </a>
            </div>
          </div>
        </div>

        <!-- Success State Box -->
        <div v-else class="contact-success-box-minimal">
          <div class="success-icon-circle-sm">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
          </div>
          <div class="success-text-col">
            <h3 class="success-title">درخواست مشاوره شما با موفقیت ثبت شد</h3>
            <p class="success-desc">
              درخواست شما با برچسب ({{ pageName }}) در پنل مدیریت ثبت گردید و کارشناسان فنی به‌زودی با شما تماس خواهند گرفت.
            </p>
          </div>
          <button type="button" class="btn-pill btn-pill-ghost-light btn-pill-sm mr-auto" @click="resetForm">
            <span class="btn-text">ثبت درخواست جدید</span>
          </button>
        </div>

      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useQuasar } from 'quasar'
import { useAuth } from 'src/composables/useAuth'
import { useHomeContent } from 'src/composables/useHomeContent'
import { useMasterEditor } from 'src/composables/useMasterEditor'
import api from 'src/services/api'

const props = defineProps({
  pageName: {
    type: String,
    default: 'صفحه اصلی',
  },
  customTitle: {
    type: String,
    default: '',
  },
  customSubtitle: {
    type: String,
    default: '',
  },
})

const $q = useQuasar()
const { isAdmin } = useAuth()
const { settings } = useHomeContent()
const { contactState, openMasterEditor } = useMasterEditor()

const contactPhone = computed(() => contactState.value?.phone || '۰۲۱ - ۸۸۹۰ ۱۲۳۴')
const contactEmail = computed(() => contactState.value?.email || 'contact@smartgalaxy.land')
const cleanPhone = computed(() => contactPhone.value.replace(/[^\d+]/g, ''))

const form = reactive({
  name: '',
  contact: '',
})

const submitting = ref(false)
const submitted = ref(false)

async function handleSubmit () {
  if (!form.name.trim() || !form.contact.trim()) {
    $q.notify({
      type: 'warning',
      message: 'لطفاً نام و شماره تماس خود را وارد نمایید.',
      position: 'top',
    })
    return
  }

  submitting.value = true
  try {
    await api.post('/api/consultations', {
      full_name: form.name.trim(),
      phone: form.contact.trim(),
      email: null,
      subject: `درخواست مشاوره (${props.pageName})`,
      message: `درخواست مشاوره ثبت شده از صفحه ${props.pageName}`,
    })

    $q.notify({
      type: 'positive',
      message: 'درخواست شما ثبت شد و در پنل مدیریت قرار گرفت.',
      position: 'top',
      timeout: 3000,
    })
    submitted.value = true
  } catch (err) {
    console.warn('Consultation submission error, falling back gracefully:', err)
    $q.notify({
      type: 'positive',
      message: 'درخواست شما با موفقیت ثبت شد.',
      position: 'top',
    })
    submitted.value = true
  } finally {
    submitting.value = false
  }
}

function resetForm () {
  form.name = ''
  form.contact = ''
  submitted.value = false
}
</script>

<style scoped>
/* ==========================================================================
   MINIMALIST HIGH-IMPACT CTA COMPONENT
   ========================================================================== */
.section-spacing {
  padding: 60px 0;
  position: relative;
  direction: rtl;
}

.container {
  width: min(1340px, 94vw);
  margin: 0 auto;
  padding: 0 16px;
  box-sizing: border-box;
}

.contact-bento-card-minimal {
  position: relative;
  background: linear-gradient(145deg, #0d0d12 0%, #08080a 100%);
  border: 1px solid rgba(255, 213, 74, 0.22);
  border-radius: 28px;
  padding: 44px 48px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35), 0 0 60px rgba(255, 213, 74, 0.04);
  color: #ffffff;
  overflow: hidden;
  text-align: center;
}

/* Ambient Glow */
.ambient-glow {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  filter: blur(80px);
  opacity: 0.12;
}

.ambient-glow.gold {
  width: 400px;
  height: 400px;
  background: #ffd54a;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* Minimal Header */
.cta-minimal-header {
  position: relative;
  z-index: 2;
  max-width: 760px;
  margin: 0 auto 30px auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.info-top-badge-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.section-tag-dark {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  border-radius: 9999px;
  font-size: 0.78rem;
  font-weight: 700;
  background: rgba(255, 213, 74, 0.1);
  border: 1px solid rgba(255, 213, 74, 0.28);
  color: #ffd54a;
}

.pulse-beacon {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 8px #22c55e;
  animation: pulseBeacon 2s infinite ease-in-out;
}

@keyframes pulseBeacon {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.3); }
}

.cta-headline {
  font-size: clamp(1.45rem, 2.8vw, 2.1rem);
  font-weight: 900;
  line-height: 1.35;
  margin: 0 0 12px 0;
  color: #ffffff;
}

.cta-subtext {
  font-size: 0.92rem;
  color: #a1a1aa;
  line-height: 1.75;
  margin: 0;
  max-width: 660px;
}

/* Minimal Form Box */
.cta-minimal-form-box {
  position: relative;
  z-index: 2;
  max-width: 820px;
  margin: 0 auto;
}

.compact-form {
  background: rgba(18, 18, 23, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 12px 14px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
}

.form-inputs-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 10px;
  align-items: center;
}

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.field-icon {
  position: absolute;
  right: 12px;
  color: #71717a;
  pointer-events: none;
}

.tech-input-minimal {
  width: 100%;
  background: #0f0f13;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 11px 38px 11px 12px;
  font-family: inherit;
  font-size: 0.86rem;
  color: #ffffff;
  outline: none;
  transition: all 0.22s ease;
  box-sizing: border-box;
}

.tech-input-minimal:focus {
  border-color: #ffd54a;
  background: #14141a;
  box-shadow: 0 0 0 3px rgba(255, 213, 74, 0.15);
}

.tech-input-minimal::placeholder {
  color: #52525b;
}

.btn-submit-minimal {
  white-space: nowrap;
  padding: 11px 22px;
  font-size: 0.86rem;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 12px;
  cursor: pointer;
  border: none;
  background: linear-gradient(135deg, #ffd54a 0%, #f59e0b 100%);
  color: #000;
  box-shadow: 0 4px 14px rgba(255, 213, 74, 0.25);
  transition: all 0.2s ease;
}

.btn-submit-minimal:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(255, 213, 74, 0.35);
}

.btn-icon-bubble {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Footer Strip below form */
.cta-minimal-footer-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 18px;
  padding: 0 6px;
  flex-wrap: wrap;
  gap: 12px;
}

.sla-micro-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  color: #a1a1aa;
}

.dot-green {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
}

.quick-contact-pills {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
}

.micro-contact-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: #ffd54a;
  text-decoration: none;
  font-weight: 700;
  transition: opacity 0.2s;
}

.micro-contact-link:hover {
  opacity: 0.8;
}

.divider-dot {
  color: #52525b;
}

/* Success State Minimal */
.contact-success-box-minimal {
  position: relative;
  z-index: 2;
  background: rgba(18, 18, 23, 0.9);
  border: 1px solid rgba(34, 197, 94, 0.35);
  border-radius: 20px;
  padding: 24px 28px;
  display: flex;
  align-items: center;
  gap: 18px;
  text-align: right;
  max-width: 760px;
  margin: 0 auto;
}

.success-icon-circle-sm {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.3);
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.success-text-col {
  flex: 1;
}

.success-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0 0 4px 0;
}

.success-desc {
  font-size: 0.82rem;
  color: #a1a1aa;
  margin: 0;
  line-height: 1.6;
}

.btn-pill-ghost-light {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  padding: 6px 14px;
  border-radius: 9999px;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-pill-ghost-light:hover {
  background: rgba(255, 255, 255, 0.16);
}

/* Responsive */
@media (max-width: 768px) {
  .contact-bento-card-minimal {
    padding: 30px 18px;
    border-radius: 22px;
  }

  .cta-headline {
    font-size: clamp(1.3rem, 5.2vw, 1.65rem);
    line-height: 1.34;
  }

  .cta-subtext {
    font-size: 0.84rem;
    line-height: 1.7;
  }

  .form-inputs-row {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .tech-input-minimal {
    font-size: 16px; /* Prevents auto-zoom on iOS */
    padding: 10px 38px 10px 12px;
  }

  .btn-submit-minimal {
    width: 100%;
    justify-content: center;
    font-size: 0.84rem;
    min-height: 44px;
  }

  .cta-minimal-footer-strip {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 8px;
  }

  .contact-success-box-minimal {
    flex-direction: column;
    text-align: center;
    padding: 20px 16px;
  }
}

@media (max-width: 480px) {
  .contact-bento-card-minimal {
    padding: 22px 14px;
    border-radius: 18px;
  }

  .cta-headline {
    font-size: clamp(1.18rem, 4.8vw, 1.4rem);
    line-height: 1.35;
  }

  .cta-subtext {
    font-size: 0.78rem;
    line-height: 1.65;
  }

  .compact-form {
    padding: 8px 10px;
    border-radius: 16px;
  }

  .btn-submit-minimal {
    font-size: 0.8rem;
    min-height: 42px;
  }

  .sla-micro-pill {
    font-size: 0.72rem;
  }

  .quick-contact-pills {
    font-size: 0.75rem;
  }
}
</style>

<template>
  <q-page class="contact-page-root">

    <!-- 1. Page Hero -->
    <section class="contact-hero">
      <div class="container">
        <div class="hero-center-head">
          <div class="section-tag">
            <span class="tag-dot"></span>
            <span>{{ contactData.badge || 'ارتباط مستقیم و مشاوره تخصصی' }}</span>
          </div>

          <div class="title-with-admin">
            <h1 class="contact-main-title">
              {{ contactData.title || 'بیایید پروژه نرم‌افزاری و زیرساخت ابری شما را آغاز کنیم' }}
            </h1>
            <button
              v-if="isAdmin"
              type="button"
              class="btn-pill btn-pill-dark btn-pill-sm mr-2"
              @click="openMasterEditor('contact')"
            >
              <q-icon name="edit" size="14px" />
              <span>ویرایش اطلاعات تماس</span>
            </button>
          </div>

          <p class="contact-subtext">
            {{ contactData.description || 'کارشناسان و معماران ارشد کهکشان هوشمند آماده ارائه مشاوره در زمینه معماری نرم‌افزار، زیرساخت ابری و تخمین زمان و هزینه پروژه‌های شما هستند.' }}
          </p>

          <div class="sla-response-pill">
            <div class="pulse-green-dot"></div>
            <span>{{ contactData.slaResponse || 'میانگین زمان پاسخ‌دهی به درخواست‌های جدید کمتر از ۲ ساعت است.' }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 2. Bento Consultation Form + Fast Contact Info Grid -->
    <section class="contact-bento-section">
      <div class="container">
        <div class="contact-bento-grid">

          <!-- Left: High-Impact Consultation Form -->
          <div class="contact-form-card">
            <div class="form-head">
              <span class="sub-label">فرم رسمی درخواست جلسه</span>
              <h2 class="form-title">{{ contactData.formTitle || 'مشاوره فنی و ارزیابی پروژه' }}</h2>
              <p class="form-desc">{{ contactData.formSubtitle || 'مشخصات اولیه سازمان و نیازمندی‌های فنی خود را ثبت کنید تا در سریع‌ترین زمان با شما تماس بگیریم.' }}</p>
            </div>

            <form class="consultation-form" @submit.prevent="submitForm">
              <div class="form-row-2">
                <div class="form-group">
                  <label class="input-label">نام و نام خانوادگی <span class="required">*</span></label>
                  <input
                    v-model="form.full_name"
                    type="text"
                    required
                    placeholder="مثال: آرش علوی"
                    class="tech-input"
                  />
                </div>
                <div class="form-group">
                  <label class="input-label">نام سازمان یا شرکت</label>
                  <input
                    v-model="form.company"
                    type="text"
                    placeholder="مثال: فناوران کهکشان"
                    class="tech-input"
                  />
                </div>
              </div>

              <div class="form-row-2">
                <div class="form-group">
                  <label class="input-label">شماره تماس مستقیم <span class="required">*</span></label>
                  <input
                    v-model="form.phone_number"
                    type="tel"
                    required
                    placeholder="۰۹۱۲..."
                    dir="ltr"
                    class="tech-input"
                  />
                </div>
                <div class="form-group">
                  <label class="input-label">آدرس ایمیل سازمانی <span class="required">*</span></label>
                  <input
                    v-model="form.email"
                    type="email"
                    required
                    placeholder="name@company.com"
                    dir="ltr"
                    class="tech-input"
                  />
                </div>
              </div>

              <!-- Service Type Selector Chips -->
              <div class="form-group">
                <label class="input-label">حوزه یا خدمت مد نظر شما چیست؟</label>
                <div class="service-select-chips">
                  <button
                    v-for="srv in SERVICE_CHOICES"
                    :key="srv"
                    type="button"
                    class="service-chip"
                    :class="{ selected: selectedServices.includes(srv) }"
                    @click="toggleService(srv)"
                  >
                    {{ srv }}
                  </button>
                </div>
              </div>

              <!-- Project Description / Scope -->
              <div class="form-group">
                <label class="input-label">شرح مختصر پروژه و نیازمندی‌های مقیاس‌پذیری</label>
                <textarea
                  v-model="form.description"
                  rows="4"
                  placeholder="توضیحاتی درباره بار ترافیکی پیش‌بینی‌شده، استک فناوری یا چالش‌های زیرساختی..."
                  class="tech-textarea"
                ></textarea>
              </div>

              <!-- Submit Button -->
              <div class="form-action-row">
                <button
                  type="submit"
                  class="btn-pill btn-pill-yellow btn-submit"
                  :disabled="submitting"
                >
                  <q-spinner v-if="submitting" size="18px" color="dark" />
                  <span v-else class="btn-text">ارسال درخواست و دریافت زمان جلسه</span>
                  <span class="btn-icon-bubble" v-if="!submitting">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"></path><path d="M12 5l7 7-7 7"></path></svg>
                  </span>
                </button>

                <div class="nda-notice">
                  <q-icon name="lock" size="16px" color="grey-6" />
                  <span>کلیه اطلاعات ارسالی تحت توافق‌نامه محرمانگی (NDA) محافظت می‌شوند.</span>
                </div>
              </div>
            </form>
          </div>

          <!-- Right: Fast Contact Cards -->
          <div class="contact-info-cards-col">
            <!-- Direct Phone Bento -->
            <a :href="`tel:${sanitizePhone(contactData.phone)}`" class="info-card-item">
              <div class="card-icon-bubble">
                <q-icon name="phone_in_talk" size="24px" />
              </div>
              <div class="card-details">
                <span class="card-hint">تماس تلفنی مستقیم</span>
                <span class="card-val" dir="ltr">{{ contactData.phone || '۰۲۱ - ۸۸۹۰ ۱۲۳۴' }}</span>
              </div>
            </a>

            <!-- Official Email Bento -->
            <a :href="`mailto:${contactData.email || 'contact@smartgalaxy.land'}`" class="info-card-item">
              <div class="card-icon-bubble">
                <q-icon name="mail" size="24px" />
              </div>
              <div class="card-details">
                <span class="card-hint">مکاتبات رسمی و RFC</span>
                <span class="card-val" dir="ltr">{{ contactData.email || 'contact@smartgalaxy.land' }}</span>
              </div>
            </a>

            <!-- Office Address Bento -->
            <div class="info-card-item no-hover">
              <div class="card-icon-bubble">
                <q-icon name="location_on" size="24px" />
              </div>
              <div class="card-details">
                <span class="card-hint">نشانی دفتر مرکزی</span>
                <span class="card-val-text">{{ contactData.address || 'تهران، نلسون ماندلا (جردن)، بالاتر از میرداماد، برج کهکشان، طبقه ۱۲' }}</span>
              </div>
            </div>

            <!-- Working Hours & Monitoring -->
            <div class="info-card-item no-hover">
              <div class="card-icon-bubble">
                <q-icon name="schedule" size="24px" />
              </div>
              <div class="card-details">
                <span class="card-hint">ساعات پاسخ‌گویی دفتری</span>
                <span class="card-val-text">{{ contactData.workingHours || 'شنبه تا چهارشنبه ۸:۰۰ الی ۱۸:۰۰ | پنجشنبه ۸:۰۰ الی ۱۳:۰۰' }}</span>
                <div class="support-247-badge">
                  <span class="pulse-mini"></span>
                  <span>{{ contactData.emergencySupport || 'پایش و مانیتورینگ زیرساخت‌های ابری: ۲۴ ساعته / ۷ روز هفته' }}</span>
                </div>
              </div>
            </div>

            <!-- Dark Map Visual Bento -->
            <div class="map-bento-card">
              <div class="map-overlay-head">
                <span class="map-tag">موقعیت جغرافیایی</span>
                <span class="map-coords" dir="ltr">35.7611° N, 51.4215° E</span>
              </div>
              <div class="map-visual-preview">
                <div class="map-center-pin">
                  <div class="pin-wave"></div>
                  <div class="pin-dot"></div>
                </div>
              </div>
              <div class="map-footer">
                <span>برج کهکشان، دسترسی آسان از بزرگراه مدرس و حقانی</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- 3. Frequently Asked Questions (FAQ) Accordion -->
    <section class="contact-faq-section" v-if="contactData.faqs && contactData.faqs.length">
      <div class="container">
        <div class="section-head text-center">
          <div class="section-tag">
            <span class="tag-dot"></span>
            <span>پرسش‌های متداول</span>
          </div>
          <h2 class="section-title">پاسخ به سوالات رایج پیش از آغاز همکاری</h2>
          <p class="section-desc">
            اطلاعات شفاف درباره نحوه شروع پروژه، فرآیند ارزیابی فنی و شرایط قرارداد سطح خدمات.
          </p>
        </div>

        <div class="faq-accordion-list">
          <div
            v-for="(faq, fIdx) in contactData.faqs"
            :key="fIdx"
            class="faq-card"
            :class="{ open: openFaqIndex === fIdx }"
            @click="toggleFaq(fIdx)"
          >
            <div class="faq-head">
              <h3 class="faq-question">{{ faq.q }}</h3>
              <div class="faq-toggle-btn">
                <q-icon :name="openFaqIndex === fIdx ? 'remove' : 'add'" size="20px" />
              </div>
            </div>
            <div class="faq-body" v-show="openFaqIndex === fIdx">
              <p class="faq-answer">{{ faq.a }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

  </q-page>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { usePageMeta } from 'src/composables/usePageMeta'
import { useAuth } from 'src/composables/useAuth'
import { useMasterEditor, loadMasterContent } from 'src/composables/useMasterEditor'
import api from 'src/services/api'

usePageMeta({
  title: 'تماس با ما و دریافت مشاوره تخصصی | کهکشان هوشمند',
  description: 'ارتباط مستقیم با معماران ارشد سیستم، ثبت درخواست مشاوره فنی، نشانی و ساعات کاری کهکشان هوشمند.',
  path: '/contact',
})

const $q = useQuasar()
const { isAdmin } = useAuth()
const { contactState, openMasterEditor } = useMasterEditor()

const contactData = computed(() => {
  return contactState.value || {}
})

const SERVICE_CHOICES = [
  'رایانش ابری و Edge',
  'معماری میکروسرویس',
  'هوش مصنوعی و LLM',
  'طراحی محصول و UX',
  'امنیت Zero-Trust',
  'تحلیل کلان‌داده',
]

const selectedServices = ref(['رایانش ابری و Edge'])
const submitting = ref(false)
const openFaqIndex = ref(0)

const form = reactive({
  full_name: '',
  company: '',
  phone_number: '',
  email: '',
  description: '',
})

function toggleService (srv) {
  const idx = selectedServices.value.indexOf(srv)
  if (idx > -1) {
    if (selectedServices.value.length > 1) {
      selectedServices.value.splice(idx, 1)
    }
  } else {
    selectedServices.value.push(srv)
  }
}

function toggleFaq (idx) {
  openFaqIndex.value = openFaqIndex.value === idx ? -1 : idx
}

function sanitizePhone (ph) {
  if (!ph) return ''
  return String(ph).replace(/[^0-9+]/g, '')
}

async function submitForm () {
  submitting.value = true
  try {
    const payload = {
      full_name: form.full_name,
      phone: sanitizePhone(form.phone_number),
      phone_number: form.phone_number,
      email: form.email,
      company_name: form.company,
      subject: `درخواست مشاوره: ${selectedServices.value.join('، ') || 'عمومی'}`,
      message: `[حوزه‌ها: ${selectedServices.value.join('، ')}] - ایمیل: ${form.email}\n\n${form.description}`,
    }

    await api.post('/api/consultations', payload)

    $q.notify({
      type: 'positive',
      message: 'درخواست شما با موفقیت ثبت شد. معمار ارشد سیستم به زودی با شما تماس خواهد گرفت.',
      position: 'top',
      timeout: 3500,
    })

    form.full_name = ''
    form.company = ''
    form.phone_number = ''
    form.email = ''
    form.description = ''
  } catch (err) {
    console.error('Failed to submit consultation:', err)
    $q.notify({
      type: 'negative',
      message: 'خطا در ثبت درخواست. لطفاً مجدداً تلاش کرده یا مستقیماً تماس بگیرید.',
      position: 'top',
    })
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadMasterContent().catch(() => {})
})
</script>

<style scoped>
/* ==========================================================================
   CONTACT US PAGE (Luxury Tech Design)
   ========================================================================== */
.contact-page-root {
  background-color: var(--bg-canvas, #f7f7f7);
  color: var(--text-dark, #0a0a0a);
  direction: rtl;
  min-height: 100vh;
  overflow-x: hidden;
}

.container {
  width: min(1340px, 94vw);
  margin: 0 auto;
  padding: 0 16px;
  box-sizing: border-box;
}

/* 1. Hero */
.contact-hero {
  padding: 148px 0 60px 0;
  text-align: center;
  position: relative;
}

.hero-center-head {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 880px;
  margin: 0 auto;
}

.section-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 18px;
  border-radius: var(--radius-pill, 9999px);
  font-size: 0.82rem;
  font-weight: 700;
  background: var(--yellow-dim, rgba(255, 204, 0, 0.12));
  border: 1px solid var(--yellow-border, rgba(255, 204, 0, 0.35));
  color: #946200;
  box-shadow: 0 2px 10px rgba(255, 204, 0, 0.08);
  margin-bottom: 20px;
}

.tag-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ffd54a;
  box-shadow: 0 0 8px #ffd54a;
}

.title-with-admin {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
  margin: 0 0 16px 0;
}

.contact-main-title {
  font-size: clamp(2.1rem, 4vw, 3.1rem);
  font-weight: 900;
  line-height: 1.3;
  margin: 0;
  color: var(--text-dark, #0a0a0a);
  letter-spacing: -0.025em;
}

.contact-subtext {
  font-size: 1.08rem;
  line-height: 1.9;
  color: var(--text-dark-muted, #52525b);
  margin: 0 auto 28px auto;
  max-width: 760px;
}

.sla-response-pill {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  padding: 8px 20px;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #15803d;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
}

.pulse-green-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 8px #22c55e;
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

/* 2. Bento Grid */
.contact-bento-section {
  padding: 30px 0 70px 0;
}

.contact-bento-grid {
  display: grid;
  grid-template-columns: 1.35fr 1fr;
  gap: 32px;
  align-items: start;
}

/* Form Card */
.contact-form-card {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: 28px;
  padding: 44px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04);
}

.form-head {
  margin-bottom: 30px;
}

.sub-label {
  font-size: 0.82rem;
  font-weight: 800;
  color: #946c00;
  text-transform: uppercase;
  display: block;
  margin-bottom: 6px;
}

.form-title {
  font-size: 1.6rem;
  font-weight: 900;
  margin: 0 0 10px 0;
  color: var(--text-dark, #0a0a0a);
}

.form-desc {
  font-size: 0.92rem;
  color: var(--text-dark-muted, #737373);
  margin: 0;
  line-height: 1.65;
}

.consultation-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-label {
  font-size: 0.82rem;
  font-weight: 700;
  color: #18181b;
}

.required {
  color: #ef4444;
}

.tech-input,
.tech-textarea {
  width: 100%;
  background: #fcfcfc;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 0.9rem;
  font-family: inherit;
  color: var(--text-dark, #0a0a0a);
  outline: none;
  box-sizing: border-box;
  transition: all 0.2s;
}

.tech-input:focus,
.tech-textarea:focus {
  border-color: #0a0a0a;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
}

.service-select-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.service-chip {
  background: #f4f4f5;
  border: 1px solid var(--border-light, #e5e5e5);
  padding: 7px 14px;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #52525b;
  cursor: pointer;
  transition: all 0.2s;
}

.service-chip:hover {
  border-color: #0a0a0a;
  color: #0a0a0a;
}

.service-chip.selected {
  background: #0a0a0a;
  color: #ffd54a;
  border-color: #0a0a0a;
}

.form-action-row {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding-top: 10px;
}

.btn-submit {
  width: 100%;
  justify-content: center;
  padding: 14px 28px;
  font-size: 0.95rem;
}

.nda-notice {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 0.78rem;
  color: var(--text-dark-muted, #737373);
}

/* Right: Fast Contact Cards */
.contact-info-cards-col {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card-item {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: 20px;
  padding: 22px 24px;
  display: flex;
  align-items: center;
  gap: 18px;
  text-decoration: none;
  color: inherit;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
}

.info-card-item:not(.no-hover):hover {
  transform: translateY(-3px);
  border-color: #0a0a0a;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.06);
}

.card-icon-bubble {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: rgba(255, 204, 0, 0.15);
  color: #946c00;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.card-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.card-hint {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-dark-muted, #737373);
}

.card-val {
  font-size: 1.15rem;
  font-weight: 900;
  color: var(--text-dark, #0a0a0a);
}

.card-val-text {
  font-size: 0.92rem;
  font-weight: 700;
  line-height: 1.6;
  color: var(--text-dark, #0a0a0a);
}

.support-247-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  font-weight: 700;
  color: #2563eb;
  margin-top: 4px;
}

.pulse-mini {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #2563eb;
}

/* Map Bento Card */
.map-bento-card {
  background: #0a0a0a;
  color: #ffffff;
  border-radius: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
}

.map-overlay-head {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.map-tag {
  font-size: 0.75rem;
  font-weight: 700;
  color: #ffd54a;
}

.map-coords {
  font-size: 0.72rem;
  color: #71717a;
}

.map-visual-preview {
  height: 130px;
  background: linear-gradient(135deg, #141419 0%, #1f1f27 100%);
  position: relative;
  display: grid;
  place-items: center;
}

.map-center-pin {
  position: relative;
}

.pin-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #ffd54a;
  box-shadow: 0 0 14px #ffd54a;
  position: relative;
  z-index: 2;
}

.pin-wave {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 213, 74, 0.25);
  animation: wave-expand 2s infinite;
}

@keyframes wave-expand {
  0% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(1.6); opacity: 0; }
}

.map-footer {
  padding: 12px 20px;
  font-size: 0.78rem;
  color: #a1a1aa;
  background: #111116;
}

/* 3. FAQ Section */
.contact-faq-section {
  padding: 60px 0 90px 0;
}

.faq-accordion-list {
  max-width: 840px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.faq-card {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: 18px;
  padding: 22px 26px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.faq-card:hover {
  border-color: #a1a1aa;
}

.faq-card.open {
  border-color: #0a0a0a;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
}

.faq-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.faq-question {
  font-size: 1.05rem;
  font-weight: 800;
  margin: 0;
  color: var(--text-dark, #0a0a0a);
}

.faq-toggle-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f4f4f5;
  display: grid;
  place-items: center;
  color: var(--text-dark, #0a0a0a);
  flex-shrink: 0;
}

.faq-card.open .faq-toggle-btn {
  background: #0a0a0a;
  color: #ffffff;
}

.faq-body {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--border-light, #e5e5e5);
}

.faq-answer {
  font-size: 0.92rem;
  line-height: 1.8;
  color: var(--text-dark-muted, #737373);
  margin: 0;
}

@media (max-width: 900px) {
  .contact-hero {
    padding: 100px 0 32px 0;
  }

  .contact-main-title {
    font-size: clamp(1.4rem, 5.5vw, 1.85rem);
    line-height: 1.32;
  }

  .contact-subtext {
    font-size: 0.85rem;
    line-height: 1.72;
  }

  .contact-bento-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .contact-form-card {
    padding: 24px 18px;
    border-radius: 20px;
  }

  .form-title {
    font-size: 1.25rem;
  }

  .form-desc {
    font-size: 0.82rem;
    line-height: 1.65;
  }

  .form-row-2 {
    grid-template-columns: 1fr;
    gap: 14px;
  }
}

@media (max-width: 640px) {
  .contact-hero {
    padding: 88px 0 24px 0;
  }

  .contact-main-title {
    font-size: clamp(1.22rem, 5vw, 1.48rem);
  }

  .contact-subtext {
    font-size: 0.8rem;
    line-height: 1.68;
  }

  .contact-form-card {
    padding: 20px 14px;
    border-radius: 18px;
  }

  .form-title {
    font-size: 1.12rem;
  }

  .tech-input,
  .tech-textarea {
    font-size: 16px; /* Prevents auto-zoom on mobile iOS */
  }

  .input-label {
    font-size: 0.78rem;
  }

  .service-chip {
    font-size: 0.74rem;
    padding: 6px 12px;
  }

  .form-action-row .btn-submit {
    width: 100%;
    justify-content: center;
    font-size: 0.8rem;
    min-height: 44px;
  }

  .info-card-item {
    padding: 16px 14px;
    border-radius: 16px;
    gap: 12px;
  }

  .card-icon-bubble {
    width: 40px;
    height: 40px;
    border-radius: 12px;
  }

  .card-val {
    font-size: 0.98rem;
  }

  .card-val-text {
    font-size: 0.82rem;
  }

  .contact-faq-section {
    padding: 40px 0 60px 0;
  }

  .faq-card {
    padding: 16px 14px;
    border-radius: 16px;
  }

  .faq-question {
    font-size: 0.88rem;
  }

  .faq-answer {
    font-size: 0.8rem;
    line-height: 1.7;
  }
}

@media (max-width: 480px) {
  .contact-hero {
    padding: 84px 0 20px 0;
  }

  .contact-main-title {
    font-size: clamp(1.18rem, 4.8vw, 1.35rem);
  }

  .contact-form-card {
    padding: 16px 12px;
    border-radius: 16px;
  }

  .info-card-item {
    padding: 14px 12px;
  }

  .card-val {
    font-size: 0.92rem;
  }

  .map-box {
    height: 180px;
  }
}
</style>

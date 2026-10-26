<template>
  <q-page class="about-page-root">

    <!-- 1. Page Hero: Clean Minimalist Tech Header matching Homepage -->
    <section class="about-hero">
      <div class="container">
        <div class="hero-center-head">
          <div class="section-tag">
            <span class="tag-dot"></span>
            <span>{{ aboutData.badge || 'درباره کهکشان هوشمند' }}</span>
          </div>

          <div class="title-with-admin">
            <h1 class="about-main-title">
              {{ aboutData.title || 'اصالت مهندسی، انضباط سازمانی' }}
            </h1>
            <button
              v-if="isAdmin"
              type="button"
              class="btn-pill btn-pill-dark btn-pill-sm mr-2"
              @click="openMasterEditor('about')"
            >
              <q-icon name="edit" size="14px" />
              <span>ویرایش محتوای درباره ما</span>
            </button>
          </div>

          <p class="about-subtext">
            {{ aboutData.desc || 'ما یک استودیوی پیشرو در معماری نرم‌افزارهای تجاری و زیرساخت‌های ابری هستیم که دقت فنی را با استانداردهای بین‌المللی سازمانی تلفیق می‌کنیم.' }}
          </p>
        </div>
      </div>
    </section>

    <!-- 2. Statement & Engineering Philosophy (Bento Split) -->
    <section class="philosophy-section">
      <div class="container">
        <div class="philosophy-bento-grid">
          <!-- Text Narrative Card -->
          <div class="philosophy-text-card">
            <div class="section-tag">
              <span class="tag-dot"></span>
              <span>بیانیه و دیدگاه مهندسی</span>
            </div>
            <h2 class="philosophy-title">
              {{ aboutData.statementTitle || 'پیشگام در مهندسی سیستم‌های توزیع‌شده با قابلیت اتکای سازمانی' }}
            </h2>
            <div class="philosophy-body">
              <p class="lead-p" v-html="aboutData.statementP1"></p>
              <p v-html="aboutData.statementP2"></p>
            </div>

            <div class="trust-check-list">
              <div class="trust-item">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#eab308" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span>تضمین کتبی ۹۹.۹۹٪ پایداری بدون وقفه در قراردادهای سازمانی</span>
              </div>
              <div class="trust-item">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#eab308" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span>شفافیت کامل معماری و تحویل ۱۰۰٪ سورس‌کد و داکر فایل‌ها به کارفرما</span>
              </div>
              <div class="trust-item">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#eab308" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span>شبکه Anycast لبه با پاسخ‌دهی زیر ۱۵ میلی‌ثانیه برای کاربران داخلی و بین‌المللی</span>
              </div>
            </div>
          </div>

          <!-- Visual Graphic Bento Card -->
          <div class="philosophy-graphic-card">
            <div class="graphic-badge-wrap">
              <div class="badge-dot"></div>
              <span>زیرساخت ابری فعال ۲۴/۷</span>
            </div>
            <img src="/Modern 3D Tech Dashboard Illustration(1).png" alt="زیرساخت ابری کهکشان هوشمند" class="graphic-illustration" />
            
            <div class="graphic-footer-strip">
              <div class="sla-pill">
                <strong>SLA Guaranteed</strong>
                <span>۹۹.۹۹٪ آپ‌تایم</span>
              </div>
              <div class="sla-pill">
                <strong>Zero-Trust</strong>
                <span>رمزنگاری mTLS 1.3</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 3. Core Values & Principles (4 Cards) -->
    <section class="values-section">
      <div class="container">
        <div class="section-head text-center">
          <div class="section-tag">
            <span class="tag-dot"></span>
            <span>اصول بنیادین</span>
          </div>
          <h2 class="section-title">ارکان مهندسی و ارزش‌های کهکشان هوشمند</h2>
          <p class="section-desc">
            ما نرم‌افزار را نه به عنوان یک محصول موقت، بلکه به عنوان یک دارایی استراتژیک بلندمدت برای سازمان شما مهندسی می‌کنیم.
          </p>
        </div>

        <div class="values-grid">
          <div
            v-for="(val, vIdx) in (aboutData.values || [])"
            :key="vIdx"
            class="value-card"
          >
            <div class="value-icon-box">
              <q-icon :name="val.icon || 'verified'" size="28px" />
            </div>
            <h3 class="value-title">{{ val.title }}</h3>
            <p class="value-desc">{{ val.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 4. Key Leadership & Systems Architects (Cyber-Tech Architectural Dossiers) -->
    <section class="team-section">
      <div class="container">
        <div class="section-head text-center">
          <div class="section-tag">
            <span class="tag-dot"></span>
            <span>سرمایه انسانی و تیم متخصصان</span>
          </div>
          <div class="head-with-action">
            <h2 class="section-title">معماران ارشد و رهبران مهندسی</h2>
            <router-link
              v-if="isAdmin"
              to="/admin/team"
              class="btn-pill btn-pill-dark btn-pill-sm mr-2"
            >
              <q-icon name="group" size="14px" />
              <span>مدیریت متخصصان در پنل</span>
            </router-link>
            <button
              v-if="isAdmin"
              type="button"
              class="btn-pill btn-pill-dark btn-pill-sm"
              @click="openMasterEditor('about')"
            >
              <q-icon name="edit" size="14px" />
              <span>ویرایش درباره ما</span>
            </button>
          </div>
          <p class="section-desc">
            متخصصانی با بیش از یک دهه تجربه عملیاتی در مدیریت سیستم‌های پرترافیک، پایگاه‌های داده توزیع‌شده و کلاسترهای کوبرنتیز.
          </p>

          <!-- Interactive Specialty Filter Pills -->
          <div class="team-filter-pills" v-if="teamSpecialties.length > 1">
            <button
              v-for="spec in teamSpecialties"
              :key="spec"
              type="button"
              class="team-filter-pill"
              :class="{ active: activeTeamFilter === spec }"
              @click="activeTeamFilter = spec"
            >
              {{ spec }}
            </button>
          </div>
        </div>

        <!-- Futuristic Architectural Terminal Dossier Grid -->
        <div class="architect-dossier-grid">
          <article
            v-for="(member, mIdx) in filteredTeamList"
            :key="member.id || mIdx"
            class="architect-card"
          >
            <!-- Card Cyber Header Bar -->
            <div class="architect-card-header">
              <div class="spec-id-tag">
                <span class="live-dot-green"></span>
                <span class="spec-code">SYS-NODE: {{ formatMemberId(member.id || mIdx + 1) }}</span>
              </div>
              <div class="architect-role-pill">
                {{ member.role }}
              </div>
            </div>

            <!-- Card Core Body Split -->
            <div class="architect-card-body">
              <!-- Holographic Portrait Column -->
              <div class="architect-avatar-column">
                <div class="avatar-holo-ring">
                  <img
                    v-if="member.image"
                    :src="member.image"
                    :alt="member.name"
                    loading="lazy"
                    class="avatar-portrait-img"
                    @error="(e) => { e.target.src = '/uploads/home/contact-programming.jpg' }"
                  />
                  <div v-else class="avatar-fallback-box">
                    <q-icon :name="member.avatarIcon || 'person'" size="54px" color="amber-7" />
                  </div>
                  <div class="holo-corner tl"></div>
                  <div class="holo-corner br"></div>
                </div>
              </div>

              <!-- Details Column -->
              <div class="architect-details-column">
                <div class="architect-name-block">
                  <h3 class="architect-name">{{ member.name }}</h3>
                  <span v-if="member.nameEn || member.roleEn" class="architect-handle" dir="ltr">
                    {{ member.nameEn ? `@${member.nameEn.toLowerCase().replace(/[^a-z0-9]/g, '.')}` : (member.roleEn || 'Systems Architect') }}
                  </span>
                </div>

                <div v-if="member.bio" class="architect-bio-quote">
                  <p>{{ member.bio }}</p>
                </div>

                <!-- Tech Skills / Competencies -->
                <div class="architect-tags-cluster">
                  <span
                    v-for="(tag, tIdx) in (member.tags && member.tags.length ? member.tags : defaultTagsForRole(member.role))"
                    :key="tIdx"
                    class="tech-stack-badge"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Card Footer: Resume & Social Connectivity -->
            <div class="architect-card-footer">
              <a
                v-if="member.id && member.hasResume"
                :href="`/api/team-members/${member.id}/resume.pdf?lang=fa`"
                target="_blank"
                class="btn-resume-action"
                title="دانلود رزومه رسمی PDF"
              >
                <q-icon name="description" size="15px" />
                <span>رزومه رسمی PDF</span>
              </a>
              <span v-else class="spec-verified-chip">
                <q-icon name="verified" size="14px" color="amber-7" />
                <span>شورای معماری کهکشان</span>
              </span>

              <div class="architect-social-dock" v-if="member.linkedin || member.github || member.website">
                <a v-if="member.linkedin" :href="member.linkedin" target="_blank" rel="noopener noreferrer" class="social-icon-btn" title="LinkedIn">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
                </a>
                <a v-if="member.github" :href="member.github" target="_blank" rel="noopener noreferrer" class="social-icon-btn" title="GitHub">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
                </a>
                <a v-if="member.website" :href="member.website" target="_blank" rel="noopener noreferrer" class="social-icon-btn" title="وب‌سایت شخصی">
                  <q-icon name="language" size="14px" />
                </a>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- 5. Milestones & Progression Timeline -->
    <section class="milestones-section">
      <div class="container">
        <div class="section-head text-center">
          <div class="section-tag">
            <span class="tag-dot"></span>
            <span>مسیر رشد</span>
          </div>
          <h2 class="section-title">نقاط عطف و گاه‌شمار دستاوردها</h2>
          <p class="section-desc">
            روایت توسعه گام‌به‌گام زیرساخت‌های ابری و اعتمادسازی در ابعاد ملی.
          </p>
        </div>

        <div class="milestones-timeline-grid">
          <div
            v-for="(ms, sIdx) in (aboutData.milestones || [])"
            :key="sIdx"
            class="milestone-card"
          >
            <div class="year-badge">{{ ms.year }}</div>
            <h3 class="milestone-title">{{ ms.title }}</h3>
            <p class="milestone-desc">{{ ms.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 6. High-Impact Unified CTA Box -->
    <CloudlandCTA page-name="درباره ما" />

  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from 'src/services/api'
import { usePageMeta } from 'src/composables/usePageMeta'
import { useAuth } from 'src/composables/useAuth'
import { useMasterEditor, loadMasterContent } from 'src/composables/useMasterEditor'
import CloudlandCTA from 'src/components/CTA/CloudlandCTA.vue'

usePageMeta({
  title: 'درباره ما | اصالت مهندسی و انضباط سازمانی کهکشان هوشمند',
  description: 'آشنایی با تیم معماران سیستم، رویکرد مهندسی نرم‌افزار، تضمین قرارداد سطح خدمات (SLA) و ارزش‌های کهکشان هوشمند.',
  path: '/about',
})

const { isAdmin } = useAuth()
const { aboutState, openMasterEditor } = useMasterEditor()

const aboutData = computed(() => {
  return aboutState.value || {}
})

const dbTeamMembers = ref([])
const activeTeamFilter = ref('همه')

function cleanHtmlToText (html) {
  if (!html) return ''
  try {
    const tmp = document.createElement('div')
    tmp.innerHTML = html
    const txt = tmp.textContent || tmp.innerText || ''
    return txt.length > 180 ? txt.slice(0, 180) + '...' : txt
  } catch {
    return String(html).replace(/<[^>]*>/g, '').slice(0, 180)
  }
}

async function loadTeamMembers () {
  try {
    const res = await api.get('/api/team-members')
    if (res.data?.data) {
      dbTeamMembers.value = res.data.data
    }
  } catch (err) {
    console.warn('Failed to load db team members', err)
  }
}

const activeTeamList = computed(() => {
  if (dbTeamMembers.value && dbTeamMembers.value.length > 0) {
    return dbTeamMembers.value.map(m => {
      let bioText = m.bio || cleanHtmlToText(m.resume_fa) || m.role_en || ''
      return {
        id: m.id,
        name: m.full_name || m.name,
        nameEn: m.full_name_en,
        role: m.role,
        roleEn: m.role_en,
        image: m.image_url || m.image,
        avatarIcon: m.avatar_icon,
        bio: bioText,
        linkedin: m.linkedin_url,
        github: m.github_url,
        website: m.website_url,
        hasResume: !!(m.resume_fa || m.resume_en),
      }
    })
  }
  return aboutData.value.team || []
})

const teamSpecialties = computed(() => {
  const specs = new Set(['همه'])
  activeTeamList.value.forEach(m => {
    if (m.role) {
      if (m.role.includes('مدیر') || m.role.includes('رهبری') || m.role.includes('CEO') || m.role.includes('CTO')) {
        specs.add('مدیریت و استراتژی')
      } else if (m.role.includes('دواپس') || m.role.includes('DevOps') || m.role.includes('کلاود') || m.role.includes('زیرساخت')) {
        specs.add('دواپس و زیرساخت ابری')
      } else if (m.role.includes('بک‌اند') || m.role.includes('Backend') || m.role.includes('فول‌استک') || m.role.includes('فرانت‌اند') || m.role.includes('نرم‌افزار')) {
        specs.add('مهندسی نرم‌افزار')
      } else if (m.role.includes('داده') || m.role.includes('هوش') || m.role.includes('AI') || m.role.includes('Data')) {
        specs.add('هوش مصنوعی و داده')
      } else {
        specs.add(m.role)
      }
    }
  })
  return Array.from(specs)
})

const filteredTeamList = computed(() => {
  if (activeTeamFilter.value === 'همه') return activeTeamList.value
  return activeTeamList.value.filter(m => {
    const role = m.role || ''
    if (activeTeamFilter.value === 'مدیریت و استراتژی') {
      return role.includes('مدیر') || role.includes('رهبری') || role.includes('CEO') || role.includes('CTO')
    }
    if (activeTeamFilter.value === 'دواپس و زیرساخت ابری') {
      return role.includes('دواپس') || role.includes('DevOps') || role.includes('کلاود') || role.includes('زیرساخت')
    }
    if (activeTeamFilter.value === 'مهندسی نرم‌افزار') {
      return role.includes('بک‌اند') || role.includes('Backend') || role.includes('فول‌استک') || role.includes('فرانت‌اند') || role.includes('نرم‌افزار')
    }
    if (activeTeamFilter.value === 'هوش مصنوعی و داده') {
      return role.includes('داده') || role.includes('هوش') || role.includes('AI') || role.includes('Data')
    }
    return role.includes(activeTeamFilter.value)
  })
})

function formatMemberId (id) {
  const num = parseInt(id) || 1
  return `ARC-${String(num).padStart(3, '0')}`
}

function defaultTagsForRole (role = '') {
  const r = (role || '').toLowerCase()
  if (r.includes('devops') || r.includes('دواپس') || r.includes('کلاود') || r.includes('زیرساخت')) {
    return ['Kubernetes', 'Terraform', 'CI/CD', 'Prometheus', 'High Availability']
  }
  if (r.includes('بک‌اند') || r.includes('backend') || r.includes('ارشد')) {
    return ['Distributed Systems', 'Python / Go', 'PostgreSQL', 'Microservices', 'Clean Arch']
  }
  if (r.includes('امنیت') || r.includes('security')) {
    return ['Zero Trust', 'SOC-2', 'Penetration Testing', 'Vault', 'IAM']
  }
  if (r.includes('فرانت') || r.includes('front')) {
    return ['Vue 3 / Quasar', 'Vite', 'Performance Optimization', 'Design Systems']
  }
  if (r.includes('هوش') || r.includes('ai') || r.includes('داده')) {
    return ['LLMs & RAG', 'Vector DB', 'PyTorch', 'Data Pipeline']
  }
  return ['System Architecture', 'Fault Tolerance', 'Code Quality', 'DevSecOps']
}

onMounted(() => {
  loadMasterContent().catch(() => {})
  loadTeamMembers()
})
</script>

<style scoped>
/* ==========================================================================
   ABOUT US PAGE (Luxury Tech Design)
   ========================================================================== */
.about-page-root {
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

/* 1. Hero with enhanced top padding for floating header */
.about-hero {
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
  margin-bottom: 20px;
  background: var(--yellow-dim, rgba(255, 204, 0, 0.12));
  border: 1px solid var(--yellow-border, rgba(255, 204, 0, 0.35));
  color: #946200;
  box-shadow: 0 2px 10px rgba(255, 204, 0, 0.08);
}

.tag-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--yellow, #ffcc00);
  box-shadow: 0 0 8px #ffcc00;
}

.title-with-admin {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
  margin: 0 0 16px 0;
}

.about-main-title {
  font-size: clamp(2.1rem, 4vw, 3.1rem);
  font-weight: 900;
  line-height: 1.3;
  margin: 0;
  color: var(--text-dark, #0a0a0a);
  letter-spacing: -0.025em;
}

.about-subtext {
  font-size: 1.08rem;
  line-height: 1.9;
  color: var(--text-dark-muted, #52525b);
  margin: 0 auto;
  max-width: 760px;
}

/* 2. Philosophy & Statement (Bento Grid) */
.philosophy-section {
  padding: 40px 0 70px 0;
}

.philosophy-bento-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.9fr;
  gap: 32px;
  align-items: stretch;
}

.philosophy-text-card {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: 28px;
  padding: 48px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04);
}

.philosophy-title {
  font-size: 1.65rem;
  font-weight: 900;
  line-height: 1.35;
  margin: 16px 0 20px 0;
  color: var(--text-dark, #0a0a0a);
}

.philosophy-body {
  font-size: 1rem;
  line-height: 1.85;
  color: #3f3f46;
  margin-bottom: 28px;
}

.lead-p {
  font-weight: 600;
  color: #18181b;
  margin-bottom: 14px;
}

.trust-check-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid var(--border-light, #e5e5e5);
}

.trust-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.9rem;
  font-weight: 700;
  color: #18181b;
}

.philosophy-graphic-card {
  background: #0a0a0a;
  color: #ffffff;
  border-radius: 28px;
  padding: 36px;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}

.graphic-badge-wrap {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  padding: 6px 14px;
  border-radius: 9999px;
  font-size: 0.76rem;
  font-weight: 700;
  color: #ffd54a;
  align-self: flex-start;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #ffd54a;
  box-shadow: 0 0 8px #ffd54a;
}

.graphic-illustration {
  max-width: 85%;
  height: auto;
  margin: 24px 0;
  filter: drop-shadow(0 15px 30px rgba(0, 0, 0, 0.5));
}

.graphic-footer-strip {
  width: 100%;
  display: flex;
  gap: 12px;
}

.sla-pill {
  flex: 1;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 12px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sla-pill strong {
  font-size: 0.72rem;
  color: #a1a1aa;
  text-transform: uppercase;
}

.sla-pill span {
  font-size: 0.95rem;
  font-weight: 900;
  color: #ffd54a;
}

/* 3. Core Values (4 Cards) */
.values-section {
  padding: 60px 0;
}

.section-head {
  max-width: 720px;
  margin: 0 auto 48px auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.section-title {
  font-size: clamp(1.6rem, 3vw, 2.3rem);
  font-weight: 900;
  margin: 12px 0 10px 0;
  color: var(--text-dark, #0a0a0a);
}

.section-desc {
  font-size: 0.98rem;
  color: var(--text-dark-muted, #737373);
  line-height: 1.7;
  margin: 0;
}

.values-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.value-card {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: 24px;
  padding: 36px 30px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  flex-direction: column;
}

.value-card:hover {
  transform: translateY(-5px);
  border-color: #0a0a0a;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.06);
}

.value-icon-box {
  width: 54px;
  height: 54px;
  border-radius: 16px;
  background: rgba(255, 204, 0, 0.15);
  color: #946c00;
  display: grid;
  place-items: center;
  margin-bottom: 20px;
}

.value-title {
  font-size: 1.15rem;
  font-weight: 800;
  margin: 0 0 12px 0;
  color: var(--text-dark, #0a0a0a);
}

.value-desc {
  font-size: 0.9rem;
  line-height: 1.75;
  color: var(--text-dark-muted, #737373);
  margin: 0;
}

/* 4. Team - Cyber-Tech Architectural Dossiers */
.team-section {
  padding: 80px 0;
  position: relative;
}

.team-filter-pills {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
  margin: 28px 0 36px 0;
}

.team-filter-pill {
  border: 1px solid var(--border-light, #e5e5e5);
  background: #ffffff;
  color: #52525b;
  font-size: 0.82rem;
  font-weight: 700;
  padding: 8px 18px;
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.team-filter-pill:hover {
  border-color: #0a0a0a;
  color: #0a0a0a;
  transform: translateY(-2px);
}

.team-filter-pill.active {
  background: #0a0a0a;
  color: #ffd54a;
  border-color: #0a0a0a;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.architect-dossier-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 28px;
}

.architect-card {
  background: #ffffff;
  border: 1px solid #e4e4e7;
  border-radius: 24px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
  position: relative;
}

.architect-card:hover {
  transform: translateY(-6px);
  border-color: #18181b;
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.1);
}

/* Header strip */
.architect-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: #09090b;
  color: #ffffff;
  border-bottom: 1px solid #27272a;
}

.spec-id-tag {
  display: flex;
  align-items: center;
  gap: 8px;
}

.live-dot-green {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
}

.spec-code {
  font-family: monospace;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: #a1a1aa;
}

.architect-role-pill {
  background: rgba(255, 204, 0, 0.14);
  border: 1px solid rgba(255, 204, 0, 0.35);
  color: #ffd54a;
  font-size: 0.72rem;
  font-weight: 800;
  padding: 3px 10px;
  border-radius: 9999px;
}

/* Body */
.architect-card-body {
  display: flex;
  gap: 20px;
  padding: 24px;
  flex: 1;
}

.architect-avatar-column {
  flex-shrink: 0;
}

.avatar-holo-ring {
  width: 96px;
  height: 96px;
  border-radius: 20px;
  background: #09090b;
  position: relative;
  overflow: hidden;
  border: 2px solid #27272a;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.avatar-portrait-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.architect-card:hover .avatar-portrait-img {
  transform: scale(1.08);
}

.avatar-fallback-box {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  background: radial-gradient(circle, #27272a 0%, #09090b 100%);
}

.holo-corner {
  position: absolute;
  width: 8px;
  height: 8px;
  border: 2px solid #ffd54a;
  pointer-events: none;
}

.holo-corner.tl {
  top: 3px;
  left: 3px;
  border-right: none;
  border-bottom: none;
}

.holo-corner.br {
  bottom: 3px;
  right: 3px;
  border-left: none;
  border-top: none;
}

.architect-details-column {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.architect-name-block {
  margin-bottom: 8px;
}

.architect-name {
  font-size: 1.18rem;
  font-weight: 800;
  color: #09090b;
  margin: 0 0 2px 0;
}

.architect-handle {
  font-size: 0.75rem;
  font-family: monospace;
  color: #71717a;
}

.architect-bio-quote {
  font-size: 0.84rem;
  line-height: 1.65;
  color: #52525b;
  margin: 6px 0 14px 0;
  flex: 1;
}

.architect-tags-cluster {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tech-stack-badge {
  background: #f4f4f5;
  color: #3f3f46;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 3px 9px;
  border-radius: 6px;
  border: 1px solid #e4e4e7;
  font-family: monospace;
  transition: all 0.2s ease;
}

.architect-card:hover .tech-stack-badge {
  background: #e4e4e7;
  color: #09090b;
}

/* Footer */
.architect-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: #fafafa;
  border-top: 1px solid #f4f4f5;
}

.btn-resume-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 204, 0, 0.14);
  color: #855900;
  border: 1px solid rgba(255, 204, 0, 0.35);
  padding: 5px 12px;
  border-radius: 9999px;
  font-size: 0.74rem;
  font-weight: 800;
  text-decoration: none;
  transition: all 0.25s ease;
}

.btn-resume-action:hover {
  background: #ffd54a;
  color: #09090b;
  transform: translateY(-1px);
}

.spec-verified-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.72rem;
  font-weight: 700;
  color: #71717a;
}

.architect-social-dock {
  display: flex;
  align-items: center;
  gap: 6px;
}

.social-icon-btn {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid #e4e4e7;
  display: grid;
  place-items: center;
  color: #52525b;
  text-decoration: none;
  transition: all 0.2s ease;
}

.social-icon-btn:hover {
  background: #09090b;
  color: #ffd54a;
  border-color: #09090b;
  transform: translateY(-2px);
}

/* 5. Milestones */
.milestones-section {
  padding: 60px 0;
}

.milestones-timeline-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}

.milestone-card {
  background: #ffffff;
  border: 1px solid var(--border-light, #e5e5e5);
  border-radius: 20px;
  padding: 28px;
  display: flex;
  flex-direction: column;
}

.year-badge {
  display: inline-block;
  background: #0a0a0a;
  color: #ffd54a;
  font-weight: 900;
  font-size: 0.85rem;
  padding: 4px 12px;
  border-radius: 9999px;
  margin-bottom: 14px;
  align-self: flex-start;
}

.milestone-title {
  font-size: 1.05rem;
  font-weight: 800;
  margin: 0 0 8px 0;
  color: var(--text-dark, #0a0a0a);
}

.milestone-desc {
  font-size: 0.86rem;
  line-height: 1.65;
  color: var(--text-dark-muted, #737373);
  margin: 0;
}

/* 6. CTA Banner */
.cta-banner-section {
  padding: 40px 0 90px 0;
}

.cta-bento-card {
  position: relative;
  background-color: var(--bg-black, #0a0a0a);
  border-radius: 36px;
  padding: 72px 48px;
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.25);
  text-align: center;
}

.cta-glow-effect {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(255, 213, 74, 0.15) 0%, transparent 70%);
  pointer-events: none;
}

.cta-bento-content {
  position: relative;
  z-index: 2;
  max-width: 720px;
  margin: 0 auto;
}

.section-tag-light {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 213, 74, 0.3);
  color: #ffd54a;
  margin: 0 auto 18px auto;
}

.cta-bento-title {
  color: #ffffff;
  font-size: clamp(1.8rem, 3.5vw, 2.6rem);
  font-weight: 900;
  line-height: 1.3;
  margin: 0 0 16px 0;
}

.cta-bento-desc {
  color: #a1a1aa;
  font-size: 1rem;
  line-height: 1.8;
  margin: 0 0 36px 0;
}

.cta-btns-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

/* Responsive Adaptations */
@media (max-width: 900px) {
  .about-hero {
    padding: 100px 0 32px 0;
  }

  .about-main-title {
    font-size: clamp(1.4rem, 5.5vw, 1.85rem);
    line-height: 1.32;
  }

  .about-subtext {
    font-size: 0.85rem;
    line-height: 1.72;
  }

  .section-tag {
    font-size: 0.72rem;
    padding: 5px 13px;
    margin-bottom: 12px;
  }

  .section-title {
    font-size: clamp(1.35rem, 5vw, 1.7rem);
    line-height: 1.3;
  }

  .section-desc {
    font-size: 0.86rem;
    line-height: 1.68;
  }

  .philosophy-bento-grid {
    grid-template-columns: 1fr;
    gap: 18px;
  }

  .philosophy-text-card {
    padding: 24px 18px;
    border-radius: 20px;
  }

  .philosophy-title {
    font-size: 1.15rem;
  }

  .philosophy-text-card p {
    font-size: 0.84rem;
    line-height: 1.75;
  }

  .philosophy-graphic-card {
    padding: 24px 18px;
    border-radius: 20px;
  }

  .graphic-statement {
    font-size: 1rem;
    line-height: 1.65;
  }

  .stat-bubble .stat-num {
    font-size: 1.35rem;
  }

  .stat-bubble .stat-label {
    font-size: 0.7rem;
  }

  .cta-bento-card {
    padding: 36px 18px;
    border-radius: 22px;
  }

  .cta-bento-title {
    font-size: clamp(1.35rem, 5vw, 1.75rem);
    line-height: 1.32;
  }

  .cta-bento-desc {
    font-size: 0.85rem;
    line-height: 1.72;
    margin-bottom: 24px;
  }

  .cta-btns-row {
    flex-direction: column;
    width: 100%;
  }

  .cta-btns-row .btn-pill {
    width: 100%;
    justify-content: center;
    font-size: 0.8rem;
    min-height: 44px;
  }

  .values-grid,
  .team-grid,
  .milestones-timeline-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}

@media (max-width: 600px) {
  .values-grid,
  .team-grid,
  .milestones-timeline-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }
}

@media (max-width: 480px) {
  .about-hero {
    padding: 88px 0 24px 0;
  }

  .about-main-title {
    font-size: clamp(1.18rem, 4.8vw, 1.4rem);
  }

  .about-subtext {
    font-size: 0.8rem;
    line-height: 1.65;
  }

  .section-title {
    font-size: clamp(1.15rem, 4.5vw, 1.35rem);
  }

  .section-desc {
    font-size: 0.78rem;
    line-height: 1.65;
  }

  .section-tag {
    font-size: 0.68rem;
    padding: 4px 12px;
  }

  .philosophy-text-card,
  .philosophy-graphic-card,
  .value-card,
  .milestone-card {
    padding: 18px 14px;
    border-radius: 18px;
  }

  .value-title {
    font-size: 0.94rem;
  }

  .value-desc {
    font-size: 0.76rem;
    line-height: 1.65;
  }

  .member-name {
    font-size: 0.96rem;
  }

  .member-role-badge {
    font-size: 0.68rem;
  }

  .member-bio {
    font-size: 0.76rem;
    line-height: 1.65;
  }

  .year-badge {
    font-size: 0.74rem;
  }

  .milestone-title {
    font-size: 0.92rem;
  }

  .milestone-desc {
    font-size: 0.76rem;
    line-height: 1.65;
  }

  .cta-bento-card {
    padding: 24px 14px;
    border-radius: 18px;
  }

  .cta-bento-title {
    font-size: clamp(1.15rem, 4.5vw, 1.35rem);
  }

  .cta-bento-desc {
    font-size: 0.78rem;
    line-height: 1.65;
  }

  .graphic-footer-strip {
    flex-direction: column;
    gap: 8px;
  }
}
</style>

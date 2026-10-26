<template>
  <section class="nx-testimonials-section">
    <div class="nx-container">

      <!-- Testimonials Header -->
      <div class="testimonials-header">
        <div class="test-title-wrap">
          <span class="test-badge">
            <span class="yellow-star">★</span>
            {{ settings.reviews_eyebrow }}
          </span>

          <div class="test-title-row">
            <h2 class="test-title">{{ settings.reviews_title }}</h2>

            <q-btn
              v-if="isAdmin && authorized"
              class="section-edit-btn"
              round
              dense
              size="sm"
              unelevated
              color="dark"
              icon="edit"
              @click="openReviewsDialog"
            >
              <q-tooltip>ویرایش نظرات مشتریان</q-tooltip>
            </q-btn>
          </div>
        </div>

        <!-- Navigation Controls -->
        <div class="test-nav-controls">
          <button
            class="test-nav-btn prev-btn"
            @click="prevSlide"
            aria-label="نظر قبلی"
          >
            <q-icon name="arrow_forward" size="18px" />
          </button>
          <button
            class="test-nav-btn next-btn"
            @click="nextSlide"
            aria-label="نظر بعدی"
          >
            <q-icon name="arrow_back" size="18px" />
          </button>
        </div>
      </div>

      <!-- Testimonials Cards Grid / Carousel -->
      <div class="testimonials-grid">
        <article
          v-for="(item, idx) in visibleReviews"
          :key="item.id || idx"
          class="test-card"
          :class="{ 'test-card-highlight': idx === activeIndex }"
        >
          <!-- Quote Icon -->
          <div class="test-quote-icon">
            <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor">
              <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
            </svg>
          </div>

          <!-- Review Text -->
          <p class="test-quote-text">
            «{{ item.text }}»
          </p>

          <!-- Client Info -->
          <div class="test-client-row">
            <div class="test-avatar">
              <span class="avatar-initials">{{ item.initials || initialsOf(item.name) }}</span>
            </div>
            <div class="test-client-meta">
              <strong class="test-client-name">{{ item.name }}</strong>
              <span class="test-client-role">{{ item.role }}</span>
            </div>
            <div class="test-rating">
              <span v-for="star in 5" :key="star" class="star-icon">★</span>
            </div>
          </div>
        </article>
      </div>

    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuth } from 'src/composables/useAuth'
import { useHomeAdmin } from 'src/composables/useHomeAdmin'
import { useHomeContent } from 'src/composables/useHomeContent'

// The header comes from the settings row, the quotes from the ordered list.
const { settings, reviews } = useHomeContent()
const { isAdmin } = useAuth()
const { authorized, openReviewsDialog } = useHomeAdmin()

const activeIndex = ref(1)

// The section has three columns, so the first three rows are the ones shown;
// the dialog reorders the list to pick which three those are.
const visibleReviews = computed(() => reviews.value.slice(0, 3))

// A row saved without initials still gets an avatar: the first letter of the
// first two words of the name.
const initialsOf = (name) => {
  const parts = String(name || '').trim().split(/\s+/).filter(Boolean)
  if (!parts.length) return ''
  if (parts.length === 1) return parts[0].slice(0, 2)
  return parts[0][0] + parts[1][0]
}

function prevSlide () {
  if (!visibleReviews.value.length) return
  activeIndex.value = (activeIndex.value - 1 + visibleReviews.value.length) % visibleReviews.value.length
}

function nextSlide () {
  if (!visibleReviews.value.length) return
  activeIndex.value = (activeIndex.value + 1) % visibleReviews.value.length
}
</script>

<style scoped>
.nx-testimonials-section {
  direction: rtl;
  width: 100%;
  padding: 50px 0 120px;
  background: var(--nx-black, #0A0A0B);
  color: #FFFFFF;
  position: relative;
  z-index: 2;
}

/* Header */
.testimonials-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 44px;
}

.test-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* The admin pencil sits on the title line (admins only). */
.test-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.test-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--nx-yellow, #FFD54A);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.yellow-star {
  font-size: 14px;
}

.test-title {
  margin: 0;
  color: #FFFFFF;
  font-size: clamp(24px, 3.2vw, 36px);
  font-weight: 900;
  letter-spacing: -0.02em;
}

/* Controls */
.test-nav-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.test-nav-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #18181C;
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s var(--cl-ease);
}

.test-nav-btn:hover {
  background: var(--nx-yellow, #FFD54A);
  color: #111113;
  border-color: var(--nx-yellow, #FFD54A);
  transform: scale(1.05);
}

/* Cards Grid */
.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 26px;
}

.test-card {
  position: relative;
  background: #141417;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 32px 28px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 280px;
  transition: all 0.3s var(--cl-ease);
}

.test-card:hover,
.test-card-highlight {
  border-color: rgba(255, 213, 74, 0.4);
  box-shadow: 0 16px 40px -10px rgba(0, 0, 0, 0.8), 0 0 25px rgba(255, 213, 74, 0.06);
  transform: translateY(-4px);
}

.test-quote-icon {
  color: var(--nx-yellow, #FFD54A);
  opacity: 0.85;
  margin-bottom: 18px;
}

.test-quote-text {
  color: #D4D4D8;
  font-size: 14.5px;
  line-height: 1.9;
  margin: 0 0 24px;
  flex-grow: 1;
}

/* Client */
.test-client-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding-top: 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.test-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: #23232A;
  border: 1.5px solid var(--nx-yellow);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-initials {
  font-size: 13px;
  font-weight: 800;
  color: var(--nx-yellow);
}

.test-client-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.test-client-name {
  color: #FFFFFF;
  font-size: 14px;
  font-weight: 800;
}

.test-client-role {
  color: #A1A1AA;
  font-size: 11.5px;
}

.test-rating {
  color: var(--nx-yellow);
  font-size: 12px;
  letter-spacing: 2px;
}

@media (max-width: 960px) {
  .testimonials-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media (max-width: 600px) {
  .testimonials-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>

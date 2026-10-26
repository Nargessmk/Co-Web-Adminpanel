<template>
  <article class="solution-card">

    <!-- Cover -->
    <router-link
      :to="`/solutions/${article.slug}`"
      class="solution-image-wrapper"
    >
      <img
        v-if="article.image_url"
        :src="formatMediaUrl(article.image_url)"
        :alt="article.title"
        class="solution-image"
        loading="lazy"
        @error="e => handleImageError(e)"
      />

      <div
        v-else
        class="solution-image-placeholder"
      >
        <q-icon
          name="menu_book"
          size="52px"
        />
      </div>

      <div class="card-shine"></div>
    </router-link>

    <!-- Content -->
    <div class="solution-content">

      <div class="solution-meta">
        <span
          v-if="article.created_at"
          class="meta-date"
        >
          <q-icon name="event" size="15px" />
          {{ formatDate(article.created_at) }}
        </span>

        <span
          v-if="article.author_name"
          class="meta-author"
        >
          <img
            v-if="article.author_image_url"
            :src="formatMediaUrl(article.author_image_url)"
            :alt="article.author_name"
            class="meta-author-avatar"
            loading="lazy"
            decoding="async"
            @error="e => handleImageError(e, '/Modern 3D Tech Dashboard Illustration(1).png')"
          />
          <q-icon
            v-else
            name="person"
            size="15px"
          />
          {{ article.author_name }}
        </span>
      </div>

      <router-link
        :to="`/solutions/${article.slug}`"
        class="solution-title-link"
      >
        <h3>{{ article.title }}</h3>
      </router-link>

      <p v-if="article.summary">
        {{ article.summary }}
      </p>

      <router-link
        :to="`/solutions/${article.slug}`"
        class="solution-link"
      >
        ادامه مطلب
        <q-icon
          name="arrow_back"
          size="18px"
        />
      </router-link>

    </div>

  </article>
</template>

<script setup>
import moment from 'moment-jalaali'
import { formatMediaUrl, handleImageError } from 'src/utils/media'

defineProps({
  article: {
    type: Object,
    required: true
  }
})

function formatDate (date) {
  if (!date) return ''
  return moment(date).format('jYYYY/jMM/jDD')
}
</script>

<style scoped>
.solution-card {
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #FFFFFF;
  border: 1.5px solid var(--nx-ink, #111113);
  border-radius: var(--nx-radius-card, 22px);
  box-shadow: var(--nx-shadow-hard, -4px 5px 0 #111113);
  color: var(--nx-ink, #111113);
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.solution-card:hover {
  transform: translate(3px, -3px);
  box-shadow: var(--nx-shadow-hard-lg, -7px 8px 0 #111113);
}

/* Cover */
.solution-image-wrapper {
  position: relative;
  display: block;
  height: 210px;
  overflow: hidden;
  background: #EFEFEF;
  border-bottom: 1.5px solid var(--nx-ink, #111113);
  text-decoration: none;
}

.solution-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.solution-card:hover .solution-image {
  transform: scale(1.06);
}

.solution-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--nx-ink, #111113);
  background:
    radial-gradient(circle at 30% 25%, rgba(255, 213, 74, 0.85), transparent 55%),
    #EFEFEF;
}

.card-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 60%;
  height: 210px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.65), transparent);
  transition: left 0.6s ease;
  pointer-events: none;
}

.solution-card:hover .card-shine {
  left: 130%;
}

/* Content */
.solution-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 22px;
  background: #FFFFFF;
}

.solution-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 14px;
  margin-bottom: 12px;
  color: #71717A;
  font-size: 12px;
  font-weight: 600;
}

.meta-date,
.meta-author {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.meta-author-avatar {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid rgba(17, 17, 19, 0.2);
}

.solution-title-link {
  text-decoration: none;
}

.solution-title-link h3 {
  margin: 0 0 10px;
  color: var(--nx-ink, #111113);
  font-size: 18px;
  font-weight: 800;
  line-height: 1.6;
  transition: color 0.3s ease;
}

.solution-card:hover .solution-title-link h3 {
  color: var(--nx-gold-ink, #8A6100);
}

.solution-content p {
  margin: 0 0 18px;
  color: #52525B;
  font-size: 13.5px;
  line-height: 1.85;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.solution-link {
  margin-top: auto;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--nx-ink, #111113);
  font-size: 13.5px;
  font-weight: 800;
  text-decoration: none;
  transition: gap 0.3s ease;
}

.solution-link .q-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--nx-yellow, #FFD54A);
  border: 1.5px solid var(--nx-ink, #111113);
  padding: 4px;
  box-shadow: -2px 3px 0 var(--nx-ink, #111113);
  transition: transform 0.25s ease;
}

.solution-card:hover .solution-link .q-icon {
  transform: translateX(-4px);
}

@media (max-width: 600px) {
  .solution-image-wrapper,
  .card-shine {
    height: 170px;
  }

  .solution-content {
    padding: 16px;
  }

  .solution-title-link h3 {
    font-size: 16px;
  }

  .solution-content p {
    font-size: 12.5px;
    line-height: 1.7;
  }
}
</style>

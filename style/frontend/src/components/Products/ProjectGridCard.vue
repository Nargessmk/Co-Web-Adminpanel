<template>
  <q-card flat class="project-card column justify-between full-height">
    <!-- Card Thumbnail / Cover -->
    <div class="project-thumb-frame">
      <router-link :to="item.link" class="thumb-link" :aria-label="item.title">
        <img :src="item.image" :alt="item.title" loading="lazy" />
      </router-link>

      <!-- Top Badges on Image -->
      <div class="thumb-badges-row">
        <span class="thumb-badge-cat">{{ item.category }}</span>
        <span v-if="item.badge" class="thumb-badge-featured">
          <span class="status-dot"></span>
          {{ item.badge }}
        </span>
      </div>

      <!-- External URL Icon if available -->
      <a
        v-if="item.externalUrl"
        :href="item.externalUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="thumb-ext-btn"
        title="مشاهده سامانه آنلاین"
        @click.stop
      >
        <q-icon name="open_in_new" size="14px" />
      </a>
    </div>

    <!-- Card Body (q-card-section) -->
    <q-card-section class="project-card-body col column">
      <div class="project-card-meta row items-center">
        <span class="project-num-tag">{{ item.num }}</span>
        <span v-if="item.tags && item.tags.length" class="meta-tag">{{ item.tags[0] }}</span>
      </div>

      <h3 class="project-card-title">
        <router-link :to="item.link" class="title-link">
          {{ item.title }}
        </router-link>
      </h3>

      <p class="project-card-desc">
        {{ item.description }}
      </p>

      <!-- Tech Stack Tags -->
      <div v-if="item.tags && item.tags.length" class="project-tags-row row items-center q-mt-auto">
        <span
          v-for="(tag, tIdx) in item.tags.slice(0, 3)"
          :key="tIdx"
          class="project-tag-pill"
        >
          {{ tag }}
        </span>
        <span v-if="item.tags.length > 3" class="project-tag-pill more-tag">
          +{{ item.tags.length - 3 }}
        </span>
      </div>
    </q-card-section>

    <!-- Card Footer / Actions (q-card-actions) -->
    <q-card-actions class="project-card-footer row items-center justify-between">
      <router-link :to="item.link" class="project-cta-link row items-center">
        <span>بررسی معماری و جزئیات</span>
        <q-icon name="arrow_back" size="15px" class="cta-arrow q-mr-xs" />
      </router-link>

      <a
        v-if="item.externalUrl"
        :href="item.externalUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="project-online-link row items-center"
        title="ورود به سامانه آنلاین"
      >
        <q-icon name="launch" size="13px" class="q-ml-xs" />
        <span>مشاهده</span>
      </a>
    </q-card-actions>
  </q-card>
</template>

<script setup>
defineProps({
  item: {
    type: Object,
    required: true,
  },
})
</script>

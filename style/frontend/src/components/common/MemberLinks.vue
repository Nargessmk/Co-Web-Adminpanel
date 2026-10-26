<template>
  <!--
    The team member's social links.

    These are the brand marks drawn inline as SVG / text rather than asked for by
    name (`fab fa-github`). This project bundles only Material Icons, so a
    Font Awesome name resolves to nothing and the button renders empty — which
    is why the GitHub and LinkedIn icons used to be missing while the website
    one (a Material icon) showed. Keeping the artwork here means the About page,
    the résumé dialog and the admin list cannot drift apart again.
  -->
  <div class="member-links" :class="[`member-links--${variant}`]">
    <a
      v-if="member.github_url"
      :href="member.github_url"
      target="_blank"
      rel="noopener"
      class="member-link github"
      title="GitHub"
      aria-label="GitHub"
    >
      <svg viewBox="0 0 16 16" :width="iconSize" :height="iconSize" fill="currentColor" aria-hidden="true">
        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
      </svg>
    </a>

    <a
      v-if="member.website_url"
      :href="member.website_url"
      target="_blank"
      rel="noopener"
      class="member-link website"
      title="Website"
      aria-label="Website"
    >
      <svg viewBox="0 0 24 24" :width="iconSize" :height="iconSize" fill="currentColor" aria-hidden="true">
        <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm6.92 6h-2.95a15.7 15.7 0 0 0-1.38-3.56A8.03 8.03 0 0 1 18.92 8zM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 1.08-2.76 1.91-3.96zM4.26 14a7.8 7.8 0 0 1 0-4h3.38a16.5 16.5 0 0 0 0 4H4.26zm.82 2h2.95c.32 1.25.79 2.45 1.38 3.56A7.99 7.99 0 0 1 5.08 16zm2.95-8H5.08a7.99 7.99 0 0 1 4.33-3.56A15.7 15.7 0 0 0 8.03 8zM12 19.96c-.83-1.2-1.48-2.53-1.91-3.96h3.82A15.7 15.7 0 0 1 12 19.96zM14.34 14H9.66a14.7 14.7 0 0 1 0-4h4.68a14.7 14.7 0 0 1 0 4zm.25 5.56c.59-1.11 1.06-2.31 1.38-3.56h2.95a8.03 8.03 0 0 1-4.33 3.56zM16.36 14a16.5 16.5 0 0 0 0-4h3.38a7.8 7.8 0 0 1 0 4h-3.38z" />
      </svg>
    </a>

    <a
      v-if="member.linkedin_url"
      :href="member.linkedin_url"
      target="_blank"
      rel="noopener"
      class="member-link linkedin"
      title="LinkedIn"
      aria-label="LinkedIn"
    >
      <svg viewBox="0 0 24 24" :width="iconSize" :height="iconSize" fill="currentColor" aria-hidden="true">
        <path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45z" />
      </svg>
    </a>
  </div>
</template>

<script setup>
/**
 * A team member's social links, in one place.
 *
 * Each icon appears only when that link is filled in. `variant` is `pill` for
 * the public pages (round, brand-coloured) and `compact` for the admin table
 * (smaller, flat) so the row fits a dense cell.
 */
import { computed } from 'vue'

const props = defineProps({
  // Accepts the member row itself, or the three URLs.
  member: { type: Object, default: () => ({}) },
  // `pill` — the public card (32px); `small` — the same card at the reduced
  // size; `compact` — the admin table cell (26px).
  variant: {
    type: String,
    default: 'pill',
    validator: (value) => ['pill', 'small', 'compact'].includes(value),
  },
})

const SIZES = { pill: 32, small: 27, compact: 26 }
const buttonSize = computed(() => SIZES[props.variant] ?? 32)
const iconSize = computed(() => (props.variant === 'compact' ? 13 : buttonSize.value * 0.47))
</script>

<style scoped>
/* LTR: the row always reads GitHub → Website → LinkedIn, and the order does not
   flip inside a Persian page. */
.member-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  direction: ltr;
}

.member-link {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  transition: transform 0.25s, box-shadow 0.25s;
}

/* Reduced size for the public team card. */
.member-links--small .member-link {
  width: 27px;
  height: 27px;
}

.member-link:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 18px rgba(16, 28, 96, 0.2);
}

.member-link.github { background: #111111; }
.member-link.website { background: #16a34a; }
.member-link.linkedin { background: #0a66c2; border-radius: 8px; }

/* Compact variant for the admin table and mobile card. */
.member-links--compact {
  gap: 6px;
  justify-content: flex-start;
}

.member-links--compact .member-link {
  width: 26px;
  height: 26px;
  box-shadow: 0 2px 6px rgba(16, 28, 96, 0.12);
}

.member-links--compact .member-link:hover {
  transform: none;
  box-shadow: 0 2px 10px rgba(16, 28, 96, 0.25);
}
</style>

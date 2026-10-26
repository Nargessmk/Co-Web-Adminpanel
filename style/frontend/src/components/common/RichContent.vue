<template>
  <!--
    Renders admin-authored rich text safely.

    Every field edited with `RichTextEditor` must be displayed through this
    component (or `safeHtml()`), never with `{{ }}` — otherwise the stored HTML
    would be printed as literal `<p>` tags. Sanitising lives here so it cannot
    be forgotten at a call site.
  -->
  <div v-if="html" class="rich-content" :class="[`rich-content--${align}`]" v-html="clean"></div>
</template>

<script setup>
/**
 * Display component for HTML written in the admin editors.
 *
 * Defence in depth: the editor sanitises on save, and this sanitises again on
 * the way out, so rows written before the editors existed — or edited through
 * any other path — are cleaned too rather than trusted.
 */
import { computed } from 'vue'
import { safeHtml } from 'src/utils/sanitize'

const props = defineProps({
  html: { type: String, default: '' },
  // `center` for text that sits under a section heading, `start` otherwise.
  align: { type: String, default: 'start' },
})

const clean = computed(() => safeHtml(props.html))
</script>

<style lang="scss">
/* Global (not scoped): the markup is injected via v-html, so scoped styles
   would not reach the generated elements. */

.rich-content {
  color: inherit;
  font-size: inherit;
  line-height: inherit;

  > :first-child { margin-top: 0; }
  > :last-child { margin-bottom: 0; }

  p { margin: 0 0 0.7em; }

  h1, h2, h3, h4, h5, h6 {
    font-weight: 800;
    line-height: 1.45;
    margin: 1.2em 0 0.5em;
  }
  h1 { font-size: 1.5em; }
  h2 { font-size: 1.32em; }
  h3 { font-size: 1.18em; }
  h4, h5, h6 { font-size: 1.05em; }

  strong, b { font-weight: 800; }
  em, i { font-style: italic; }

  ul, ol {
    margin: 0 0 0.7em;
    padding-inline-start: 1.5em;
  }
  li { margin-bottom: 0.3em; }

  a {
    color: inherit;
    font-weight: 600;
    text-decoration: underline;
  }

  blockquote {
    margin: 0 0 0.7em;
    padding: 0.5em 1em;
    border-inline-start: 3px solid #f5a300;
    background: rgba(245, 163, 0, 0.07);
  }

  pre {
    background: #101c60;
    color: #eef1fa;
    padding: 0.9em 1.1em;
    border-radius: 10px;
    overflow-x: auto;
    direction: ltr;
    text-align: left;
    line-height: 1.7;
    font-size: 0.88em;
    margin: 0 0 0.7em;
  }
  code {
    background: rgba(16, 28, 96, 0.07);
    color: #b5320f;
    padding: 0.1em 0.35em;
    border-radius: 4px;
    font-size: 0.9em;
  }
  pre code { background: none; color: inherit; padding: 0; }

  img {
    max-width: 100%;
    height: auto;
    border-radius: 10px;
  }

  hr {
    border: none;
    border-top: 1px solid rgba(0, 0, 0, 0.12);
    margin: 1.2em 0;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 0 0 0.7em;
  }
  th, td {
    border: 1px solid rgba(0, 0, 0, 0.12);
    padding: 0.5em 0.7em;
    text-align: start;
  }
  th { background: rgba(16, 28, 96, 0.05); font-weight: 700; }
}

.rich-content--center { text-align: center; }
</style>

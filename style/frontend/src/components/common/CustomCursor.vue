<template>
  <div v-if="isEnabled" class="custom-cursor-container" aria-hidden="true">
    <!-- Inner Dot -->
    <div
      ref="cursorDotRef"
      class="cursor-dot"
      :class="{
        'is-active': isHovered,
        'is-down': isMouseDown,
        'is-hidden': !isVisible
      }"
    ></div>

    <!-- Outer Follower Ring -->
    <div
      ref="cursorRingRef"
      class="cursor-ring"
      :class="{
        'is-active': isHovered,
        'is-down': isMouseDown,
        'is-hidden': !isVisible
      }"
    ></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const isEnabled = ref(false)
const isVisible = ref(false)
const isHovered = ref(false)
const isMouseDown = ref(false)

const cursorDotRef = ref(null)
const cursorRingRef = ref(null)

let mouseX = -100
let mouseY = -100
let ringX = -100
let ringY = -100
let rafId = null

function render () {
  // Smooth lerp for ring follower
  ringX += (mouseX - ringX) * 0.18
  ringY += (mouseY - ringY) * 0.18

  if (cursorDotRef.value) {
    cursorDotRef.value.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0)`
  }

  if (cursorRingRef.value) {
    cursorRingRef.value.style.transform = `translate3d(${ringX}px, ${ringY}px, 0)`
  }

  rafId = requestAnimationFrame(render)
}

function onMouseMove (e) {
  mouseX = e.clientX
  mouseY = e.clientY
  if (!isVisible.value) {
    isVisible.value = true
    ringX = mouseX
    ringY = mouseY
  }

  // Interactive targets check
  const target = e.target
  if (target) {
    const isInteractive = target.closest('a, button, input, textarea, select, [role="button"], .cat-pill, .btn-pill, .q-btn, .clickable')
    isHovered.value = !!isInteractive
  }
}

function onMouseDownHandler () {
  isMouseDown.value = true
}

function onMouseUpHandler () {
  isMouseDown.value = false
}

function onMouseLeave () {
  isVisible.value = false
}

function onMouseEnter () {
  isVisible.value = true
}

onMounted(() => {
  if (typeof window === 'undefined') return

  // Only enable on pointer fine devices (desktop/mouse, not touch)
  const hasFinePointer = window.matchMedia('(pointer: fine)').matches
  if (!hasFinePointer) {
    isEnabled.value = false
    return
  }

  isEnabled.value = true
  window.addEventListener('mousemove', onMouseMove, { passive: true })
  window.addEventListener('mousedown', onMouseDownHandler, { passive: true })
  window.addEventListener('mouseup', onMouseUpHandler, { passive: true })
  document.addEventListener('mouseleave', onMouseLeave)
  document.addEventListener('mouseenter', onMouseEnter)

  rafId = requestAnimationFrame(render)
})

onUnmounted(() => {
  if (typeof window === 'undefined') return
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mousedown', onMouseDownHandler)
  window.removeEventListener('mouseup', onMouseUpHandler)
  document.removeEventListener('mouseleave', onMouseLeave)
  document.removeEventListener('mouseenter', onMouseEnter)

  if (rafId) {
    cancelAnimationFrame(rafId)
  }
})
</script>

<style scoped>
.custom-cursor-container {
  pointer-events: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 99999;
  overflow: hidden;
}

/* Central dot */
.cursor-dot {
  position: fixed;
  top: -4px;
  left: -4px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #ffd54a;
  box-shadow: 0 0 10px rgba(255, 213, 74, 0.8);
  pointer-events: none;
  transition: opacity 0.2s ease, width 0.2s ease, height 0.2s ease, background-color 0.2s ease;
  will-change: transform;
  z-index: 100000;
}

/* Follower ring */
.cursor-ring {
  position: fixed;
  top: -18px;
  left: -18px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1.5px solid rgba(255, 213, 74, 0.55);
  background-color: rgba(255, 213, 74, 0.04);
  backdrop-filter: blur(0.5px);
  pointer-events: none;
  transition: opacity 0.2s ease, width 0.25s cubic-bezier(0.16, 1, 0.3, 1), height 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease, background-color 0.2s ease, top 0.25s cubic-bezier(0.16, 1, 0.3, 1), left 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  will-change: transform;
  z-index: 99999;
}

/* Hover on interactive elements */
.cursor-ring.is-active {
  top: -24px;
  left: -24px;
  width: 48px;
  height: 48px;
  border-color: #ffd54a;
  background-color: rgba(255, 213, 74, 0.12);
  box-shadow: 0 0 16px rgba(255, 213, 74, 0.25);
}

.cursor-dot.is-active {
  background-color: #ffffff;
  transform-origin: center;
}

/* Click / mouse down state */
.cursor-ring.is-down {
  top: -14px;
  left: -14px;
  width: 28px;
  height: 28px;
  border-color: #ffcc00;
  background-color: rgba(255, 204, 0, 0.25);
}

.cursor-dot.is-down {
  width: 5px;
  height: 5px;
  top: -2.5px;
  left: -2.5px;
}

/* Hidden state */
.cursor-dot.is-hidden,
.cursor-ring.is-hidden {
  opacity: 0;
}
</style>

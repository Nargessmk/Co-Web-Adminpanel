<template>
  <div class="hero-orbit">

    <!-- Background glow -->
    <div class="orbit-glow"></div>

    <!-- Animated ring gradients -->
    <div class="ring-glow ring-glow-inner"></div>
    <div class="ring-glow ring-glow-outer"></div>

    <!-- Outer orbit -->
    <!-- The rings and the cards inside them counter-rotate on the same clock:
         remounting both whenever the list changes keeps their animations in
         step, otherwise a card added later stays tilted for good. -->
    <div :key="`outer-${orbitVersion}`" class="orbit orbit-outer">

      <HeroOrbitItem
        v-for="(item, index) in outerItems"
        :key="`outer-${orbitVersion}-${item.label}-${index}`"
        :label="item.label"
        :icon="item.icon"
        :color="item.color"
        :x="item.x"
        :y="item.y"
      />

    </div>


    <!-- Inner orbit -->
    <div :key="`inner-${orbitVersion}`" class="orbit orbit-inner">

      <HeroOrbitItem
        v-for="(item, index) in innerItems"
        :key="`inner-${orbitVersion}-${item.label}-${index}`"
        :label="item.label"
        :icon="item.icon"
        :color="item.color"
        :x="item.x"
        :y="item.y"
      />

    </div>


    <!-- =========================
         CENTER BRAND
    ========================== -->

    <div class="orbit-center">

      <div class="center-glow"></div>

      <div class="center-circle">

        <!-- The site logo the admin set in the header/footer dialog -->
        <div
          class="cloudland-logo-wrapper"
          :class="{ 'wrapper-text': !siteLogo }"
        >

          <img
            v-if="siteLogo"
            :src="siteLogo"
            :alt="siteName"
            class="cloudland-logo"
            decoding="async"
          />

          <span v-else class="cloudland-logo-text">{{ siteName }}</span>

        </div>

        <div class="center-caption">
          {{ homeSettings.orbit_caption }}
        </div>

      </div>

    </div>


    <!-- Decorative dots -->
    <span class="light-dot dot-1"></span>
    <span class="light-dot dot-2"></span>
    <span class="light-dot dot-3"></span>
    <span class="light-dot dot-4"></span>
    <span class="light-dot dot-5"></span>

  </div>
</template>


<script setup>

import { computed } from 'vue'

import HeroOrbitItem from './HeroOrbitItem.vue'
import { useSiteContent } from 'src/composables/useSiteContent'
import { useHomeContent } from 'src/composables/useHomeContent'

const { settings: siteSettings } = useSiteContent()
const { settings: homeSettings, orbitItems } = useHomeContent()

const siteLogo = computed(() => siteSettings.value.logo_url || '')
const siteName = computed(() => siteSettings.value.site_name || 'CloudLand')

/* =========================================
   POSITIONS
   Items are placed on a circle by their index, so adding or removing one
   in the admin dialog keeps the ring balanced.
========================================== */

function place (ring, startDegrees, radius) {
  const rows = (orbitItems.value || []).filter((item) => (
    (item.ring === 'outer' ? 'outer' : 'inner') === ring && item.label && item.icon
  ))

  const step = 360 / Math.max(rows.length, 1)

  return rows.map((item, index) => {
    const angle = ((startDegrees + index * step) * Math.PI) / 180
    return {
      ...item,
      x: Math.round(Math.cos(angle) * radius),
      y: Math.round(Math.sin(angle) * radius),
    }
  })
}

/* Inner ring: the four cardinals; outer ring: the four corners. */
const innerItems = computed(() => place('inner', -90, 125))
const outerItems = computed(() => place('outer', -135, 135 * Math.SQRT2))

// Changes only when an item is added, removed or edited — the two rings are
// remounted together so their rotations restart in step with the cards.
const orbitVersion = computed(() => (orbitItems.value || [])
  .map((item) => `${item.ring}:${item.label}:${item.icon}:${item.color}`)
  .join('|'))

</script>


<style scoped>

/* =========================================
   MAIN ORBIT
========================================== */

.hero-orbit {

  position: relative;

  width: 620px;
  height: 620px;
  max-width: 100%;

  display: flex;

  align-items: center;
  justify-content: center;

  direction: ltr;

}


/* =========================================
   BACKGROUND GLOW
========================================== */

.orbit-glow {

  position: absolute;

  width: 430px;
  height: 430px;

  border-radius: 50%;

  background:
    radial-gradient(
      circle,
      rgba(220, 225, 255, 0.85) 0%,
      rgba(238, 240, 255, 0.5) 38%,
      rgba(248, 249, 255, 0) 72%
    );

  filter: blur(5px);

  pointer-events: none;

}


/* =========================================
   RING GLOW EFFECTS
========================================== */

.ring-glow {
  position: absolute;

  left: 50%;
  top: 50%;

  border-radius: 50%;

  pointer-events: none;
}

.ring-glow-inner {
  width: 280px;
  height: 280px;

  margin-left: -140px;
  margin-top: -140px;

  border: 2px solid transparent;

  background:
    linear-gradient(#fff, #fff) padding-box,
    linear-gradient(135deg, rgba(26, 36, 114, 0.15), rgba(245, 163, 0, 0.2), rgba(26, 36, 114, 0.15)) border-box;

  animation: spin-slow 15s linear infinite;
}

.ring-glow-outer {
  width: 410px;
  height: 410px;

  margin-left: -205px;
  margin-top: -205px;

  border: 1.5px solid transparent;

  background:
    linear-gradient(#fff, #fff) padding-box,
    linear-gradient(315deg, rgba(245, 163, 0, 0.1), rgba(26, 36, 114, 0.12), rgba(245, 163, 0, 0.1)) border-box;

  animation: spin-slow 22s linear infinite reverse;
}


/* =========================================
   ORBITS
========================================== */

.orbit {
  position: absolute;
  left: 50%;
  top: 50%;
  border-radius: 50%;
  border: 1.5px dashed rgba(37, 99, 235, 0.18);
  pointer-events: none;
}


/* Inner */

.orbit-inner {

  width: 270px;
  height: 270px;

  margin-left: -135px;
  margin-top: -135px;

  animation:
    rotate-inner
    20s
    linear
    infinite;

}


/* Outer */

.orbit-outer {

  width: 400px;
  height: 400px;

  margin-left: -200px;
  margin-top: -200px;

  animation:
    rotate-outer
    27s
    linear
    infinite;

}


/* =========================================
   KEEP ITEMS UPRIGHT
========================================== */

.orbit-inner :deep(.orbit-card) {

  animation:
    counter-inner
    20s
    linear
    infinite;

}


.orbit-outer :deep(.orbit-card) {

  animation:
    counter-outer
    27s
    linear
    infinite;

}


/* =========================================
   CENTER
========================================== */

.orbit-center {

  position: relative;

  z-index: 30;

  width: 160px;
  height: 160px;

  display: flex;

  align-items: center;
  justify-content: center;

}


/* =========================================
   CENTER GLOW
========================================== */

.center-glow {

  position: absolute;

  width: 200px;
  height: 200px;

  border-radius: 50%;

  background:
    radial-gradient(
      circle,
      rgba(26, 36, 114, 0.12),
      rgba(245, 163, 0, 0.06),
      rgba(26, 36, 114, 0) 70%
    );

  filter: blur(20px);

  animation:
    center-pulse
    3.5s
    ease-in-out
    infinite;

}


/* =========================================
   CENTER CIRCLE
========================================== */

.center-circle {
  position: relative;
  width: 155px;
  height: 155px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(226, 232, 240, 0.9);
  box-shadow:
    0 16px 40px -4px rgba(15, 23, 42, 0.1),
    0 0 0 6px rgba(255, 255, 255, 0.6),
    inset 0 1px 2px rgba(255, 255, 255, 1);
  overflow: hidden;
  transition: transform 0.4s var(--cl-ease), border-color 0.4s var(--cl-ease), box-shadow 0.4s var(--cl-ease);
}

.center-circle:hover {
  transform: scale(1.04);
  border-color: rgba(37, 99, 235, 0.3);
  box-shadow:
    0 24px 50px -4px rgba(37, 99, 235, 0.16),
    0 0 0 6px rgba(37, 99, 235, 0.08),
    inset 0 1px 2px rgba(255, 255, 255, 1);
}


/* =========================================
   CLOUDLAND LOGO
========================================== */

.cloudland-logo-wrapper {

  width: 105px;
  height: 72px;

  display: flex;

  align-items: center;
  justify-content: center;

  overflow: hidden;

  animation:
    logo-float
    4s
    ease-in-out
    infinite;

}


/*
  The original logo contains a white
  background. Since the center is also
  white, we remove the visual edge.
*/

.cloudland-logo {

  width: 108px;
  height: auto;

  display: block;

  object-fit: contain;

  transition: filter 0.4s ease;
}

.center-circle:hover .cloudland-logo {
  filter: drop-shadow(0 4px 16px rgba(245, 163, 0, 0.2));
}

/* No logo stored: the site name stands in for the image */
.cloudland-logo-wrapper.wrapper-text {
  width: auto;
  min-width: 105px;
  padding: 0 8px;
}

.cloudland-logo-text {
  color: #1A2472;
  font-family: 'Vazirmatn', sans-serif;
  font-size: 15px;
  font-weight: 800;
  white-space: nowrap;
}



/* =========================================
   CENTER CAPTION
========================================== */

.center-caption {

  margin-top: 4px;

  color:
    #1A2472;

  font-family:
    'Vazirmatn',
    sans-serif;

  font-size: 10px;

  font-weight: 700;

  white-space: nowrap;

}


/* =========================================
   LIGHT DOTS
========================================== */

.light-dot {

  position: absolute;

  width: 7px;
  height: 7px;

  border-radius: 50%;

  animation:
    dot-float
    4s
    ease-in-out
    infinite;

}


/* Dot 1 */

.dot-1 {
  top: 105px;
  right: 65px;

  background: #1a2472;
  box-shadow: 0 0 15px rgba(26, 36, 114, 0.35);
}


/* Dot 2 */

.dot-2 {
  bottom: 120px;
  right: 85px;

  background: #f5a300;
  box-shadow: 0 0 15px rgba(245, 163, 0, 0.4);

  animation-delay: 1s;
}


/* Dot 3 */

.dot-3 {
  bottom: 85px;
  left: 90px;

  background: #1a2472;
  box-shadow: 0 0 15px rgba(26, 36, 114, 0.35);

  animation-delay: 2s;
}


/* Dot 4 */

.dot-4 {
  top: 80px;
  left: 65px;

  background: #f5a300;
  box-shadow: 0 0 12px rgba(245, 163, 0, 0.35);

  animation-delay: 0.5s;
  width: 5px;
  height: 5px;
}


/* Dot 5 */

.dot-5 {
  top: 200px;
  right: 25px;

  background: #1a2472;
  box-shadow: 0 0 10px rgba(26, 36, 114, 0.3);

  animation-delay: 3s;
  width: 5px;
  height: 5px;
}


/* =========================================
   ANIMATIONS
========================================== */

@keyframes rotate-inner {

  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }

}


@keyframes rotate-outer {

  from {
    transform: rotate(360deg);
  }

  to {
    transform: rotate(0deg);
  }

}


@keyframes counter-inner {

  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(-360deg);
  }

}


@keyframes counter-outer {

  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }

}


@keyframes center-pulse {

  0%,
  100% {

    transform:
      scale(1);

    opacity:
      0.6;

  }

  50% {

    transform:
      scale(1.1);

    opacity:
      1;

  }

}


@keyframes logo-float {

  0%,
  100% {

    transform:
      translateY(0);

  }

  50% {

    transform:
      translateY(-5px);

  }

}


@keyframes dot-float {

  0%,
  100% {

    transform:
      translateY(0);

    opacity:
      0.6;

  }

  50% {

    transform:
      translateY(-12px);

    opacity:
      1;

  }

}


/* =========================================
   RESPONSIVE
========================================== */

@media (max-width: 900px) {

  .hero-orbit {

    width: 500px;
    height: 500px;

  }

}

@media (max-width: 600px) {

  .hero-orbit {

    width: 300px;
    height: 300px;

    transform:
      scale(0.8);

  }

}

@media (max-width: 400px) {

  .hero-orbit {

    width: 250px;
    height: 250px;

    transform:
      scale(0.7);

  }

}

</style>

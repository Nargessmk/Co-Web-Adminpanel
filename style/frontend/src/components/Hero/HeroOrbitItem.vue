<template>
  <div class="orbit-item">
    <div class="orbit-card double-bezel">
      <div class="orbit-card-inner double-bezel-inner">
        <div class="icon-ring" :style="{ backgroundColor: hexToAlpha(color, 0.1) }">
          <q-icon
            :name="icon"
            size="20px"
            class="orbit-icon"
            :style="{ color }"
          />
        </div>

        <span class="orbit-label">
          {{ label }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: '#2563EB'
  },
  x: {
    type: Number,
    required: true
  },
  y: {
    type: Number,
    required: true
  },
  animation: {
    type: String,
    default: 'inner'
  }
})

function hexToAlpha(color, alpha) {
  if (color.startsWith('#')) {
    let c = color.substring(1)
    if (c.length === 3) {
      c = c[0] + c[0] + c[1] + c[1] + c[2] + c[2]
    }
    const r = parseInt(c.substring(0, 2), 16)
    const g = parseInt(c.substring(2, 4), 16)
    const b = parseInt(c.substring(4, 6), 16)
    return `rgba(${r}, ${g}, ${b}, ${alpha})`
  }
  return 'rgba(37, 99, 235, 0.1)'
}
</script>

<style scoped>
.orbit-item {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 78px;
  height: 78px;
  margin-left: -39px;
  margin-top: -39px;
  transform: translate(
    calc(v-bind(x) * 1px),
    calc(v-bind(y) * 1px)
  );
  z-index: 10;
}

.orbit-card {
  width: 78px;
  height: 78px;
  padding: 3px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.08), inset 0 1px 1px rgba(255, 255, 255, 0.9);
  transition: transform 0.3s var(--cl-ease), box-shadow 0.3s var(--cl-ease), border-color 0.3s var(--cl-ease);
}

.orbit-card-inner {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  border-radius: 17px;
  background: #ffffff;
}

.orbit-card:hover {
  transform: scale(1.12);
  border-color: rgba(37, 99, 235, 0.35);
  box-shadow: 0 10px 24px -4px rgba(37, 99, 235, 0.15), 0 0 12px rgba(37, 99, 235, 0.1);
}

.icon-ring {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.orbit-label {
  color: var(--cl-text);
  font-family: inherit;
  font-size: 10.5px;
  font-weight: 700;
  white-space: nowrap;
  letter-spacing: -0.01em;
}

.orbit-icon {
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.05));
}

@media (max-width: 600px) {
  .orbit-item {
    width: 60px;
    height: 60px;
    margin-left: -30px;
    margin-top: -30px;
  }

  .orbit-card {
    width: 60px;
    height: 60px;
    padding: 2px;
    border-radius: 16px;
  }

  .orbit-card-inner {
    border-radius: 14px;
    gap: 2px;
  }

  .icon-ring {
    width: 26px;
    height: 26px;
  }

  .orbit-icon {
    font-size: 16px !important;
  }

  .orbit-label {
    font-size: 8.5px;
  }
}
</style>

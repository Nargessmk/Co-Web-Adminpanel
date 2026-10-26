<template>
  <section class="engineering-process-section">
    <div class="container">
      <div class="process-head text-center">
        <div class="section-tag">
          <span class="tag-dot"></span>
          <span>انضباط سازمانی</span>
        </div>
        <h2 class="process-title">فرآیند مهندسی و اجرای پروژه‌ها</h2>
        <p class="process-desc">
          از نخستین گفت‌وگو تا استقرار نهایی در محیط عملیاتی، فرآیند اجرای پروژه‌ها بر پایه چرخه‌های بازخورد سریع و استانداردهای چابک سازمانی بنا شده است.
        </p>
      </div>

      <!-- Process Steps Grid using Quasar Responsive Classes & q-card -->
      <div class="row q-col-gutter-md">
        <div
          v-for="(step, sIdx) in solutionsStore.processSteps"
          :key="sIdx"
          class="col-12 col-sm-6 col-md-3"
        >
          <q-card flat class="process-step-card column justify-between full-height">
            <q-card-section class="q-pa-none">
              <div class="step-num-pill">{{ step.num }}</div>
              <h3 class="step-card-title">{{ step.title }}</h3>
              <p class="step-card-desc">{{ step.desc }}</p>
            </q-card-section>

            <q-card-section class="q-pa-none">
              <div class="step-deliverable">
                <strong>خروجی کلیدی:</strong> {{ step.deliverable }}
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useSolutionsStore } from 'src/stores/solutions'

const solutionsStore = useSolutionsStore()
</script>

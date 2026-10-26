<template>
  <q-select
    :model-value="modelValue"
    :options="options"
    emit-value
    map-options
    outlined
    dense
    option-dense
    :label="label"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <template #option="scope">
      <q-item v-bind="scope.itemProps">
        <q-item-section avatar>
          <q-icon :name="scope.opt.value" />
        </q-item-section>
        <q-item-section>
          <q-item-label>{{ scope.opt.label }}</q-item-label>
        </q-item-section>
      </q-item>
    </template>
    <template #selected>
      <span class="selected-icon">
        <q-icon :name="modelValue" />
        {{ selectedLabel }}
      </span>
    </template>
  </q-select>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: 'آیکون' },
  // Another page can pass its own palette; the About list stays the default.
  options: { type: Array, default: null }
})

defineEmits(['update:modelValue'])

// Icons that fit the About page sections.
const ICON_OPTIONS = [
  { label: 'تیک / موفقیت', value: 'task_alt' },
  { label: 'گروه افراد', value: 'groups' },
  { label: 'تجربه / مدال', value: 'workspace_premium' },
  { label: 'پشتیبانی', value: 'headset_mic' },
  { label: 'ایده / هدف', value: 'emoji_objects' },
  { label: 'چشم‌انداز', value: 'visibility' },
  { label: 'ارزش / علاقه', value: 'favorite' },
  { label: 'رشد', value: 'trending_up' },
  { label: 'ابر', value: 'cloud_upload' },
  { label: 'جهانی شدن', value: 'public' },
  { label: 'هوش مصنوعی', value: 'smart_toy' },
  { label: 'تیم متنوع', value: 'diversity_3' },
  { label: 'امنیت', value: 'security' },
  { label: 'سرعت', value: 'bolt' },
  { label: 'نوآوری', value: 'lightbulb' },
  { label: 'کارمند پشتیبانی', value: 'support_agent' },
  { label: 'ایمیل', value: 'mail' },
  { label: 'محصولات', value: 'inventory_2' },
  { label: 'تماس تلفنی', value: 'call' },
  { label: 'گفتگو', value: 'chat' },
  { label: 'وبسایت', value: 'language' },
  { label: 'ستاره', value: 'star' },
  { label: 'کدنویسی', value: 'code' },
  { label: 'تحلیل', value: 'insights' },
  { label: 'همکاری', value: 'handshake' },
  { label: 'پروژه', value: 'work' },
  { label: 'زمان‌بندی', value: 'schedule' },
  { label: 'انبار / فروشگاه', value: 'storefront' }
]

const selectedLabel = computed(() => {
  const list = props.options || ICON_OPTIONS
  const found = list.find((option) => option.value === props.modelValue)
  return found ? found.label : (props.modelValue || 'انتخاب آیکون')
})
</script>

<style scoped>
.selected-icon {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
</style>

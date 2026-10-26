<template>
  <div class="master-rich-editor" :class="[`dir-${dir}`, { 'has-error': !!error }]">
    <!-- Top Action Toolbar -->
    <div class="editor-toolbar">
      <!-- Group: History -->
      <div class="toolbar-group">
        <button type="button" class="tool-btn" title="بازگشت (Ctrl+Z)" @click="exec('undo')">
          <q-icon name="undo" size="18px" />
        </button>
        <button type="button" class="tool-btn" title="ازنو (Ctrl+Y)" @click="exec('redo')">
          <q-icon name="redo" size="18px" />
        </button>
      </div>

      <div class="toolbar-divider"></div>

      <!-- Group: Formats & Headings -->
      <div class="toolbar-group">
        <q-btn-dropdown
          flat
          dense
          no-caps
          class="heading-dropdown-btn"
          :label="currentFormatLabel"
        >
          <q-list class="editor-dropdown-list">
            <q-item clickable v-close-popup @click="formatBlock('p')">
              <q-item-section>متن معمولی (پاراگراف)</q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="formatBlock('h2')">
              <q-item-section><span style="font-weight: 800; font-size: 16px;">عنوان اصلی (H2)</span></q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="formatBlock('h3')">
              <q-item-section><span style="font-weight: 700; font-size: 14px;">عنوان فرعی (H3)</span></q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="formatBlock('blockquote')">
              <q-item-section><span style="font-style: italic; color: #52525b;">نقل‌قول (Quote)</span></q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="formatBlock('pre')">
              <q-item-section><code style="font-family: monospace; font-size: 12px;">بلوک کد (Code)</code></q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </div>

      <div class="toolbar-divider"></div>

      <!-- Group: Inline styles -->
      <div class="toolbar-group">
        <button type="button" class="tool-btn" title="بولد (Ctrl+B)" @click="exec('bold')">
          <q-icon name="format_bold" size="18px" />
        </button>
        <button type="button" class="tool-btn" title="ایتالیک (Ctrl+I)" @click="exec('italic')">
          <q-icon name="format_italic" size="18px" />
        </button>
        <button type="button" class="tool-btn" title="خط زیر متن (Ctrl+U)" @click="exec('underline')">
          <q-icon name="format_underlined" size="18px" />
        </button>
        <button type="button" class="tool-btn" title="خط‌خورده" @click="exec('strikeThrough')">
          <q-icon name="strikethrough_s" size="18px" />
        </button>
      </div>

      <div class="toolbar-divider"></div>

      <!-- Group: Color Picker -->
      <div class="toolbar-group">
        <q-btn-dropdown flat dense class="color-dropdown-btn" title="رنگ متن">
          <template #label>
            <span class="color-tool-preview" :style="{ backgroundColor: activeColor }"></span>
            <q-icon name="format_color_text" size="16px" />
          </template>
          <div class="color-palette-popover">
            <div class="palette-title">انتخاب رنگ متن</div>
            <div class="colors-grid">
              <button
                v-for="c in THEME_COLORS"
                :key="c.color"
                type="button"
                class="color-chip-btn"
                :style="{ backgroundColor: c.color }"
                :title="c.label"
                @click="applyTextColor(c.color)"
              ></button>
            </div>
          </div>
        </q-btn-dropdown>
      </div>

      <div class="toolbar-divider"></div>

      <!-- Group: Alignments -->
      <div class="toolbar-group">
        <button type="button" class="tool-btn" title="راست‌چین" @click="exec('justifyRight')">
          <q-icon name="format_align_right" size="18px" />
        </button>
        <button type="button" class="tool-btn" title="وسط‌چین" @click="exec('justifyCenter')">
          <q-icon name="format_align_center" size="18px" />
        </button>
        <button type="button" class="tool-btn" title="چپ‌چین" @click="exec('justifyLeft')">
          <q-icon name="format_align_left" size="18px" />
        </button>
        <button type="button" class="tool-btn" title="هم‌تراز (Justify)" @click="exec('justifyFull')">
          <q-icon name="format_align_justify" size="18px" />
        </button>
      </div>

      <div class="toolbar-divider"></div>

      <!-- Group: Lists -->
      <div class="toolbar-group">
        <button type="button" class="tool-btn" title="فهرست نقطه‌ای" @click="exec('insertUnorderedList')">
          <q-icon name="format_list_bulleted" size="18px" />
        </button>
        <button type="button" class="tool-btn" title="فهرست شماره‌دار" @click="exec('insertOrderedList')">
          <q-icon name="format_list_numbered" size="18px" />
        </button>
        <button type="button" class="tool-btn" title="خط جداکننده" @click="exec('insertHorizontalRule')">
          <q-icon name="horizontal_rule" size="18px" />
        </button>
      </div>

      <div class="toolbar-divider"></div>

      <!-- Group: Media & Links -->
      <div class="toolbar-group">
        <button type="button" class="tool-btn" title="افزودن لینک" @click="promptLink">
          <q-icon name="link" size="18px" />
        </button>
        <button type="button" class="tool-btn" title="حذف لینک" @click="exec('unlink')">
          <q-icon name="link_off" size="18px" />
        </button>
        <button type="button" class="tool-btn highlight-tool" title="درج یا آپلود تصویر از سیستم" @click="openImageModal">
          <q-icon name="add_photo_alternate" size="18px" />
        </button>
      </div>

      <!-- Group: Utilities -->
      <div class="toolbar-group toolbar-group--end">
        <button type="button" class="tool-btn" title="پاک‌سازی فرمت" @click="exec('removeFormat')">
          <q-icon name="format_clear" size="17px" />
        </button>
        <button
          type="button"
          class="tool-btn"
          :class="{ active: showSource }"
          title="مشاهده کد HTML"
          @click="showSource = !showSource"
        >
          <q-icon name="code" size="18px" />
        </button>
      </div>
    </div>

    <!-- WYSIWYG Editable Canvas -->
    <div
      v-show="!showSource"
      ref="editableRef"
      class="editor-canvas"
      contenteditable="true"
      :style="{ minHeight: `${minHeight}px` }"
      :placeholder="placeholder"
      @input="handleInput"
      @paste="handlePaste"
      @drop.prevent="handleCanvasDrop"
      @dragover.prevent
    ></div>

    <!-- Raw HTML Code Editor -->
    <div v-show="showSource" class="editor-source-view">
      <div class="source-header">
        <q-icon name="terminal" size="14px" />
        <span>ویرایشگر مستقیم کد HTML</span>
      </div>
      <textarea
        v-model="rawHtml"
        class="source-textarea"
        :style="{ minHeight: `${minHeight}px` }"
        @input="handleSourceInput"
        placeholder="کد HTML را اینجا وارد کنید..."
      ></textarea>
    </div>

    <!-- Footer meta bar -->
    <div class="editor-meta-bar">
      <span v-if="hint" class="editor-hint">{{ hint }}</span>
      <span v-if="error" class="editor-error">{{ error }}</span>
      <span class="editor-stats">{{ wordCount }} کلمه | {{ charCount }} نویسه</span>
    </div>

    <!-- Image Upload & Insert Dialog -->
    <q-dialog v-model="imageModalOpen" persistent>
      <q-card class="editor-image-modal">
        <q-card-section class="modal-head-row">
          <div class="modal-title-wrap">
            <q-icon name="add_photo_alternate" size="22px" color="amber-9" />
            <span class="text-subtitle1 text-weight-bold">درج یا آپلود تصویر در متن</span>
          </div>
          <q-btn flat round dense icon="close" v-close-popup :disable="uploadingImage" />
        </q-card-section>

        <q-tabs
          v-model="imageTab"
          dense
          class="text-grey-8"
          active-color="amber-9"
          indicator-color="amber-9"
          align="justify"
        >
          <q-tab name="upload" icon="cloud_upload" label="آپلود از سیستم" />
          <q-tab name="library" icon="photo_library" label="کتابخانه رسانه" />
          <q-tab name="url" icon="link" label="لینک مستقیم (URL)" />
        </q-tabs>

        <q-separator />

        <q-card-section class="q-pa-md">
          <!-- 1. Tab: Upload from Computer -->
          <div v-if="imageTab === 'upload'" class="upload-pane">
            <div
              class="image-dropzone-box"
              :class="{ 'is-drag-over': isDraggingFile }"
              @click="$refs.modalFileInput.click()"
              @dragover.prevent="isDraggingFile = true"
              @dragleave.prevent="isDraggingFile = false"
              @drop.prevent="onDropModalFile"
            >
              <input
                ref="modalFileInput"
                type="file"
                accept="image/*"
                style="display: none;"
                @change="onModalFileSelected"
              />

              <div v-if="localPreviewUrl" class="local-preview-wrap">
                <img :src="localPreviewUrl" alt="پیش‌نمایش" class="local-preview-img" />
                <span class="local-preview-name">{{ selectedImageFile?.name }} ({{ formatSize(selectedImageFile?.size || 0) }})</span>
                <span class="local-preview-change-hint">برای تعویض تصویر کلیک کنید</span>
              </div>

              <div v-else class="dropzone-empty-wrap">
                <q-icon name="cloud_upload" size="44px" color="amber-9" />
                <span class="dropzone-main-text">تصویر را اینجا بکشید یا برای انتخاب از سیستم کلیک کنید</span>
                <span class="dropzone-sub-text">فرمت‌های مجاز: PNG, JPG, WebP, GIF, SVG (حداکثر ۱۰ مگابایت)</span>
              </div>
            </div>

            <div v-if="uploadingImage" class="q-mt-sm">
              <q-linear-progress indeterminate color="amber-9" class="q-mb-xs" />
              <div class="text-caption text-center text-grey-8">در حال آپلود و ذخیره‌سازی تصویر در سرور...</div>
            </div>
          </div>

          <!-- 2. Tab: Library -->
          <div v-else-if="imageTab === 'library'" class="library-pane">
            <div v-if="loadingLibrary" class="text-center q-pa-lg">
              <q-spinner color="amber-9" size="32px" />
              <div class="text-caption text-grey-7 q-mt-xs">در حال دریافت تصاویر از کتابخانه رسانه...</div>
            </div>

            <div v-else-if="libraryImages.length === 0" class="text-center q-pa-lg text-grey-6">
              <q-icon name="photo" size="44px" />
              <div class="q-mt-xs text-caption">هیچ تصویری در کتابخانه یافت نشد. می‌توانید از تب اول آپلود کنید.</div>
            </div>

            <div v-else class="library-grid-box">
              <div
                v-for="img in libraryImages"
                :key="img.id"
                class="lib-grid-item"
                :class="{ selected: selectedLibItem?.id === img.id }"
                @click="selectedLibItem = img"
              >
                <img :src="img.url" :alt="img.original_name || img.filename" loading="lazy" />
                <span class="lib-img-name">{{ img.original_name || img.filename }}</span>
                <span class="lib-img-size">{{ img.file_size_formatted }}</span>
                <q-icon
                  v-if="selectedLibItem?.id === img.id"
                  name="check_circle"
                  color="amber-9"
                  class="lib-select-check"
                  size="22px"
                />
              </div>
            </div>
          </div>

          <!-- 3. Tab: Direct URL -->
          <div v-else-if="imageTab === 'url'" class="url-pane">
            <q-input
              v-model="imageUrlInput"
              outlined
              dense
              label="آدرس اینترنتی تصویر (URL)"
              placeholder="https://example.com/photo.jpg یا /uploads/..."
            />
            <div v-if="imageUrlInput" class="q-mt-md text-center">
              <img
                :src="imageUrlInput"
                alt="پیش‌نمایش"
                style="max-height: 180px; max-width: 100%; border-radius: 10px; border: 1px solid #e4e4e7;"
              />
            </div>
          </div>

          <!-- Image Alt / Caption -->
          <div class="q-mt-md">
            <q-input
              v-model="imageAltInput"
              outlined
              dense
              label="توضیح یا متن جایگزین تصویر (Alt - اختیاری)"
              placeholder="توضیح کوتاه تصویر برای سئو و دسترس‌پذیری"
            />
          </div>
        </q-card-section>

        <q-separator />

        <q-card-actions align="between" class="q-pa-md">
          <q-btn flat label="انصراف" v-close-popup :disable="uploadingImage" />
          <q-btn
            unelevated
            color="dark"
            label="درج تصویر در متن"
            :loading="uploadingImage"
            :disable="!canInsertImage"
            @click="confirmInsertImage"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useQuasar } from 'quasar'
import { sanitizeHtml } from 'src/utils/sanitize'
import api from 'src/services/api'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'متن خود را بنویسید…' },
  minHeight: { type: Number, default: 160 },
  readonly: { type: Boolean, default: false },
  disable: { type: Boolean, default: false },
  error: { type: String, default: '' },
  hint: { type: String, default: '' },
  dir: { type: String, default: 'rtl' },
})

const emit = defineEmits(['update:modelValue'])
const $q = useQuasar()

const editableRef = ref(null)
const showSource = ref(false)
const rawHtml = ref('')
const currentFormatLabel = ref('پاراگراف')
const activeColor = ref('#0a0a0a')

// Image Modal & Upload State
const imageModalOpen = ref(false)
const imageTab = ref('upload') // 'upload' | 'library' | 'url'
const uploadingImage = ref(false)
const isDraggingFile = ref(false)
const selectedImageFile = ref(null)
const localPreviewUrl = ref('')
const imageUrlInput = ref('')
const imageAltInput = ref('')

// Library State
const libraryImages = ref([])
const loadingLibrary = ref(false)
const selectedLibItem = ref(null)

let savedRange = null

const THEME_COLORS = [
  { color: '#0a0a0a', label: 'مشکی اصلی' },
  { color: '#52525b', label: 'خاکستری متوسط' },
  { color: '#71717a', label: 'خاکستری ملایم' },
  { color: '#fed72b', label: 'زرد کهکشان هوشمند' },
  { color: '#d97706', label: 'کهربایی' },
  { color: '#2563eb', label: 'آبی فنی' },
  { color: '#16a34a', label: 'سبز موفقیت' },
  { color: '#dc2626', label: 'قرمز' },
  { color: '#9333ea', label: 'بنفش' },
]

onMounted(() => {
  if (editableRef.value) {
    editableRef.value.innerHTML = props.modelValue || ''
    rawHtml.value = props.modelValue || ''
  }
})

watch(() => props.modelValue, (newVal) => {
  if (editableRef.value && editableRef.value.innerHTML !== newVal) {
    editableRef.value.innerHTML = newVal || ''
    rawHtml.value = newVal || ''
  }
})

function saveSelection () {
  const sel = window.getSelection()
  if (sel && sel.rangeCount > 0) {
    savedRange = sel.getRangeAt(0)
  }
}

function restoreSelection () {
  if (savedRange) {
    const sel = window.getSelection()
    sel.removeAllRanges()
    sel.addRange(savedRange)
  }
}

function exec (command, value = null) {
  if (props.readonly || props.disable) return
  editableRef.value?.focus()
  document.execCommand(command, false, value)
  emitContent()
}

function formatBlock (tag) {
  exec('formatBlock', tag)
  const map = {
    p: 'پاراگراف',
    h2: 'عنوان H2',
    h3: 'عنوان H3',
    blockquote: 'نقل‌قول',
    pre: 'کد',
  }
  currentFormatLabel.value = map[tag] || tag
}

function applyTextColor (color) {
  activeColor.value = color
  exec('foreColor', color)
}

function promptLink () {
  $q.dialog({
    title: 'درج لینک استاندارد',
    message: 'آدرس اینترنتی مورد نظر را وارد نمایید:',
    prompt: {
      model: 'https://',
      type: 'text',
      outlined: true,
      dense: true,
    },
    cancel: { label: 'انصراف', flat: true },
    ok: { label: 'تایید و درج', color: 'dark' },
    persistent: true,
  }).onOk((url) => {
    const val = String(url || '').trim()
    if (!/^(https?:\/\/|mailto:|tel:|\/|#)/i.test(val)) {
      $q.notify({ type: 'warning', message: 'لینک باید با http، https یا / آغاز شود' })
      return
    }
    exec('createLink', val)
  })
}

// ------------------------------------------------------------- Image modal & upload ----
function openImageModal () {
  saveSelection()
  selectedImageFile.value = null
  localPreviewUrl.value = ''
  imageUrlInput.value = ''
  imageAltInput.value = ''
  selectedLibItem.value = null
  imageTab.value = 'upload'
  imageModalOpen.value = true
  loadLibraryImages()
}

async function loadLibraryImages () {
  loadingLibrary.value = true
  try {
    const res = await api.get('/api/media', { params: { type: 'image', limit: 28 } })
    libraryImages.value = res.data.data || []
  } catch {
    libraryImages.value = []
  } finally {
    loadingLibrary.value = false
  }
}

function onModalFileSelected (e) {
  const file = e.target.files?.[0]
  if (file) {
    processSelectedFile(file)
  }
}

function onDropModalFile (e) {
  isDraggingFile.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) {
    processSelectedFile(file)
  }
}

function processSelectedFile (file) {
  selectedImageFile.value = file
  localPreviewUrl.value = URL.createObjectURL(file)
}

const canInsertImage = computed(() => {
  if (imageTab.value === 'upload') return !!selectedImageFile.value
  if (imageTab.value === 'library') return !!selectedLibItem.value
  if (imageTab.value === 'url') return !!imageUrlInput.value.trim()
  return false
})

async function confirmInsertImage () {
  if (imageTab.value === 'upload') {
    if (!selectedImageFile.value) return
    uploadingImage.value = true
    try {
      const formData = new FormData()
      formData.append('file', selectedImageFile.value)
      formData.append('folder', 'general')
      const res = await api.post('/api/media/upload', formData)
      const url = res.data?.data?.url
      if (!url) throw new Error('آدرس تصویر دریافت نشد')
      insertImageToCanvas(url, imageAltInput.value || selectedImageFile.value.name)
      imageModalOpen.value = false
      $q.notify({ type: 'positive', message: 'تصویر با موفقیت آپلود و در متن درج شد.' })
    } catch (err) {
      $q.notify({
        type: 'negative',
        message: 'خطا در آپلود تصویر: ' + (err.response?.data?.message || err.message),
      })
    } finally {
      uploadingImage.value = false
    }
  } else if (imageTab.value === 'library') {
    if (!selectedLibItem.value) return
    insertImageToCanvas(selectedLibItem.value.url, imageAltInput.value || selectedLibItem.value.original_name)
    imageModalOpen.value = false
  } else if (imageTab.value === 'url') {
    const url = imageUrlInput.value.trim()
    if (!url) return
    insertImageToCanvas(url, imageAltInput.value)
    imageModalOpen.value = false
  }
}

function insertImageToCanvas (url, alt = '') {
  editableRef.value?.focus()
  restoreSelection()
  const cleanAlt = String(alt || 'تصویر').replace(/"/g, '&quot;')
  const imgHtml = `<img src="${url}" alt="${cleanAlt}" style="max-width: 100%; height: auto; border-radius: 12px; margin: 14px auto; display: block; box-shadow: 0 4px 18px rgba(0,0,0,0.06);" />`
  
  try {
    document.execCommand('insertHTML', false, imgHtml)
  } catch {
    if (editableRef.value) {
      editableRef.value.innerHTML += imgHtml
    }
  }
  emitContent()
}

// Direct Drag & Drop or Paste of image on canvas
async function uploadAndInsertDirectFile (file) {
  $q.notify({ type: 'info', message: 'در حال آپلود تصویر…', timeout: 1200 })
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('folder', 'general')
    const res = await api.post('/api/media/upload', formData)
    const url = res.data?.data?.url
    if (url) {
      insertImageToCanvas(url, file.name)
      $q.notify({ type: 'positive', message: 'تصویر با موفقیت در متن درج شد.' })
    }
  } catch {
    $q.notify({ type: 'negative', message: 'خطا در آپلود تصویر کشیده‌شده یا چسبانده‌شده' })
  }
}

function handleCanvasDrop (e) {
  const files = e.dataTransfer?.files
  if (files && files.length > 0 && files[0].type.startsWith('image/')) {
    saveSelection()
    uploadAndInsertDirectFile(files[0])
  }
}

function handlePaste (e) {
  const files = e.clipboardData?.files
  if (files && files.length > 0 && files[0].type.startsWith('image/')) {
    e.preventDefault()
    saveSelection()
    uploadAndInsertDirectFile(files[0])
    return
  }

  e.preventDefault()
  const text = e.clipboardData?.getData('text/plain') || ''
  const html = e.clipboardData?.getData('text/html')

  if (html) {
    const clean = sanitizeHtml(html)
    document.execCommand('insertHTML', false, clean)
  } else {
    const cleanText = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\n/g, '<br>')
    document.execCommand('insertHTML', false, cleanText)
  }
  emitContent()
}

function handleInput () {
  emitContent()
}

function handleSourceInput () {
  if (editableRef.value) {
    editableRef.value.innerHTML = rawHtml.value
  }
  emit('update:modelValue', rawHtml.value)
}

function emitContent () {
  if (!editableRef.value) return
  const html = editableRef.value.innerHTML
  const cleaned = sanitizeHtml(html)
  rawHtml.value = cleaned
  emit('update:modelValue', cleaned)
}

function formatSize (bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const wordCount = computed(() => {
  const text = (editableRef.value?.innerText || '').trim()
  if (!text) return 0
  return text.split(/\s+/).length
})

const charCount = computed(() => {
  return (editableRef.value?.innerText || '').length
})
</script>

<style scoped>
.master-rich-editor {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 18px;
  background: #ffffff;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
  transition: border-color 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}

.master-rich-editor:focus-within {
  border-color: #0a0a0a;
  box-shadow: 0 0 0 3px rgba(254, 215, 43, 0.35);
}

.master-rich-editor.has-error {
  border-color: #ef4444;
}

/* Toolbar */
.editor-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  padding: 6px 10px;
  background: #fbfbfb;
  border-bottom: 1px solid rgba(0, 0, 0, 0.07);
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 2px;
}

.toolbar-group--end {
  margin-right: auto;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: rgba(0, 0, 0, 0.08);
  margin: 0 4px;
}

.tool-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: transparent;
  border: none;
  color: #52525b;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tool-btn:hover {
  background: rgba(0, 0, 0, 0.06);
  color: #0a0a0a;
}

.tool-btn.active {
  background: #0a0a0a;
  color: #ffffff;
}

.heading-dropdown-btn {
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  color: #0a0a0a;
  background: rgba(0, 0, 0, 0.04);
  padding: 2px 8px;
}

.color-dropdown-btn {
  border-radius: 8px;
  padding: 2px 6px;
}

.color-tool-preview {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.2);
  margin-left: 4px;
}

.color-palette-popover {
  padding: 12px;
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  min-width: 180px;
}

.palette-title {
  font-size: 11.5px;
  font-weight: 700;
  color: #71717a;
  margin-bottom: 8px;
}

.colors-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
}

.color-chip-btn {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  cursor: pointer;
  transition: transform 0.15s ease;
}

.color-chip-btn:hover {
  transform: scale(1.15);
}

/* Canvas Area */
.editor-canvas {
  padding: 16px 20px;
  outline: none;
  font-family: 'Estedad', sans-serif;
  font-size: 14px;
  line-height: 1.85;
  color: var(--text-dark, #0a0a0a);
  direction: rtl;
  text-align: right;
  overflow-y: auto;
}

.dir-ltr .editor-canvas {
  direction: ltr;
  text-align: left;
}

.editor-canvas:empty:before {
  content: attr(placeholder);
  color: #a1a1aa;
  pointer-events: none;
  display: block;
}

/* Source View */
.editor-source-view {
  display: flex;
  flex-direction: column;
}

.source-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: #18181b;
  color: #a1a1aa;
  font-size: 11px;
  font-weight: 600;
}

.source-textarea {
  width: 100%;
  padding: 12px 16px;
  background: #09090b;
  color: #38bdf8;
  font-family: 'Fira Code', monospace;
  font-size: 12.5px;
  line-height: 1.6;
  border: none;
  outline: none;
  resize: vertical;
  direction: ltr;
  text-align: left;
}

/* Meta Footer */
.editor-meta-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 14px;
  background: #fbfbfb;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  font-size: 11px;
  color: #71717a;
}

.editor-error {
  color: #ef4444;
  font-weight: 700;
}

.editor-stats {
  font-family: 'Outfit', sans-serif;
  font-size: 11px;
  color: #a1a1aa;
  margin-right: auto;
}

.highlight-tool {
  background: rgba(254, 215, 43, 0.2) !important;
  color: #b45309 !important;
  font-weight: 700;
}

/* Image Upload & Selection Modal */
.editor-image-modal {
  min-width: 580px;
  max-width: 92vw;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.22);
}

.modal-head-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px 10px;
}

.modal-title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.image-dropzone-box {
  border: 2px dashed rgba(0, 0, 0, 0.16);
  border-radius: 16px;
  padding: 32px 20px;
  text-align: center;
  cursor: pointer;
  background: #fafafa;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.image-dropzone-box:hover,
.image-dropzone-box.is-drag-over {
  border-color: #ffd54a;
  background: rgba(255, 213, 74, 0.08);
  transform: translateY(-1px);
}

.dropzone-empty-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.dropzone-main-text {
  font-weight: 800;
  font-size: 0.95rem;
  color: #0a0a0a;
}

.dropzone-sub-text {
  font-size: 0.78rem;
  color: #71717a;
}

.local-preview-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.local-preview-img {
  max-height: 200px;
  max-width: 100%;
  border-radius: 12px;
  object-fit: contain;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.local-preview-name {
  font-size: 0.84rem;
  font-weight: 700;
  color: #0a0a0a;
}

.local-preview-change-hint {
  font-size: 0.74rem;
  color: #71717a;
  background: rgba(0, 0, 0, 0.05);
  padding: 3px 10px;
  border-radius: 6px;
}

.library-grid-box {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(115px, 1fr));
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
  padding: 6px;
}

.lib-grid-item {
  position: relative;
  border: 2px solid transparent;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  aspect-ratio: 1;
  background: #111116;
  transition: all 0.18s ease;
}

.lib-grid-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.15);
}

.lib-grid-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.lib-grid-item.selected {
  border-color: #ffd54a;
  box-shadow: 0 0 0 3px rgba(255, 213, 74, 0.45);
}

.lib-img-name {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(0deg, rgba(0, 0, 0, 0.85), transparent);
  color: #ffffff;
  font-size: 10px;
  font-weight: 600;
  padding: 8px 6px 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  direction: ltr;
  text-align: left;
}

.lib-img-size {
  position: absolute;
  top: 6px;
  left: 6px;
  background: rgba(0, 0, 0, 0.65);
  color: #ffd54a;
  font-size: 9px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
  direction: ltr;
}

.lib-select-check {
  position: absolute;
  top: 6px;
  right: 6px;
  background: #ffffff;
  border-radius: 50%;
}
</style>


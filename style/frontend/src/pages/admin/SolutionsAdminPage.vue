<template>
  <div class="admin-solutions">
    <!-- 1. TABLE LIST VIEW -->
    <div v-if="viewMode === 'list'" class="admin-view-list-container">
      <div class="page-header">
        <h3>مدیریت راهکارها و مقالات</h3>
        <q-btn color="primary" unelevated label="مقاله جدید" icon="add" @click="openDialog()" />
      </div>

      <div class="table-card">
        <q-table
          :rows="articles"
          :columns="columns"
          row-key="id"
          :loading="loading"
          flat
          :pagination="pagination"
          no-data-label="هیچ مقاله‌ای یافت نشد"
          :rows-per-page-label="'ردیف در هر صفحه'"
          :pagination-label="paginationLabel"
          :grid="isMobile"
          :filter="filter"
        >
          <template #top-right>
            <q-input v-model="filter" dense outlined placeholder="جستجو در مقالات..." class="mobile-search" :style="{ width: isMobile ? '160px' : '240px' }">
              <template #append><q-icon name="search" /></template>
            </q-input>
          </template>

          <template #body-cell-image="props">
            <q-td :props="props">
              <div class="thumb-wrap">
                <img v-if="props.row.image_url" :src="formatMediaUrl(props.row.image_url)" class="table-thumb" loading="lazy" decoding="async" @error="e => handleImageError(e)" />
                <div v-else class="no-image"><q-icon name="menu_book" /></div>

                <div class="thumb-actions">
                  <q-btn flat round dense icon="image" size="sm" color="primary" @click="openDialog(props.row, true)">
                    <q-tooltip>ویرایش تصویر</q-tooltip>
                  </q-btn>
                  <q-btn flat round dense icon="delete" size="sm" color="negative" @click="confirmDelete(props.row)">
                    <q-tooltip>حذف مقاله</q-tooltip>
                  </q-btn>
                </div>
              </div>
            </q-td>
          </template>

          <template #body-cell-product="props">
            <q-td :props="props">
              <span v-if="props.row.product_title" class="ref-chip">{{ props.row.product_title }}</span>
              <span v-else class="muted">—</span>
            </q-td>
          </template>

          <template #body-cell-author="props">
            <q-td :props="props">
              <span v-if="props.row.author_name" class="ref-chip">{{ props.row.author_name }}</span>
              <span v-else class="muted">—</span>
            </q-td>
          </template>

          <template #body-cell-status="props">
            <q-td :props="props">
              <span class="status-chip" :class="{ active: props.row.is_active }">
                {{ props.row.is_active ? 'فعال' : 'غیرفعال' }}
              </span>
            </q-td>
          </template>

          <template #body-cell-created_at="props">
            <q-td :props="props">
              {{ formatDate(props.row.created_at) }}
            </q-td>
          </template>

          <template #body-cell-actions="props">
            <q-td :props="props">
              <q-btn flat round dense icon="visibility" size="sm" color="info" @click="openViewDialog(props.row)">
                <q-tooltip>پیش‌نمایش مقاله</q-tooltip>
              </q-btn>
              <q-btn flat round dense icon="edit" size="sm" color="primary" @click="openDialog(props.row)">
                <q-tooltip>صفحه ویرایش</q-tooltip>
              </q-btn>
              <q-btn flat round dense icon="delete" size="sm" color="negative" @click="confirmDelete(props.row)">
                <q-tooltip>حذف</q-tooltip>
              </q-btn>
            </q-td>
          </template>

          <template #item="props">
            <div class="mobile-card">
              <div class="mobile-card-header">
                <div class="thumb-wrap">
                  <img v-if="props.row.image_url" :src="formatMediaUrl(props.row.image_url)" class="mobile-card-thumb" loading="lazy" decoding="async" @error="e => handleImageError(e)" />
                  <div v-else class="mobile-card-thumb-placeholder"><q-icon name="menu_book" /></div>

                  <div class="thumb-actions">
                    <q-btn flat round dense icon="image" size="sm" color="primary" @click="openDialog(props.row, true)">
                      <q-tooltip>ویرایش تصویر</q-tooltip>
                    </q-btn>
                    <q-btn flat round dense icon="delete" size="sm" color="negative" @click="confirmDelete(props.row)">
                      <q-tooltip>حذف مقاله</q-tooltip>
                    </q-btn>
                  </div>
                </div>
                <div class="mobile-card-title">
                  <strong>{{ props.row.title }}</strong>
                  <span class="mobile-card-role">
                    {{ props.row.author_name || 'بدون نویسنده' }}
                  </span>
                </div>
                <span class="status-chip" :class="{ active: props.row.is_active }">
                  {{ props.row.is_active ? 'فعال' : 'غیرفعال' }}
                </span>
              </div>
              <div class="mobile-card-footer">
                <span class="mobile-card-date">{{ formatDate(props.row.created_at) }}</span>
                <div class="mobile-card-actions">
                  <q-btn flat round dense icon="visibility" size="sm" color="info" @click="openViewDialog(props.row)" />
                  <q-btn flat round dense icon="edit" size="sm" color="primary" @click="openDialog(props.row)" />
                  <q-btn flat round dense icon="delete" size="sm" color="negative" @click="confirmDelete(props.row)" />
                </div>
              </div>
            </div>
          </template>
        </q-table>
      </div>
    </div>

    <!-- 2. DEDICATED FULL-PAGE EDIT VIEW -->
    <div v-else-if="viewMode === 'edit'" class="admin-edit-page">
      <!-- Top Navigation Bar -->
      <div class="edit-page-top-nav">
        <div class="edit-nav-right">
          <button type="button" class="btn-back-to-list" @click="closeEditView">
            <span class="back-icon">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </span>
            <span>بازگشت به لیست مقالات</span>
          </button>
          <div class="edit-nav-breadcrumbs">
            <span>مدیریت راهکارها</span>
            <span class="crumb-sep">/</span>
            <span class="crumb-active">{{ editing ? 'ویرایش مقاله' : 'مقاله جدید' }}</span>
          </div>
        </div>

        <div class="edit-page-heading-wrap">
          <h2>{{ editing ? (form.title || 'ویرایش مقاله') : 'ایجاد مقاله جدید' }}</h2>
          <span class="edit-badge-pill">
            <span class="pill-dot"></span>
            <span>{{ form.is_active ? 'آماده انتشار' : 'پیش‌نویس' }}</span>
          </span>
        </div>

        <div class="edit-nav-actions">
          <q-btn flat label="انصراف" @click="closeEditView" />
          <q-btn color="primary" unelevated label="ذخیره مقاله" icon="save" :loading="saving" @click="saveArticle" />
        </div>
      </div>

      <!-- Bento Edit Form -->
      <q-form ref="formRef" @submit.prevent="saveArticle" class="edit-form-wrapper">
        <div class="edit-page-bento-grid">
          <!-- Main Content Column -->
          <div class="edit-column-main">
            <!-- Card 1: Core Details -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="edit_note" size="20px" />
                </div>
                <div>
                  <h4>اطلاعات اصلی مقاله</h4>
                  <p>عنوان، آدرس صفحه (اسلاگ) و خلاصه اجرایی جهت نمایش در لیست‌ها</p>
                </div>
              </div>
              <div class="bento-card-body">
                <div class="form-row">
                  <q-input v-model="form.title" outlined label="عنوان مقاله*" :rules="[val => !!val || 'عنوان الزامی است']" />
                  <q-input v-model="form.slug" outlined label="نامک (slug)" placeholder="my-article-slug" hint="در صورت خالی بودن بر اساس عنوان ساخته می‌شود" input-class="url-input" />
                </div>
                <q-input v-model="form.summary" outlined label="خلاصه مقاله" type="textarea" rows="2" placeholder="توضیح مختصری که در کارت‌های صفحه اصلی و لیست مقالات نمایش داده می‌شود" />
              </div>
            </div>

            <!-- Card 2: Full Rich Text Editor -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble accent">
                  <q-icon name="menu_book" size="20px" />
                </div>
                <div>
                  <h4>متن کامل و محتوای تفصیلی</h4>
                  <p>نگارش مقاله با ابزارهای کامل قالب‌بندی، تیترها، فهرست‌ها و نقل‌قول‌ها</p>
                </div>
              </div>
              <div class="bento-card-body">
                <RichTextEditor
                  v-model="form.content"
                  :min-height="420"
                  placeholder="متن کامل مقاله و تحلیل تخصصی را در اینجا بنویسید…"
                  hint="پشتیبانی کامل از سرفصل‌ها، کد، نقل‌قول و قالب‌بندی متن"
                />
              </div>
            </div>

            <!-- Card 3: Source References -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble info">
                  <q-icon name="link" size="20px" />
                </div>
                <div>
                  <h4>منابع و مراجع تخصصی</h4>
                  <p>در صورت اقتباس از مستندات یا استانداردهای معتبر، لینک و عنوان منبع را درج کنید</p>
                </div>
              </div>
              <div class="bento-card-body">
                <div class="form-row">
                  <q-input v-model="form.source_title" outlined label="عنوان مرجع یا منبع" placeholder="مثال: مستندات رسمی PostgreSQL یا RFC 8446" />
                  <q-input v-model="form.source_url" outlined label="آدرس وب‌سایت منبع" placeholder="https://example.com/source" input-class="url-input" />
                </div>
              </div>
            </div>
          </div>

          <!-- Side Settings Column -->
          <div class="edit-column-side">
            <!-- Side Card 1: Featured Image -->
            <div class="edit-bento-card" ref="imageUploadRef">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="image" size="20px" />
                </div>
                <div>
                  <h4>تصویر شاخص مقاله</h4>
                  <p>نسبت تصویر ایده‌آل ۱۶:۹</p>
                </div>
              </div>
              <div class="bento-card-body">
                <div class="upload-area" @click="pickFile">
                  <img v-if="imagePreview" :src="imagePreview" class="upload-preview" />
                  <div v-else class="upload-placeholder">
                    <q-icon name="cloud_upload" size="36px" />
                    <span>کلیک برای انتخاب تصویر</span>
                    <span class="upload-hint">JPG, PNG, WebP — حداکثر ۱۰ مگابایت</span>
                  </div>
                </div>
                <input ref="fileInput" type="file" accept="image/*" style="display: none" @change="onFileSelect" />

                <div v-if="imagePreview" class="profile-image-actions">
                  <q-btn flat dense icon="swap_horiz" color="primary" label="تعویض تصویر" @click="pickFile" />
                  <q-btn flat dense icon="delete" color="negative" label="حذف تصویر" @click="deleteImage" />
                </div>
              </div>
            </div>

            <!-- Side Card 2: Status & Visibility -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble success">
                  <q-icon name="toggle_on" size="20px" />
                </div>
                <div>
                  <h4>وضعیت انتشار</h4>
                  <p>کنترل نمایش عمومی در وب‌سایت</p>
                </div>
              </div>
              <div class="bento-card-body">
                <q-toggle v-model="form.is_active" label="فعال (نمایش برای کاربران سایت)" />
                <span class="form-hint">مقالات فعال بر اساس زمان ثبت در صفحه راهکارها و صفحه اصلی فهرست می‌شوند.</span>
              </div>
            </div>

            <!-- Side Card 3: Categorization & Relations -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="category" size="20px" />
                </div>
                <div>
                  <h4>دسته‌بندی و روابط</h4>
                  <p>تخصیص نویسنده و اتصال به سامانه ابری</p>
                </div>
              </div>
              <div class="bento-card-body">
                <q-select
                  v-model="form.category"
                  :options="['رایانش ابری', 'معماری میکروسرویس', 'هوش مصنوعی', 'امنیت ابری', 'دیزاین سیستم', 'معماری نرم‌افزار', 'شبکه و زیرساخت']"
                  outlined
                  label="دسته‌بندی موضوعی"
                  use-input
                  new-value-mode="add-unique"
                />
                <q-input v-model="form.topic" outlined label="موضوع تخصصی" placeholder="الگوهای توزیع‌شده" />
                <q-select
                  v-model="form.related_product_id"
                  :options="productOptions"
                  outlined
                  emit-value
                  map-options
                  clearable
                  label="محصول مرتبط (سامانه‌های سازمانی)"
                />
                <q-select
                  v-model="form.author_id"
                  :options="authorOptions"
                  outlined
                  emit-value
                  map-options
                  clearable
                  label="نویسنده (عضو تیم)"
                />
              </div>
            </div>

            <!-- Side Card 4: Metadata -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="label" size="20px" />
                </div>
                <div>
                  <h4>برچسب‌ها و زمان مطالعه</h4>
                </div>
              </div>
              <div class="bento-card-body">
                <q-input v-model="form.read_time" outlined label="مدت زمان مطالعه" placeholder="۵ دقیقه مطالعه" />
                <q-input v-model="form.tags_text" outlined label="برچسب‌ها (با کاما)" placeholder="Kafka, Anycast, Docker" />
              </div>
            </div>
          </div>
        </div>

        <!-- Sticky Bottom Action Bar -->
        <div class="edit-page-sticky-bar">
          <div class="sticky-bar-info">
            <span class="dot"></span>
            <span>در حال ویرایش مقاله: <strong>{{ form.title || 'پیش‌نویس جدید' }}</strong></span>
          </div>
          <div class="sticky-bar-buttons">
            <button type="button" class="btn-admin-cancel" @click="closeEditView">انصراف و بازگشت</button>
            <button type="submit" class="btn-admin-save" :disabled="saving">
              <span class="save-bubble">
                <q-spinner-dots v-if="saving" size="14px" />
                <q-icon v-else name="check" size="14px" />
              </span>
              <span>{{ saving ? 'در حال ذخیره‌سازی...' : 'ذخیره و ثبت نهایی' }}</span>
            </button>
          </div>
        </div>
      </q-form>
    </div>

    <!-- 3. DEDICATED PREVIEW VIEW -->
    <div v-else-if="viewMode === 'view' && viewingArticle" class="admin-edit-page">
      <div class="edit-page-top-nav">
        <div class="edit-nav-right">
          <button type="button" class="btn-back-to-list" @click="viewMode = 'list'">
            <span class="back-icon">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </span>
            <span>بازگشت به لیست</span>
          </button>
          <div class="edit-nav-breadcrumbs">
            <span>مدیریت راهکارها</span>
            <span class="crumb-sep">/</span>
            <span class="crumb-active">پیش‌نمایش مقاله</span>
          </div>
        </div>
        <div class="edit-nav-actions">
          <q-btn color="primary" unelevated icon="edit" label="ویرایش این مقاله" @click="openDialog(viewingArticle)" />
          <q-btn color="negative" flat icon="delete" label="حذف" @click="deleteFromView" />
        </div>
      </div>

      <div class="edit-bento-card preview-article-full">
        <img v-if="viewingArticle.image_url" :src="formatMediaUrl(viewingArticle.image_url)" class="view-cover" loading="lazy" decoding="async" @error="e => handleImageError(e)" />
        <div class="view-meta-row">
          <span class="status-chip" :class="{ active: viewingArticle.is_active }">
            {{ viewingArticle.is_active ? 'منتشر شده' : 'غیرفعال' }}
          </span>
          <span>{{ formatDate(viewingArticle.created_at) }}</span>
          <span v-if="viewingArticle.author_name">نویسنده: {{ viewingArticle.author_name }}</span>
          <span v-if="viewingArticle.category">دسته: {{ viewingArticle.category }}</span>
        </div>
        <h3 class="view-title">{{ viewingArticle.title }}</h3>
        <p v-if="viewingArticle.summary" class="view-summary">{{ viewingArticle.summary }}</p>
        <div v-if="viewingArticle.content" class="view-content" v-html="viewingArticle.content"></div>
        <div v-if="viewingArticle.product_title" class="view-ref">
          محصول مرتبط: <strong>{{ viewingArticle.product_title }}</strong>
        </div>
        <div v-if="viewingArticle.source_url || viewingArticle.source_title" class="view-ref">
          منبع:
          <a v-if="viewingArticle.source_url" :href="viewingArticle.source_url" target="_blank" class="view-source">
            {{ viewingArticle.source_title || viewingArticle.source_url }}
          </a>
          <strong v-else>{{ viewingArticle.source_title }}</strong>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useQuasar } from 'quasar'
import moment from 'moment-jalaali'
import api from 'src/services/api'
import RichTextEditor from 'src/components/common/RichTextEditor.vue'
import { formatMediaUrl, handleImageError } from 'src/utils/media'

const $q = useQuasar()

const viewMode = ref('list') // 'list' | 'edit' | 'view'
const articles = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogOpen = ref(false)
const editing = ref(null)
const imagePreview = ref(null)
const imageUploadRef = ref(null)
const filter = ref('')
let imageFile = null

const MAX_IMAGE_SIZE = 10 * 1024 * 1024 // 10MB

const products = ref([])
const teamMembers = ref([])

const viewDialogOpen = ref(false)
const viewingArticle = ref(null)

const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value <= 800)
function onResize () { windowWidth.value = window.innerWidth }

const pagination = ref({ rowsPerPage: 10, page: 1 })
function paginationLabel (first, last, total) {
  return `${first}–${last} از ${total}`
}

function formatDate (date) {
  if (!date) return ''
  return moment(date).format('jYYYY/jMM/jDD - HH:mm')
}

const columns = [
  { name: 'image', label: 'تصویر', align: 'center' },
  { name: 'title', label: 'عنوان', field: 'title', align: 'right', sortable: true },
  { name: 'author', label: 'نویسنده', field: 'author_name', align: 'right', sortable: true },
  { name: 'product', label: 'محصول مرتبط', field: 'product_title', align: 'right' },
  { name: 'status', label: 'وضعیت', align: 'center' },
  { name: 'created_at', label: 'تاریخ ایجاد', field: 'created_at', align: 'right', sortable: true },
  { name: 'actions', label: 'عملیات', align: 'center' },
]

const productOptions = computed(() =>
  products.value.map((p) => ({ label: p.title, value: p.id }))
)

const authorOptions = computed(() =>
  teamMembers.value.map((m) => ({ label: `${m.full_name} — ${m.role}`, value: m.id }))
)

const defaultForm = {
  title: '',
  slug: '',
  summary: '',
  content: '',
  category: 'رایانش ابری',
  read_time: '۵ دقیقه مطالعه',
  topic: 'معماری سیستم',
  tags_text: '',
  source_title: '',
  source_url: '',
  related_product_id: null,
  author_id: null,
  is_active: true,
}
const form = ref({ ...defaultForm })
const formRef = ref(null)

function openDialog (row = null, focusImage = false) {
  editing.value = row
  if (row) {
    let parsedTags = ''
    if (typeof row.tags === 'string') {
      try {
        const arr = JSON.parse(row.tags)
        parsedTags = Array.isArray(arr) ? arr.join(', ') : row.tags
      } catch {
        parsedTags = row.tags
      }
    } else if (Array.isArray(row.tags)) {
      parsedTags = row.tags.join(', ')
    }

    form.value = {
      title: row.title,
      slug: row.slug || '',
      summary: row.summary || '',
      content: row.content || '',
      category: row.category || 'رایانش ابری',
      read_time: row.read_time || '۵ دقیقه مطالعه',
      topic: row.topic || 'معماری سیستم',
      tags_text: parsedTags,
      source_title: row.source_title || '',
      source_url: row.source_url || '',
      related_product_id: row.related_product_id || row.product_id || null,
      author_id: row.author_id || null,
      is_active: row.is_active !== undefined ? Boolean(row.is_active) : true,
    }
    imagePreview.value = row.image_url ? formatMediaUrl(row.image_url) : null
  } else {
    form.value = { ...defaultForm }
    imagePreview.value = null
  }
  imageFile = null
  viewMode.value = 'edit'
  dialogOpen.value = false

  if (focusImage) {
    nextTick(() => {
      imageUploadRef.value?.scrollIntoView?.({ behavior: 'smooth', block: 'center' })
    })
  }
}

function closeEditView () {
  viewMode.value = 'list'
  editing.value = null
  form.value = { ...defaultForm }
  imageFile = null
  imagePreview.value = null
}

function pickFile () {
  imageUploadRef.value?.querySelector?.('input[type="file"]')?.click()
}

function onFileSelect (e) {
  const file = e.target.files[0]
  e.target.value = ''
  if (!file) return

  if (file.size > MAX_IMAGE_SIZE) {
    $q.notify({ type: 'negative', message: 'حجم تصویر نباید بیشتر از ۱۰ مگابایت باشد' })
    return
  }

  imageFile = file
  imagePreview.value = URL.createObjectURL(file)
}

function confirmRemoveImage (row) {
  if (!row) return
  $q.dialog({
    title: 'حذف تصویر اصلی',
    message: 'آیا از حذف تصویر اصلی مقاله اطمینان دارید؟',
    cancel: 'انصراف',
    ok: { label: 'حذف', color: 'negative' },
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/api/solutions/admin/${row.id}/image`)
      row.image_url = null
      if (!imageFile) imagePreview.value = null
      $q.notify({ type: 'positive', message: 'تصویر اصلی حذف شد' })
      loadArticles()
    } catch (e) {
      $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در حذف تصویر' })
    }
  })
}

function deleteImage () {
  confirmRemoveImage(editing.value)
}

function openViewDialog (row) {
  viewingArticle.value = row
  viewMode.value = 'view'
}

function editFromView (focusImage = false) {
  const row = viewingArticle.value
  openDialog(row, focusImage)
}

function deleteImageFromView () {
  confirmRemoveImage(viewingArticle.value)
}

function deleteFromView () {
  const row = viewingArticle.value
  viewMode.value = 'list'
  confirmDelete(row)
}

async function saveArticle () {
  const valid = await formRef.value.validate()
  if (!valid) return

  saving.value = true
  try {
    const fd = new FormData()
    fd.append('title', form.value.title)
    fd.append('slug', form.value.slug || '')
    fd.append('summary', form.value.summary || '')
    fd.append('content', form.value.content || '')
    fd.append('category', form.value.category || '')
    fd.append('read_time', form.value.read_time || '')
    fd.append('topic', form.value.topic || '')
    fd.append('tags', form.value.tags_text || '')
    fd.append('source_title', form.value.source_title || '')
    fd.append('source_url', form.value.source_url || '')
    fd.append('related_product_id', form.value.related_product_id || '')
    fd.append('author_id', form.value.author_id || '')
    fd.append('is_active', form.value.is_active)
    if (imageFile) fd.append('image', imageFile)

    if (editing.value) {
      await api.put(`/api/solutions/admin/${editing.value.id}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      $q.notify({ type: 'positive', message: 'مقاله با موفقیت بروزرسانی شد' })
    } else {
      await api.post('/api/solutions/admin', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      $q.notify({ type: 'positive', message: 'مقاله جدید با موفقیت ایجاد شد' })
    }
    viewMode.value = 'list'
    dialogOpen.value = false
    loadArticles()
  } catch (e) {
    $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در ذخیره' })
  } finally {
    saving.value = false
  }
}

function confirmDelete (row) {
  $q.dialog({
    title: 'حذف مقاله',
    message: `آیا از حذف "${row.title}" اطمینان دارید؟`,
    cancel: 'انصراف',
    ok: { label: 'حذف', color: 'negative' },
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/api/solutions/admin/${row.id}`)
      $q.notify({ type: 'positive', message: 'مقاله حذف شد' })
      loadArticles()
    } catch (e) {
      $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در حذف' })
    }
  })
}

async function loadArticles () {
  loading.value = true
  try {
    const res = await api.get('/api/solutions/admin/all')
    articles.value = res.data.data || []
  } catch (e) { console.error(e) } finally { loading.value = false }
}

async function loadReferences () {
  try {
    const [productsRes, teamRes] = await Promise.all([
      api.get('/api/products/admin/all').catch(() => api.get('/api/products', { params: { limit: 100 } })),
      api.get('/api/team-members/admin/all').catch(() => api.get('/api/team-members')),
    ])
    products.value = productsRes.data.data || []
    teamMembers.value = teamRes.data.data || []
  } catch (e) {
    console.error('Failed to load references:', e)
  }
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  loadArticles()
  loadReferences()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.page-header h3 { font-size: 20px; font-weight: 800; color: #0a0a0b; margin: 0; }
.table-card { background: white; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.table-thumb { width: 56px; height: 42px; object-fit: cover; border-radius: 8px; border: 1px solid #e2e8f0; }
.no-image { width: 56px; height: 42px; background: #f4f4f5; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #71717a; border: 1px solid #e2e8f0; }
.status-chip { font-size: 11px; padding: 4px 12px; border-radius: 9999px; font-weight: 700; background: #fee2e2; color: #ef4444; }
.status-chip.active { background: #ecfdf5; color: #059669; }
.ref-chip { font-size: 12px; font-weight: 600; color: #0a0a0b; background: #f4f4f5; padding: 4px 10px; border-radius: 8px; display: inline-block; }
.muted { color: #a1a1aa; }

.thumb-wrap { position: relative; display: inline-block; line-height: 0; border-radius: 8px; }
.thumb-actions { display: flex; align-items: center; justify-content: center; gap: 4px; margin-top: 6px; }
.thumb-actions .q-btn { background: #fff; box-shadow: 0 1px 4px rgba(10,10,11,0.18); }
@media (hover: hover) and (min-width: 801px) {
  .thumb-actions {
    position: absolute;
    inset: 0;
    margin-top: 0;
    border-radius: 8px;
    background: rgba(10, 10, 11, 0.65);
    opacity: 0;
    transition: opacity 0.15s;
    line-height: normal;
  }
  .thumb-wrap:hover .thumb-actions,
  .thumb-wrap:focus-within .thumb-actions { opacity: 1; }
}

.delete-profile-btn { margin-top: 8px; }
.view-image-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.image-upload label { display: block; font-size: 13px; font-weight: 700; color: #0a0a0b; margin-bottom: 8px; }
.rich-field { margin-bottom: 8px; }
.rich-field > label { display: block; font-size: 13px; font-weight: 700; color: #0a0a0b; margin-bottom: 8px; }
.profile-image-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.upload-area { border: 2px dashed #cbd5e1; border-radius: 14px; padding: 24px; text-align: center; cursor: pointer; transition: all 0.2s; min-height: 140px; display: flex; align-items: center; justify-content: center; background: #fbfbfe; }
.upload-area:hover { border-color: #fed72b; background: #fefce8; }
.upload-preview { max-width: 100%; max-height: 160px; object-fit: contain; border-radius: 8px; }
.upload-placeholder { display: flex; flex-direction: column; align-items: center; gap: 8px; color: #71717a; }
.upload-hint { font-size: 11px; color: #a1a1aa; }
.form-hint { display: flex; align-items: center; font-size: 12px; color: #71717a; line-height: 1.8; }

.view-card { width: 620px; max-width: 95vw; border-radius: 16px; }
.view-cover { width: 100%; max-height: 240px; object-fit: cover; border-radius: 12px; margin-bottom: 14px; }
.view-meta-row { display: flex; flex-wrap: wrap; align-items: center; gap: 14px; font-size: 12px; color: #71717a; margin-bottom: 12px; }
.view-title { margin: 0 0 10px; font-size: 20px; font-weight: 800; color: #0a0a0b; }
.view-summary { margin: 0 0 12px; font-size: 13.5px; color: #52525b; line-height: 1.9; }
.view-content { padding: 16px; background: #fafafa; border: 1px solid #e2e8f0; border-radius: 12px; font-size: 13px; line-height: 2; color: #27272a; white-space: pre-wrap; margin-bottom: 14px; max-height: 260px; overflow: auto; }
.view-ref { font-size: 13px; color: #52525b; margin-bottom: 8px; }
.view-source { color: #d97706; font-weight: 700; text-decoration: none; }
.view-meta { display: flex; flex-wrap: wrap; gap: 20px; font-size: 12px; color: #71717a; padding-top: 12px; border-top: 1px solid #f1f5f9; }

@media (max-width: 900px) {
  .page-header { flex-direction: column; align-items: stretch; gap: 14px; }
  .page-header .q-btn { width: 100%; justify-content: center; min-height: 42px; }
}

@media (max-width: 600px) {
  .form-row { grid-template-columns: 1fr; }
  .table-card { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .table-thumb { width: 42px; height: 32px; }
  .no-image { width: 42px; height: 32px; }
}

@media (max-width: 480px) {
  .table-card .mobile-search { width: 100% !important; margin: 0 !important; }
}

@media (max-width: 320px) {
  .mobile-card { padding: 10px 8px; border-radius: 12px; }
  .mobile-card-header { gap: 8px; margin-bottom: 8px; }
  .mobile-card-thumb, .mobile-card-thumb-placeholder { width: 40px; height: 34px; border-radius: 6px; }
  .mobile-card-title strong { font-size: 12px; }
  .upload-area { padding: 14px 10px; min-height: 90px; }
  .view-card {
    width: 100vw !important;
    max-width: 100vw !important;
    min-width: 0 !important;
    height: 100vh !important;
    max-height: 100vh !important;
    border-radius: 0 !important;
    margin: 0 !important;
  }
}

.mobile-card { background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 14px; margin-bottom: 10px; width: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
.mobile-card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.mobile-card-thumb { width: 52px; height: 40px; border-radius: 8px; object-fit: cover; flex-shrink: 0; }
.mobile-card-thumb-placeholder { width: 52px; height: 40px; border-radius: 8px; background: #f4f4f5; display: flex; align-items: center; justify-content: center; color: #71717a; flex-shrink: 0; }
.mobile-card-title { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.mobile-card-title strong { font-size: 13px; color: #0a0a0b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mobile-card-role { font-size: 11px; color: #71717a; }
.mobile-card-footer { display: flex; align-items: center; justify-content: space-between; padding-top: 8px; border-top: 1px solid #f1f5f9; }
.mobile-card-date { font-size: 11px; color: #71717a; }
.mobile-card-actions { display: flex; gap: 2px; }
.mobile-search { margin-left: 8px; }
</style>

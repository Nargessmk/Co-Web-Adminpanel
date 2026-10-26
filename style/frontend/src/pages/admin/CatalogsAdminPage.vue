<template>
  <div class="admin-catalogs">
    <!-- List Mode -->
    <div v-if="viewMode === 'list'">
      <div class="page-header">
        <div class="page-header-titles">
          <h3>مدیریت کاتالوگ‌ها</h3>
          <span class="page-subtitle">مشاهده، آپلود و ویرایش اسناد، کاتالوگ‌ها و مشخصات فنی محصولات</span>
        </div>
        <q-btn color="primary" unelevated label="کاتالوگ جدید" icon="add" class="btn-create" @click="openDialog()" />
      </div>

      <div class="table-card">
        <q-table
          :rows="catalogs"
          :columns="columns"
          row-key="id"
          :loading="loading"
          flat
          :pagination="pagination"
          no-data-label="هیچ کاتالوگی یافت نشد"
          :rows-per-page-label="'ردیف در هر صفحه'"
          :pagination-label="paginationLabel"
          :grid="isMobile"
          :filter="filter"
        >
          <template #top-right>
            <q-input v-model="filter" dense outlined placeholder="جستجو..." class="mobile-search" :style="{ width: isMobile ? '160px' : '220px' }">
              <template #append><q-icon name="search" /></template>
            </q-input>
          </template>

          <template #body-cell-file="props">
            <q-td :props="props">
              <a :href="formatMediaUrl(props.row.file_url)" target="_blank" class="file-link">
                <q-icon :name="getFileIcon(props.row.file_url)" size="20px" />
                <span>{{ getFileExtension(props.row.file_url) }}</span>
              </a>
            </q-td>
          </template>

          <template #body-cell-product="props">
            <q-td :props="props">
              <router-link :to="`/products/${props.row.product_slug}`" class="product-link" target="_blank">
                {{ props.row.product_title }}
              </router-link>
            </q-td>
          </template>

          <template #body-cell-created_at="props">
            <q-td :props="props">
              {{ formatDate(props.row.created_at) }}
            </q-td>
          </template>

          <template #body-cell-actions="props">
            <q-td :props="props">
              <q-btn flat round dense icon="edit" size="sm" color="primary" @click="openDialog(props.row)" />
              <q-btn flat round dense icon="delete" size="sm" color="negative" @click="confirmDelete(props.row)" />
            </q-td>
          </template>

          <template #item="props">
            <div class="mobile-card">
              <div class="mobile-card-header">
                <div class="mobile-card-file-icon"><q-icon :name="getFileIcon(props.row.file_url)" /></div>
                <div class="mobile-card-title">
                  <strong>{{ props.row.title }}</strong>
                  <router-link :to="`/products/${props.row.product_slug}`" class="product-link" target="_blank">
                    {{ props.row.product_title }}
                  </router-link>
                </div>
              </div>
              <div class="mobile-card-footer">
                <div class="mobile-card-meta">
                  <a :href="formatMediaUrl(props.row.file_url)" target="_blank" class="file-link">
                    <q-icon :name="getFileIcon(props.row.file_url)" size="16px" />
                    <span>{{ getFileExtension(props.row.file_url) }}</span>
                  </a>
                  <span class="mobile-card-date">{{ formatDate(props.row.created_at) }}</span>
                </div>
                <div class="mobile-card-actions">
                  <q-btn flat round dense icon="edit" size="sm" color="primary" @click="openDialog(props.row)" />
                  <q-btn flat round dense icon="delete" size="sm" color="negative" @click="confirmDelete(props.row)" />
                </div>
              </div>
            </div>
          </template>
        </q-table>
      </div>
    </div>

    <!-- Edit Mode (Dedicated Full Page) -->
    <div v-else-if="viewMode === 'edit'" class="admin-edit-page">
      <!-- Top Navigation -->
      <div class="edit-page-top-nav">
        <div class="nav-breadcrumbs-group">
          <button type="button" class="btn-back-to-list" @click="closeEditView">
            <q-icon name="arrow_forward" size="18px" />
            <span>بازگشت به لیست کاتالوگ‌ها</span>
          </button>
          <div class="edit-breadcrumbs">
            <span class="crumb-root">کاتالوگ‌ها</span>
            <span class="crumb-sep">/</span>
            <span class="crumb-current">{{ editing ? (form.title || 'ویرایش کاتالوگ') : 'کاتالوگ جدید' }}</span>
          </div>
        </div>

        <div class="nav-actions-group">
          <q-btn flat label="انصراف" color="grey-7" class="btn-cancel-nav" @click="closeEditView" />
          <q-btn color="primary" unelevated label="ذخیره اطلاعات" icon="save" :loading="saving" class="btn-save-nav" @click="saveCatalog" />
        </div>
      </div>

      <!-- Bento Form -->
      <q-form ref="formRef" @submit.prevent="saveCatalog" class="edit-form-wrap">
        <div class="edit-page-bento-grid">
          <div class="bento-col-main">
            <!-- Catalog Information Card -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="description" size="20px" />
                </div>
                <div>
                  <h4 class="bento-card-title">مشخصات و عنوان کاتالوگ</h4>
                  <p class="bento-card-desc">عنوان نمایشی و پیوند کاتالوگ به محصول مربوطه</p>
                </div>
              </div>
              <div class="bento-card-body">
                <q-input v-model="form.title" outlined label="عنوان کاتالوگ یا سند*" :rules="[val => !!val || 'عنوان الزامی است']" />
                
                <div style="margin-top: 16px;">
                  <q-select
                    v-if="!editing"
                    v-model="form.product_id"
                    :options="products"
                    option-value="id"
                    option-label="title"
                    emit-value
                    map-options
                    outlined
                    label="محصول مرتبط*"
                    :rules="[val => !!val || 'انتخاب محصول الزامی است']"
                  />
                  <div v-else class="attached-product-banner">
                    <span class="banner-label">محصول متصل:</span>
                    <strong class="banner-val">{{ editing.product_title }}</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="bento-col-side">
            <!-- File Upload Card -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="cloud_upload" size="20px" />
                </div>
                <div>
                  <h4 class="bento-card-title">فایل پیوست سند</h4>
                  <p class="bento-card-desc">بارگذاری فایل PDF یا مدارک محصول</p>
                </div>
              </div>
              <div class="bento-card-body">
                <div class="file-upload">
                  <div class="upload-area" @click="$refs.fileInput.click()">
                    <q-icon v-if="!filePreview" name="cloud_upload" size="44px" color="primary" />
                    <div v-if="!filePreview" class="upload-placeholder">
                      <span class="upload-main-text">کلیک کنید یا فایل را بکشید</span>
                      <span class="upload-hint">PDF, DOC, XLS, PPT, CSV, ZIP — حداکثر 10MB</span>
                    </div>
                    <div v-else class="file-preview">
                      <q-icon :name="getFileIcon(filePreview)" size="36px" color="primary" />
                      <span class="file-name-preview">{{ filePreviewName }}</span>
                      <q-btn flat round dense icon="close" size="sm" @click.stop="clearFile" />
                    </div>
                  </div>
                  <input ref="fileInput" type="file" accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.csv,.zip" style="display: none" @change="onFileSelect" />
                </div>

                <div v-if="editing && !filePreview" class="current-file-badge">
                  <q-icon name="check_circle" size="18px" color="positive" />
                  <span>فایل فعلی روی سرور حفظ خواهد شد مگر اینکه فایل جدیدی انتخاب کنید.</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sticky Bottom Bar -->
        <div class="edit-page-sticky-bar">
          <div class="sticky-bar-info">
            <span class="sticky-bar-status">در حال ویرایش کاتالوگ: {{ form.title || 'کاتالوگ جدید' }}</span>
          </div>
          <div class="sticky-bar-actions">
            <q-btn flat label="انصراف و بازگشت" color="grey-7" class="btn-cancel" @click="closeEditView" />
            <q-btn type="submit" color="primary" unelevated label="ذخیره اطلاعات" icon="save" :loading="saving" class="btn-save" />
          </div>
        </div>
      </q-form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useQuasar } from 'quasar'
import api from 'src/services/api'
import moment from 'moment-jalaali'
import { formatMediaUrl } from 'src/utils/media'

const $q = useQuasar()
const catalogs = ref([])
const products = ref([])
const loading = ref(false)
const saving = ref(false)
const viewMode = ref('list') // 'list' | 'edit'
const editing = ref(null)
const filePreview = ref(null)
const filePreviewName = ref('')
const filter = ref('')
let fileObj = null

const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value <= 800)

function onResize () { windowWidth.value = window.innerWidth }

const pagination = ref({ rowsPerPage: 10, page: 1 })

function paginationLabel (first, last, total) {
  return `${first}–${last} از ${total}`
}

const columns = [
  { name: 'title', label: 'عنوان', field: 'title', align: 'right', sortable: true },
  { name: 'product', label: 'محصول', field: 'product_title', align: 'right' },
  { name: 'file', label: 'فایل', align: 'center' },
  { name: 'created_at', label: 'تاریخ ایجاد', field: 'created_at', align: 'right', sortable: true },
  { name: 'actions', label: 'عملیات', align: 'center' },
]

const defaultForm = { title: '', product_id: null }
const form = ref({ ...defaultForm })
const formRef = ref(null)

function openDialog (row = null) {
  editing.value = row
  if (row) {
    form.value = { title: row.title, product_id: row.product_id }
    filePreview.value = null
    filePreviewName.value = ''
  } else {
    form.value = { ...defaultForm }
    filePreview.value = null
    filePreviewName.value = ''
  }
  fileObj = null
  viewMode.value = 'edit'
}

function closeEditView () {
  viewMode.value = 'list'
  editing.value = null
}

function onFileSelect (e) {
  const file = e.target.files[0]
  if (!file) return
  fileObj = file
  filePreview.value = URL.createObjectURL(file)
  filePreviewName.value = file.name
}

function clearFile () {
  fileObj = null
  filePreview.value = null
  filePreviewName.value = ''
}

function getFileIcon (url) {
  if (!url) return 'insert_drive_file'
  const ext = url.split('.').pop()?.toLowerCase()
  const icons = {
    pdf: 'picture_as_pdf',
    doc: 'article',
    docx: 'article',
    xls: 'table_chart',
    xlsx: 'table_chart',
    ppt: 'slideshow',
    pptx: 'slideshow',
    csv: 'table_chart',
    zip: 'folder_zip',
  }
  return icons[ext] || 'insert_drive_file'
}

function getFileExtension (url) {
  if (!url) return ''
  return url.split('.').pop()?.toUpperCase() || ''
}

function formatDate (date) {
  if (!date) return ''
  return moment(date).format('jYYYY/jMM/jDD - HH:mm')
}

async function saveCatalog () {
  const valid = await formRef.value.validate()
  if (!valid) return

  saving.value = true
  try {
    const fd = new FormData()
    fd.append('title', form.value.title)

    if (editing.value) {
      if (fileObj) {
        fd.append('file', fileObj)
      }
      await api.put(`/api/catalogs/admin/${editing.value.id}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      $q.notify({ type: 'positive', message: 'کاتالوگ بروزرسانی شد' })
    } else {
      fd.append('product_id', form.value.product_id)
      if (fileObj) {
        fd.append('file', fileObj)
      }
      await api.post(`/api/catalogs/admin/product/${form.value.product_id}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      $q.notify({ type: 'positive', message: 'کاتالوگ ایجاد شد' })
    }
    viewMode.value = 'list'
    loadCatalogs()
  } catch (e) {
    $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در ذخیره' })
  } finally {
    saving.value = false
  }
}

function confirmDelete (row) {
  $q.dialog({
    title: 'حذف کاتالوگ',
    message: `آیا از حذف "${row.title}" اطمینان دارید؟\nاین عمل قابل بازگشت نیست.`,
    cancel: 'انصراف',
    ok: { label: 'حذف', color: 'negative' },
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/api/catalogs/admin/${row.id}`)
      $q.notify({ type: 'positive', message: 'کاتالوگ حذف شد' })
      loadCatalogs()
    } catch (e) {
      $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در حذف' })
    }
  })
}

async function loadCatalogs () {
  loading.value = true
  try {
    const res = await api.get('/api/catalogs/admin')
    catalogs.value = res.data.data || []
  } catch (e) { console.error(e) } finally { loading.value = false }
}

async function loadProducts () {
  try {
    const res = await api.get('/api/products/admin/all')
    products.value = res.data.data || []
  } catch (e) { /* */ }
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  loadCatalogs()
  loadProducts()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.page-header-titles h3 { font-size: 20px; font-weight: 800; color: #0a0a0b; margin: 0; }
.page-subtitle { font-size: 13px; color: #71717a; margin-top: 4px; display: block; }
.btn-create { border-radius: 9999px; font-weight: 700; padding: 8px 20px; background: #fed72b !important; color: #0a0a0b !important; }

.table-card { background: white; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.file-link { display: inline-flex; align-items: center; gap: 6px; color: #0a0a0b; text-decoration: none; font-weight: 700; font-size: 12px; background: #f4f4f5; padding: 4px 10px; border-radius: 8px; transition: all 0.2s; }
.file-link:hover { background: #fed72b; color: #0a0a0b; }
.product-link { color: #0a0a0b; text-decoration: none; font-weight: 700; transition: color 0.2s; }
.product-link:hover { color: #d97706; }

.edit-form-wrap { display: flex; flex-direction: column; width: 100%; }
.attached-product-banner { display: flex; align-items: center; gap: 10px; padding: 12px 16px; background: #fafafa; border: 1px solid #e2e8f0; border-radius: 12px; font-size: 13px; }
.banner-label { color: #71717a; }
.banner-val { color: #0a0a0b; }

.upload-area { border: 2px dashed #cbd5e1; border-radius: 14px; padding: 28px; text-align: center; cursor: pointer; transition: all 0.2s; min-height: 120px; display: flex; align-items: center; justify-content: center; background: #fbfbfe; }
.upload-area:hover { border-color: #fed72b; background: #fefce8; }
.upload-placeholder { display: flex; flex-direction: column; align-items: center; gap: 8px; color: #71717a; }
.upload-main-text { font-size: 13px; font-weight: 600; color: #0a0a0b; }
.upload-hint { font-size: 11px; color: #a1a1aa; }
.file-preview { display: flex; align-items: center; gap: 10px; color: #0a0a0b; font-weight: 700; }
.file-name-preview { font-size: 13px; max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.current-file-badge { display: flex; align-items: center; gap: 8px; margin-top: 12px; padding: 10px 14px; background: #ecfdf5; border-radius: 10px; font-size: 12px; color: #065f46; }

@media (max-width: 900px) {
  .page-header { flex-direction: column; align-items: stretch; gap: 14px; }
  .page-header .q-btn { width: 100%; justify-content: center; min-height: 42px; }
}

@media (max-width: 600px) {
  .table-card { overflow-x: auto; }
}

@media (max-width: 480px) {
  .table-card .mobile-search { width: 100% !important; margin: 0 !important; }
}

@media (max-width: 320px) {
  .mobile-card { padding: 10px 8px; border-radius: 12px; }
  .mobile-card-header { gap: 8px; margin-bottom: 8px; }
  .mobile-card-file-icon { width: 34px; height: 34px; border-radius: 8px; }
  .mobile-card-title strong { font-size: 12px; }
  .upload-area { padding: 14px 10px; min-height: 90px; }
  .file-name-preview { max-width: 130px; }
}

.mobile-card { background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 14px; margin-bottom: 10px; width: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
.mobile-card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.mobile-card-file-icon { width: 44px; height: 44px; border-radius: 12px; background: #fafafa; border: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: center; color: #0a0a0b; flex-shrink: 0; }
.mobile-card-title { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.mobile-card-title strong { font-size: 13px; color: #0a0a0b; }
.mobile-card-footer { display: flex; align-items: center; justify-content: space-between; padding-top: 10px; border-top: 1px solid #f1f5f9; }
.mobile-card-meta { display: flex; flex-direction: column; gap: 4px; }
.mobile-card-date { font-size: 11px; color: #a1a1aa; }
.mobile-card-actions { display: flex; gap: 2px; }
.mobile-search { margin-left: 8px; }
</style>

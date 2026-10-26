<template>
  <div class="admin-categories">
    <!-- List Mode -->
    <div v-if="viewMode === 'list'">
      <div class="page-header">
        <div class="page-header-titles">
          <h3>مدیریت دسته‌بندی‌ها</h3>
          <span class="page-subtitle">سازمان‌دهی دسته‌بندی محصولات و راهکارها</span>
        </div>
        <q-btn color="primary" unelevated label="دسته جدید" icon="add" class="btn-create" @click="openDialog()" />
      </div>

      <div class="table-card">
        <q-table
          :rows="categories"
          :columns="columns"
          row-key="id"
          :loading="loading"
          flat
          :pagination="pagination"
          no-data-label="هیچ دسته‌ای یافت نشد"
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

          <template #body-cell-slug="props">
            <q-td :props="props">
              <code class="slug-code">{{ props.row.slug }}</code>
            </q-td>
          </template>

          <template #body-cell-product_count="props">
            <q-td :props="props">
              <span class="count-badge">{{ props.row.product_count || 0 }} محصول</span>
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
                <div class="mobile-card-icon"><q-icon name="category" /></div>
                <div class="mobile-card-title">
                  <strong>{{ props.row.name }}</strong>
                  <code class="slug-code">{{ props.row.slug }}</code>
                </div>
                <span class="count-badge">{{ props.row.product_count || 0 }} محصول</span>
              </div>
              <p v-if="props.row.description" class="mobile-card-desc">{{ props.row.description }}</p>
              <div class="mobile-card-footer">
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
      <!-- Top Nav -->
      <div class="edit-page-top-nav">
        <div class="nav-breadcrumbs-group">
          <button type="button" class="btn-back-to-list" @click="closeEditView">
            <q-icon name="arrow_forward" size="18px" />
            <span>بازگشت به لیست دسته‌ها</span>
          </button>
          <div class="edit-breadcrumbs">
            <span class="crumb-root">دسته‌بندی‌ها</span>
            <span class="crumb-sep">/</span>
            <span class="crumb-current">{{ editing ? (form.name || 'ویرایش دسته') : 'دسته جدید' }}</span>
          </div>
        </div>

        <div class="nav-actions-group">
          <q-btn flat label="انصراف" color="grey-7" class="btn-cancel-nav" @click="closeEditView" />
          <q-btn color="primary" unelevated label="ذخیره اطلاعات" icon="save" :loading="saving" class="btn-save-nav" @click="saveCategory" />
        </div>
      </div>

      <!-- Bento Form -->
      <q-form ref="formRef" @submit.prevent="saveCategory" class="edit-form-wrap">
        <div class="edit-page-bento-grid">
          <div class="bento-col-main">
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="category" size="20px" />
                </div>
                <div>
                  <h4 class="bento-card-title">مشخصات اصلی دسته‌بندی</h4>
                  <p class="bento-card-desc">نام و نشانی یکتا (نامک) برای سازمان‌دهی محصولات در سایت</p>
                </div>
              </div>
              <div class="bento-card-body">
                <div class="form-row">
                  <q-input v-model="form.name" outlined label="نام دسته*" :rules="[val => !!val || 'نام دسته الزامی است']" />
                  <q-input
                    v-model="form.slug"
                    outlined
                    label="نامک انگلیسی (Slug)*"
                    placeholder="e.g. cloud-infrastructure"
                    :rules="[val => !!val || 'نامک الزامی است']"
                    input-class="url-input"
                    input-style="direction: ltr; text-align: left;"
                  />
                </div>
                <div style="margin-top: 16px;">
                  <q-input v-model="form.description" outlined label="توضیحات کوتاه درباره دسته" type="textarea" rows="4" />
                </div>
              </div>
            </div>
          </div>

          <div class="bento-col-side">
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="info" size="20px" />
                </div>
                <div>
                  <h4 class="bento-card-title">اطلاعات تکمیلی</h4>
                </div>
              </div>
              <div class="bento-card-body">
                <div v-if="editing" class="category-stat-box">
                  <span class="stat-label">تعداد محصولات زیرمجموعه:</span>
                  <span class="stat-val">{{ editing.product_count || 0 }} محصول</span>
                </div>
                <div class="category-tip-box">
                  <q-icon name="lightbulb" size="18px" color="amber-8" />
                  <span>تغییر نامک (Slug) ممکن است پیوندهای قدیمی دسته‌بندی در موتورهای جستجو را تحت تاثیر قرار دهد.</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sticky Bottom Bar -->
        <div class="edit-page-sticky-bar">
          <div class="sticky-bar-info">
            <span class="sticky-bar-status">در حال ویرایش دسته: {{ form.name || 'دسته جدید' }}</span>
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

const $q = useQuasar()
const categories = ref([])
const loading = ref(false)
const saving = ref(false)
const viewMode = ref('list') // 'list' | 'edit'
const editing = ref(null)
const filter = ref('')

const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value <= 800)

function onResize () { windowWidth.value = window.innerWidth }

const pagination = ref({ rowsPerPage: 10, page: 1 })

function paginationLabel (first, last, total) {
  return `${first}–${last} از ${total}`
}

const columns = [
  { name: 'name', label: 'نام', field: 'name', align: 'right', sortable: true },
  { name: 'slug', label: 'نامک', field: 'slug', align: 'right' },
  { name: 'description', label: 'توضیحات', field: 'description', align: 'right' },
  { name: 'product_count', label: 'تعداد محصولات', align: 'center' },
  { name: 'actions', label: 'عملیات', align: 'center' },
]

const defaultForm = { name: '', slug: '', description: '' }
const form = ref({ ...defaultForm })
const formRef = ref(null)

function openDialog (row = null) {
  editing.value = row
  form.value = row ? { name: row.name, slug: row.slug, description: row.description || '' } : { ...defaultForm }
  viewMode.value = 'edit'
}

function closeEditView () {
  viewMode.value = 'list'
  editing.value = null
}

async function saveCategory () {
  const valid = await formRef.value.validate()
  if (!valid) return

  saving.value = true
  try {
    if (editing.value) {
      await api.put(`/api/categories/admin/${editing.value.id}`, form.value)
      $q.notify({ type: 'positive', message: 'دسته بروزرسانی شد' })
    } else {
      await api.post('/api/categories/admin', form.value)
      $q.notify({ type: 'positive', message: 'دسته ایجاد شد' })
    }
    viewMode.value = 'list'
    loadCategories()
  } catch (e) {
    $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در ذخیره' })
  } finally { saving.value = false }
}

async function confirmDelete (row) {
  let productCount = 0
  try {
    const res = await api.get(`/api/categories/admin/${row.id}/count`)
    productCount = res.data.data?.count || 0
  } catch (e) { /* ignore */ }

  if (productCount > 0) {
    $q.dialog({
      title: 'هشدار حذف دسته',
      message: `دسته "${row.name}" دارای ${productCount} محصول است. با حذف این دسته، تمام محصولات مرتبط (${productCount} محصول) نیز حذف خواهند شد. آیا مطمئن هستید؟`,
      cancel: 'انصراف',
      ok: { label: 'بله، حذف شود', color: 'negative' },
      persistent: true,
    }).onOk(async () => {
      try {
        await api.delete(`/api/categories/admin/${row.id}`)
        $q.notify({ type: 'positive', message: 'دسته و محصولات مرتبط حذف شدند' })
        loadCategories()
      } catch (e) {
        $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در حذف' })
      }
    })
  } else {
    $q.dialog({
      title: 'حذف دسته',
      message: `آیا از حذف "${row.name}" اطمینان دارید؟`,
      cancel: 'انصراف',
      ok: { label: 'حذف', color: 'negative' },
      persistent: true,
    }).onOk(async () => {
      try {
        await api.delete(`/api/categories/admin/${row.id}`)
        $q.notify({ type: 'positive', message: 'دسته حذف شد' })
        loadCategories()
      } catch (e) {
        $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در حذف' })
      }
    })
  }
}

async function loadCategories () {
  loading.value = true
  try {
    const res = await api.get('/api/categories')
    const cats = res.data.data || []
    const counts = await Promise.all(
      cats.map(c => api.get(`/api/categories/admin/${c.id}/count`).then(r => r.data.data?.count || 0).catch(() => 0))
    )
    categories.value = cats.map((c, i) => ({ ...c, product_count: counts[i] }))
  } catch (e) { console.error(e) } finally { loading.value = false }
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  loadCategories()
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
.slug-code { background: #f4f4f5; padding: 3px 8px; border-radius: 6px; font-size: 12px; color: #0a0a0b; font-weight: 600; }
.count-badge { font-size: 12px; padding: 4px 12px; border-radius: 9999px; background: #fef3c7; color: #92400e; font-weight: 700; }

.edit-form-wrap { display: flex; flex-direction: column; width: 100%; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.category-stat-box { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #fafafa; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 12px; }
.stat-label { font-size: 13px; color: #71717a; }
.stat-val { font-size: 13px; font-weight: 800; color: #0a0a0b; }

.category-tip-box { display: flex; gap: 10px; align-items: flex-start; padding: 12px 14px; background: #fffbeb; border: 1px solid #fef3c7; border-radius: 12px; font-size: 12px; color: #92400e; line-height: 1.7; }

@media (max-width: 900px) {
  .page-header { flex-direction: column; align-items: stretch; gap: 14px; }
  .page-header .q-btn { width: 100%; justify-content: center; min-height: 42px; }
}

@media (max-width: 600px) {
  .form-row { grid-template-columns: 1fr; }
  .table-card { overflow-x: auto; }
}

@media (max-width: 480px) {
  .table-card .mobile-search { width: 100% !important; margin: 0 !important; }
}

@media (max-width: 320px) {
  .mobile-card { padding: 10px 8px; border-radius: 12px; }
  .mobile-card-icon { width: 34px; height: 34px; border-radius: 8px; }
  .mobile-card-title strong { font-size: 12px; }
  .count-badge { font-size: 10px; padding: 2px 6px; }
  .category-stat-box { padding: 8px 10px; font-size: 11px; }
  .category-tip-box { padding: 8px 10px; font-size: 10.5px; }
}

.mobile-card { background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 14px; margin-bottom: 10px; width: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
.mobile-card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.mobile-card-icon { width: 40px; height: 40px; border-radius: 10px; background: #f4f4f5; display: flex; align-items: center; justify-content: center; color: #0a0a0b; flex-shrink: 0; }
.mobile-card-title { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.mobile-card-title strong { font-size: 13px; color: #0a0a0b; }
.mobile-card-desc { font-size: 12px; color: #71717a; margin: 0 0 10px; line-height: 1.6; }
.mobile-card-footer { display: flex; align-items: center; justify-content: flex-end; padding-top: 8px; border-top: 1px solid #f1f5f9; }
.mobile-card-actions { display: flex; gap: 2px; }
.mobile-search { margin-left: 8px; }
</style>

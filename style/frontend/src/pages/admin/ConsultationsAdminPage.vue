<template>
  <div class="admin-consultations">
    <div class="page-header">
      <h3>مدیریت مشاوره‌ها</h3>
    </div>

    <div class="table-card">
      <q-table
        :rows="consultations"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        :pagination="pagination"
        no-data-label="هیچ درخواستی یافت نشد"
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

        <template #body-cell-status="props">
          <q-td :props="props">
            <q-select
              :model-value="props.row.status"
              :options="statusOptions"
              emit-value
              map-options
              dense
              outlined
              class="status-select"
              @update:model-value="val => updateStatus(props.row.id, val)"
            />
          </q-td>
        </template>

        <template #body-cell-created_at="props">
          <q-td :props="props">
            {{ toJalali(props.row.created_at) }}
          </q-td>
        </template>

        <template #body-cell-actions="props">
          <q-td :props="props">
            <q-btn flat round dense icon="visibility" size="sm" color="primary" @click="viewConsultation(props.row)" />
            <q-btn flat round dense icon="delete" size="sm" color="negative" @click="confirmDelete(props.row)" />
          </q-td>
        </template>

        <template #item="props">
          <div class="mobile-card">
            <div class="mobile-card-header">
              <div class="mobile-card-avatar"><q-icon name="person" /></div>
              <div class="mobile-card-title">
                <strong>{{ props.row.full_name }}</strong>
                <span class="mobile-card-phone" dir="ltr">{{ props.row.phone }}</span>
              </div>
            </div>
            <div v-if="props.row.subject" class="mobile-card-subject">{{ subjectLabel(props.row.subject) }}</div>
            <div class="mobile-card-status-row">
              <span class="mobile-card-status-label">وضعیت:</span>
              <q-select
                :model-value="props.row.status"
                :options="statusOptions"
                emit-value
                map-options
                dense
                outlined
                class="mobile-status-select"
                @update:model-value="val => updateStatus(props.row.id, val)"
              />
            </div>
            <div class="mobile-card-footer">
              <span class="mobile-card-date">{{ toJalali(props.row.created_at) }}</span>
              <div class="mobile-card-actions">
                <q-btn flat round dense icon="visibility" size="sm" color="primary" @click="viewConsultation(props.row)" />
                <q-btn flat round dense icon="delete" size="sm" color="negative" @click="confirmDelete(props.row)" />
              </div>
            </div>
          </div>
        </template>
      </q-table>
    </div>

    <!-- View Dialog -->
    <q-dialog v-model="viewDialogOpen">
      <q-card class="view-card" v-if="selectedConsultation">
        <q-card-section class="dialog-header">
          <h3>جزئیات درخواست مشاوره</h3>
          <q-btn flat round dense icon="close" @click="viewDialogOpen = false" />
        </q-card-section>
        <q-card-section class="detail-body">
          <div class="detail-row"><label>نام کامل</label><span>{{ selectedConsultation.full_name }}</span></div>
          <div class="detail-row"><label>تلفن</label><span dir="ltr">{{ selectedConsultation.phone }}</span></div>
          <div class="detail-row" v-if="selectedConsultation.email"><label>ایمیل</label><span dir="ltr">{{ selectedConsultation.email }}</span></div>
          <div class="detail-row" v-if="selectedConsultation.company_name"><label>شرکت</label><span>{{ selectedConsultation.company_name }}</span></div>
          <div class="detail-row" v-if="selectedConsultation.subject"><label>موضوع</label><span>{{ subjectLabel(selectedConsultation.subject) }}</span></div>
          <div class="detail-row" v-if="selectedConsultation.message"><label>پیام</label><span class="message-text">{{ selectedConsultation.message }}</span></div>
          <div class="detail-row"><label>تاریخ ثبت</label><span>{{ toJalali(selectedConsultation.created_at) }}</span></div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useQuasar } from 'quasar'
import moment from 'moment-jalaali'
import api from 'src/services/api'

const $q = useQuasar()
const consultations = ref([])
const loading = ref(false)
const viewDialogOpen = ref(false)
const selectedConsultation = ref(null)
const filter = ref('')

const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value <= 800)

function onResize () { windowWidth.value = window.innerWidth }

const pagination = ref({ rowsPerPage: 10, page: 1 })

function paginationLabel (first, last, total) {
  return `${first}–${last} از ${total}`
}

function toJalali (date) {
  if (!date) return ''
  return moment(date).format('jYYYY/jMM/jDD — HH:mm')
}

const statusOptions = [
  { label: 'جدید', value: 'new' },
  { label: 'بررسی شده', value: 'reviewed' },
  { label: 'تماس گرفته شده', value: 'contacted' },
  { label: 'بسته شده', value: 'closed' },
]

function statusLabel (s) {
  const map = { new: 'جدید', reviewed: 'بررسی شده', contacted: 'تماس گرفته شده', closed: 'بسته شده' }
  return map[s] || s
}

function subjectLabel (s) {
  const map = { product: 'مشاوره درباره محصولات', demo: 'درخواست دمو', implementation: 'پیاده‌سازی سامانه', 'custom-development': 'توسعه نرم‌افزار اختصاصی', other: 'سایر موارد' }
  return map[s] || s
}

const columns = [
  { name: 'full_name', label: 'نام', field: 'full_name', align: 'right', sortable: true },
  { name: 'phone', label: 'تلفن', field: 'phone', align: 'right' },
  { name: 'subject', label: 'موضوع', field: row => subjectLabel(row.subject), align: 'right' },
  { name: 'status', label: 'وضعیت', align: 'center' },
  { name: 'created_at', label: 'تاریخ ثبت', field: 'created_at', align: 'right', sortable: true },
  { name: 'actions', label: 'عملیات', align: 'center' },
]

function viewConsultation (row) { selectedConsultation.value = row; viewDialogOpen.value = true }

async function updateStatus (id, status) {
  try {
    await api.put(`/api/consultations/admin/${id}`, { status })
    const c = consultations.value.find(x => x.id === id)
    if (c) c.status = status
    $q.notify({ type: 'positive', message: 'وضعیت بروزرسانی شد' })
  } catch (e) { $q.notify({ type: 'negative', message: 'خطا در بروزرسانی' }) }
}

function confirmDelete (row) {
  $q.dialog({
    title: 'حذف درخواست',
    message: `آیا از حذف درخواست "${row.full_name}" اطمینان دارید؟`,
    cancel: 'انصراف',
    ok: { label: 'حذف', color: 'negative' },
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/api/consultations/admin/${row.id}`)
      $q.notify({ type: 'positive', message: 'درخواست حذف شد' })
      loadConsultations()
    } catch (e) { $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در حذف' }) }
  })
}

async function loadConsultations () {
  loading.value = true
  try { const res = await api.get('/api/consultations/admin'); consultations.value = res.data.data || [] } catch (e) { console.error(e) } finally { loading.value = false }
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  loadConsultations()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.page-header h3 { font-size: 20px; font-weight: 800; color: #0a0a0b; margin: 0; }
.table-card { background: white; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.status-select { min-width: 140px; }
.view-card { width: 560px; max-width: 95vw; border-radius: 16px; border: 1px solid #e2e8f0; }
.dialog-header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 18px 24px; }
.dialog-header h3 { margin: 0; font-size: 17px; font-weight: 800; color: #0a0a0b; }
.detail-body { display: flex; flex-direction: column; gap: 16px; padding: 24px; }
.detail-row { display: flex; flex-direction: column; gap: 4px; }
.detail-row label { font-size: 12px; font-weight: 700; color: #71717a; }
.detail-row span { font-size: 14px; color: #0a0a0b; font-weight: 600; }
.message-text { background: #fafafa; border: 1px solid #e2e8f0; padding: 14px; border-radius: 10px; line-height: 1.8; white-space: pre-wrap; font-weight: 400 !important; color: #3f3f46 !important; }

@media (max-width: 900px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
}

@media (max-width: 600px) {
  .page-header h3 {
    font-size: 16px;
  }
  .table-card {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .table-card .mobile-search {
    width: 100% !important;
    margin: 0 !important;
  }
  .status-select {
    min-width: 100px;
    font-size: 11px;
  }
  .view-card {
    width: 100vw !important;
    max-width: 100vw !important;
    min-width: 0 !important;
    height: 100vh !important;
    max-height: 100vh !important;
    border-radius: 0 !important;
    margin: 0 !important;
  }
  .detail-body {
    gap: 12px;
    padding: 16px;
  }
  .detail-row label {
    font-size: 11px;
  }
  .detail-row span {
    font-size: 13px;
  }
  .message-text {
    font-size: 12px;
    padding: 10px;
  }
}

@media (max-width: 320px) {
  .mobile-card {
    padding: 10px 8px;
    border-radius: 12px;
  }
  .mobile-card-avatar {
    width: 32px;
    height: 32px;
    border-radius: 8px;
  }
  .mobile-card-title strong {
    font-size: 12px;
  }
  .mobile-card-status-row {
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
  }
  .mobile-status-select {
    max-width: 100%;
    width: 100%;
  }
  .dialog-header {
    padding: 12px 14px;
  }
  .detail-body {
    padding: 12px 10px;
  }
}

/* Mobile card layout */
.mobile-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 10px;
  width: 100%;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.mobile-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.mobile-card-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #0a0a0b;
  color: #fed72b;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.mobile-card-title {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.mobile-card-title strong {
  font-size: 13px;
  color: #0a0a0b;
}
.mobile-card-phone {
  font-size: 11px;
  color: #71717a;
}
.mobile-card-subject {
  font-size: 12px;
  color: #52525b;
  margin-bottom: 8px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.mobile-card-status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.mobile-card-status-label {
  font-size: 11px;
  color: #71717a;
  font-weight: 600;
  white-space: nowrap;
}
.mobile-status-select {
  flex: 1;
  max-width: 180px;
}
.mobile-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 8px;
  border-top: 1px solid #f1f5f9;
}
.mobile-card-date {
  font-size: 10px;
  color: #a1a1aa;
}
.mobile-card-actions {
  display: flex;
  gap: 2px;
}
.mobile-search {
  margin-left: 8px;
}
.status-badge {
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 20px;
  font-weight: 600;
  white-space: nowrap;
}
.status-badge.new { background: #fef3c7; color: #92400e; }
.status-badge.reviewed { background: #e0e7ff; color: #4f46e5; }
.status-badge.contacted { background: #dcfce7; color: #16a34a; }
.status-badge.closed { background: #f3f4f6; color: #6b7280; }
</style>

<template>
  <div class="admin-products">
    <!-- 1. TABLE LIST VIEW -->
    <div v-if="viewMode === 'list'" class="admin-view-list-container">
      <div class="page-header">
        <div class="page-header-titles">
          <h3>مدیریت محصولات و سامانه‌ها</h3>
          <span class="page-subtitle">مشاهده، افزودن و ویرایش سامانه‌ها و پروژه‌های شاخص سازمانی</span>
        </div>
        <button type="button" class="btn-brand-yellow-pill" @click="openDialog()">
          <q-icon name="add" size="18px" />
          <span>محصول جدید</span>
        </button>
      </div>

      <div class="table-card">
        <q-table
          :rows="products"
          :columns="columns"
          row-key="id"
          :loading="loading"
          flat
          :pagination="pagination"
          no-data-label="هیچ محصولی یافت نشد"
          :rows-per-page-label="'ردیف در هر صفحه'"
          :pagination-label="paginationLabel"
          :grid="isMobile"
          :filter="filter"
        >
          <template #top-right>
            <q-input v-model="filter" dense outlined placeholder="جستجو در محصولات..." class="mobile-search" :style="{ width: isMobile ? '160px' : '220px' }">
              <template #append><q-icon name="search" /></template>
            </q-input>
          </template>

          <template #body-cell-image="props">
            <q-td :props="props">
              <img v-if="props.row.image_url" :src="formatMediaUrl(props.row.image_url)" class="table-thumb" loading="lazy" decoding="async" @error="e => handleImageError(e)" />
              <div v-else class="no-image"><q-icon name="image" /></div>
            </q-td>
          </template>

          <template #body-cell-status="props">
            <q-td :props="props">
              <span class="status-chip" :class="{ active: props.row.is_active }">
                {{ props.row.is_active ? 'فعال' : 'غیرفعال' }}
              </span>
            </q-td>
          </template>

          <template #body-cell-featured="props">
            <q-td :props="props">
              <q-btn flat round dense :icon="props.row.is_featured ? 'star' : 'star_border'" :color="props.row.is_featured ? 'amber' : 'grey'" @click="toggleFeatured(props.row)" />
            </q-td>
          </template>

          <template #body-cell-created_at="props">
            <q-td :props="props">
              {{ formatDate(props.row.created_at) }}
            </q-td>
          </template>

          <template #body-cell-actions="props">
            <q-td :props="props">
              <q-btn flat round dense icon="visibility" size="sm" color="info" @click="visitProduct(props.row)">
                <q-tooltip>مشاهده در وب‌سایت</q-tooltip>
              </q-btn>
              <q-btn flat round dense icon="edit" size="sm" color="primary" @click="openDialog(props.row)">
                <q-tooltip>صفحه ویرایش</q-tooltip>
              </q-btn>
              <q-btn flat round dense icon="delete" size="sm" color="negative" @click="confirmDelete(props.row)">
                <q-tooltip>حذف محصول</q-tooltip>
              </q-btn>
            </q-td>
          </template>

          <template #item="props">
            <div class="mobile-card">
              <div class="mobile-card-header">
                <img v-if="props.row.image_url" :src="formatMediaUrl(props.row.image_url)" class="mobile-card-thumb" loading="lazy" decoding="async" @error="e => handleImageError(e)" />
                <div v-else class="mobile-card-thumb-placeholder"><q-icon name="image" /></div>
                <div class="mobile-card-title">
                  <strong>{{ props.row.title }}</strong>
                  <span class="mobile-card-category">{{ props.row.category_name || 'بدون دسته' }}</span>
                </div>
                <span class="status-chip" :class="{ active: props.row.is_active }">
                  {{ props.row.is_active ? 'فعال' : 'غیرفعال' }}
                </span>
              </div>
              <div class="mobile-card-footer">
                <span class="mobile-card-date">{{ formatDate(props.row.created_at) }}</span>
                <div class="mobile-card-actions">
                  <q-btn flat round dense :icon="props.row.is_featured ? 'star' : 'star_border'" :color="props.row.is_featured ? 'amber' : 'grey'" size="sm" @click="toggleFeatured(props.row)" />
                  <q-btn flat round dense icon="visibility" size="sm" color="info" @click="visitProduct(props.row)" />
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
      <!-- Top Navigation -->
      <div class="edit-page-top-nav">
        <div class="edit-nav-right">
          <button type="button" class="btn-back-to-list" @click="closeEditView">
            <span class="back-icon">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </span>
            <span>بازگشت به لیست محصولات</span>
          </button>
          <div class="edit-nav-breadcrumbs">
            <span>مدیریت محصولات</span>
            <span class="crumb-sep">/</span>
            <span class="crumb-active">{{ editing ? 'ویرایش محصول' : 'محصول جدید' }}</span>
          </div>
        </div>

        <div class="edit-page-heading-wrap">
          <h2>{{ editing ? (form.title || 'ویرایش محصول') : 'ایجاد محصول جدید' }}</h2>
          <span class="edit-badge-pill">
            <span class="pill-dot"></span>
            <span>{{ form.is_active ? 'فعال و منتشر شده' : 'پیش‌نویس' }}</span>
          </span>
        </div>

        <div class="edit-nav-actions">
          <button v-if="editing" type="button" class="btn-pill-subtle" @click="onGalleryClick">
            <q-icon name="photo_library" size="17px" />
            <span>گالری تصاویر</span>
          </button>
          <button v-if="editing" type="button" class="btn-pill-subtle" @click="onVideoClick">
            <q-icon name="video_library" size="17px" />
            <span>ویدیو محصول</span>
          </button>
          <button type="button" class="btn-pill-cancel" @click="closeEditView">
            <span>انصراف</span>
          </button>
          <button type="button" class="btn-pill-save-brand" :disabled="saving" @click="saveProduct">
            <span class="btn-icon-bubble">
              <q-spinner-dots v-if="saving" size="14px" />
              <q-icon v-else name="save" size="16px" />
            </span>
            <span>{{ saving ? 'در حال ذخیره...' : 'ذخیره تغییرات' }}</span>
          </button>
        </div>
      </div>

      <!-- Bento Edit Form -->
      <q-form ref="formRef" @submit.prevent="saveProduct" class="edit-form-wrapper">
        <div class="edit-page-bento-grid">
          <!-- Main Content Column -->
          <div class="edit-column-main">
            <!-- Card 1: Core Info -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="dashboard_customize" size="20px" />
                </div>
                <div>
                  <h4>اطلاعات اصلی محصول / سامانه</h4>
                  <p>عنوان تجاری، آدرس صفحه یکتا (اسلاگ) و خلاصه اجرایی جهت نمایش در کارت‌ها</p>
                </div>
              </div>
              <div class="bento-card-body">
                <div class="form-row">
                  <q-input v-model="form.title" outlined label="عنوان محصول / سامانه*" :rules="[val => !!val || 'عنوان الزامی است']" />
                  <q-input v-model="form.slug" outlined label="نامک (Slug)*" :rules="[val => !!val || 'نامک الزامی است']" input-class="url-input" />
                </div>
                <q-input v-model="form.short_description" outlined label="توضیح کوتاه و ارزش پیشنهادی" type="textarea" rows="2" placeholder="معرفی فشرده در ۲ یا ۳ خط" />
              </div>
            </div>

            <!-- Card 2: Full Description & Architecture -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble accent">
                  <q-icon name="architecture" size="20px" />
                </div>
                <div>
                  <h4>توضیحات کامل و معماری سیستم</h4>
                  <p>تشریح قابلیت‌ها، ساختار فنی، استانداردهای رعایت‌شده و جزئیات پیاده‌سازی</p>
                </div>
              </div>
              <div class="bento-card-body">
                <RichTextEditor
                  v-model="form.description"
                  :min-height="360"
                  placeholder="توضیحات کامل محصول را بنویسید…"
                  hint="قالب‌بندی، فهرست و لینک پشتیبانی می‌شود. اسکریپت و کد اجرایی به‌طور خودکار حذف می‌شود."
                />
              </div>
            </div>

            <!-- Card 3: Performance & Scale KPIs (3 metrics) -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble success">
                  <q-icon name="speed" size="20px" />
                </div>
                <div>
                  <h4>شاخص‌های کلیدی عملکرد و مقیاس‌پذیری (KPIs)</h4>
                  <p>۳ معیار شاخص فنی یا عددی که بر روی کارت محصول در صفحه اصلی و کاتالوگ نمایش داده می‌شوند</p>
                </div>
              </div>
              <div class="bento-card-body">
                <div class="kpi-metric-box">
                  <span class="kpi-metric-box-title">شاخص اول (معیار اصلی ترافیک / حجم کاربری)</span>
                  <div class="form-row">
                    <q-input v-model="form.metric1_val" outlined label="مقدار شاخص ۱" placeholder="مثال: ۱.۸M+ یا ۱۰k TPS" />
                    <q-input v-model="form.metric1_lbl" outlined label="عنوان شاخص ۱" placeholder="مثال: تراکنش روزانه" />
                  </div>
                </div>

                <div class="kpi-metric-box">
                  <span class="kpi-metric-box-title">شاخص دوم (معیار سرعت و لتنسی)</span>
                  <div class="form-row">
                    <q-input v-model="form.metric2_val" outlined label="مقدار شاخص ۲" placeholder="مثال: ۱۲ms یا زیر ۸ میلی‌ثانیه" />
                    <q-input v-model="form.metric2_lbl" outlined label="عنوان شاخص ۲" placeholder="مثال: لتنسی نودها" />
                  </div>
                </div>

                <div class="kpi-metric-box">
                  <span class="kpi-metric-box-title">شاخص سوم (معیار پایداری و استاندارد امنیتی)</span>
                  <div class="form-row">
                    <q-input v-model="form.metric3_val" outlined label="مقدار شاخص ۳" placeholder="مثال: ۹۹.۹۹۹٪ یا Zero-Trust" />
                    <q-input v-model="form.metric3_lbl" outlined label="عنوان شاخص ۳" placeholder="مثال: SLA پایداری یا استاندارد ISO" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Card 4: Links -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble info">
                  <q-icon name="link" size="20px" />
                </div>
                <div>
                  <h4>لینک سایت، دمو یا مستندات</h4>
                </div>
              </div>
              <div class="bento-card-body">
                <q-input v-model="form.url" outlined label="لینک سایت یا محصول" placeholder="https://example.com یا /contact" input-class="url-input" />
              </div>
            </div>
          </div>

          <!-- Side Settings Column -->
          <div class="edit-column-side">
            <!-- Side Card 1: Main Image -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="image" size="20px" />
                </div>
                <div>
                  <h4>تصویر شاخص محصول</h4>
                  <p>کاور اصلی برای کارت‌ها و صفحه جزئیات</p>
                </div>
              </div>
              <div class="bento-card-body">
                <div class="upload-area" @click="$refs.fileInput.click()">
                  <img v-if="imagePreview" :src="imagePreview" class="upload-preview" />
                  <div v-else class="upload-placeholder">
                    <q-icon name="cloud_upload" size="36px" />
                    <span>کلیک برای انتخاب تصویر</span>
                    <span class="upload-hint">JPG, PNG, WebP — حداکثر ۱۰MB</span>
                  </div>
                </div>
                <input ref="fileInput" type="file" accept="image/*" style="display: none" @change="onFileSelect" />

                <div v-if="editing && imagePreview" class="profile-image-actions">
                  <q-btn flat dense icon="swap_horiz" color="primary" label="تعویض تصویر" @click="$refs.fileInput.click()" />
                  <q-btn flat dense icon="delete" color="negative" label="حذف تصویر" @click="deleteProfileImage" />
                </div>
              </div>
            </div>

            <!-- Side Card 2: Status & Featured -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble success">
                  <q-icon name="verified" size="20px" />
                </div>
                <div>
                  <h4>وضعیت و سطح دسترسی</h4>
                </div>
              </div>
              <div class="bento-card-body">
                <div class="toggle-group" style="display: flex; flex-direction: column; gap: 8px;">
                  <q-toggle v-model="form.is_active" label="فعال (نمایش عمومی در سایت)" />
                  <q-toggle v-model="form.is_featured" label="پروژه ویژه و شاخص ملی" />
                </div>
              </div>
            </div>

            <!-- Side Card 3: Category & Badge -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="category" size="20px" />
                </div>
                <div>
                  <h4>دسته‌بندی و نشان</h4>
                </div>
              </div>
              <div class="bento-card-body">
                <q-select v-model="form.category_id" :options="categories" option-value="id" option-label="name" emit-value map-options outlined label="دسته‌بندی*" :rules="[val => !!val || 'دسته‌بندی الزامی است']" clearable />
                <q-input v-model="form.badge" outlined label="نشان اختصاصی (Badge)" placeholder="مثال: استقرار فعال در ۲۶ استان کشور" />
              </div>
            </div>

            <!-- Side Card 4: Tech Stack Tags -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="integration_instructions" size="20px" />
                </div>
                <div>
                  <h4>پشته فناوری و ابزارها</h4>
                </div>
              </div>
              <div class="bento-card-body">
                <q-input v-model="form.tags_text" outlined label="تگ‌های فناوری (با کاما)" placeholder="Kafka, Golang Core, Kubernetes, Redis" />
              </div>
            </div>

            <!-- Side Card 5: Gallery & Media Actions -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble info">
                  <q-icon name="perm_media" size="20px" />
                </div>
                <div>
                  <h4>رسانه‌های تکمیلی</h4>
                  <p>گالری عکس‌ها و ویدیوهای تعاملی سامانه</p>
                </div>
              </div>
              <div class="bento-card-body">
                <div style="display: flex; flex-direction: column; gap: 10px;">
                  <button type="button" class="btn-pill-subtle full-width" @click="onGalleryClick">
                    <q-icon name="photo_library" size="18px" />
                    <span>مدیریت گالری تصاویر ({{ productImages.length }} تصویر)</span>
                  </button>
                  <button type="button" class="btn-pill-subtle full-width" @click="onVideoClick">
                    <q-icon name="video_library" size="18px" />
                    <span>مدیریت ویدیوهای محصول ({{ productVideos.length }} ویدیو)</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sticky Bottom Action Bar -->
        <div class="edit-page-sticky-bar">
          <div class="sticky-bar-info">
            <span class="dot"></span>
            <span>در حال ویرایش محصول: <strong>{{ form.title || 'پیش‌نویس جدید' }}</strong></span>
          </div>
          <div class="sticky-bar-buttons">
            <button type="button" class="btn-pill-cancel" @click="closeEditView">انصراف و بازگشت</button>
            <button type="submit" class="btn-pill-save-brand" :disabled="saving">
              <span class="btn-icon-bubble">
                <q-spinner-dots v-if="saving" size="14px" />
                <q-icon v-else name="save" size="16px" />
              </span>
              <span>{{ saving ? 'در حال ذخیره‌سازی...' : 'ذخیره محصول' }}</span>
            </button>
          </div>
        </div>
      </q-form>
    </div>

    <q-dialog v-model="imageManagerOpen">
      <q-card class="image-manager-card">
        <q-card-section class="dialog-header">
          <h3>گالری تصاویر محصول</h3>
          <q-btn flat round dense icon="close" @click="imageManagerOpen = false" />
        </q-card-section>
        <q-card-section>
          <div class="upload-zone" @click="$refs.imageUploadInput.click()" @dragover.prevent @drop.prevent="onImageDrop">
            <q-icon name="cloud_upload" size="36px" color="primary" />
            <span>تصویر جدید آپلود کنید (کلیک یا Drag & Drop)</span>
            <span class="upload-hint">JPG, PNG, GIF, WebP — حداکثر ۱۰MB</span>
            <input ref="imageUploadInput" type="file" accept="image/*" multiple style="display: none" @change="onImageFilesSelect" />
          </div>

          <!-- Upload Progress Bar for Images -->
          <div v-if="isUploading && uploadStatusText.includes('تصویر')" class="upload-progress-box q-my-md">
            <div class="row items-center justify-between text-caption text-weight-medium q-mb-xs">
              <span class="text-primary">{{ uploadStatusText }}</span>
              <span class="text-weight-bold text-primary">{{ uploadProgress }}٪</span>
            </div>
            <q-linear-progress
              stripe
              rounded
              size="10px"
              :value="uploadProgress / 100"
              color="primary"
              track-color="blue-1"
            />
          </div>

          <div v-if="productImages.length === 0" class="no-images">
            <q-icon name="image_not_supported" size="48px" color="grey-4" />
            <p>هنوز تصویری آپلود نشده است</p>
          </div>

          <div v-else class="image-grid">
            <div
              v-for="(img, index) in productImages"
              :key="img.id"
              class="image-item"
              draggable="true"
              @dragstart="onDragStart(index)"
              @dragover.prevent
              @drop="onDrop(index)"
            >
              <img :src="img.image_url" :alt="'Image ' + (index + 1)" @click="viewImage(img)" />
              <div class="image-actions">
                <q-btn flat round dense icon="visibility" color="white" size="sm" title="مشاهده" @click="viewImage(img)" />
                <q-btn flat round dense icon="swap_horiz" color="amber" size="sm" title="تعویض تصویر" @click="onReplaceImageClick(img)" />
                <q-btn flat round dense icon="delete" color="negative" size="sm" title="حذف" @click="confirmDeleteImage(img)" />
              </div>
              <span class="image-order">{{ index + 1 }}</span>
            </div>
          </div>
          <input ref="imageReplaceInput" type="file" accept="image/*" style="display: none" @change="onImageReplaceSelect" />
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Image Preview Dialog -->
    <q-dialog v-model="imageViewOpen">
      <q-card class="image-view-card">
        <q-card-section class="dialog-header">
          <h3>مشاهده تصویر</h3>
          <q-btn flat round dense icon="close" @click="imageViewOpen = false" />
        </q-card-section>
        <q-card-section class="image-view-body">
          <img :src="imageViewUrl" alt="Product image preview" />
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Product Videos Manager -->
    <q-dialog v-model="videoManagerOpen">
      <q-card class="image-manager-card">
        <q-card-section class="dialog-header">
          <h3>ویدیوهای محصول</h3>
          <q-btn flat round dense icon="close" @click="videoManagerOpen = false" />
        </q-card-section>
        <q-card-section>
          <div class="upload-zone" @click="$refs.videoUploadInput.click()" @dragover.prevent @drop.prevent="onVideoDrop">
            <q-icon name="cloud_upload" size="36px" color="primary" />
            <span>ویدیو جدید آپلود کنید (کلیک یا Drag & Drop)</span>
            <span class="upload-hint">MP4, WebM, OGG, MOV — حداکثر ۱۰۰MB</span>
            <input ref="videoUploadInput" type="file" accept="video/*" multiple style="display: none" @change="onVideoFilesSelect" />
          </div>

          <!-- Upload Progress Bar for Videos -->
          <div v-if="isUploading && uploadStatusText.includes('ویدیو')" class="upload-progress-box q-my-md">
            <div class="row items-center justify-between text-caption text-weight-medium q-mb-xs">
              <span class="text-primary">{{ uploadStatusText }}</span>
              <span class="text-weight-bold text-primary">{{ uploadProgress }}٪</span>
            </div>
            <q-linear-progress
              stripe
              rounded
              size="10px"
              :value="uploadProgress / 100"
              color="primary"
              track-color="blue-1"
            />
          </div>

          <div v-if="productVideos.length === 0" class="no-images">
            <q-icon name="videocam_off" size="48px" color="grey-4" />
            <p>هنوز ویدیویی آپلود نشده است</p>
          </div>

          <div v-else class="video-grid">
            <div
              v-for="(vid, index) in productVideos"
              :key="vid.id"
              class="video-item"
              draggable="true"
              @dragstart="onVideoDragStart(index)"
              @dragover.prevent
              @drop="onVideoReorderDrop(index)"
            >
              <video :src="vid.video_url" :poster="vid.thumbnail_url" controls preload="metadata" class="video-preview"></video>
              <span class="image-order">{{ index + 1 }}</span>
              <div class="video-item-info">
                <span class="video-item-title" :title="vid.title">{{ vid.title || 'ویدیو محصول' }}</span>
                <div class="video-item-actions">
                  <q-btn flat round dense icon="edit" color="primary" size="sm" title="ویرایش عنوان" @click="renameVideo(vid)" />
                  <q-btn flat round dense icon="swap_horiz" color="warning" size="sm" title="تعویض فایل ویدیو" @click="onReplaceVideoClick(vid)" />
                  <q-btn flat round dense icon="delete" color="negative" size="sm" title="حذف" @click="confirmDeleteVideo(vid)" />
                </div>
              </div>
            </div>
          </div>
          <input ref="videoReplaceInput" type="file" accept="video/*" style="display: none" @change="onVideoReplaceSelect" />
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import api from 'src/services/api'
import moment from 'moment-jalaali'
import RichTextEditor from 'src/components/common/RichTextEditor.vue'
import { formatMediaUrl, handleImageError } from 'src/utils/media'

const $q = useQuasar()
const router = useRouter()
const viewMode = ref('list') // 'list' | 'edit'
const products = ref([])
const categories = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogOpen = ref(false)
const editing = ref(null)
const imagePreview = ref(null)
const filter = ref('')
let imageFile = null

function closeEditView () {
  viewMode.value = 'list'
  editing.value = null
  form.value = { ...defaultForm }
  imagePreview.value = null
  imageFile = null
  productImages.value = []
  productVideos.value = []
  pendingGalleryFiles.value = []
  pendingGalleryVideos.value = []
}

const imageManagerOpen = ref(false)
const productImages = ref([])
const pendingGalleryFiles = ref([])
const dragIndex = ref(null)

const videoManagerOpen = ref(false)
const productVideos = ref([])
const pendingGalleryVideos = ref([])
const videoReplaceInput = ref(null)
let replaceTargetVideo = null

const imageViewOpen = ref(false)
const imageViewUrl = ref('')
const imageReplaceInput = ref(null)
let replaceTargetImage = null
const videoDragIndex = ref(null)

const uploadProgress = ref(0)
const isUploading = ref(false)
const uploadStatusText = ref('')

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
  { name: 'category', label: 'دسته‌بندی', field: 'category_name', align: 'right' },
  { name: 'status', label: 'وضعیت', align: 'center' },
  { name: 'featured', label: 'ویژه', align: 'center' },
  { name: 'created_at', label: 'تاریخ ایجاد', field: 'created_at', align: 'right', sortable: true },
  { name: 'actions', label: 'عملیات', align: 'center' },
]

const defaultForm = {
  title: '',
  slug: '',
  short_description: '',
  description: '',
  category_id: null,
  is_active: true,
  is_featured: false,
  url: '',
  badge: '',
  tags_text: '',
  metric1_val: '',
  metric1_lbl: '',
  metric2_val: '',
  metric2_lbl: '',
  metric3_val: '',
  metric3_lbl: '',
}
const form = ref({ ...defaultForm })
const formRef = ref(null)

function openDialog (row = null) {
  editing.value = row
  if (row) {
    let parsedTags = ''
    if (typeof row.tags_json === 'string') {
      try {
        const arr = JSON.parse(row.tags_json)
        parsedTags = Array.isArray(arr) ? arr.join(', ') : row.tags_json
      } catch {
        parsedTags = row.tags_json
      }
    } else if (Array.isArray(row.tags_json)) {
      parsedTags = row.tags_json.join(', ')
    }

    let m1Val = '', m1Lbl = '', m2Val = '', m2Lbl = '', m3Val = '', m3Lbl = ''
    if (row.metrics_json) {
      try {
        const metricsArr = typeof row.metrics_json === 'string' ? JSON.parse(row.metrics_json) : row.metrics_json
        if (Array.isArray(metricsArr)) {
          if (metricsArr[0]) { m1Val = metricsArr[0].val || ''; m1Lbl = metricsArr[0].lbl || '' }
          if (metricsArr[1]) { m2Val = metricsArr[1].val || ''; m2Lbl = metricsArr[1].lbl || '' }
          if (metricsArr[2]) { m3Val = metricsArr[2].val || ''; m3Lbl = metricsArr[2].lbl || '' }
        }
      } catch {}
    }

    form.value = {
      title: row.title,
      slug: row.slug,
      short_description: row.short_description || '',
      description: row.description || '',
      category_id: row.category_id,
      is_active: row.is_active,
      is_featured: row.is_featured,
      url: row.url || '',
      badge: row.badge || '',
      tags_text: parsedTags,
      metric1_val: m1Val,
      metric1_lbl: m1Lbl,
      metric2_val: m2Val,
      metric2_lbl: m2Lbl,
      metric3_val: m3Val,
      metric3_lbl: m3Lbl,
    }
    imagePreview.value = row.image_url ? formatMediaUrl(row.image_url) : null
    pendingGalleryFiles.value = []
    pendingGalleryVideos.value = []
    loadProductImages()
    loadProductVideos()
  } else {
    form.value = { ...defaultForm }
    imagePreview.value = null
    productImages.value = []
    productVideos.value = []
    pendingGalleryFiles.value = []
    pendingGalleryVideos.value = []
  }
  imageFile = null
  viewMode.value = 'edit'
  dialogOpen.value = false
}

function onFileSelect (e) {
  const file = e.target.files[0]
  e.target.value = ''
  if (!file) return
  imageFile = file
  imagePreview.value = URL.createObjectURL(file)
}

async function deleteProfileImage () {
  if (!editing.value) return
  $q.dialog({
    title: 'حذف تصویر اصلی',
    message: 'آیا از حذف تصویر اصلی محصول اطمینان دارید؟',
    cancel: 'انصراف',
    ok: { label: 'حذف', color: 'negative' },
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/api/products/admin/${editing.value.id}/image`)
      imagePreview.value = null
      imageFile = null
      $q.notify({ type: 'positive', message: 'تصویر اصلی حذف شد' })
      loadProducts()
    } catch (e) {
      $q.notify({ type: 'negative', message: 'خطا در حذف تصویر' })
    }
  })
}

function visitProduct (row) {
  router.push(`/products/${row.slug}`)
}

async function toggleFeatured (row) {
  const newValue = !row.is_featured
  try {
    await api.put(`/api/products/admin/${row.id}`, { is_featured: newValue })
    row.is_featured = newValue
    $q.notify({ type: 'positive', message: newValue ? 'محصول ویژه شد' : 'محصول از ویژه خارج شد' })
  } catch (e) {
    $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در بروزرسانی' })
  }
}

async function saveProduct () {
  const valid = await formRef.value.validate()
  if (!valid) return

  saving.value = true
  try {
    const fd = new FormData()
    fd.append('title', form.value.title)
    fd.append('slug', form.value.slug)
    fd.append('short_description', form.value.short_description)
    fd.append('description', form.value.description)
    fd.append('category_id', form.value.category_id || '')
    fd.append('is_active', form.value.is_active)
    fd.append('is_featured', form.value.is_featured)
    fd.append('url', form.value.url)
    fd.append('badge', form.value.badge || '')

    // Assemble tags array
    const tagsArr = (form.value.tags_text || '')
      .split(/[,،]/)
      .map(t => t.trim())
      .filter(Boolean)
    fd.append('tags_json', JSON.stringify(tagsArr))

    // Assemble metrics array
    const metricsArr = []
    if (form.value.metric1_val || form.value.metric1_lbl) {
      metricsArr.push({ val: form.value.metric1_val, lbl: form.value.metric1_lbl })
    }
    if (form.value.metric2_val || form.value.metric2_lbl) {
      metricsArr.push({ val: form.value.metric2_val, lbl: form.value.metric2_lbl })
    }
    if (form.value.metric3_val || form.value.metric3_lbl) {
      metricsArr.push({ val: form.value.metric3_val, lbl: form.value.metric3_lbl })
    }
    fd.append('metrics_json', JSON.stringify(metricsArr))

    if (imageFile) fd.append('image', imageFile)

    if (editing.value) {
      await api.put(`/api/products/admin/${editing.value.id}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      $q.notify({ type: 'positive', message: 'محصول با موفقیت بروزرسانی شد' })
      viewMode.value = 'list'
      dialogOpen.value = false
    } else {
      const res = await api.post('/api/products/admin', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      const newProduct = res.data.data
      editing.value = newProduct

      // Upload any staged gallery images
      if (pendingGalleryFiles.value.length > 0) {
        for (const item of pendingGalleryFiles.value) {
          const imgFd = new FormData()
          imgFd.append('image', item.file)
          try {
            await api.post(`/api/products/admin/${newProduct.id}/images`, imgFd, {
              headers: { 'Content-Type': 'multipart/form-data' }
            })
          } catch (err) {
            console.error('Failed to upload staged gallery image', err)
          }
        }
        pendingGalleryFiles.value = []
      }

      // Upload any staged videos
      if (pendingGalleryVideos.value.length > 0) {
        for (const item of pendingGalleryVideos.value) {
          const vidFd = new FormData()
          vidFd.append('video', item.file)
          vidFd.append('title', (item.file.name || 'ویدیو محصول').replace(/\.[^.]+$/, ''))
          try {
            await api.post(`/api/products/admin/${newProduct.id}/videos`, vidFd, {
              headers: { 'Content-Type': 'multipart/form-data' }
            })
          } catch (err) {
            console.error('Failed to upload staged video', err)
          }
        }
        pendingGalleryVideos.value = []
      }

      $q.notify({ type: 'positive', message: 'محصول جدید با موفقیت ایجاد شد' })
      viewMode.value = 'list'
      dialogOpen.value = false
    }
    loadProducts()
  } catch (e) {
    $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در ذخیره' })
  } finally {
    saving.value = false
  }
}

function confirmDelete (row) {
  $q.dialog({
    title: 'حذف محصول',
    message: `آیا از حذف "${row.title}" اطمینان دارید؟`,
    cancel: 'انصراف',
    ok: { label: 'حذف', color: 'negative' },
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/api/products/admin/${row.id}`)
      $q.notify({ type: 'positive', message: 'محصول حذف شد' })
      loadProducts()
    } catch (e) {
      $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در حذف' })
    }
  })
}

async function loadProducts () {
  loading.value = true
  try {
    const res = await api.get('/api/products/admin/all')
    products.value = res.data.data || []
  } catch (e) { console.error(e) } finally { loading.value = false }
}

async function openImageManager () {
  imageManagerOpen.value = true
  if (editing.value) {
    await loadProductImages()
  }
}

async function onGalleryClick () {
  await openImageManager()
}

async function loadProductImages () {
  if (!editing.value) return
  try {
    const res = await api.get(`/api/products/${editing.value.id}/images`)
    productImages.value = res.data.data || []
  } catch (e) {
    $q.notify({ type: 'negative', message: 'خطا در بارگذاری تصاویر' })
  }
}

async function onImageFilesSelect (e) {
  const files = Array.from(e.target.files || [])
  for (const file of files) {
    if (editing.value) {
      await uploadGalleryImage(file)
    } else {
      stageGalleryImage(file)
    }
  }
  e.target.value = ''
}

async function onImageDrop (e) {
  const files = Array.from(e.dataTransfer.files || [])
  for (const file of files) {
    if (file.type.startsWith('image/')) {
      if (editing.value) {
        await uploadGalleryImage(file)
      } else {
        stageGalleryImage(file)
      }
    }
  }
}

function stageGalleryImage (file) {
  const tempId = 'temp-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9)
  const previewUrl = URL.createObjectURL(file)
  pendingGalleryFiles.value.push({ tempId, file })
  productImages.value.push({
    id: tempId,
    image_url: previewUrl,
    isPending: true,
  })
}

async function uploadGalleryImage (file) {
  if (!editing.value) return
  isUploading.value = true
  uploadProgress.value = 0
  uploadStatusText.value = `در حال بارگذاری تصویر: ${file.name || ''}...`

  const fd = new FormData()
  fd.append('image', file)
  try {
    await api.post(`/api/products/admin/${editing.value.id}/images`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        }
      }
    })
    await loadProductImages()
    $q.notify({ type: 'positive', message: 'تصویر آپلود شد' })
  } catch (e) {
    $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در آپلود تصویر' })
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
    uploadStatusText.value = ''
  }
}

function confirmDeleteImage (img) {
  $q.dialog({
    title: 'حذف تصویر',
    message: 'آیا از حذف این تصویر اطمینان دارید؟',
    cancel: 'انصراف',
    ok: { label: 'حذف', color: 'negative' },
    persistent: true,
  }).onOk(async () => {
    if (img.isPending || !editing.value) {
      productImages.value = productImages.value.filter(item => item.id !== img.id)
      pendingGalleryFiles.value = pendingGalleryFiles.value.filter(item => item.tempId !== img.id)
      $q.notify({ type: 'positive', message: 'تصویر از گالری حذف شد' })
      return
    }
    try {
      await api.delete(`/api/products/admin/images/${img.id}`)
      await loadProductImages()
      $q.notify({ type: 'positive', message: 'تصویر حذف شد' })
    } catch (e) {
      $q.notify({ type: 'negative', message: 'خطا در حذف تصویر' })
    }
  })
}

function viewImage (img) {
  imageViewUrl.value = img.image_url
  imageViewOpen.value = true
}

function onReplaceImageClick (img) {
  replaceTargetImage = img
  imageReplaceInput.value?.click()
}

async function onImageReplaceSelect (e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file || !replaceTargetImage) return
  const fd = new FormData()
  fd.append('image', file)
  try {
    await api.put(`/api/products/admin/images/${replaceTargetImage.id}`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    await loadProductImages()
    $q.notify({ type: 'positive', message: 'تصویر تعویض شد' })
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.message || 'خطا در تعویض تصویر' })
  } finally {
    replaceTargetImage = null
  }
}

// ========================
// Product videos manager
// ========================
async function openVideoManager () {
  videoManagerOpen.value = true
  if (editing.value) {
    await loadProductVideos()
  }
}

async function onVideoClick () {
  await openVideoManager()
}

async function loadProductVideos () {
  if (!editing.value) return
  try {
    const res = await api.get(`/api/products/${editing.value.id}/videos`)
    productVideos.value = res.data.data || []
  } catch (e) {
    $q.notify({ type: 'negative', message: 'خطا در بارگذاری ویدیوها' })
  }
}

async function onVideoFilesSelect (e) {
  const files = Array.from(e.target.files || [])
  for (const file of files) {
    if (editing.value) {
      await uploadProductVideo(file)
    } else {
      stageProductVideo(file)
    }
  }
  e.target.value = ''
}

async function onVideoDrop (e) {
  const files = Array.from(e.dataTransfer.files || [])
  for (const file of files) {
    if (file.type.startsWith('video/')) {
      if (editing.value) {
        await uploadProductVideo(file)
      } else {
        stageProductVideo(file)
      }
    }
  }
}

function stageProductVideo (file) {
  if (file.size > MAX_VIDEO_SIZE) {
    $q.notify({ type: 'negative', message: 'حجم ویدیو نباید بیشتر از ۱۰۰ مگابایت باشد' })
    return
  }
  const tempId = 'temp-vid-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9)
  const previewUrl = URL.createObjectURL(file)
  pendingGalleryVideos.value.push({ tempId, file })
  productVideos.value.push({
    id: tempId,
    title: (file.name || 'ویدیو محصول').replace(/\.[^.]+$/, ''),
    video_url: previewUrl,
    isPending: true,
  })
}

const MAX_VIDEO_SIZE = 100 * 1024 * 1024 // 100MB

async function uploadProductVideo (file) {
  if (!editing.value) return
  if (file.size > MAX_VIDEO_SIZE) {
    $q.notify({ type: 'negative', message: 'حجم ویدیو نباید بیشتر از ۱۰۰ مگابایت باشد' })
    return
  }
  isUploading.value = true
  uploadProgress.value = 0
  uploadStatusText.value = `در حال بارگذاری ویدیو: ${file.name || ''}...`

  const fd = new FormData()
  fd.append('video', file)
  fd.append('title', (file.name || 'ویدیو محصول').replace(/\.[^.]+$/, ''))
  try {
    await api.post(`/api/products/admin/${editing.value.id}/videos`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        }
      }
    })
    await loadProductVideos()
    $q.notify({ type: 'positive', message: 'ویدیو آپلود شد' })
  } catch (e) {
    $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در آپلود ویدیو' })
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
    uploadStatusText.value = ''
  }
}

function renameVideo (vid) {
  $q.dialog({
    title: 'ویرایش عنوان ویدیو',
    prompt: {
      model: vid.title || '',
      label: 'عنوان',
      type: 'text',
    },
    cancel: 'انصراف',
    ok: { label: 'ذخیره', color: 'primary' },
    persistent: true,
  }).onOk(async (title) => {
    try {
      await api.put(`/api/products/admin/videos/${vid.id}`, { title })
      await loadProductVideos()
      $q.notify({ type: 'positive', message: 'عنوان ویدیو بروزرسانی شد' })
    } catch (e) {
      $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در بروزرسانی ویدیو' })
    }
  })
}

function onReplaceVideoClick (vid) {
  replaceTargetVideo = vid
  videoReplaceInput.value?.click()
}

async function onVideoReplaceSelect (e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file || !replaceTargetVideo) return
  const fd = new FormData()
  fd.append('video', file)
  try {
    await api.put(`/api/products/admin/videos/${replaceTargetVideo.id}`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    await loadProductVideos()
    $q.notify({ type: 'positive', message: 'فایل ویدیو تعویض شد' })
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.message || 'خطا در تعویض ویدیو' })
  } finally {
    replaceTargetVideo = null
  }
}

function confirmDeleteVideo (vid) {
  $q.dialog({
    title: 'حذف ویدیو',
    message: 'آیا از حذف این ویدیو اطمینان دارید؟',
    cancel: 'انصراف',
    ok: { label: 'حذف', color: 'negative' },
    persistent: true,
  }).onOk(async () => {
    if (vid.isPending || !editing.value) {
      productVideos.value = productVideos.value.filter(item => item.id !== vid.id)
      pendingGalleryVideos.value = pendingGalleryVideos.value.filter(item => item.tempId !== vid.id)
      $q.notify({ type: 'positive', message: 'ویدیو حذف شد' })
      return
    }
    try {
      await api.delete(`/api/products/admin/videos/${vid.id}`)
      await loadProductVideos()
      $q.notify({ type: 'positive', message: 'ویدیو حذف شد' })
    } catch (e) {
      $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در حذف ویدیو' })
    }
  })
}

function onVideoDragStart (index) {
  videoDragIndex.value = index
}

async function onVideoReorderDrop (dropIndex) {
  if (videoDragIndex.value === null || videoDragIndex.value === dropIndex) return
  const items = [...productVideos.value]
  const [moved] = items.splice(videoDragIndex.value, 1)
  items.splice(dropIndex, 0, moved)
  productVideos.value = items
  videoDragIndex.value = null

  const payload = items.map((item, idx) => ({
    id: item.id,
    sort_order: idx,
  }))
  try {
    await api.put('/api/products/admin/videos/reorder', { videos: payload })
  } catch (e) {
    $q.notify({ type: 'negative', message: 'خطا در مرتب‌سازی ویدیوها' })
    await loadProductVideos()
  }
}

function onDragStart (index) {
  dragIndex.value = index
}

async function onDrop (dropIndex) {
  if (dragIndex.value === null || dragIndex.value === dropIndex) return
  const items = [...productImages.value]
  const [moved] = items.splice(dragIndex.value, 1)
  items.splice(dropIndex, 0, moved)
  productImages.value = items
  dragIndex.value = null

  const payload = items.map((item, idx) => ({
    id: item.id,
    sort_order: idx,
  }))
  try {
    await api.put('/api/products/admin/images/reorder', { images: payload })
  } catch (e) {
    $q.notify({ type: 'negative', message: 'خطا در مرتب‌سازی' })
    await loadProductImages()
  }
}

onMounted(async () => {
  window.addEventListener('resize', onResize)
  loadProducts()
  try { const res = await api.get('/api/categories'); categories.value = res.data.data || [] } catch (e) { /* */ }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.page-header h3 { font-size: 20px; font-weight: 800; color: #0a0a0b; margin: 0; }
.table-card { background: white; border-radius: 14px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.table-thumb { width: 48px; height: 48px; object-fit: cover; border-radius: 8px; }
.no-image { width: 48px; height: 48px; background: #f4f4f5; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #71717a; }
.status-chip { font-size: 11px; padding: 4px 12px; border-radius: 9999px; font-weight: 700; background: #fee2e2; color: #ef4444; }
.status-chip.active { background: #ecfdf5; color: #059669; }
.dialog-card { width: 650px; max-width: 95vw; border-radius: 16px; }
.dialog-header { display: flex; align-items: center; justify-content: space-between; }
.dialog-header h3 { margin: 0; font-size: 16px; font-weight: 700; color: #0a0a0b; }
.dialog-form { display: flex; flex-direction: column; gap: 16px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.toggle-group { display: flex; gap: 16px; align-items: center; }
.image-upload label { display: block; font-size: 13px; font-weight: 700; color: #0a0a0b; margin-bottom: 8px; }
.rich-field { margin-bottom: 8px; }
.rich-field > label { display: block; font-size: 13px; font-weight: 700; color: #0a0a0b; margin-bottom: 8px; }
.upload-area { border: 2px dashed #cbd5e1; border-radius: 12px; padding: 24px; text-align: center; cursor: pointer; transition: border-color 0.2s; min-height: 140px; display: flex; align-items: center; justify-content: center; }
.upload-area:hover { border-color: #fed72b; }
.upload-preview { max-width: 200px; max-height: 120px; object-fit: contain; border-radius: 8px; }
.upload-placeholder { display: flex; flex-direction: column; align-items: center; gap: 8px; color: #7a83a1; }
.upload-hint { font-size: 11px; color: #aaa; }
.profile-image-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.dialog-actions { display: flex; justify-content: flex-start; gap: 12px; padding-top: 8px; }

@media (max-width: 900px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  .page-header .q-btn {
    align-self: flex-start;
  }
}

@media (max-width: 600px) {
  .page-header h3 {
    font-size: 15px;
  }
  .page-header .q-btn {
    font-size: 12px;
    padding: 6px 14px;
  }
  .table-card {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .table-card .q-table {
    min-width: 700px;
  }
  .table-thumb {
    width: 32px;
    height: 32px;
  }
  .no-image {
    width: 32px;
    height: 32px;
  }
  .form-row {
    grid-template-columns: 1fr;
  }
  .toggle-group {
    flex-direction: column;
    align-items: flex-start;
  }
  .dialog-actions {
    flex-direction: column;
  }
  .dialog-actions .q-btn {
    width: 100%;
  }
  .dialog-card {
    border-radius: 12px;
  }
}

/* Mobile card layout */
.mobile-card {
  background: white;
  border: 1px solid #e8ecf5;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 10px;
  width: 100%;
}
.mobile-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.mobile-card-thumb {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}
.mobile-card-thumb-placeholder {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: #F5EDE5;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ccc;
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
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mobile-card-category {
  font-size: 11px;
  color: #71717a;
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
  color: #aaa;
}
.mobile-card-actions {
  display: flex;
  gap: 2px;
}
.mobile-search {
  margin-left: 8px;
}

.image-manager-card {
  width: 700px;
  max-width: 95vw;
  border-radius: 16px;
}

.upload-zone {
  border: 2px dashed #d0d4ee;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #7a83a1;
  margin-bottom: 16px;
}

.upload-zone:hover {
  border-color: #fed72b;
  background: #fefce8;
}

.no-images {
  text-align: center;
  padding: 40px 20px;
  color: #aaa;
}

.no-images p {
  margin-top: 12px;
  font-size: 14px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.image-item {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  border: 2px solid #e8ecf5;
  aspect-ratio: 1;
  cursor: grab;
  transition: all 0.2s;
}

.image-item:active {
  cursor: grabbing;
}

.image-item:hover {
  border-color: #f5a300;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 4px;
  padding: 4px;
  background: rgba(0, 0, 0, 0.6);
  opacity: 0;
  transition: opacity 0.2s;
}

.image-item:hover .image-actions {
  opacity: 1;
}

.image-order {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 10px;
  font-weight: 700;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.video-item {
  position: relative;
  cursor: grab;
  border: 2px solid #e8ecf5;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
  transition: border-color 0.2s;
}

.video-item:active {
  cursor: grabbing;
}

.video-item:hover {
  border-color: #f5a300;
}

.video-preview {
  display: block;
  width: 100%;
  height: 130px;
  object-fit: contain;
  background: #000;
}

.video-item-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px;
}

.video-item-title {
  min-width: 0;
  font-size: 12px;
  font-weight: 600;
  color: #0a0a0b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.video-item-actions {
  display: flex;
  gap: 2px;
  flex-shrink: 0;
}

.image-view-card {
  width: 750px;
  max-width: 95vw;
  border-radius: 16px;
}

.image-view-body {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7ff;
  padding: 16px;
}

.image-view-body img {
  max-width: 100%;
  max-height: 75vh;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(26, 36, 114, 0.2);
}

@media (max-width: 768px) {
  .image-manager-card,
  .image-view-card {
    width: 100vw !important;
    max-width: 100vw !important;
    min-width: 0 !important;
    height: 100vh !important;
    max-height: 100vh !important;
    border-radius: 0 !important;
    margin: 0 !important;
  }

  .image-actions {
    opacity: 1;
    background: rgba(0, 0, 0, 0.7);
  }

  .video-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(95px, 1fr));
    gap: 8px;
  }

  .upload-zone {
    padding: 16px 12px;
  }

  .upload-zone span {
    font-size: 12px;
  }
}

@media (max-width: 320px) {
  .image-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
  }

  .upload-zone {
    padding: 12px 8px;
    margin-bottom: 10px;
  }

  .image-actions .q-btn {
    width: 26px;
    height: 26px;
    padding: 0;
  }
}
</style>

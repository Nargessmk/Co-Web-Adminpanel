<template>
  <div class="media-admin-page">
    <!-- 1. Header & Actions -->
    <div class="tech-page-header">
      <div class="header-info-group">
        <div class="header-section-tag">
          <span class="status-live-dot"></span>
          <span>مدیریت یکپارچه رسانه‌ها و دارایی‌ها</span>
        </div>
        <h1 class="header-main-title">کتابخانه رسانه‌ها و فایل‌ها</h1>
        <p class="header-sub-desc">
          مشاهده، جستجو، آپلود و مدیریت کلیه تصاویر، ویدیوها و اسناد آپلود شده در سامانه کهکشان هوشمند.
        </p>
      </div>

      <div class="header-actions-group">
        <button class="tech-action-btn primary" @click="openUploadDialog">
          <q-icon name="cloud_upload" size="18px" />
          <span>آپلود فایل جدید</span>
        </button>
        <button class="tech-action-btn secondary" :disabled="loading || isSyncing" @click="syncAllMedia" title="اسکن خودکار و همگام‌سازی تمام تصاویر، ویدیوها و گالری‌های محصولات">
          <q-icon name="sync" size="18px" :class="{ 'spin-icon': isSyncing }" />
          <span>اسکن و همگام‌سازی</span>
        </button>
        <button class="tech-action-btn secondary" :disabled="loading" @click="fetchMedia">
          <q-icon name="refresh" size="18px" :class="{ 'spin-icon': loading }" />
          <span>بروزرسانی</span>
        </button>
      </div>
    </div>

    <!-- 2. Stats Bento Cards -->
    <div class="stats-bento-grid">
      <div class="stat-card">
        <div class="stat-icon-bubble yellow">
          <q-icon name="folder_zip" size="24px" />
        </div>
        <div class="stat-meta">
          <span class="stat-title">کل رسانه‌ها و فایل‌ها</span>
          <div class="stat-value-row">
            <span class="stat-number">{{ stats.total_files }}</span>
            <span class="stat-unit">فایل ({{ stats.total_size_formatted }})</span>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-bubble green">
          <q-icon name="image" size="24px" />
        </div>
        <div class="stat-meta">
          <span class="stat-title">تصاویر و گرافیک‌ها</span>
          <div class="stat-value-row">
            <span class="stat-number">{{ stats.total_images }}</span>
            <span class="stat-unit">تصویر ثبت‌شده</span>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-bubble purple">
          <q-icon name="smart_display" size="24px" />
        </div>
        <div class="stat-meta">
          <span class="stat-title">ویدیوهای بارگذاری‌شده</span>
          <div class="stat-value-row">
            <span class="stat-number">{{ stats.total_videos }}</span>
            <span class="stat-unit">ویدیو</span>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-bubble blue">
          <q-icon name="description" size="24px" />
        </div>
        <div class="stat-meta">
          <span class="stat-title">اسناد، کاتالوگ و پیوست‌ها</span>
          <div class="stat-value-row">
            <span class="stat-number">{{ stats.total_documents }}</span>
            <span class="stat-unit">سند و فایل</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Filter Controls & Toolbar -->
    <div class="media-toolbar-card">
      <div class="type-filter-pills">
        <button
          v-for="t in typeFilters"
          :key="t.key"
          type="button"
          class="filter-pill-btn"
          :class="{ active: activeType === t.key }"
          @click="setTypeFilter(t.key)"
        >
          <q-icon :name="t.icon" size="16px" />
          <span>{{ t.label }}</span>
          <span v-if="t.count !== undefined" class="pill-count">{{ t.count }}</span>
        </button>
      </div>

      <!-- Folder Filter Pills -->
      <div class="folder-filter-pills">
        <button
          v-for="f in folderFilters"
          :key="f.key"
          type="button"
          class="filter-pill-btn folder-pill-btn"
          :class="{ active: activeFolder === f.key }"
          @click="setFolderFilter(f.key)"
        >
          <q-icon :name="f.icon" size="14px" />
          <span>{{ f.label }}</span>
        </button>
      </div>

      <div class="search-and-view-controls">
        <div class="search-box-wrap">
          <q-icon name="search" size="18px" class="search-ico" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="جستجو بر اساس نام فایل..."
            class="search-input-field"
            @input="onSearchInput"
          />
          <button v-if="searchQuery" class="clear-search-btn" @click="clearSearch">✕</button>
        </div>

        <!-- Optimization and Multi-select Action Buttons in Toolbar -->
        <div class="toolbar-opt-actions">
          <button
            type="button"
            class="tech-tool-btn select-all-btn"
            :class="{ active: isAllSelected }"
            @click="toggleSelectAll"
            title="انتخاب یا لغو انتخاب تمام فایل‌های صفحه جاری"
          >
            <q-icon :name="isAllSelected ? 'check_box' : (selectedMediaIds.length > 0 ? 'indeterminate_check_box' : 'check_box_outline_blank')" size="16px" />
            <span>{{ isAllSelected ? 'لغو انتخاب همه' : 'انتخاب همه' }}</span>
            <span v-if="selectedMediaIds.length > 0" class="tool-count-pill">{{ selectedMediaIds.length }}</span>
          </button>

          <button
            type="button"
            class="tech-tool-btn opt-webp"
            :disabled="isProcessing || selectedImageCount === 0"
            @click="batchConvertToWebp"
            title="تبدیل تصاویر انتخاب‌شده به فرمت سبک WebP"
          >
            <q-icon name="auto_awesome" size="16px" :class="{ 'spin-icon': isProcessing }" />
            <span>تبدیل به WebP</span>
            <span v-if="selectedImageCount > 0" class="tool-count-pill">{{ selectedImageCount }}</span>
          </button>

          <button
            type="button"
            class="tech-tool-btn opt-compress"
            :disabled="isProcessing || selectedImageCount === 0"
            @click="batchCompressImages"
            title="فشرده‌سازی حجم تصاویر بدون افت کیفیت دیداری"
          >
            <q-icon name="compress" size="16px" :class="{ 'spin-icon': isProcessing }" />
            <span>فشرده‌سازی حجم تصاویر</span>
            <span v-if="selectedImageCount > 0" class="tool-count-pill">{{ selectedImageCount }}</span>
          </button>
        </div>

        <div class="view-mode-toggle">
          <button
            type="button"
            class="view-btn"
            :class="{ active: viewMode === 'grid' }"
            title="نمایش شبکه‌ای"
            @click="viewMode = 'grid'"
          >
            <q-icon name="grid_view" size="18px" />
          </button>
          <button
            type="button"
            class="view-btn"
            :class="{ active: viewMode === 'table' }"
            title="نمایش جدولی"
            @click="viewMode = 'table'"
          >
            <q-icon name="format_list_bulleted" size="18px" />
          </button>
        </div>
      </div>
    </div>

    <!-- Floating / Sticky Selection Dock for Batch Actions -->
    <transition name="dock-slide">
      <div v-if="selectedMediaIds.length > 0" class="batch-selection-dock">
        <div class="dock-badge-summary">
          <q-icon name="check_circle" size="20px" color="amber-7" />
          <span>{{ selectedMediaIds.length }} مورد انتخاب‌شده ({{ selectedImageCount }} تصویر)</span>
        </div>

        <div class="dock-actions-row">
          <button
            type="button"
            class="dock-btn webp"
            :disabled="isProcessing || selectedImageCount === 0"
            @click="batchConvertToWebp"
          >
            <q-icon name="auto_awesome" size="16px" :class="{ 'spin-icon': isProcessing }" />
            <span>تبدیل {{ selectedImageCount }} تصویر به WebP</span>
          </button>

          <button
            type="button"
            class="dock-btn compress"
            :disabled="isProcessing || selectedImageCount === 0"
            @click="batchCompressImages"
          >
            <q-icon name="compress" size="16px" :class="{ 'spin-icon': isProcessing }" />
            <span>فشرده‌سازی حجم {{ selectedImageCount }} تصویر</span>
          </button>

          <button
            type="button"
            class="dock-btn delete-batch"
            :disabled="isProcessing"
            @click="batchDeleteMedia"
          >
            <q-icon name="delete" size="16px" />
            <span>حذف گروهی ({{ selectedMediaIds.length }})</span>
          </button>

          <button
            type="button"
            class="dock-btn cancel"
            @click="clearSelection"
          >
            <q-icon name="close" size="16px" />
            <span>لغو انتخاب</span>
          </button>
        </div>
      </div>
    </transition>

    <!-- 4. Content Area -->
    <div class="media-content-container">
      <!-- Loading Skeleton -->
      <div v-if="loading && mediaList.length === 0" class="media-grid-layout">
        <div v-for="n in 8" :key="n" class="skeleton-media-card">
          <div class="skeleton-thumb"></div>
          <div class="skeleton-meta">
            <div class="sk-line w-80"></div>
            <div class="sk-line w-40"></div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="mediaList.length === 0" class="empty-media-card">
        <q-icon name="folder_open" size="64px" color="grey-5" />
        <h3>هیچ فایلی یافت نشد</h3>
        <p>فایلی با این مشخصات یا در این دسته‌بندی وجود ندارد. می‌توانید فایل جدید آپلود کنید.</p>
        <button class="tech-action-btn primary" @click="openUploadDialog">
          <q-icon name="cloud_upload" size="16px" />
          <span>آپلود اولین فایل</span>
        </button>
      </div>

      <!-- A. Grid View -->
      <div v-else-if="viewMode === 'grid'" class="media-grid-layout">
        <div
          v-for="item in mediaList"
          :key="item.id"
          class="media-card"
          :class="{ 'is-selected': selectedMediaIds.includes(item.id) }"
          @click="openPreview(item)"
        >
          <!-- Thumbnail Frame -->
          <div class="media-thumb-box">
            <!-- Multi-select checkbox overlay for all media items -->
            <div
              class="card-select-trigger"
              :class="{ selected: selectedMediaIds.includes(item.id) }"
              @click.stop="toggleSelect(item.id)"
              title="انتخاب مورد"
            >
              <q-icon :name="selectedMediaIds.includes(item.id) ? 'check_box' : 'check_box_outline_blank'" size="20px" />
            </div>

            <!-- Image Thumbnail -->
            <img
              v-if="item.file_type === 'image'"
              :src="formatMediaUrl(item.url)"
              :alt="item.original_name"
              loading="lazy"
              class="media-thumb-img"
              @error="e => handleImageError(e)"
            />

            <!-- Video Thumbnail / Icon -->
            <div v-else-if="item.file_type === 'video'" class="media-type-placeholder video-bg">
              <q-icon name="movie" size="48px" color="deep-purple-3" />
              <span class="video-play-tag">
                <q-icon name="play_arrow" size="16px" />
                <span>ویدیو</span>
              </span>
            </div>

            <!-- Document / File Thumbnail -->
            <div v-else class="media-type-placeholder doc-bg">
              <q-icon :name="getDocIcon(item.filename)" size="48px" :color="getDocColor(item.filename)" />
              <span class="doc-ext-badge">{{ getExtension(item.filename) }}</span>
            </div>

            <!-- Top Overlay Badges -->
            <div class="thumb-top-badges">
              <span class="media-type-pill" :class="item.file_type">
                {{ getTypeLabel(item.file_type) }}
              </span>
              <span class="media-size-pill">{{ item.file_size_formatted }}</span>
            </div>

            <!-- Quick Action Hover Bar -->
            <div class="thumb-hover-actions" @click.stop>
              <button
                v-if="item.file_type === 'image' && !item.filename.toLowerCase().endsWith('.webp')"
                class="hover-action-btn opt-webp-btn"
                title="تبدیل به WebP"
                @click="singleConvertToWebp(item)"
              >
                <q-icon name="auto_awesome" size="15px" />
              </button>
              <button
                v-if="item.file_type === 'image'"
                class="hover-action-btn opt-comp-btn"
                title="فشرده‌سازی حجم بدون افت کیفیت"
                @click="singleCompress(item)"
              >
                <q-icon name="compress" size="15px" />
              </button>
              <button class="hover-action-btn" title="کپی لینک مستقیم" @click="copyUrl(item.url)">
                <q-icon name="content_copy" size="16px" />
              </button>
              <button class="hover-action-btn" title="پیش‌نمایش کامل" @click="openPreview(item)">
                <q-icon name="visibility" size="16px" />
              </button>
              <a :href="item.url" target="_blank" download class="hover-action-btn" title="دانلود فایل">
                <q-icon name="download" size="16px" />
              </a>
              <button class="hover-action-btn delete" title="حذف فایل" @click="confirmDelete(item)">
                <q-icon name="delete" size="16px" />
              </button>
            </div>
          </div>

          <!-- Media Info Details -->
          <div class="media-info-box">
            <h4 class="media-name" :title="item.original_name || item.filename">
              {{ item.original_name || item.filename }}
            </h4>
            <div class="media-sub-meta">
              <span class="media-date">{{ formatDate(item.created_at) }}</span>
              <span class="media-folder-tag" v-if="item.folder">{{ item.folder }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- B. Table View -->
      <div v-else class="media-table-card">
        <table class="tech-media-table">
          <thead>
            <tr>
              <th style="width: 44px; text-align: center;">
                <input
                  type="checkbox"
                  :checked="isAllSelected"
                  @change="toggleSelectAll"
                  title="انتخاب همه تصاویر"
                />
              </th>
              <th style="width: 70px;">پیش‌نمایش</th>
              <th>نام فایل</th>
              <th style="width: 110px;">نوع رسانه</th>
              <th style="width: 110px;">حجم</th>
              <th style="width: 110px;">پوشه</th>
              <th style="width: 140px;">تاریخ بارگذاری</th>
              <th style="width: 200px;">عملیات</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in mediaList"
              :key="item.id"
              :class="{ 'table-row-selected': selectedMediaIds.includes(item.id) }"
            >
              <td style="text-align: center;" @click.stop>
                <input
                  type="checkbox"
                  :checked="selectedMediaIds.includes(item.id)"
                  @change="toggleSelect(item.id)"
                />
              </td>
              <td>
                <div class="table-thumb-box" @click="openPreview(item)">
                  <img v-if="item.file_type === 'image'" :src="formatMediaUrl(item.url)" alt="" @error="e => handleImageError(e)" />
                  <q-icon v-else-if="item.file_type === 'video'" name="movie" size="22px" color="deep-purple" />
                  <q-icon v-else :name="getDocIcon(item.filename)" size="22px" :color="getDocColor(item.filename)" />
                </div>
              </td>
              <td>
                <div class="table-filename-cell">
                  <span class="name-main" :title="item.original_name || item.filename">
                    {{ item.original_name || item.filename }}
                  </span>
                  <span class="name-sub">{{ item.filename }}</span>
                </div>
              </td>
              <td>
                <span class="media-type-pill" :class="item.file_type">
                  {{ getTypeLabel(item.file_type) }}
                </span>
              </td>
              <td>
                <span class="table-size-text">{{ item.file_size_formatted }}</span>
              </td>
              <td>
                <span class="media-folder-tag">{{ item.folder || 'general' }}</span>
              </td>
              <td>
                <span class="table-date-text">{{ formatDate(item.created_at) }}</span>
              </td>
              <td>
                <div class="table-actions-cell">
                  <button
                    v-if="item.file_type === 'image' && !item.filename.toLowerCase().endsWith('.webp')"
                    class="tbl-btn opt-webp"
                    title="تبدیل به WebP"
                    @click="singleConvertToWebp(item)"
                  >
                    <q-icon name="auto_awesome" size="14px" />
                  </button>
                  <button
                    v-if="item.file_type === 'image'"
                    class="tbl-btn opt-compress"
                    title="فشرده‌سازی حجم بدون افت کیفیت"
                    @click="singleCompress(item)"
                  >
                    <q-icon name="compress" size="14px" />
                  </button>
                  <button class="tbl-btn" title="کپی لینک" @click="copyUrl(item.url)">
                    <q-icon name="content_copy" size="15px" />
                  </button>
                  <button class="tbl-btn" title="پیش‌نمایش" @click="openPreview(item)">
                    <q-icon name="visibility" size="15px" />
                  </button>
                  <a :href="item.url" target="_blank" download class="tbl-btn" title="دانلود">
                    <q-icon name="download" size="15px" />
                  </a>
                  <button class="tbl-btn delete" title="حذف" @click="confirmDelete(item)">
                    <q-icon name="delete" size="15px" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 5. Pagination Bar with Page Size Selector -->
      <div v-if="pagination.total > 0" class="media-pagination-bar">
        <div class="pagination-page-size-wrap">
          <span class="page-size-label">تعداد در هر صفحه:</span>
          <div class="page-size-options">
            <button
              v-for="size in [12, 24, 48, 96]"
              :key="size"
              type="button"
              class="page-size-btn"
              :class="{ active: pagination.limit === size }"
              @click="changePageSize(size)"
            >
              {{ size }}
            </button>
          </div>
        </div>

        <div class="pagination-nav-wrap">
          <button
            class="page-nav-btn"
            :disabled="pagination.page <= 1"
            @click="goToPage(pagination.page - 1)"
          >
            <q-icon name="chevron_right" size="18px" />
            <span>قبلی</span>
          </button>

          <div class="pagination-pages-pills">
            <button
              v-for="p in visiblePages"
              :key="p"
              type="button"
              class="page-num-pill"
              :class="{ active: pagination.page === p, ellipsis: p === '...' }"
              :disabled="p === '...'"
              @click="p !== '...' && goToPage(p)"
            >
              {{ p }}
            </button>
          </div>

          <button
            class="page-nav-btn"
            :disabled="pagination.page >= pagination.totalPages"
            @click="goToPage(pagination.page + 1)"
          >
            <span>بعدی</span>
            <q-icon name="chevron_left" size="18px" />
          </button>
        </div>

        <span class="page-current-indicator">
          صفحه {{ pagination.page }} از {{ pagination.totalPages || 1 }} (مجموعاً {{ pagination.total }} فایل)
        </span>
      </div>
    </div>

    <!-- 6. Upload Modal Dialog -->
    <q-dialog v-model="uploadDialogOpen" persistent>
      <q-card class="upload-dialog-card">
        <q-card-section class="dialog-head-row">
          <div class="title-wrap">
            <q-icon name="cloud_upload" size="24px" color="amber-9" />
            <span class="text-h6 text-weight-bold">آپلود رسانه جدید</span>
          </div>
          <q-btn flat round dense icon="close" v-close-popup :disable="uploading" />
        </q-card-section>

        <q-separator />

        <q-card-section class="q-pa-lg">
          <!-- Dropzone -->
          <div
            class="modal-dropzone"
            :class="{ 'is-drag-over': isDragging }"
            @click="$refs.dialogFileInput.click()"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="onDropFiles"
          >
            <input
              ref="dialogFileInput"
              type="file"
              multiple
              style="display: none;"
              @change="onDialogFilesSelected"
            />
            <q-icon name="upload_file" size="52px" color="amber-9" />
            <span class="dropzone-text-bold">فایل‌ها را اینجا رها کنید یا برای انتخاب کلیک کنید</span>
            <span class="dropzone-text-sub">
              پشتیبانی از انواع تصاویر (PNG, JPG, WebP, SVG, GIF)، ویدیوها (MP4, WebM) و اسناد (PDF, ZIP, DOCX)
            </span>
          </div>

          <!-- Target folder selector -->
          <div class="q-mt-md row items-center q-gutter-sm">
            <span class="text-caption text-grey-8 text-weight-bold">پوشه ذخیره‌سازی:</span>
            <q-radio v-model="uploadFolder" val="general" label="عمومی (general)" dense />
            <q-radio v-model="uploadFolder" val="products" label="محصولات (products)" dense />
            <q-radio v-model="uploadFolder" val="catalogs" label="کاتالوگ‌ها (catalogs)" dense />
          </div>

          <!-- Staged files list -->
          <div v-if="stagedFiles.length > 0" class="staged-files-list q-mt-md">
            <div class="staged-head">فایل‌های انتخاب‌شده ({{ stagedFiles.length }} فایل):</div>
            <div v-for="(file, idx) in stagedFiles" :key="idx" class="staged-file-item">
              <div class="staged-info">
                <q-icon :name="getFileIcon(file.name)" size="18px" />
                <span class="staged-name">{{ file.name }}</span>
                <span class="staged-size">{{ formatSize(file.size) }}</span>
              </div>
              <button class="remove-staged-btn" :disabled="uploading" @click.stop="removeStagedFile(idx)">✕</button>
            </div>
          </div>

          <!-- Progress -->
          <div v-if="uploading" class="q-mt-lg">
            <q-linear-progress indeterminate color="amber-9" class="q-mb-xs" />
            <div class="text-caption text-center text-grey-8">
              در حال ذخیره‌سازی و پردازش فایل‌ها ({{ uploadProgressText }})...
            </div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-actions align="between" class="q-pa-md">
          <q-btn flat label="انصراف" v-close-popup :disable="uploading" />
          <q-btn
            unelevated
            color="dark"
            label="شروع آپلود فایل‌ها"
            icon="cloud_upload"
            :loading="uploading"
            :disable="stagedFiles.length === 0"
            @click="submitUpload"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- 7. Media Preview & Details Modal -->
    <q-dialog v-model="previewDialogOpen">
      <q-card v-if="selectedPreviewItem" class="preview-dialog-card">
        <q-card-section class="preview-head">
          <div class="title-wrap">
            <q-icon :name="selectedPreviewItem.file_type === 'image' ? 'image' : (selectedPreviewItem.file_type === 'video' ? 'movie' : 'description')" size="22px" />
            <span class="text-subtitle1 text-weight-bold ellipsis" style="max-width: 450px;">
              {{ selectedPreviewItem.original_name || selectedPreviewItem.filename }}
            </span>
          </div>
          <q-btn flat round dense icon="close" v-close-popup />
        </q-card-section>

        <q-card-section class="preview-body">
          <div class="preview-visual-box">
            <!-- Full Image Preview -->
            <img
              v-if="selectedPreviewItem.file_type === 'image'"
              :src="formatMediaUrl(selectedPreviewItem.url)"
              :alt="selectedPreviewItem.original_name"
              class="full-preview-img"
              @error="e => handleImageError(e)"
            />

            <!-- Video Player -->
            <video
              v-else-if="selectedPreviewItem.file_type === 'video'"
              controls
              autoplay
              class="full-preview-video"
            >
              <source :src="formatMediaUrl(selectedPreviewItem.url)" :type="selectedPreviewItem.mimetype || 'video/mp4'" />
              مرورگر شما از پخش مستقیم این ویدیو پشتیبانی نمی‌کند.
            </video>

            <!-- Doc Download Prompt -->
            <div v-else class="full-preview-doc">
              <q-icon :name="getDocIcon(selectedPreviewItem.filename)" size="72px" :color="getDocColor(selectedPreviewItem.filename)" />
              <h4 class="q-my-sm">{{ selectedPreviewItem.filename }}</h4>
              <p class="text-caption text-grey-6">برای باز کردن یا مشاهده این سند می‌توانید از دکمه زیر استفاده کنید.</p>
              <a :href="selectedPreviewItem.url" target="_blank" class="tech-action-btn primary q-mt-sm">
                <q-icon name="open_in_new" size="16px" />
                <span>باز کردن در برگه جدید</span>
              </a>
            </div>
          </div>

          <!-- Metadata table -->
          <div class="preview-details-box">
            <div class="detail-row">
              <span class="lbl">نام اصلی:</span>
              <span class="val">{{ selectedPreviewItem.original_name || '-' }}</span>
            </div>
            <div class="detail-row">
              <span class="lbl">نام فایل در سرور:</span>
              <span class="val font-mono">{{ selectedPreviewItem.filename }}</span>
            </div>
            <div class="detail-row">
              <span class="lbl">حجم فایل:</span>
              <span class="val">{{ selectedPreviewItem.file_size_formatted }} ({{ selectedPreviewItem.file_size }} بایت)</span>
            </div>
            <div class="detail-row">
              <span class="lbl">نوع پرونده:</span>
              <span class="val">{{ selectedPreviewItem.mimetype || '-' }}</span>
            </div>
            <div class="detail-row">
              <span class="lbl">پوشه:</span>
              <span class="val">{{ selectedPreviewItem.folder || 'general' }}</span>
            </div>
            <div class="detail-row">
              <span class="lbl">تاریخ بارگذاری:</span>
              <span class="val">{{ formatDate(selectedPreviewItem.created_at) }}</span>
            </div>
            <div class="detail-row url-row">
              <span class="lbl">آدرس عمومی (URL):</span>
              <div class="url-copy-box">
                <input type="text" readonly :value="selectedPreviewItem.url" class="url-input" />
                <button class="copy-btn" @click="copyUrl(selectedPreviewItem.url)">
                  <q-icon name="content_copy" size="14px" />
                  <span>کپی</span>
                </button>
              </div>
            </div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-actions align="between" class="q-pa-md">
          <button class="tech-action-btn danger-outline" @click="confirmDelete(selectedPreviewItem)">
            <q-icon name="delete" size="16px" />
            <span>حذف فایل از سرور</span>
          </button>

          <div class="row q-gutter-sm items-center">
            <button
              v-if="selectedPreviewItem?.file_type === 'image' && !selectedPreviewItem?.filename?.toLowerCase()?.endsWith('.webp')"
              class="tech-action-btn warning-soft"
              :disabled="isProcessing"
              @click="singleConvertToWebp(selectedPreviewItem)"
              title="تبدیل این تصویر به فرمت نسل جدید WebP"
            >
              <q-icon name="auto_awesome" size="16px" :class="{ 'spin-icon': isProcessing }" />
              <span>تبدیل به WebP</span>
            </button>
            <button
              v-if="selectedPreviewItem?.file_type === 'image'"
              class="tech-action-btn success-soft"
              :disabled="isProcessing"
              @click="singleCompress(selectedPreviewItem)"
              title="فشرده‌سازی هوشمند بدون افت کیفیت دیداری"
            >
              <q-icon name="compress" size="16px" :class="{ 'spin-icon': isProcessing }" />
              <span>فشرده‌سازی حجم</span>
            </button>
            <a :href="selectedPreviewItem.url" target="_blank" download class="tech-action-btn secondary">
              <q-icon name="download" size="16px" />
              <span>دانلود فایل</span>
            </a>
            <button class="tech-action-btn primary" @click="copyUrl(selectedPreviewItem.url)">
              <q-icon name="link" size="16px" />
              <span>کپی لینک مستقیم</span>
            </button>
          </div>
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { formatMediaUrl, handleImageError } from 'src/utils/media'
import api from 'src/services/api'

const $q = useQuasar()

// State
const loading = ref(false)
const mediaList = ref([])
const activeType = ref('all')
const activeFolder = ref('all')
const searchQuery = ref('')
const viewMode = ref('grid') // 'grid' | 'table'

// Selection & Image Optimization State
const selectedMediaIds = ref([])
const isProcessing = ref(false)
const isSyncing = ref(false)

const selectedImageCount = computed(() => {
  return mediaList.value.filter(m => selectedMediaIds.value.includes(m.id) && m.file_type === 'image').length
})

const isAllSelected = computed(() => {
  if (mediaList.value.length === 0) return false
  return mediaList.value.every(m => selectedMediaIds.value.includes(m.id))
})

function toggleSelect (id) {
  const idx = selectedMediaIds.value.indexOf(id)
  if (idx > -1) {
    selectedMediaIds.value.splice(idx, 1)
  } else {
    selectedMediaIds.value.push(id)
  }
}

function toggleSelectAll () {
  if (mediaList.value.length === 0) return
  if (isAllSelected.value) {
    const pageIds = mediaList.value.map(m => m.id)
    selectedMediaIds.value = selectedMediaIds.value.filter(id => !pageIds.includes(id))
  } else {
    mediaList.value.forEach(m => {
      if (!selectedMediaIds.value.includes(m.id)) {
        selectedMediaIds.value.push(m.id)
      }
    })
  }
}

function clearSelection () {
  selectedMediaIds.value = []
}

async function batchDeleteMedia () {
  if (selectedMediaIds.value.length === 0) return
  const count = selectedMediaIds.value.length
  $q.dialog({
    title: 'حذف گروهی فایل‌ها',
    message: `آیا از حذف دائم ${count} فایل انتخاب‌شده اطمینان دارید؟ این عملیات قابل بازگشت نیست.`,
    cancel: { label: 'انصراف', flat: true },
    ok: { label: `بله، ${count} فایل حذف شود`, color: 'negative', unelevated: true },
    persistent: true,
  }).onOk(async () => {
    isProcessing.value = true
    try {
      const res = await api.post('/api/media/batch-delete', { ids: selectedMediaIds.value })
      const payload = res.data?.data || res.data
      $q.notify({
        type: 'positive',
        message: `${payload.deleted_count || count} فایل با موفقیت حذف شدند.`,
        position: 'top',
      })
      selectedMediaIds.value = []
      await fetchMedia()
    } catch (err) {
      $q.notify({
        type: 'negative',
        message: 'خطا در حذف گروهی فایل‌ها: ' + (err.response?.data?.message || err.message),
        position: 'top',
      })
    } finally {
      isProcessing.value = false
    }
  })
}

async function batchConvertToWebp () {
  const targetIds = selectedMediaIds.value.filter(id => {
    const item = mediaList.value.find(m => m.id === id)
    return item && item.file_type === 'image'
  })
  if (targetIds.length === 0) {
    $q.notify({
      type: 'warning',
      message: 'لطفاً حداقل یک تصویر را برای تبدیل به WebP انتخاب کنید.',
      position: 'top',
    })
    return
  }

  isProcessing.value = true
  try {
    const res = await api.post('/api/media/convert-webp', { ids: targetIds }, { timeout: 120000 })
    const payload = res.data?.data || res.data
    const converted_count = payload.converted_count ?? (payload.items ? payload.items.length : 0)
    const total_saved_bytes = payload.total_saved_bytes ?? 0

    if (converted_count > 0) {
      $q.notify({
        type: 'positive',
        message: `${converted_count} تصویر با موفقیت به فرمت سبک WebP تبدیل و جایگزین شدند. صرفه‌جویی: ${formatSize(total_saved_bytes)}`,
        icon: 'auto_awesome',
        position: 'top',
        timeout: 4000,
      })
    } else if (payload.already_webp) {
      $q.notify({
        type: 'info',
        message: 'تصاویر انتخاب‌شده در حال حاضر با فرمت بهینه WebP هستند.',
        icon: 'check_circle',
        position: 'top',
        timeout: 3500,
      })
    } else {
      $q.notify({
        type: 'warning',
        message: res.data?.message || 'تصویری تبدیل نشد یا عملیات با خطا مواجه شد.',
        icon: 'warning',
        position: 'top',
        timeout: 4000,
      })
    }
    selectedMediaIds.value = []
    await fetchMedia()
    if (selectedPreviewItem.value) {
      const updated = mediaList.value.find(m => m.id === selectedPreviewItem.value.id)
      if (updated) {
        selectedPreviewItem.value = { ...updated, url: (updated.url || '') + (updated.url?.includes('?') ? '&' : '?') + 't=' + Date.now() }
      }
    }
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: 'خطا در تبدیل تصاویر به WebP: ' + (err.response?.data?.message || err.response?.data?.detail || err.message),
      position: 'top',
      timeout: 5000,
    })
  } finally {
    isProcessing.value = false
  }
}

async function batchCompressImages () {
  const targetIds = selectedMediaIds.value.filter(id => {
    const item = mediaList.value.find(m => m.id === id)
    return item && item.file_type === 'image'
  })
  if (targetIds.length === 0) {
    $q.notify({
      type: 'warning',
      message: 'لطفاً حداقل یک تصویر را برای فشرده‌سازی انتخاب کنید.',
      position: 'top',
    })
    return
  }

  isProcessing.value = true
  try {
    const res = await api.post('/api/media/compress', { ids: targetIds }, { timeout: 120000 })
    const payload = res.data?.data || res.data
    const total_saved_bytes = payload.total_saved_bytes ?? 0
    const compressed_count = payload.compressed_count ?? targetIds.length

    if (total_saved_bytes > 0) {
      $q.notify({
        type: 'positive',
        message: `${compressed_count} تصویر بدون افت کیفیت فشرده‌سازی شدند. صرفه‌جویی در حجم: ${formatSize(total_saved_bytes)}`,
        icon: 'compress',
        position: 'top',
        timeout: 4000,
      })
    } else {
      $q.notify({
        type: 'info',
        message: 'تصاویر انتخاب‌شده قبلاً در بهینه‌ترین وضعیت ذخیره شده‌اند.',
        icon: 'check',
        position: 'top',
      })
    }
    selectedMediaIds.value = []
    await fetchMedia()
    if (selectedPreviewItem.value) {
      const updated = mediaList.value.find(m => m.id === selectedPreviewItem.value.id)
      if (updated) selectedPreviewItem.value = updated
    }
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: 'خطا در فشرده‌سازی تصاویر: ' + (err.response?.data?.detail || err.message),
      position: 'top',
    })
  } finally {
    isProcessing.value = false
  }
}

async function singleConvertToWebp (item) {
  if (!item || item.file_type !== 'image') return
  isProcessing.value = true
  try {
    const res = await api.post('/api/media/convert-webp', { ids: [item.id] }, { timeout: 120000 })
    const payload = res.data?.data || res.data
    const count = payload.converted_count ?? (payload.items ? payload.items.length : 0)
    const total_saved_bytes = payload.total_saved_bytes ?? 0

    if (count > 0) {
      $q.notify({
        type: 'positive',
        message: `تصویر "${item.original_name || item.filename}" با موفقیت به WebP تبدیل و جایگزین شد. صرفه‌جویی: ${formatSize(total_saved_bytes)}`,
        icon: 'auto_awesome',
        position: 'top',
        timeout: 4000,
      })
    } else if (payload.already_webp) {
      $q.notify({
        type: 'info',
        message: `تصویر "${item.original_name || item.filename}" در حال حاضر با فرمت بهینه WebP است.`,
        icon: 'check_circle',
        position: 'top',
        timeout: 3500,
      })
    } else {
      $q.notify({
        type: 'warning',
        message: res.data?.message || 'تبدیل تصویر انجام نشد یا قبلاً تبدیل شده است.',
        icon: 'warning',
        position: 'top',
        timeout: 4000,
      })
    }

    await fetchMedia()
    if (selectedPreviewItem.value?.id === item.id) {
      const updated = mediaList.value.find(m => m.id === item.id)
      if (updated) {
        selectedPreviewItem.value = { ...updated, url: (updated.url || '') + (updated.url?.includes('?') ? '&' : '?') + 't=' + Date.now() }
      }
    }
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: 'خطا در تبدیل تصویر: ' + (err.response?.data?.message || err.response?.data?.detail || err.message),
      position: 'top',
      timeout: 5000,
    })
  } finally {
    isProcessing.value = false
  }
}

async function singleCompress (item) {
  if (!item || item.file_type !== 'image') return
  isProcessing.value = true
  try {
    const res = await api.post('/api/media/compress', { ids: [item.id] }, { timeout: 120000 })
    const payload = res.data?.data || res.data
    const total_saved_bytes = payload.total_saved_bytes ?? 0

    if (total_saved_bytes > 0) {
      $q.notify({
        type: 'positive',
        message: `تصویر "${item.original_name || item.filename}" بدون افت کیفیت فشرده شد. صرفه‌جویی: ${formatSize(total_saved_bytes)}`,
        icon: 'compress',
        position: 'top',
      })
    } else {
      $q.notify({
        type: 'info',
        message: 'این تصویر قبلاً در بالاترین سطح بهینه‌سازی ذخیره شده است.',
        position: 'top',
      })
    }
    await fetchMedia()
    if (selectedPreviewItem.value?.id === item.id) {
      const updated = mediaList.value.find(m => m.id === item.id)
      if (updated) selectedPreviewItem.value = updated
    }
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: 'خطا در فشرده‌سازی تصویر: ' + (err.response?.data?.detail || err.message),
      position: 'top',
    })
  } finally {
    isProcessing.value = false
  }
}

const stats = reactive({
  total_files: 0,
  total_images: 0,
  total_videos: 0,
  total_documents: 0,
  total_size_bytes: 0,
  total_size_formatted: '۰ بایت',
})

const pagination = reactive({
  page: 1,
  limit: 24,
  total: 0,
  totalPages: 0,
})

const visiblePages = computed(() => {
  const total = pagination.totalPages || 1
  const current = pagination.page
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }
  const pages = []
  if (current <= 4) {
    for (let i = 1; i <= 5; i++) pages.push(i)
    pages.push('...')
    pages.push(total)
  } else if (current >= total - 3) {
    pages.push(1)
    pages.push('...')
    for (let i = total - 4; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    pages.push('...')
    pages.push(current - 1)
    pages.push(current)
    pages.push(current + 1)
    pages.push('...')
    pages.push(total)
  }
  return pages
})

function changePageSize (size) {
  if (pagination.limit === size) return
  pagination.limit = size
  pagination.page = 1
  fetchMedia()
}

const typeFilters = computed(() => [
  { key: 'all', label: 'همه فایل‌ها', icon: 'all_inclusive', count: stats.total_files },
  { key: 'image', label: 'تصاویر', icon: 'image', count: stats.total_images },
  { key: 'video', label: 'ویدیوها', icon: 'smart_display', count: stats.total_videos },
  { key: 'document', label: 'اسناد و کاتالوگ', icon: 'description', count: stats.total_documents },
])

const folderFilters = computed(() => [
  { key: 'all', label: 'همه پوشه‌ها', icon: 'folder_open' },
  { key: 'products', label: 'محصولات و گالری', icon: 'inventory_2' },
  { key: 'catalogs', label: 'کاتالوگ‌ها و اسناد', icon: 'folder' },
  { key: 'articles', label: 'مقالات و وبلاگ', icon: 'article' },
  { key: 'team', label: 'اعضای تیم', icon: 'groups' },
  { key: 'home', label: 'صفحه اصلی و تماس', icon: 'home' },
  { key: 'icons3d', label: 'آیکون‌های سه‌بعدی', icon: 'token' },
  { key: 'general', label: 'عمومی و لوگو', icon: 'category' },
])

// Upload Dialog State
const uploadDialogOpen = ref(false)
const uploading = ref(false)
const isDragging = ref(false)
const uploadFolder = ref('general')
const stagedFiles = ref([])
const uploadProgressText = ref('')

// Preview Dialog State
const previewDialogOpen = ref(false)
const selectedPreviewItem = ref(null)

// Search debounce
let searchTimer = null
function onSearchInput () {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    pagination.page = 1
    fetchMedia()
  }, 350)
}

function clearSearch () {
  searchQuery.value = ''
  pagination.page = 1
  fetchMedia()
}

function setTypeFilter (type) {
  if (activeType.value === type) return
  activeType.value = type
  pagination.page = 1
  fetchMedia()
}

function setFolderFilter (folder) {
  if (activeFolder.value === folder) return
  activeFolder.value = folder
  pagination.page = 1
  fetchMedia()
}

function goToPage (p) {
  if (p < 1 || p > pagination.totalPages) return
  pagination.page = p
  fetchMedia()
  window.scrollTo({ top: 100, behavior: 'smooth' })
}

async function fetchMedia () {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      limit: pagination.limit,
    }
    if (activeType.value && activeType.value !== 'all') {
      params.type = activeType.value
    }
    if (activeFolder.value && activeFolder.value !== 'all') {
      params.folder = activeFolder.value
    }
    if (searchQuery.value && searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }

    const response = await api.get('/api/media', { params })
    const body = response.data

    mediaList.value = body.data || []
    if (body.pagination) {
      pagination.page = body.pagination.page
      pagination.limit = body.pagination.limit
      pagination.total = body.pagination.total
      pagination.totalPages = body.pagination.totalPages
    }
    if (body.stats) {
      Object.assign(stats, body.stats)
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'خطا در بارگذاری رسانه‌ها: ' + (error.response?.data?.message || error.message),
    })
  } finally {
    loading.value = false
  }
}

async function syncAllMedia () {
  isSyncing.value = true
  try {
    const res = await api.post('/api/media/sync')
    const count = res.data?.data?.synced_count || 0
    $q.notify({
      type: 'positive',
      message: count > 0
        ? `اسکن با موفقیت انجام شد: ${count} رسانه جدید از محصولات و فایل‌ها شناسایی و ثبت گردید.`
        : 'تمامی فایل‌ها، تصاویر محصولات و ویدیوها همگام‌سازی شده‌اند.',
      icon: 'sync',
      position: 'top',
    })
    pagination.page = 1
    await fetchMedia()
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: 'خطا در همگام‌سازی رسانه‌ها: ' + (err.response?.data?.message || err.message),
      position: 'top',
    })
  } finally {
    isSyncing.value = false
  }
}

// Upload Handling
function openUploadDialog () {
  stagedFiles.value = []
  uploadFolder.value = 'general'
  uploadDialogOpen.value = true
}

function onDialogFilesSelected (e) {
  const files = Array.from(e.target.files || [])
  for (const f of files) {
    if (!stagedFiles.value.some(existing => existing.name === f.name && existing.size === f.size)) {
      stagedFiles.value.push(f)
    }
  }
  e.target.value = ''
}

function onDropFiles (e) {
  isDragging.value = false
  const files = Array.from(e.dataTransfer?.files || [])
  for (const f of files) {
    if (!stagedFiles.value.some(existing => existing.name === f.name && existing.size === f.size)) {
      stagedFiles.value.push(f)
    }
  }
}

function removeStagedFile (index) {
  stagedFiles.value.splice(index, 1)
}

async function submitUpload () {
  if (stagedFiles.value.length === 0) return
  uploading.value = true
  let successCount = 0
  let failCount = 0

  for (let i = 0; i < stagedFiles.value.length; i++) {
    const file = stagedFiles.value[i]
    uploadProgressText.value = `${i + 1} از ${stagedFiles.value.length}`
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('folder', uploadFolder.value)
      await api.post('/api/media/upload', formData)
      successCount++
    } catch {
      failCount++
    }
  }

  uploading.value = false
  uploadDialogOpen.value = false
  stagedFiles.value = []

  if (successCount > 0) {
    $q.notify({
      type: 'positive',
      message: `${successCount} فایل با موفقیت آپلود و در کتابخانه ثبت شد.`,
    })
    fetchMedia()
  }
  if (failCount > 0) {
    $q.notify({
      type: 'negative',
      message: `${failCount} فایل به دلیل خطا آپلود نشد.`,
    })
  }
}

// Preview & Copy & Delete
function openPreview (item) {
  selectedPreviewItem.value = item
  previewDialogOpen.value = true
}

function copyUrl (url) {
  if (!url) return
  const fullUrl = url.startsWith('http') ? url : (window.location.origin + url)
  navigator.clipboard.writeText(fullUrl).then(() => {
    $q.notify({
      type: 'positive',
      message: 'آدرس فایل با موفقیت در کلیپ‌بورد کپی شد.',
      icon: 'content_copy',
      timeout: 1800,
    })
  }).catch(() => {
    $q.notify({
      type: 'warning',
      message: 'امکان کپی خودکار فراهم نشد: ' + fullUrl,
    })
  })
}

function confirmDelete (item) {
  $q.dialog({
    title: 'حذف فایل از سرور',
    message: `آیا از حذف دائم فایل "${item.original_name || item.filename}" اطمینان دارید؟`,
    cancel: { label: 'انصراف', flat: true },
    ok: { label: 'بله، حذف شود', color: 'negative', unelevated: true },
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/api/media/${item.id}`)
      $q.notify({
        type: 'positive',
        message: 'فایل با موفقیت حذف شد.',
      })
      if (selectedPreviewItem.value?.id === item.id) {
        previewDialogOpen.value = false
      }
      fetchMedia()
    } catch (err) {
      $q.notify({
        type: 'negative',
        message: 'خطا در حذف فایل: ' + (err.response?.data?.message || err.message),
      })
    }
  })
}

// Helpers
function getTypeLabel (type) {
  const map = {
    image: 'تصویر',
    video: 'ویدیو',
    document: 'سند',
    other: 'فایل',
  }
  return map[type] || 'فایل'
}

function getExtension (filename) {
  const parts = String(filename || '').split('.')
  return parts.length > 1 ? parts.pop().toUpperCase() : 'FILE'
}

function getDocIcon (filename) {
  const ext = getExtension(filename).toLowerCase()
  if (ext === 'pdf') return 'picture_as_pdf'
  if (['doc', 'docx'].includes(ext)) return 'description'
  if (['xls', 'xlsx', 'csv'].includes(ext)) return 'table_view'
  if (['zip', 'rar', 'tar', 'gz'].includes(ext)) return 'folder_zip'
  if (['mp4', 'mov', 'webm'].includes(ext)) return 'movie'
  return 'insert_drive_file'
}

function getDocColor (filename) {
  const ext = getExtension(filename).toLowerCase()
  if (ext === 'pdf') return 'red-8'
  if (['doc', 'docx'].includes(ext)) return 'blue-8'
  if (['xls', 'xlsx', 'csv'].includes(ext)) return 'green-8'
  if (['zip', 'rar'].includes(ext)) return 'amber-9'
  return 'grey-8'
}

function getFileIcon (filename) {
  const ext = getExtension(filename).toLowerCase()
  if (['jpg', 'jpeg', 'png', 'webp', 'svg', 'gif'].includes(ext)) return 'image'
  if (['mp4', 'webm', 'mov'].includes(ext)) return 'movie'
  return getDocIcon(filename)
}

function formatSize (bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatDate (dateStr) {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('fa-IR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return dateStr
  }
}

onMounted(() => {
  fetchMedia()
})
</script>

<style scoped>
.media-admin-page {
  padding: 8px 4px 60px;
  direction: rtl;
}

/* 1. Tech Page Header */
.tech-page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 28px;
}

.header-info-group {
  max-width: 680px;
}

.header-section-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 204, 0, 0.12);
  border: 1px solid rgba(255, 204, 0, 0.35);
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 0.74rem;
  font-weight: 700;
  color: #946200;
  margin-bottom: 10px;
}

.status-live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 8px #22c55e;
}

.header-main-title {
  margin: 0 0 8px;
  font-size: 1.7rem;
  font-weight: 900;
  color: #0a0a0a;
  letter-spacing: -0.02em;
}

.header-sub-desc {
  margin: 0;
  font-size: 0.88rem;
  color: #71717a;
  line-height: 1.7;
}

.header-actions-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tech-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 18px;
  border-radius: 12px;
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
  border: none;
  text-decoration: none;
  transition: all 0.2s ease;
}

.tech-action-btn.primary {
  background: #111113;
  color: #ffd54a;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
}

.tech-action-btn.primary:hover {
  background: #27272a;
  transform: translateY(-2px);
}

.tech-action-btn.secondary {
  background: #ffffff;
  color: #0a0a0a;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.tech-action-btn.secondary:hover {
  background: #f4f4f5;
}

.tech-action-btn.danger-outline {
  background: transparent;
  color: #dc2626;
  border: 1px solid rgba(220, 38, 38, 0.25);
}

.tech-action-btn.danger-outline:hover {
  background: rgba(220, 38, 38, 0.08);
}

.spin-icon {
  animation: spin 1s infinite linear;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

/* 2. Stats Bento Grid */
.stats-bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.07);
  border-radius: 18px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.02);
}

.stat-icon-bubble {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-bubble.yellow { background: rgba(255, 204, 0, 0.15); color: #b45309; }
.stat-icon-bubble.green { background: rgba(34, 197, 94, 0.12); color: #16a34a; }
.stat-icon-bubble.purple { background: rgba(147, 51, 234, 0.12); color: #9333ea; }
.stat-icon-bubble.blue { background: rgba(37, 99, 235, 0.12); color: #2563eb; }

.stat-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-title {
  font-size: 0.74rem;
  font-weight: 700;
  color: #71717a;
}

.stat-value-row {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.stat-number {
  font-size: 1.45rem;
  font-weight: 900;
  color: #0a0a0a;
}

.stat-unit {
  font-size: 0.75rem;
  color: #a1a1aa;
}

/* 3. Toolbar Card */
.media-toolbar-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.07);
  border-radius: 16px;
  padding: 14px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.type-filter-pills {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-pill-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 9999px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: #f4f4f5;
  color: #52525b;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-pill-btn:hover {
  background: #e4e4e7;
  color: #0a0a0a;
}

.filter-pill-btn.active {
  background: #111113;
  color: #ffd54a;
  border-color: #111113;
}

.pill-count {
  font-size: 0.7rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 1px 6px;
  border-radius: 9999px;
}

.folder-filter-pills {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.folder-pill-btn {
  font-size: 0.76rem;
  padding: 5px 12px;
  background: #fafafa;
  border-color: rgba(0, 0, 0, 0.06);
}

.folder-pill-btn.active {
  background: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
}

.search-and-view-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-box-wrap {
  position: relative;
  display: flex;
  align-items: center;
  width: 260px;
}

.search-ico {
  position: absolute;
  right: 12px;
  color: #a1a1aa;
  pointer-events: none;
}

.search-input-field {
  width: 100%;
  padding: 8px 36px 8px 30px;
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: #ffffff;
  font-size: 0.84rem;
  outline: none;
  transition: all 0.2s;
}

.search-input-field:focus {
  border-color: #ffd54a;
  box-shadow: 0 0 0 3px rgba(255, 213, 74, 0.25);
}

.clear-search-btn {
  position: absolute;
  left: 10px;
  background: transparent;
  border: none;
  font-size: 11px;
  color: #a1a1aa;
  cursor: pointer;
}

.view-mode-toggle {
  display: flex;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 10px;
  overflow: hidden;
}

.view-btn {
  background: #ffffff;
  border: none;
  padding: 7px 10px;
  color: #71717a;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.18s;
}

.view-btn.active {
  background: #111113;
  color: #ffd54a;
}

/* 4. Grid View */
.media-grid-layout {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.media-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.02);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.media-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.07);
  border-color: rgba(0, 0, 0, 0.16);
}

.media-thumb-box {
  position: relative;
  height: 175px;
  background: #0d0d12;
  background-image: 
    linear-gradient(45deg, #16161f 25%, transparent 25%), 
    linear-gradient(-45deg, #16161f 25%, transparent 25%), 
    linear-gradient(45deg, transparent 75%, #16161f 75%), 
    linear-gradient(-45deg, transparent 75%, #16161f 75%);
  background-size: 16px 16px;
  background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
}

.media-thumb-img {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  display: block;
  margin: auto;
  transition: transform 0.35s ease;
}

.media-card:hover .media-thumb-img {
  transform: scale(1.05);
}

.media-type-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.video-bg { background: linear-gradient(135deg, #181822 0%, #2e1065 100%); }
.doc-bg { background: linear-gradient(135deg, #181822 0%, #1e293b 100%); }

.video-play-tag,
.doc-ext-badge {
  font-size: 0.72rem;
  font-weight: 800;
  padding: 3px 10px;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(6px);
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 4px;
}

.thumb-top-badges {
  position: absolute;
  top: 10px;
  right: 10px;
  left: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  pointer-events: none;
  z-index: 2;
}

.media-type-pill {
  font-size: 0.68rem;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 9999px;
  color: #ffffff;
  background: rgba(15, 15, 18, 0.85);
  backdrop-filter: blur(8px);
}

.media-type-pill.image { background: rgba(34, 197, 94, 0.9); }
.media-type-pill.video { background: rgba(147, 51, 234, 0.9); }
.media-type-pill.document { background: rgba(37, 99, 235, 0.9); }

.media-size-pill {
  font-size: 0.68rem;
  font-weight: 700;
  background: rgba(15, 15, 18, 0.75);
  backdrop-filter: blur(8px);
  color: #ffffff;
  padding: 2px 7px;
  border-radius: 6px;
}

.thumb-hover-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px 12px;
  background: linear-gradient(0deg, rgba(13, 13, 15, 0.9) 0%, transparent 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transform: translateY(8px);
  transition: all 0.22s ease;
  z-index: 3;
}

.media-card:hover .thumb-hover-actions {
  opacity: 1;
  transform: translateY(0);
}

.hover-action-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
}

.hover-action-btn:hover {
  background: #ffd54a;
  color: #000000;
  transform: scale(1.1);
}

.hover-action-btn.delete:hover {
  background: #dc2626;
  color: #ffffff;
}

.media-info-box {
  padding: 12px 14px;
}

.media-name {
  margin: 0 0 6px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #0a0a0a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.media-sub-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.72rem;
  color: #71717a;
}

.media-folder-tag {
  background: rgba(0, 0, 0, 0.04);
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
}

/* 5. Table View */
.media-table-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.07);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.02);
}

.tech-media-table {
  width: 100%;
  border-collapse: collapse;
  text-align: right;
  font-size: 0.84rem;
}

.tech-media-table th {
  background: #f8fafc;
  padding: 14px 16px;
  font-weight: 800;
  color: #52525b;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.tech-media-table td {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  color: #0a0a0a;
  vertical-align: middle;
}

.table-thumb-box {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  overflow: hidden;
  background: #0d0d12;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 3px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.table-thumb-box img {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
}

.table-filename-cell {
  display: flex;
  flex-direction: column;
  max-width: 280px;
}

.name-main {
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.name-sub {
  font-size: 0.72rem;
  color: #71717a;
  font-family: monospace;
}

.table-actions-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tbl-btn {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: #f4f4f5;
  border: 1px solid rgba(0, 0, 0, 0.06);
  color: #52525b;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
}

.tbl-btn:hover {
  background: #111113;
  color: #ffd54a;
}

.tbl-btn.delete:hover {
  background: #dc2626;
  color: #ffffff;
}

/* Skeletons & Empty State */
.skeleton-media-card {
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.skeleton-thumb {
  height: 160px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e4e4e7 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-meta {
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sk-line {
  height: 12px;
  border-radius: 4px;
  background: #f0f0f0;
}
.sk-line.w-80 { width: 80%; }
.sk-line.w-40 { width: 40%; }

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.empty-media-card {
  padding: 80px 20px;
  background: #ffffff;
  border-radius: 18px;
  border: 1px dashed rgba(0, 0, 0, 0.12);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.empty-media-card h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 800;
  color: #0a0a0a;
}

.empty-media-card p {
  margin: 0 0 12px;
  font-size: 0.88rem;
  color: #71717a;
}

/* Pagination Bar */
.media-pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 32px;
  padding: 16px 20px;
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.02);
  flex-wrap: wrap;
}

.pagination-page-size-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-size-label {
  font-size: 0.8rem;
  font-weight: 700;
  color: #71717a;
}

.page-size-options {
  display: flex;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  overflow: hidden;
  background: #f4f4f5;
}

.page-size-btn {
  background: transparent;
  border: none;
  padding: 6px 12px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #52525b;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 1px solid rgba(0, 0, 0, 0.06);
}

.page-size-btn:last-child {
  border-left: none;
}

.page-size-btn.active {
  background: #111113;
  color: #ffd54a;
}

.page-size-btn:hover:not(.active) {
  background: rgba(0, 0, 0, 0.05);
}

.pagination-nav-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-pages-pills {
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-num-pill {
  min-width: 34px;
  height: 34px;
  padding: 0 6px;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: #ffffff;
  color: #3f3f46;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.page-num-pill:hover:not(:disabled):not(.active) {
  background: #f4f4f5;
  border-color: #cbd5e1;
}

.page-num-pill.active {
  background: #111113;
  color: #ffd54a;
  border-color: #111113;
}

.page-num-pill.ellipsis {
  border: none;
  background: transparent;
  cursor: default;
  color: #a1a1aa;
}

.page-nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: #ffffff;
  color: #0a0a0a;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.page-nav-btn:hover:not(:disabled) {
  background: #111113;
  color: #ffd54a;
}

.page-nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-current-indicator {
  font-size: 0.84rem;
  font-weight: 700;
  color: #71717a;
}

/* Modals */
.upload-dialog-card {
  min-width: 580px;
  max-width: 90vw;
  border-radius: 20px;
}

.dialog-head-row,
.preview-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
}

.title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-dropzone {
  border: 2px dashed rgba(0, 0, 0, 0.15);
  border-radius: 16px;
  padding: 36px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  background: #fafafa;
  transition: all 0.22s;
}

.modal-dropzone:hover,
.modal-dropzone.is-drag-over {
  border-color: #ffd54a;
  background: rgba(255, 213, 74, 0.05);
}

.dropzone-text-bold {
  font-weight: 800;
  font-size: 0.95rem;
  color: #0a0a0a;
}

.dropzone-text-sub {
  font-size: 0.78rem;
  color: #71717a;
  max-width: 400px;
}

.staged-files-list {
  background: #f4f4f5;
  border-radius: 12px;
  padding: 12px;
  max-height: 180px;
  overflow-y: auto;
}

.staged-head {
  font-size: 0.78rem;
  font-weight: 800;
  color: #52525b;
  margin-bottom: 8px;
}

.staged-file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  background: #ffffff;
  border-radius: 8px;
  margin-bottom: 6px;
  font-size: 0.8rem;
}

.staged-info {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}

.staged-name {
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 280px;
}

.staged-size {
  color: #71717a;
  font-size: 0.72rem;
}

.remove-staged-btn {
  background: transparent;
  border: none;
  color: #dc2626;
  cursor: pointer;
  font-weight: 700;
}

/* Preview Modal */
.preview-dialog-card {
  min-width: 720px;
  max-width: 90vw;
  border-radius: 20px;
}

.preview-body {
  padding: 20px;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 24px;
}

.preview-visual-box {
  background: #0d0d12;
  background-image: 
    linear-gradient(45deg, #16161f 25%, transparent 25%), 
    linear-gradient(-45deg, #16161f 25%, transparent 25%), 
    linear-gradient(45deg, transparent 75%, #16161f 75%), 
    linear-gradient(-45deg, transparent 75%, #16161f 75%);
  background-size: 16px 16px;
  background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
  border-radius: 16px;
  overflow: hidden;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.full-preview-img {
  max-width: 100%;
  max-height: 460px;
  width: auto;
  height: auto;
  object-fit: contain;
}

.full-preview-video {
  max-width: 100%;
  max-height: 380px;
}

.full-preview-doc {
  text-align: center;
  padding: 30px;
  color: #ffffff;
}

.preview-details-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  font-size: 0.82rem;
}

.detail-row .lbl {
  color: #71717a;
  font-weight: 700;
  font-size: 0.75rem;
}

.detail-row .val {
  color: #0a0a0a;
  font-weight: 600;
}

.font-mono {
  font-family: monospace;
}

.url-copy-box {
  display: flex;
  gap: 6px;
  margin-top: 4px;
}

.url-input {
  flex: 1;
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: monospace;
  font-size: 0.78rem;
  background: #f8fafc;
  direction: ltr;
  text-align: left;
}

.copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 8px;
  border: 1.5px solid #fed72b;
  background: #ffffff;
  color: #0a0a0b;
  font-size: 0.76rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.copy-btn:hover {
  background: #fed72b;
  color: #000000;
}

/* Batch Optimization Buttons & Selection Dock */
.toolbar-opt-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tech-tool-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.tech-tool-btn.select-all-btn {
  background: #ffffff;
  color: #3f3f46;
  border-color: rgba(0, 0, 0, 0.12);
}

.tech-tool-btn.select-all-btn:hover,
.tech-tool-btn.select-all-btn.active {
  background: #f4f4f5;
  color: #18181b;
  border-color: #ffd54a;
}

.tech-tool-btn.opt-webp {
  background: #fef3c7;
  color: #b45309;
  border-color: #fde68a;
}

.tech-tool-btn.opt-webp:hover:not(:disabled) {
  background: #fed72b;
  border-color: #eab308;
  color: #000;
  transform: translateY(-1px);
}

.tech-tool-btn.opt-compress {
  background: #ecfdf5;
  color: #047857;
  border-color: #a7f3d0;
}

.tech-tool-btn.opt-compress:hover:not(:disabled) {
  background: #10b981;
  color: #fff;
  transform: translateY(-1px);
}

.tech-tool-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tool-count-pill {
  background: #fed72b;
  color: #09090b;
  border-radius: 9999px;
  padding: 1px 7px;
  font-size: 0.72rem;
  font-weight: 800;
}

/* Floating Batch Selection Dock */
.batch-selection-dock {
  background: #ffffff;
  color: #09090b;
  border-radius: 16px;
  padding: 12px 20px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  border: 2px solid #fed72b;
}

.dock-badge-summary {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.88rem;
  font-weight: 700;
  color: #09090b;
}

.dock-actions-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.dock-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.dock-btn.webp {
  background: #fed72b;
  color: #000;
  border: 1px solid #eab308;
}

.dock-btn.webp:hover:not(:disabled) {
  background: #f59e0b;
  transform: translateY(-1px);
}

.dock-btn.compress {
  background: #10b981;
  color: #fff;
}

.dock-btn.compress:hover:not(:disabled) {
  background: #34d399;
  transform: translateY(-1px);
}

.dock-btn.delete-batch {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fca5a5;
}

.dock-btn.delete-batch:hover:not(:disabled) {
  background: #dc2626;
  color: #ffffff;
  transform: translateY(-1px);
}

.dock-btn.cancel {
  background: #ffffff;
  color: #0f172a;
  border: 1.5px solid #cbd5e1;
}

.dock-btn.cancel:hover {
  background: #fefce8;
  border-color: #fed72b;
  color: #000000;
}

.dock-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Card Selection Overlay */
.card-select-trigger {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(4px);
  color: #ffffff;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.25);
}

.card-select-trigger:hover {
  transform: scale(1.1);
}

.card-select-trigger.selected {
  background: #ffd54a;
  color: #09090b;
  border-color: #ffd54a;
}

.media-card.is-selected {
  border-color: #ffd54a !important;
  box-shadow: 0 0 0 2px #ffd54a, 0 12px 30px rgba(0, 0, 0, 0.1);
}

.table-row-selected {
  background-color: rgba(255, 213, 74, 0.08) !important;
}

.hover-action-btn.opt-webp-btn {
  background: rgba(245, 158, 11, 0.9);
  color: #000;
}

.hover-action-btn.opt-comp-btn {
  background: rgba(16, 185, 129, 0.9);
  color: #fff;
}

.tbl-btn.opt-webp {
  color: #d97706;
}

.tbl-btn.opt-webp:hover {
  background: rgba(245, 158, 11, 0.15);
}

.tbl-btn.opt-compress {
  color: #059669;
}

.tbl-btn.opt-compress:hover {
  background: rgba(16, 185, 129, 0.15);
}

.tech-action-btn.warning-soft {
  background: rgba(245, 158, 11, 0.14);
  color: #b45309;
  border: 1px solid rgba(245, 158, 11, 0.35);
}

.tech-action-btn.warning-soft:hover:not(:disabled) {
  background: #f59e0b;
  color: #000;
}

.tech-action-btn.success-soft {
  background: rgba(16, 185, 129, 0.14);
  color: #047857;
  border: 1px solid rgba(16, 185, 129, 0.35);
}

.tech-action-btn.success-soft:hover:not(:disabled) {
  background: #10b981;
  color: #fff;
}

.dock-slide-enter-active,
.dock-slide-leave-active {
  transition: all 0.3s ease;
}

.dock-slide-enter-from,
.dock-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Responsive */
@media (max-width: 1024px) {
  .stats-bento-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .tech-page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .header-actions-group {
    flex-direction: column;
    width: 100%;
    gap: 8px;
  }

  .header-actions-group .tech-action-btn {
    width: 100%;
    justify-content: center;
    min-height: 42px;
  }

  .preview-body {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 14px;
  }

  .preview-visual-box {
    min-height: 180px;
    padding: 10px;
  }

  .upload-dialog-card,
  .preview-dialog-card {
    min-width: 0 !important;
    width: 100vw !important;
    max-width: 100vw !important;
    height: 100vh !important;
    max-height: 100vh !important;
    border-radius: 0 !important;
    margin: 0 !important;
  }

  .stats-bento-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .media-toolbar-card {
    flex-direction: column;
    align-items: stretch;
    gap: 14px;
    padding: 14px 12px;
  }

  .search-box-wrap {
    width: 100%;
  }

  .search-and-view-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .toolbar-opt-actions {
    flex-direction: column;
    width: 100%;
    gap: 8px;
  }

  .tech-tool-btn {
    width: 100%;
    justify-content: center;
    min-height: 40px;
  }

  .batch-selection-dock {
    flex-direction: column;
    align-items: stretch;
    bottom: 10px;
    right: 8px;
    left: 8px;
    padding: 12px 14px;
  }

  .dock-actions-row {
    flex-direction: column;
    gap: 8px;
  }

  .dock-btn {
    width: 100%;
    justify-content: center;
    min-height: 40px;
  }

  .thumb-hover-actions {
    opacity: 1 !important;
    transform: translateY(0) !important;
  }

  .media-table-card {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .media-pagination-bar {
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
  }

  .pagination-page-size-wrap,
  .pagination-nav-wrap {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .media-grid-layout {
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 10px;
  }

  .media-thumb-box {
    height: 125px;
    padding: 6px;
  }

  .media-info-box {
    padding: 8px 10px;
  }

  .media-name {
    font-size: 0.8rem;
  }

  .stat-card {
    padding: 12px 14px;
  }
}

@media (max-width: 320px) {
  .media-grid-layout {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .media-thumb-box {
    height: 130px;
  }

  .type-filter-pills,
  .folder-filter-pills {
    gap: 4px;
  }

  .filter-pill-btn {
    padding: 4px 8px;
    font-size: 0.72rem;
  }

  .staged-file-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .staged-name {
    max-width: 200px;
  }

  .url-copy-box {
    flex-direction: column;
  }
}

@media (hover: none) {
  .thumb-hover-actions {
    opacity: 1 !important;
    transform: translateY(0) !important;
  }
}
</style>

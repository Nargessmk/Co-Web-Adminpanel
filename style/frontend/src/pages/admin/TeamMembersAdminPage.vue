<template>
  <div class="admin-team">
    <!-- List Mode -->
    <div v-if="viewMode === 'list'">
      <div class="page-header">
        <div class="page-header-titles">
          <h3>مدیریت افراد تیم</h3>
          <span class="page-subtitle">افزودن و ویرایش مشخصات پرسنل، تخصص‌ها، رزومه‌ها و پیوندهای شبکه‌های اجتماعی</span>
        </div>
        <q-btn color="primary" unelevated label="عضو جدید" icon="add" class="btn-create" @click="openDialog()" />
      </div>

      <div class="table-card">
        <q-table
          :rows="members"
          :columns="columns"
          row-key="id"
          :loading="loading"
          flat
          :pagination="pagination"
          no-data-label="هیچ عضوی یافت نشد"
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

          <template #body-cell-image="props">
            <q-td :props="props">
              <img v-if="props.row.image_url" :src="formatMediaUrl(props.row.image_url)" class="table-thumb" loading="lazy" decoding="async" @error="e => handleImageError(e)" />
              <div v-else class="no-image"><q-icon :name="props.row.avatar_icon || 'person'" /></div>
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

          <template #body-cell-links="props">
            <q-td :props="props">
              <MemberLinks :member="props.row" variant="compact" />
            </q-td>
          </template>

          <template #body-cell-actions="props">
            <q-td :props="props">
              <q-btn flat round dense icon="visibility" size="sm" color="info" @click="openViewDialog(props.row)" />
              <q-btn flat round dense icon="edit" size="sm" color="primary" @click="openDialog(props.row)" />
              <q-btn flat round dense icon="delete" size="sm" color="negative" @click="confirmDelete(props.row)" />
            </q-td>
          </template>

          <template #item="props">
            <div class="mobile-card">
              <div class="mobile-card-header">
                <img v-if="props.row.image_url" :src="formatMediaUrl(props.row.image_url)" class="mobile-card-thumb" loading="lazy" decoding="async" @error="e => handleImageError(e)" />
                <div v-else class="mobile-card-thumb-placeholder"><q-icon name="person" /></div>
                <div class="mobile-card-title">
                  <strong>{{ props.row.full_name }}</strong>
                  <span class="mobile-card-role">{{ props.row.role }}</span>
                </div>
                <span class="status-chip" :class="{ active: props.row.is_active }">
                  {{ props.row.is_active ? 'فعال' : 'غیرفعال' }}
                </span>
              </div>
              <div class="mobile-card-footer">
                <MemberLinks :member="props.row" variant="compact" />
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

    <!-- Edit Mode (Dedicated Full Page) -->
    <div v-else-if="viewMode === 'edit'" class="admin-edit-page">
      <!-- Top Nav -->
      <div class="edit-page-top-nav">
        <div class="nav-breadcrumbs-group">
          <button type="button" class="btn-back-to-list" @click="closeEditView">
            <q-icon name="arrow_forward" size="18px" />
            <span>بازگشت به لیست اعضا</span>
          </button>
          <div class="edit-breadcrumbs">
            <span class="crumb-root">تیم کهکشان</span>
            <span class="crumb-sep">/</span>
            <span class="crumb-current">{{ editing ? (form.full_name || 'ویرایش عضو تیم') : 'عضو جدید تیم' }}</span>
          </div>
        </div>

        <div class="nav-actions-group">
          <q-btn flat label="انصراف" color="grey-7" class="btn-cancel-nav" @click="closeEditView" />
          <q-btn color="primary" unelevated label="ذخیره اطلاعات" icon="save" :loading="saving" class="btn-save-nav" @click="saveMember" />
        </div>
      </div>

      <!-- Bento Form Grid -->
      <q-form ref="formRef" @submit.prevent="saveMember" class="edit-form-wrap">
        <div class="edit-page-bento-grid">
          <!-- Main Column -->
          <div class="bento-col-main">
            <!-- Basic Profile Bento Card -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="badge" size="20px" />
                </div>
                <div>
                  <h4 class="bento-card-title">اطلاعات فردی و شغلی (دو زبانه)</h4>
                  <p class="bento-card-desc">نام و سمت شغلی عضو تیم را به دو زبان فارسی و انگلیسی مشخص کنید</p>
                </div>
              </div>
              <div class="bento-card-body">
                <div class="form-row">
                  <q-input v-model="form.full_name" outlined label="نام و نام خانوادگی (فارسی)*" :rules="[val => !!val || 'نام الزامی است']" />
                  <q-input
                    v-model="form.full_name_en"
                    outlined
                    label="Full name (English)*"
                    placeholder="Soroush Rahimi"
                    :rules="[val => !!val || 'English name is required']"
                    input-class="url-input"
                    input-style="direction: ltr; text-align: left;"
                  />
                </div>

                <div class="form-row" style="margin-top: 16px;">
                  <q-input v-model="form.role" outlined label="سمت / نقش (فارسی)*" :rules="[val => !!val || 'سمت الزامی است']" />
                  <q-input
                    v-model="form.role_en"
                    outlined
                    label="Job title (English)*"
                    placeholder="Senior Backend Engineer"
                    :rules="[val => !!val || 'English job title is required']"
                    input-class="url-input"
                    input-style="direction: ltr; text-align: left;"
                  />
                </div>
              </div>
            </div>

            <!-- Social Links Bento Card -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="share" size="20px" />
                </div>
                <div>
                  <h4 class="bento-card-title">لینک‌های شبکه‌های اجتماعی</h4>
                  <p class="bento-card-desc">پیوند پروفایل‌های لینکدین، گیت‌هاب و سایت اختصاصی برای دسترسی مراجعان</p>
                </div>
              </div>
              <div class="bento-card-body">
                <div class="form-row url-row">
                  <q-input v-model="form.linkedin_url" outlined label="لینکدین" placeholder="https://linkedin.com/in/..." input-class="url-input">
                    <template #prepend>
                      <svg class="url-field-icon linkedin" viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true">
                        <path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45z" />
                      </svg>
                    </template>
                  </q-input>
                  <q-input v-model="form.github_url" outlined label="گیت‌هاب" placeholder="https://github.com/..." input-class="url-input">
                    <template #prepend>
                      <svg class="url-field-icon github" viewBox="0 0 16 16" width="18" height="18" fill="currentColor" aria-hidden="true">
                        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
                      </svg>
                    </template>
                  </q-input>
                </div>

                <div style="margin-top: 16px;">
                  <q-input v-model="form.website_url" outlined label="وبسایت اختصاصی" placeholder="https://example.com" input-class="url-input">
                    <template #prepend><q-icon name="language" color="primary" size="20px" /></template>
                  </q-input>
                </div>
              </div>
            </div>

            <!-- Resume & Biography Bento Card -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="description" size="20px" />
                </div>
                <div>
                  <h4 class="bento-card-title">سوابق حرفه‌ای و رزومه جامع</h4>
                  <p class="bento-card-desc">انتخاب ساختار رزومه و نگارش متن‌های فارسی و انگلیسی با ویرایشگر غنی</p>
                </div>
              </div>
              <div class="bento-card-body">
                <div class="template-row">
                  <label>قالب چیدمان رزومه</label>
                  <q-btn-toggle
                    v-model="form.resume_template"
                    :options="TEMPLATE_OPTIONS"
                    unelevated
                    toggle-color="primary"
                    color="grey-2"
                    text-color="grey-8"
                    spread
                  />
                  <span class="template-hint">{{ templateHint }}</span>
                </div>

                <div class="resume-editors-stack">
                  <div class="resume-editor-block">
                    <div class="resume-editor-title-row">
                      <span class="editor-lang-badge">FA</span>
                      <strong class="editor-title-label">رزومه و بیوگرافی فارسی</strong>
                      <q-btn flat dense size="sm" icon="auto_fix_high" color="primary" label="ساختار استاندارد" class="btn-skeleton" @click="fillSkeleton('fa')" />
                    </div>
                    <RichTextEditor
                      v-model="form.resume_fa"
                      :min-height="260"
                      placeholder="رزومه خود را به فارسی بنویسید…"
                      hint="بخش‌های استاندارد: خلاصه، سوابق کاری، تحصیلات، مهارت‌ها."
                    />
                  </div>

                  <div class="resume-editor-block" style="margin-top: 24px;">
                    <div class="resume-editor-title-row">
                      <span class="editor-lang-badge en">EN</span>
                      <strong class="editor-title-label">رزومه انگلیسی (Resume EN)</strong>
                      <q-btn flat dense size="sm" icon="auto_fix_high" color="primary" label="Standard Skeleton" class="btn-skeleton" @click="fillSkeleton('en')" />
                    </div>
                    <RichTextEditor
                      v-model="form.resume_en"
                      dir="ltr"
                      :min-height="260"
                      placeholder="Write your resume in English…"
                      hint="Use standard sections: Summary, Experience, Education, Skills."
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Side Column -->
          <div class="bento-col-side">
            <!-- Avatar Picker Card -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="account_circle" size="20px" />
                </div>
                <div>
                  <h4 class="bento-card-title">تصویر یا آیکون پروفایل</h4>
                  <p class="bento-card-desc">انتخاب عکس پرسنلی یا آیکون تخصص برای نمایش</p>
                </div>
              </div>
              <div class="bento-card-body">
                <div class="avatar-preview-row">
                  <div class="avatar-preview-circle">
                    <img v-if="imagePreview" :src="imagePreview" alt="" />
                    <q-icon v-else :name="form.avatar_icon || 'person'" size="36px" />
                  </div>
                  <div class="avatar-preview-text">
                    <strong>پیش‌نمایش زنده</strong>
                    <span>{{ imagePreview ? 'عکس بارگذاری‌شده در صفحه درباره ما نمایش داده می‌شود.' : 'آیکون انتخابی در صورت عدم وجود عکس نمایش داده می‌شود.' }}</span>
                  </div>
                </div>

                <q-btn-toggle
                  v-model="avatarMode"
                  class="avatar-mode-toggle"
                  :options="AVATAR_MODE_OPTIONS"
                  unelevated
                  toggle-color="primary"
                  color="grey-2"
                  text-color="grey-8"
                  spread
                />

                <div v-show="avatarMode === 'image'">
                  <div class="upload-area" @click="$refs.fileInput.click()">
                    <img v-if="imagePreview" :src="imagePreview" class="upload-preview" />
                    <div v-else class="upload-placeholder">
                      <q-icon name="cloud_upload" size="40px" />
                      <span>کلیک کنید یا تصویر را بکشید</span>
                      <span class="upload-hint">JPG, PNG, GIF, WebP — حداکثر 10MB</span>
                    </div>
                  </div>
                  <input ref="fileInput" type="file" accept="image/*" style="display: none" @change="onFileSelect" />

                  <div v-if="imagePreview" class="profile-image-actions">
                    <q-btn flat dense icon="image" color="primary" label="تغییر تصویر" @click="$refs.fileInput.click()" />
                    <q-btn flat dense icon="delete" color="negative" label="حذف تصویر" @click="removeImage" />
                  </div>
                </div>

                <div v-show="avatarMode === 'icon'" class="icon-grid-wrap">
                  <div class="icon-grid">
                    <button
                      v-for="option in TEAM_ICON_OPTIONS"
                      :key="option.value"
                      type="button"
                      class="icon-tile"
                      :class="{ selected: form.avatar_icon === option.value }"
                      :title="option.label"
                      :aria-label="option.label"
                      :aria-pressed="form.avatar_icon === option.value"
                      @click="form.avatar_icon = option.value"
                    >
                      <q-icon :name="option.value" size="24px" />
                    </button>
                  </div>
                  <span class="template-hint">{{ iconHint }}</span>
                </div>
              </div>
            </div>

            <!-- Status & Settings Card -->
            <div class="edit-bento-card">
              <div class="bento-card-header">
                <div class="bento-icon-bubble">
                  <q-icon name="tune" size="20px" />
                </div>
                <div>
                  <h4 class="bento-card-title">تنظیمات وضعیت و انتشار</h4>
                  <p class="bento-card-desc">ترتیب قرارگیری و فعال بودن عضو در صفحه درباره ما</p>
                </div>
              </div>
              <div class="bento-card-body">
                <div class="setting-toggle-row">
                  <div>
                    <strong class="setting-toggle-title">وضعیت نمایش در وبسایت</strong>
                    <p class="setting-toggle-desc">در صورت فعال بودن، در صفحه درباره ما نمایش داده خواهد شد</p>
                  </div>
                  <q-toggle v-model="form.is_active" color="primary" />
                </div>
                <div style="margin-top: 16px;">
                  <q-input v-model="form.sort_order" outlined label="ترتیب نمایش (اولویت عددی)" type="number" hint="اعداد کوچک‌تر ابتدا نمایش داده می‌شوند" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sticky Bottom Bar -->
        <div class="edit-page-sticky-bar">
          <div class="sticky-bar-info">
            <span class="sticky-bar-status">در حال ویرایش: {{ form.full_name || 'عضو جدید' }}</span>
          </div>
          <div class="sticky-bar-actions">
            <q-btn flat label="انصراف و بازگشت" color="grey-7" class="btn-cancel" @click="closeEditView" />
            <q-btn type="submit" color="primary" unelevated label="ذخیره اطلاعات" icon="save" :loading="saving" class="btn-save" />
          </div>
        </div>
      </q-form>
    </div>

    <!-- View Mode (Dedicated Full Page) -->
    <div v-else-if="viewMode === 'view' && viewingMember" class="admin-edit-page">
      <div class="edit-page-top-nav">
        <div class="nav-breadcrumbs-group">
          <button type="button" class="btn-back-to-list" @click="closeEditView">
            <q-icon name="arrow_forward" size="18px" />
            <span>بازگشت به لیست اعضا</span>
          </button>
          <div class="edit-breadcrumbs">
            <span class="crumb-root">تیم کهکشان</span>
            <span class="crumb-sep">/</span>
            <span class="crumb-current">{{ viewingMember.full_name }}</span>
          </div>
        </div>
        <div class="nav-actions-group">
          <q-btn color="primary" unelevated label="ویرایش عضو" icon="edit" class="btn-save-nav" @click="openDialog(viewingMember)" />
        </div>
      </div>

      <div class="edit-page-bento-grid">
        <div class="bento-col-main">
          <!-- Profile Card -->
          <div class="edit-bento-card">
            <div class="view-profile-hero">
              <img v-if="viewingMember.image_url" :src="formatMediaUrl(viewingMember.image_url)" class="view-avatar-large" loading="lazy" decoding="async" @error="e => handleImageError(e)" />
              <div v-else class="view-avatar-placeholder-large">
                <q-icon :name="viewingMember.avatar_icon || 'person'" size="56px" />
              </div>
              <div class="view-hero-text">
                <div class="view-hero-header-line">
                  <h3>{{ viewingMember.full_name }}</h3>
                  <span class="status-chip" :class="{ active: viewingMember.is_active }">
                    {{ viewingMember.is_active ? 'فعال در وبسایت' : 'غیرفعال' }}
                  </span>
                </div>
                <div v-if="viewingMember.full_name_en" class="view-role-en" dir="ltr">{{ viewingMember.full_name_en }}</div>
                <div class="view-role-badge">{{ viewingMember.role }}</div>
                <div v-if="viewingMember.role_en" class="view-role-en" dir="ltr">{{ viewingMember.role_en }}</div>
              </div>
            </div>
          </div>

          <!-- Resumes View -->
          <div class="edit-bento-card" v-if="viewingMember.resume_fa || viewingMember.resume_en">
            <div class="bento-card-header">
              <div class="bento-icon-bubble">
                <q-icon name="article" size="20px" />
              </div>
              <div>
                <h4 class="bento-card-title">رزومه و سوابق تخصصی</h4>
                <p class="bento-card-desc">قالب رزومه: {{ viewingMember.resume_template || 'classic' }}</p>
              </div>
            </div>
            <div class="bento-card-body">
              <div v-if="viewingMember.resume_fa" class="resume-view-box">
                <div class="resume-view-head"><span class="editor-lang-badge">FA</span> <strong>رزومه فارسی</strong></div>
                <RichContent class="resume-content" :html="viewingMember.resume_fa" />
              </div>
              <div v-if="viewingMember.resume_en" class="resume-view-box" style="margin-top: 20px;">
                <div class="resume-view-head"><span class="editor-lang-badge en">EN</span> <strong>English Resume</strong></div>
                <RichContent class="resume-content ltr" :html="viewingMember.resume_en" />
              </div>
            </div>
          </div>
        </div>

        <div class="bento-col-side">
          <!-- Links Card -->
          <div class="edit-bento-card" v-if="viewingMember.linkedin_url || viewingMember.github_url || viewingMember.website_url">
            <div class="bento-card-header">
              <div class="bento-icon-bubble">
                <q-icon name="link" size="20px" />
              </div>
              <div>
                <h4 class="bento-card-title">پیوندهای شبکه‌های اجتماعی</h4>
              </div>
            </div>
            <div class="bento-card-body">
              <div class="view-links-list">
                <a v-if="viewingMember.linkedin_url" :href="viewingMember.linkedin_url" target="_blank" rel="noopener" class="view-link-item">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true" style="color:#0a66c2">
                    <path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45z" />
                  </svg>
                  <span>لینکدین</span>
                </a>
                <a v-if="viewingMember.github_url" :href="viewingMember.github_url" target="_blank" rel="noopener" class="view-link-item">
                  <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor" aria-hidden="true" style="color:#111111">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
                  </svg>
                  <span>گیت‌هاب</span>
                </a>
                <a v-if="viewingMember.website_url" :href="viewingMember.website_url" target="_blank" rel="noopener" class="view-link-item">
                  <q-icon name="language" color="primary" />
                  <span>وبسایت شخصی</span>
                </a>
              </div>
            </div>
          </div>

          <!-- Metadata Card -->
          <div class="edit-bento-card">
            <div class="bento-card-header">
              <div class="bento-icon-bubble">
                <q-icon name="info" size="20px" />
              </div>
              <div>
                <h4 class="bento-card-title">شناسنامه رکورد</h4>
              </div>
            </div>
            <div class="bento-card-body">
              <div class="meta-field-row">
                <span class="meta-label">ترتیب نمایش:</span>
                <span class="meta-val">{{ viewingMember.sort_order }}</span>
              </div>
              <div class="meta-field-row">
                <span class="meta-label">تاریخ ایجاد:</span>
                <span class="meta-val">{{ formatDate(viewingMember.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useQuasar } from 'quasar'
import moment from 'moment-jalaali'
import RichTextEditor from 'src/components/common/RichTextEditor.vue'
import RichContent from 'src/components/common/RichContent.vue'
import MemberLinks from 'src/components/common/MemberLinks.vue'
import { formatMediaUrl, handleImageError } from 'src/utils/media'
import api from 'src/services/api'

const $q = useQuasar()

const members = ref([])
const loading = ref(false)
const saving = ref(false)
const viewMode = ref('list') // 'list' | 'edit' | 'view'
const editing = ref(null)
const imagePreview = ref(null)
const avatarMode = ref('image')
const filter = ref('')
let imageFile = null

const viewingMember = ref(null)

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
  { name: 'full_name', label: 'نام', field: 'full_name', align: 'right', sortable: true },
  { name: 'role', label: 'سمت', field: 'role', align: 'right', sortable: true },
  { name: 'links', label: 'لینک‌ها', align: 'center' },
  { name: 'status', label: 'وضعیت', align: 'center' },
  { name: 'created_at', label: 'تاریخ ایجاد', field: 'created_at', align: 'right', sortable: true },
  { name: 'actions', label: 'عملیات', align: 'center' },
]

const defaultForm = {
  full_name: '',
  full_name_en: '',
  role: '',
  role_en: '',
  linkedin_url: '',
  github_url: '',
  website_url: '',
  resume_en: '',
  resume_fa: '',
  resume_template: 'classic',
  avatar_icon: '',
  sort_order: 0,
  is_active: true,
}

const TEAM_ICON_OPTIONS = [
  { label: 'شخص', value: 'person' },
  { label: 'چهره', value: 'face' },
  { label: 'مرد', value: 'man' },
  { label: 'زن', value: 'woman' },
  { label: 'افراد', value: 'people' },
  { label: 'تیم', value: 'groups' },
  { label: 'جمعیت', value: 'people_alt' },
  { label: 'حساب کاربری', value: 'account_circle' },
  { label: 'پرتره', value: 'portrait' },
  { label: 'نشان', value: 'badge' },
  { label: 'کدنویسی', value: 'code' },
  { label: 'ترمینال', value: 'terminal' },
  { label: 'توسعه‌دهنده', value: 'developer_board' },
  { label: 'مهندس', value: 'engineering' },
  { label: 'تست و باگ', value: 'bug_report' },
  { label: 'داده', value: 'data_object' },
  { label: 'تحلیل داده', value: 'query_stats' },
  { label: 'بینش', value: 'insights' },
  { label: 'آمار', value: 'analytics' },
  { label: 'ذخیره‌سازی', value: 'storage' },
  { label: 'طراح', value: 'palette' },
  { label: 'نقاشی', value: 'brush' },
  { label: 'طراحی', value: 'draw' },
  { label: 'معماری', value: 'architecture' },
  { label: 'خدمات طراحی', value: 'design_services' },
  { label: 'مالی', value: 'receipt_long' },
  { label: 'پرداخت', value: 'payments' },
  { label: 'بانک', value: 'account_balance' },
  { label: 'کیف پول', value: 'wallet' },
  { label: 'حقوق', value: 'gavel' },
  { label: 'بازاریابی', value: 'campaign' },
  { label: 'فروشگاه', value: 'storefront' },
  { label: 'قیمت‌گذاری', value: 'price_check' },
  { label: 'پشتیبانی', value: 'support_agent' },
]

const TEMPLATE_OPTIONS = [
  { label: 'کلاسیک', value: 'classic' },
  { label: 'مدرن', value: 'modern' },
  { label: 'فشرده', value: 'compact' },
]

const templateHint = computed(() => {
  switch (form.value.resume_template) {
    case 'modern':
      return 'چیدمان بازتر و خوانا — مناسب رزومه یک‌صفحه‌ای.'
    case 'compact':
      return 'فشرده‌تر — برای رزومه‌های بلند که باید در چند صفحه جا شوند.'
    default:
      return 'چیدمان استاندارد: خلاصه، سوابق، تحصیلات، مهارت‌ها.'
  }
})

const AVATAR_MODE_OPTIONS = [
  { label: 'عکس', value: 'image' },
  { label: 'آیکون', value: 'icon' },
]

const iconHint = computed(() => {
  if (imagePreview.value) {
    return 'تا زمانی که عکسی بارگذاری شده باشد، آیکون استفاده نمی‌شود. با حذف عکس، آیکون انتخابی نمایش داده می‌شود.'
  }
  const chosen = TEAM_ICON_OPTIONS.find((option) => option.value === form.value.avatar_icon)
  return chosen
    ? `آیکون انتخاب‌شده: «${chosen.label}» — چون عکسی بارگذاری نشده، در صفحه درباره ما نمایش داده می‌شود.`
    : 'یک آیکون انتخاب کنید تا جای عکس در صفحه درباره ما نمایش داده شود.'
})

const RESUME_SKELETON = [
  '<h2>خلاصه</h2>',
  '<p>در یک یا دو جمله خودتان را معرفی کنید.</p>',
  '<h2>سوابق کاری</h2>',
  '<ul><li>سمت — نام شرکت (سال تا سال)</li><li>توضیح کوتاه دستاوردها</li></ul>',
  '<h2>تحصیلات</h2>',
  '<p>مدرک تحصیلی — دانشگاه</p>',
  '<h2>مهارت‌ها</h2>',
  '<ul><li>مهارت اول</li><li>مهارت دوم</li></ul>',
].join('')

function fillSkeleton (lang) {
  const field = lang === 'fa' ? 'resume_fa' : 'resume_en'
  form.value[field] = RESUME_SKELETON
}

const form = ref({ ...defaultForm })
const formRef = ref(null)

function openDialog (row = null) {
  editing.value = row
  if (row) {
    form.value = {
      full_name: row.full_name,
      full_name_en: row.full_name_en || '',
      role: row.role,
      role_en: row.role_en || '',
      linkedin_url: row.linkedin_url || '',
      github_url: row.github_url || '',
      website_url: row.website_url || '',
      resume_en: row.resume_en || '',
      resume_fa: row.resume_fa || '',
      resume_template: row.resume_template || 'classic',
      avatar_icon: row.avatar_icon || '',
      sort_order: row.sort_order || 0,
      is_active: row.is_active,
    }
    imagePreview.value = row.image_url ? formatMediaUrl(row.image_url) : null
    avatarMode.value = row.image_url ? 'image' : 'icon'
  } else {
    form.value = { ...defaultForm }
    imagePreview.value = null
    avatarMode.value = 'image'
  }
  imageFile = null
  viewMode.value = 'edit'
}

function closeEditView () {
  viewMode.value = 'list'
  editing.value = null
  viewingMember.value = null
}

function openViewDialog (row) {
  viewingMember.value = row
  viewMode.value = 'view'
}

function onFileSelect (e) {
  const file = e.target.files[0]
  e.target.value = ''
  if (!file) return
  imageFile = file
  imagePreview.value = URL.createObjectURL(file)
}

function removeImage () {
  const row = editing.value

  if (!row || !row.image_url) {
    imageFile = null
    imagePreview.value = null
    return
  }

  $q.dialog({
    title: 'حذف تصویر',
    message: 'آیا از حذف تصویر پروفایل این عضو تیم اطمینان دارید؟',
    cancel: 'انصراف',
    ok: { label: 'حذف', color: 'negative' },
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/api/team-members/admin/${row.id}/image`)
      row.image_url = null
      imageFile = null
      imagePreview.value = null
      $q.notify({ type: 'positive', message: 'تصویر پروفایل حذف شد' })
      loadMembers()
    } catch (e) {
      $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در حذف تصویر' })
    }
  })
}

async function saveMember () {
  const valid = await formRef.value.validate()
  if (!valid) return

  saving.value = true
  try {
    const fd = new FormData()
    fd.append('full_name', form.value.full_name)
    fd.append('full_name_en', form.value.full_name_en)
    fd.append('role', form.value.role)
    fd.append('role_en', form.value.role_en)
    fd.append('linkedin_url', form.value.linkedin_url)
    fd.append('github_url', form.value.github_url)
    fd.append('website_url', form.value.website_url)
    fd.append('resume_en', form.value.resume_en)
    fd.append('resume_fa', form.value.resume_fa)
    fd.append('resume_template', form.value.resume_template)
    fd.append('avatar_icon', form.value.avatar_icon || '')
    fd.append('sort_order', form.value.sort_order)
    fd.append('is_active', form.value.is_active)
    if (imageFile) fd.append('image', imageFile)

    if (editing.value) {
      await api.put(`/api/team-members/admin/${editing.value.id}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      $q.notify({ type: 'positive', message: 'عضو تیم بروزرسانی شد' })
    } else {
      await api.post('/api/team-members/admin', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      $q.notify({ type: 'positive', message: 'عضو تیم ایجاد شد' })
    }
    viewMode.value = 'list'
    loadMembers()
  } catch (e) {
    $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در ذخیره' })
  } finally {
    saving.value = false
  }
}

function confirmDelete (row) {
  $q.dialog({
    title: 'حذف عضو تیم',
    message: `آیا از حذف "${row.full_name}" اطمینان دارید؟`,
    cancel: 'انصراف',
    ok: { label: 'حذف', color: 'negative' },
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/api/team-members/admin/${row.id}`)
      $q.notify({ type: 'positive', message: 'عضو تیم حذف شد' })
      if (viewMode.value !== 'list') {
        viewMode.value = 'list'
      }
      loadMembers()
    } catch (e) {
      $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در حذف' })
    }
  })
}

async function loadMembers () {
  loading.value = true
  try {
    const res = await api.get('/api/team-members/admin/all')
    members.value = res.data.data || []
  } catch (e) { console.error(e) } finally { loading.value = false }
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  loadMembers()
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
.table-thumb { width: 44px; height: 44px; object-fit: cover; border-radius: 50%; border: 1px solid #e2e8f0; }
.no-image { width: 44px; height: 44px; background: #f4f4f5; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #71717a; border: 1px solid #e2e8f0; }
.status-chip { font-size: 11px; padding: 4px 12px; border-radius: 9999px; font-weight: 700; background: #fee2e2; color: #ef4444; }
.status-chip.active { background: #ecfdf5; color: #059669; }

.edit-form-wrap { display: flex; flex-direction: column; width: 100%; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.template-row { margin-bottom: 20px; }
.template-row > label { display: block; font-size: 13px; font-weight: 700; color: #0a0a0b; margin-bottom: 8px; }
.template-hint { display: block; margin-top: 6px; font-size: 12px; color: #71717a; line-height: 1.7; }

.resume-editors-stack { display: flex; flex-direction: column; }
.resume-editor-title-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.editor-lang-badge { font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 6px; background: #fed72b; color: #0a0a0b; }
.editor-lang-badge.en { background: #0a0a0b; color: #fed72b; }
.editor-title-label { font-size: 14px; font-weight: 700; color: #0a0a0b; flex: 1; }
.btn-skeleton { border-radius: 8px; font-size: 12px; font-weight: 600; }

.avatar-preview-row { display: flex; align-items: center; gap: 14px; padding: 14px; background: #fafafa; border: 1px solid #e2e8f0; border-radius: 14px; margin-bottom: 14px; }
.avatar-preview-circle { width: 64px; height: 64px; flex: 0 0 64px; border-radius: 50%; background: #0a0a0b; color: #fed72b; display: flex; align-items: center; justify-content: center; overflow: hidden; border: 2px solid #fed72b; }
.avatar-preview-circle img { width: 100%; height: 100%; object-fit: cover; }
.avatar-preview-text { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: #71717a; line-height: 1.7; }
.avatar-preview-text strong { font-size: 13px; color: #0a0a0b; }
.avatar-mode-toggle { margin-bottom: 14px; border-radius: 10px; }

.upload-area { border: 2px dashed #cbd5e1; border-radius: 14px; padding: 24px; text-align: center; cursor: pointer; transition: all 0.2s; min-height: 140px; display: flex; align-items: center; justify-content: center; background: #fbfbfe; }
.upload-area:hover { border-color: #fed72b; background: #fefce8; }
.upload-preview { max-width: 120px; max-height: 120px; object-fit: cover; border-radius: 50%; border: 3px solid #fed72b; }
.upload-placeholder { display: flex; flex-direction: column; align-items: center; gap: 8px; color: #71717a; }
.upload-hint { font-size: 11px; color: #a1a1aa; }
.profile-image-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }

.icon-grid-wrap { margin-top: 4px; }
.icon-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(48px, 1fr)); gap: 8px; max-height: 240px; overflow-y: auto; padding: 10px; border: 1px solid #e2e8f0; border-radius: 12px; background: #fbfbfe; }
.icon-tile { aspect-ratio: 1 / 1; display: flex; align-items: center; justify-content: center; border: 2px solid transparent; border-radius: 10px; background: #fff; color: #0a0a0b; cursor: pointer; transition: all 0.15s; font: inherit; padding: 0; }
.icon-tile:hover { border-color: #fed72b; background: #fefce8; color: #0a0a0b; }
.icon-tile.selected { border-color: #0a0a0b; background: #fed72b; color: #0a0a0b; }

.setting-toggle-row { display: flex; align-items: center; justify-content: space-between; padding: 14px; background: #fafafa; border: 1px solid #e2e8f0; border-radius: 12px; }
.setting-toggle-title { display: block; font-size: 13px; color: #0a0a0b; margin-bottom: 2px; }
.setting-toggle-desc { margin: 0; font-size: 12px; color: #71717a; }

.url-field-icon { display: block; }
.url-field-icon.linkedin { color: #0a66c2; }
.url-field-icon.github { color: #0a0a0b; }

/* View details styling */
.view-profile-hero { display: flex; align-items: center; gap: 20px; padding: 8px 0; }
.view-avatar-large { width: 96px; height: 96px; border-radius: 50%; object-fit: cover; border: 3px solid #fed72b; }
.view-avatar-placeholder-large { width: 96px; height: 96px; border-radius: 50%; background: #0a0a0b; color: #fed72b; display: flex; align-items: center; justify-content: center; border: 3px solid #fed72b; }
.view-hero-text { display: flex; flex-direction: column; gap: 4px; flex: 1; }
.view-hero-header-line { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.view-hero-header-line h3 { margin: 0; font-size: 20px; font-weight: 800; color: #0a0a0b; }
.view-role-badge { display: inline-block; font-size: 13px; font-weight: 700; color: #b45309; background: #fef3c7; padding: 3px 12px; border-radius: 9999px; width: fit-content; }
.view-role-en { font-size: 12px; color: #71717a; direction: ltr; text-align: left; }

.resume-view-box { border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; background: #fafafa; }
.resume-view-head { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0; }
.resume-content { font-size: 13px; line-height: 2; color: #3f3f46; }
.resume-content.ltr { direction: ltr; text-align: left; }

.view-links-list { display: flex; flex-direction: column; gap: 8px; }
.view-link-item { display: inline-flex; align-items: center; gap: 10px; padding: 10px 14px; background: #fafafa; border: 1px solid #e2e8f0; border-radius: 10px; text-decoration: none; color: #0a0a0b; font-size: 13px; font-weight: 600; transition: all 0.2s; }
.view-link-item:hover { background: #f4f4f5; border-color: #cbd5e1; }

.meta-field-row { display: flex; justify-content: space-between; font-size: 13px; padding: 10px 0; border-bottom: 1px solid #f1f5f9; }
.meta-field-row:last-child { border-bottom: none; }
.meta-label { color: #71717a; }
.meta-val { font-weight: 700; color: #0a0a0b; }

.mobile-card { background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 14px; margin-bottom: 10px; width: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
.mobile-card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.mobile-card-thumb { width: 44px; height: 44px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.mobile-card-thumb-placeholder { width: 44px; height: 44px; border-radius: 50%; background: #f4f4f5; display: flex; align-items: center; justify-content: center; color: #71717a; flex-shrink: 0; }
.mobile-card-title { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.mobile-card-title strong { font-size: 13px; color: #0a0a0b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mobile-card-role { font-size: 11px; color: #71717a; }
.mobile-card-footer { display: flex; align-items: center; justify-content: space-between; padding-top: 10px; border-top: 1px solid #f1f5f9; }
.mobile-card-actions { display: flex; gap: 2px; }
.mobile-search { margin-left: 8px; }

@media (max-width: 900px) {
  .page-header { flex-direction: column; align-items: stretch; gap: 14px; }
  .page-header .q-btn { width: 100%; justify-content: center; min-height: 42px; }
}

@media (max-width: 600px) {
  .form-row { grid-template-columns: 1fr; }
  .table-card { overflow-x: auto; }
  .view-profile-hero { flex-direction: column; text-align: center; align-items: center; gap: 14px; }
  .view-hero-header-line { flex-direction: column; align-items: center; gap: 6px; }
}

@media (max-width: 480px) {
  .table-card .mobile-search { width: 100% !important; margin: 0 !important; }
  .template-row .q-btn-toggle,
  .avatar-mode-toggle { flex-direction: column; }
}

@media (max-width: 320px) {
  .mobile-card { padding: 10px 8px; border-radius: 12px; }
  .mobile-card-thumb, .mobile-card-thumb-placeholder { width: 36px; height: 36px; }
  .view-avatar-large, .view-avatar-placeholder-large { width: 64px; height: 64px; }
  .avatar-preview-row { flex-direction: column; align-items: center; text-align: center; gap: 8px; }
  .setting-toggle-row { flex-direction: column; align-items: flex-start; gap: 8px; }
  .icon-grid { grid-template-columns: repeat(auto-fill, minmax(40px, 1fr)); padding: 6px; }
}
</style>

<template>
  <div class="admin-settings">
    <!-- Top Hero Header -->
    <div class="settings-top-hero">
      <div class="settings-hero-titles">
        <div class="hero-badge">
          <span class="badge-dot"></span>
          <span>پیکربندی هویت و کنترل عمومی سیستم</span>
        </div>
        <h2>تنظیمات کلی وب‌سایت</h2>
        <p>مدیریت مشخصات برند، شماره‌های تماس فوتر، ویجت شناور پشتیبانی، مدیریت محتوای بصری و امنیت ادمین‌ها</p>
      </div>
      <div class="settings-hero-action">
        <a href="/" target="_blank" class="btn-brand-dark">
          <span>پیش‌نمایش زنده وب‌سایت</span>
          <q-icon name="open_in_new" size="16px" />
        </a>
      </div>
    </div>

    <!-- Navigation Tabs Bar -->
    <div class="settings-tabs-bar">
      <button
        type="button"
        class="settings-tab-btn"
        :class="{ active: activeTab === 'identity' }"
        @click="activeTab = 'identity'"
      >
        <q-icon name="public" size="18px" />
        <span>هویت سایت و تماس فوتر</span>
      </button>

      <button
        type="button"
        class="settings-tab-btn"
        :class="{ active: activeTab === 'quick_widget' }"
        @click="activeTab = 'quick_widget'"
      >
        <q-icon name="support_agent" size="18px" />
        <span>ویجت دسترسی سریع</span>
      </button>

      <button
        type="button"
        class="settings-tab-btn"
        :class="{ active: activeTab === 'cms_hub' }"
        @click="activeTab = 'cms_hub'"
      >
        <q-icon name="dashboard_customize" size="18px" />
        <span>مدیریت بصری صفحات (CMS)</span>
      </button>

      <button
        type="button"
        class="settings-tab-btn"
        :class="{ active: activeTab === 'security' }"
        @click="activeTab = 'security'"
      >
        <q-icon name="security" size="18px" />
        <span>امنیت و حساب کاربری</span>
      </button>
    </div>

    <!-- TAB 1: Site Identity & Contact Information -->
    <div v-show="activeTab === 'identity'" class="settings-tab-pane animate-in">
      <div class="settings-bento-grid">
        <!-- Card 1: Core Brand Info -->
        <div class="settings-bento-card">
          <div class="bento-card-header">
            <div class="bento-icon-bubble">
              <q-icon name="business" size="20px" />
            </div>
            <div>
              <h4>مشخصات برند و فوتر سایت</h4>
              <p>عناوین رسمی و متن معرفی که در پایین تمام صفحات سایت نمایش داده می‌شوند</p>
            </div>
          </div>
          <div class="bento-card-body">
            <q-input v-model="siteSettings.site_name" outlined label="نام رسمی وب‌سایت*" placeholder="سرزمین کهکشان هوشمند" />
            <div style="margin-top: 16px;">
              <q-input v-model="siteSettings.footer_description" outlined label="متن معرفی و بیانیه ارزش فوتر" type="textarea" rows="2" placeholder="پلتفرم جامع مهندسی نرم‌افزار، مقیاس‌پذیری و سامانه‌های سازمانی" />
            </div>
            <div style="margin-top: 16px;">
              <q-input v-model="siteSettings.footer_copyright" outlined label="متن حق نشر (کپی‌رایت) فوتر" placeholder="© ۱۴۰۵ تمامی حقوق مادی و معنوی متعلق به سرزمین کهکشان هوشمند است." />
            </div>
          </div>
        </div>

        <!-- Card 2: Contact Details -->
        <div class="settings-bento-card">
          <div class="bento-card-header">
            <div class="bento-icon-bubble">
              <q-icon name="contact_phone" size="20px" />
            </div>
            <div>
              <h4>اطلاعات تماس رسمی و پشتیبانی</h4>
              <p>شماره تلفن‌ها و راه‌های ارتباطی درج شده در فوتر و صفحه ارتباط با ما</p>
            </div>
          </div>
          <div class="bento-card-body">
            <div class="form-row">
              <q-input v-model="siteSettings.footer_contact_phone" outlined label="شماره تلفن تماس سازمانی" placeholder="۰۲۱ - ۸۸۹۰ ۱۲۳۴" dir="ltr" input-style="direction: ltr; text-align: left;" />
              <q-input v-model="siteSettings.footer_contact_email" outlined label="پست الکترونیکی (ایمیل)" placeholder="contact@smartgalaxy.land" dir="ltr" input-style="direction: ltr; text-align: left;" />
            </div>
            <div style="margin-top: 16px;">
              <q-input v-model="siteSettings.footer_contact_address" outlined label="نشانی پستی دفتر مرکزی" placeholder="تهران، خیابان ولیعصر..." />
            </div>
          </div>
        </div>

        <!-- Card 3: Header Action Button (CTA) -->
        <div class="settings-bento-card full-span">
          <div class="bento-card-header">
            <div class="bento-icon-bubble">
              <q-icon name="touch_app" size="20px" />
            </div>
            <div>
              <h4>دکمه اقدام سربرگ (Header CTA Button)</h4>
              <p>متن و مقصد کلیک دکمه اصلی موجود در بالای تمام صفحات وب‌سایت</p>
            </div>
          </div>
          <div class="bento-card-body">
            <div class="form-row">
              <q-input v-model="siteSettings.header_cta_label" outlined label="عنوان دکمه هدر" placeholder="شروع همکاری" />
              <q-input v-model="siteSettings.header_cta_link" outlined label="لینک مقصد دکمه" placeholder="#sec-contact یا /contact" input-class="url-input" />
            </div>
          </div>
        </div>
      </div>

      <!-- Action Button Row -->
      <div class="settings-action-bar">
        <button type="button" class="btn-pill-save-brand" :disabled="siteSaving" @click="saveSiteSettings">
          <span class="btn-icon-bubble">
            <q-spinner-dots v-if="siteSaving" size="14px" />
            <q-icon v-else name="save" size="16px" />
          </span>
          <span>{{ siteSaving ? 'در حال ذخیره‌سازی...' : 'ذخیره تنظیمات هویت سایت' }}</span>
        </button>
      </div>
    </div>

    <!-- TAB 2: Quick Floating Widget -->
    <div v-show="activeTab === 'quick_widget'" class="settings-tab-pane animate-in">
      <div class="settings-bento-grid">
        <div class="settings-bento-card full-span">
          <div class="bento-card-header">
            <div class="bento-icon-bubble">
              <q-icon name="chat" size="20px" />
            </div>
            <div>
              <h4>ویجت شناور دسترسی سریع و پشتیبانی</h4>
              <p>دکمه شناور گوشه سایت جهت برقراری تماس سریع تلفنی، پیام‌رسان تلگرام، واتساپ و مشاوره آنلاین</p>
            </div>
          </div>
          <div class="bento-card-body">
            <div class="setting-toggle-card">
              <div>
                <strong>نمایش ویجت شناور در سایت</strong>
                <p>در صورت غیرفعال بودن، دکمه شناور در گوشه پایین صفحات سایت مخفی می‌شود</p>
              </div>
              <q-toggle v-model="siteSettings.quick_is_enabled" color="primary" />
            </div>

            <div class="form-row" style="margin-top: 20px;">
              <q-input v-model="siteSettings.quick_phone" outlined label="شماره تماس مستقیم" placeholder="02188901234" dir="ltr" input-style="direction: ltr; text-align: left;" />
              <q-input v-model="siteSettings.quick_phone_label" outlined label="عنوان دکمه تماس" placeholder="تماس تلفنی مستقیم" />
            </div>

            <div class="form-row" style="margin-top: 16px;">
              <q-input v-model="siteSettings.quick_telegram" outlined label="لینک یا آیدی تلگرام" placeholder="https://t.me/yourid" dir="ltr" input-style="direction: ltr; text-align: left;" />
              <q-input v-model="siteSettings.quick_telegram_label" outlined label="عنوان دکمه تلگرام" placeholder="پشتیبانی تلگرام" />
            </div>

            <div class="form-row" style="margin-top: 16px;">
              <q-input v-model="siteSettings.quick_whatsapp" outlined label="شماره واتساپ" placeholder="09120000000" dir="ltr" input-style="direction: ltr; text-align: left;" />
              <q-input v-model="siteSettings.quick_cta_label" outlined label="عنوان دکمه اقدام مشاوره" placeholder="درخواست مشاوره فوری" />
            </div>

            <div style="margin-top: 16px;">
              <q-input v-model="siteSettings.quick_cta_link" outlined label="لینک دکمه مشاوره" placeholder="/contact یا #sec-contact" input-class="url-input" />
            </div>
          </div>
        </div>
      </div>

      <!-- Action Button Row -->
      <div class="settings-action-bar">
        <button type="button" class="btn-pill-save-brand" :disabled="quickSaving" @click="saveQuickSettings">
          <span class="btn-icon-bubble">
            <q-spinner-dots v-if="quickSaving" size="14px" />
            <q-icon v-else name="save" size="16px" />
          </span>
          <span>{{ quickSaving ? 'در حال ذخیره‌سازی...' : 'ذخیره تنظیمات ویجت شناور' }}</span>
        </button>
      </div>
    </div>

    <!-- TAB 3: Visual CMS Page Editor Hub -->
    <div v-show="activeTab === 'cms_hub'" class="settings-tab-pane animate-in">
      <div class="cms-hub-intro">
        <div class="cms-hub-badge">
          <span class="badge-dot"></span>
          <span>ویرایشگر درون‌صفحه‌ای اختصاصی (In-Page Visual CMS)</span>
        </div>
        <h3>مرکز مدیریت محتوا و صفحات وب‌سایت</h3>
        <p>شما می‌توانید با ورود به هر صفحه به عنوان مدیر، تمامی متون، عکس‌ها، کارت‌ها و عناوین را مستقیماً ویرایش و آنی ذخیره کنید.</p>
      </div>

      <div class="cms-cards-grid">
        <!-- Page 1: Home -->
        <div class="cms-card">
          <div class="cms-card-icon">
            <q-icon name="home" size="22px" />
          </div>
          <div class="cms-card-content">
            <h4>صفحه اصلی (خانه)</h4>
            <p>ویرایش هیرو، عکس شاخص برنامه‌نویسی، خدمات و کارت‌ها، گالری پروژه‌ها، آمار و بنر همکاری CTA</p>
            <div class="cms-card-actions">
              <a href="/" target="_blank" class="btn-cms-open">
                <span>ویرایش درون‌صفحه‌ای</span>
                <q-icon name="arrow_back" size="16px" />
              </a>
            </div>
          </div>
        </div>

        <!-- Page 2: About -->
        <div class="cms-card">
          <div class="cms-card-icon">
            <q-icon name="info" size="22px" />
          </div>
          <div class="cms-card-content">
            <h4>صفحه درباره ما</h4>
            <p>هدر، مأموریت‌ها و چشم‌انداز، مسیر پیشرفت، مزایای اعتماد و بنر دعوت به همکاری</p>
            <div class="cms-card-actions">
              <a href="/about" target="_blank" class="btn-cms-open">
                <span>ویرایش درون‌صفحه‌ای</span>
                <q-icon name="arrow_back" size="16px" />
              </a>
            </div>
          </div>
        </div>

        <!-- Page 3: Contact -->
        <div class="cms-card">
          <div class="cms-card-icon">
            <q-icon name="contact_support" size="22px" />
          </div>
          <div class="cms-card-content">
            <h4>صفحه ارتباط با ما</h4>
            <p>هدر، عنوان و زیرعنوان فرم، متن دکمه ارسال، راه‌های ارتباطی و کارت در کنار شما هستیم</p>
            <div class="cms-card-actions">
              <a href="/contact" target="_blank" class="btn-cms-open">
                <span>ویرایش درون‌صفحه‌ای</span>
                <q-icon name="arrow_back" size="16px" />
              </a>
            </div>
          </div>
        </div>

        <!-- Page 4: Products -->
        <div class="cms-card">
          <div class="cms-card-icon">
            <q-icon name="inventory_2" size="22px" />
          </div>
          <div class="cms-card-content">
            <h4>محصولات و کاتالوگ</h4>
            <p>تایتل و برچسب صفحه، فیلتر دسته‌ها، پیام وضعیت خالی، و عناوین بخش‌های صفحه محصول</p>
            <div class="cms-card-actions">
              <a href="/products" target="_blank" class="btn-cms-open">
                <span>ویرایش درون‌صفحه‌ای</span>
                <q-icon name="arrow_back" size="16px" />
              </a>
              <router-link to="/admin/catalogs" class="btn-cms-link">مدیریت کاتالوگ‌ها</router-link>
            </div>
          </div>
        </div>

        <!-- Page 5: Solutions -->
        <div class="cms-card">
          <div class="cms-card-icon">
            <q-icon name="menu_book" size="22px" />
          </div>
          <div class="cms-card-content">
            <h4>راهکارها و مقالات</h4>
            <p>تایتل و برچسب سربرگ، پیام وضعیت خالی، و عناوین بلوک‌های اختصاصی مطالعه مقاله</p>
            <div class="cms-card-actions">
              <a href="/solutions" target="_blank" class="btn-cms-open">
                <span>ویرایش درون‌صفحه‌ای</span>
                <q-icon name="arrow_back" size="16px" />
              </a>
              <router-link to="/admin/solutions" class="btn-cms-link">مدیریت مقالات</router-link>
            </div>
          </div>
        </div>

        <!-- Page 6: Header & Footer -->
        <div class="cms-card">
          <div class="cms-card-icon">
            <q-icon name="web" size="22px" />
          </div>
          <div class="cms-card-content">
            <h4>هدر، فوتر و ناوبری</h4>
            <p>لوگو، منوی اصلی، دکمه‌های اقدام، شبکه‌های اجتماعی، آدرس و شماره‌های تماس فوتر</p>
            <div class="cms-card-actions">
              <a href="/" target="_blank" class="btn-cms-open">
                <span>ویرایش در صفحه اصلی</span>
                <q-icon name="arrow_back" size="16px" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 4: Security, Admin Accounts & Appearance -->
    <div v-show="activeTab === 'security'" class="settings-tab-pane animate-in">
      <div class="settings-bento-grid">
        <!-- Profile Card -->
        <div class="settings-bento-card">
          <div class="bento-card-header">
            <div class="bento-icon-bubble">
              <q-icon name="account_circle" size="20px" />
            </div>
            <div>
              <h4>مشخصات حساب کاربری من</h4>
              <p>تغییر نام، نام کاربری و عکس پروفایل ادمین فعلی</p>
            </div>
          </div>
          <div class="bento-card-body">
            <div class="profile-avatar-row">
              <div class="avatar-wrapper" @click="showAvatarDialog = true">
                <img v-if="profileForm.avatar" :src="profileForm.avatar" class="avatar-img" loading="lazy" decoding="async" />
                <div v-else class="avatar-placeholder">
                  <q-icon name="person" size="36px" />
                </div>
                <div class="avatar-overlay">
                  <q-icon name="camera_alt" size="18px" />
                </div>
              </div>
              <div class="avatar-desc">
                <strong>تصویر نمایه کاربری</strong>
                <span>کلیک برای تغییر عکس از فایل یا دوربین</span>
              </div>
            </div>

            <q-form ref="profileFormRef" @submit.prevent="saveProfile" class="profile-form">
              <div class="form-row">
                <q-input v-model="profileForm.full_name" outlined label="نام کامل*" :rules="[val => !!val || 'نام کامل الزامی است', val => val.length >= 2 || 'حداقل ۲ کاراکتر وارد کنید', val => !/\d/.test(val) || 'نام نباید شامل عدد باشد']" />
                <q-input v-model="profileForm.username" outlined label="نام کاربری*" :rules="[val => !!val || 'نام کاربری الزامی است', val => val.length >= 3 || 'حداقل ۳ کاراکتر وارد کنید']" />
              </div>
              <div style="margin-top: 14px;">
                <button type="submit" class="btn-pill-save-brand" :disabled="profileSaving">
                  <span class="btn-icon-bubble">
                    <q-spinner-dots v-if="profileSaving" size="14px" />
                    <q-icon v-else name="save" size="16px" />
                  </span>
                  <span>{{ profileSaving ? 'در حال ذخیره‌سازی...' : 'ذخیره پروفایل' }}</span>
                </button>
              </div>
            </q-form>
          </div>
        </div>

        <!-- Password Change Card -->
        <div class="settings-bento-card">
          <div class="bento-card-header">
            <div class="bento-icon-bubble">
              <q-icon name="lock" size="20px" />
            </div>
            <div>
              <h4>تغییر رمز عبور</h4>
              <p>بروزرسانی گذرواژه عبور برای امنیت حساب</p>
            </div>
          </div>
          <div class="bento-card-body">
            <q-form ref="passwordFormRef" @submit.prevent="changePassword" class="password-form">
              <q-input v-model="passwordForm.current_password" outlined label="رمز عبور فعلی*" type="password" :rules="[val => !!val || 'رمز عبور فعلی الزامی است']" />
              <div style="margin-top: 14px;">
                <q-input v-model="passwordForm.new_password" outlined label="رمز عبور جدید*" type="password" :rules="[val => !!val || 'رمز عبور جدید الزامی است']" />
              </div>
              <div style="margin-top: 14px;">
                <q-input v-model="passwordForm.confirm_password" outlined label="تکرار رمز عبور جدید*" type="password" :rules="[val => !!val || 'تکرار رمز عبور الزامی است', val => val === passwordForm.new_password || 'رمزها مطابقت ندارند']" />
              </div>
              <div style="margin-top: 14px;">
                <button type="submit" class="btn-brand-yellow-pill" :disabled="passwordSaving">
                  <q-icon name="key" size="16px" />
                  <span>{{ passwordSaving ? 'در حال ثبت...' : 'تغییر رمز عبور' }}</span>
                </button>
              </div>
            </q-form>
          </div>
        </div>

        <!-- Admins Management Card -->
        <div class="settings-bento-card full-span">
          <div class="bento-card-header" style="justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 14px;">
              <div class="bento-icon-bubble">
                <q-icon name="group" size="20px" />
              </div>
              <div>
                <h4>مدیریت حساب‌های مدیران سیستم</h4>
                <p>لیست حساب‌های مجاز به ورود به پنل مدیریت سامانه</p>
              </div>
            </div>
            <button type="button" class="btn-brand-yellow-pill" @click="showAdminDialog = true">
              <q-icon name="add" size="16px" />
              <span>افزودن ادمین جدید</span>
            </button>
          </div>
          <div class="bento-card-body">
            <div class="admins-grid">
              <div v-for="a in admins" :key="a.id" class="admin-item-card">
                <div class="admin-item-avatar">
                  <img v-if="a.avatar || a.profileImage" :src="a.avatar || a.profileImage" loading="lazy" decoding="async" />
                  <div v-else class="admin-avatar-placeholder"><q-icon name="person" size="24px" /></div>
                </div>
                <div class="admin-item-details">
                  <strong>{{ a.full_name || a.fullName || a.username }}</strong>
                  <span class="admin-item-user">@{{ a.username }}</span>
                  <span class="role-pill" :class="{ main: (a.roles || []).includes('admin') }">
                    {{ (a.roles || []).includes('admin') ? 'مدیر کل' : 'ادمین محدود' }}
                  </span>
                </div>
                <div class="admin-item-actions">
                  <q-btn v-if="a.id !== currentAdminId" flat round dense icon="delete" color="negative" size="sm" @click="confirmDeleteAdmin(a)">
                    <q-tooltip>حذف حساب کاربری</q-tooltip>
                  </q-btn>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Appearance & Theme Card -->
        <div class="settings-bento-card full-span">
          <div class="bento-card-header">
            <div class="bento-icon-bubble">
              <q-icon name="dark_mode" size="20px" />
            </div>
            <div>
              <h4>تنظیمات پوسته و ظاهر پنل</h4>
              <p>شخصی‌سازی حالت روشن یا تیره نمایش کنترل پنل</p>
            </div>
          </div>
          <div class="bento-card-body">
            <div class="setting-toggle-card">
              <div>
                <strong>حالت تاریک پنل مدیریت (Dark Mode)</strong>
                <p>تغییر ظاهر رابط کاربری پنل ادمین به تم تیره شب</p>
              </div>
              <q-toggle v-model="darkMode" @update:model-value="toggleDarkMode" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Avatar Dialog -->
    <q-dialog v-model="showAvatarDialog" persistent>
      <q-card class="avatar-dialog">
        <q-card-section class="dialog-header">
          <h3>تغییر تصویر نمایه</h3>
          <q-btn flat round dense icon="close" @click="closeAvatarDialog" />
        </q-card-section>
        <q-card-section class="avatar-dialog-body">
          <div class="avatar-options">
            <button type="button" class="btn-pill-subtle" @click="$refs.avatarFileInput.click()">
              <q-icon name="upload" size="18px" />
              <span>انتخاب از فایل</span>
            </button>
            <button type="button" class="btn-pill-subtle" @click="startCamera">
              <q-icon name="camera_alt" size="18px" />
              <span>عکاسی با دوربین</span>
            </button>
          </div>
          <input ref="avatarFileInput" type="file" accept="image/*" style="display: none" @change="onFileSelect" />

          <div v-if="cameraActive" class="camera-container">
            <video ref="cameraVideo" autoplay playsinline class="camera-video"></video>
            <canvas ref="cameraCanvas" style="display: none"></canvas>
            <button type="button" class="btn-brand-yellow-pill" @click="capturePhoto">
              <q-icon name="camera" size="16px" />
              <span>ثبت عکس</span>
            </button>
          </div>

          <div v-if="avatarPreview" class="avatar-preview-section">
            <img :src="avatarPreview" class="avatar-preview-img" />
            <div class="avatar-preview-actions">
              <button type="button" class="btn-pill-cancel" @click="closeAvatarDialog">انصراف</button>
              <button type="button" class="btn-brand-yellow-pill" :disabled="avatarSaving" @click="confirmAvatar">
                <span>{{ avatarSaving ? 'در حال ذخیره...' : 'تأیید و ذخیره' }}</span>
              </button>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Create Admin Dialog -->
    <q-dialog v-model="showAdminDialog" persistent>
      <q-card class="dialog-card">
        <q-card-section class="dialog-header">
          <h3>افزودن ادمین جدید</h3>
          <q-btn flat round dense icon="close" @click="showAdminDialog = false" />
        </q-card-section>
        <q-card-section>
          <q-form ref="adminFormRef" @submit.prevent="createNewAdmin" class="dialog-form">
            <q-input v-model="newAdminForm.full_name" outlined label="نام کامل*" :rules="[val => !!val || 'نام کامل الزامی است', val => val.length >= 2 || 'حداقل ۲ کاراکتر وارد کنید', val => !/\d/.test(val) || 'نام نباید شامل عدد باشد']" />
            <q-input v-model="newAdminForm.username" outlined label="نام کاربری*" :rules="[val => !!val || 'نام کاربری الزامی است', val => val.length >= 3 || 'حداقل ۳ کاراکتر وارد کنید']" />
            <q-input v-model="newAdminForm.password" outlined label="رمز عبور*" type="password" :rules="[val => !!val || 'رمز عبور الزامی است']" />
            <q-select v-model="newAdminForm.role" :options="roleOptions" emit-value map-options outlined label="نقش دسترسی" />
            <div class="dialog-actions">
              <button type="button" class="btn-pill-cancel" @click="showAdminDialog = false">انصراف</button>
              <button type="submit" class="btn-brand-yellow-pill" :disabled="adminSaving">
                <span>{{ adminSaving ? 'در حال ایجاد...' : 'ایجاد حساب ادمین' }}</span>
              </button>
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useQuasar } from 'quasar'
import { useAuth } from 'src/composables/useAuth'
import api from 'src/services/api'

const $q = useQuasar()
const route = useRoute()
const { admin: currentAdmin, updateAdminData } = useAuth()

const validTabs = ['identity', 'quick_widget', 'cms_hub', 'security']
const initialTab = (route.query.tab && validTabs.includes(route.query.tab)) ? route.query.tab : 'identity'
const activeTab = ref(initialTab) // 'identity' | 'quick_widget' | 'cms_hub' | 'security'

watch(() => route.query.tab, (newTab) => {
  if (newTab && validTabs.includes(newTab)) {
    activeTab.value = newTab
  }
})

// Site settings state
const siteSettings = ref({
  site_name: '',
  footer_description: '',
  footer_contact_phone: '',
  footer_contact_email: '',
  footer_contact_address: '',
  footer_copyright: '',
  header_cta_label: '',
  header_cta_link: '',
  quick_is_enabled: true,
  quick_phone: '',
  quick_phone_label: '',
  quick_telegram: '',
  quick_telegram_label: '',
  quick_whatsapp: '',
  quick_cta_label: '',
  quick_cta_link: '',
})
const siteSaving = ref(false)
const quickSaving = ref(false)

async function loadSiteSettings () {
  try {
    const res = await api.get('/api/site')
    const s = res.data?.data?.settings || {}
    siteSettings.value = {
      site_name: s.site_name || '',
      footer_description: s.footer_description || '',
      footer_contact_phone: s.footer_contact_phone || '',
      footer_contact_email: s.footer_contact_email || '',
      footer_contact_address: s.footer_contact_address || '',
      footer_copyright: s.footer_copyright || '',
      header_cta_label: s.header_cta_label || '',
      header_cta_link: s.header_cta_link || '',
      quick_is_enabled: s.quick_is_enabled === 'true' || s.quick_is_enabled === true,
      quick_phone: s.quick_phone || '',
      quick_phone_label: s.quick_phone_label || '',
      quick_telegram: s.quick_telegram || '',
      quick_telegram_label: s.quick_telegram_label || '',
      quick_whatsapp: s.quick_whatsapp || '',
      quick_cta_label: s.quick_cta_label || '',
      quick_cta_link: s.quick_cta_link || '',
    }
  } catch (e) {
    console.error('Failed to load site settings', e)
  }
}

async function saveSiteSettings () {
  siteSaving.value = true
  try {
    await api.put('/api/site/admin/settings', {
      site_name: siteSettings.value.site_name,
      footer_description: siteSettings.value.footer_description,
      footer_contact_phone: siteSettings.value.footer_contact_phone,
      footer_contact_email: siteSettings.value.footer_contact_email,
      footer_contact_address: siteSettings.value.footer_contact_address,
      footer_copyright: siteSettings.value.footer_copyright,
      header_cta_label: siteSettings.value.header_cta_label,
      header_cta_link: siteSettings.value.header_cta_link,
    })
    $q.notify({ type: 'positive', message: 'تنظیمات کلی وب‌سایت با موفقیت ذخیره شد' })
  } catch (e) {
    $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در ذخیره تنظیمات' })
  } finally {
    siteSaving.value = false
  }
}

async function saveQuickSettings () {
  quickSaving.value = true
  try {
    await api.put('/api/site/admin/settings', {
      quick_is_enabled: siteSettings.value.quick_is_enabled ? 'true' : 'false',
      quick_phone: siteSettings.value.quick_phone,
      quick_phone_label: siteSettings.value.quick_phone_label,
      quick_telegram: siteSettings.value.quick_telegram,
      quick_telegram_label: siteSettings.value.quick_telegram_label,
      quick_whatsapp: siteSettings.value.quick_whatsapp,
      quick_cta_label: siteSettings.value.quick_cta_label,
      quick_cta_link: siteSettings.value.quick_cta_link,
    })
    $q.notify({ type: 'positive', message: 'تنظیمات ویجت شناور با موفقیت ذخیره شد' })
  } catch (e) {
    $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در ذخیره تنظیمات ویجت' })
  } finally {
    quickSaving.value = false
  }
}

// Profile & Admin State
const profileForm = ref({ full_name: '', username: '', avatar: null })
const profileFormRef = ref(null)
const profileSaving = ref(false)

const showAvatarDialog = ref(false)
const cameraActive = ref(false)
const avatarPreview = ref(null)
const avatarSaving = ref(false)
const cameraVideo = ref(null)
const cameraCanvas = ref(null)
const avatarFileInput = ref(null)
let cameraStream = null
let avatarFile = null

const passwordForm = ref({ current_password: '', new_password: '', confirm_password: '' })
const passwordFormRef = ref(null)
const passwordSaving = ref(false)

const admins = ref([])
const showAdminDialog = ref(false)
const adminSaving = ref(false)
const newAdminForm = ref({ full_name: '', username: '', password: '', role: 'admin' })
const adminFormRef = ref(null)
const roleOptions = [
  { label: 'ادمین اصلی', value: 'admin' },
  { label: 'ادمین محدود', value: 'limited' },
]

const darkMode = ref(localStorage.getItem('admin_dark_mode') === 'true')
const currentAdminId = ref(currentAdmin.value?.id)

function toggleDarkMode (val) {
  localStorage.setItem('admin_dark_mode', val)
  document.documentElement.classList.toggle('dark', val)
}

function onFileSelect (e) {
  const file = e.target.files[0]
  if (!file) return
  avatarFile = file
  avatarPreview.value = URL.createObjectURL(file)
  stopCamera()
}

async function startCamera () {
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
    cameraActive.value = true
    await new Promise(r => setTimeout(r, 100))
    if (cameraVideo.value) {
      cameraVideo.value.srcObject = cameraStream
    }
  } catch (e) {
    $q.notify({ type: 'negative', message: 'دسترسی به دوربین امکان‌پذیر نیست' })
  }
}

function capturePhoto () {
  const video = cameraVideo.value
  const canvas = cameraCanvas.value
  if (!video || !canvas) return
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  const ctx = canvas.getContext('2d')
  ctx.drawImage(video, 0, 0)
  canvas.toBlob(blob => {
    avatarFile = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' })
    avatarPreview.value = URL.createObjectURL(blob)
    stopCamera()
  }, 'image/jpeg', 0.9)
}

function stopCamera () {
  cameraActive.value = false
  if (cameraStream) {
    cameraStream.getTracks().forEach(t => t.stop())
    cameraStream = null
  }
}

function closeAvatarDialog () {
  showAvatarDialog.value = false
  stopCamera()
  avatarPreview.value = null
  avatarFile = null
}

async function confirmAvatar () {
  if (!avatarFile) return
  avatarSaving.value = true
  try {
    const fd = new FormData()
    fd.append('avatar', avatarFile)
    const res = await api.put('/api/auth/profile', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    updateAdminData(res.data.data)
    profileForm.value.avatar = res.data.data.avatar
    $q.notify({ type: 'positive', message: 'تصویر پروفایل با موفقیت بروزرسانی شد' })
    closeAvatarDialog()
  } catch (e) {
    $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در بروزرسانی تصویر' })
  } finally {
    avatarSaving.value = false
  }
}

async function saveProfile () {
  const valid = await profileFormRef.value.validate()
  if (!valid) return

  profileSaving.value = true
  try {
    const fd = new FormData()
    fd.append('full_name', profileForm.value.full_name)
    fd.append('username', profileForm.value.username)
    const res = await api.put('/api/auth/profile', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    updateAdminData(res.data.data)
    $q.notify({ type: 'positive', message: 'اطلاعات پروفایل با موفقیت ذخیره شد' })
  } catch (e) {
    $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در بروزرسانی' })
  } finally {
    profileSaving.value = false
  }
}

async function changePassword () {
  const valid = await passwordFormRef.value.validate()
  if (!valid) return

  passwordSaving.value = true
  try {
    await api.put('/api/auth/password', {
      current_password: passwordForm.value.current_password,
      new_password: passwordForm.value.new_password,
    })
    passwordForm.value = { current_password: '', new_password: '', confirm_password: '' }
    $q.notify({ type: 'positive', message: 'رمز عبور با موفقیت تغییر یافت' })
  } catch (e) {
    $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در تغییر رمز' })
  } finally {
    passwordSaving.value = false
  }
}

async function loadAdmins () {
  try {
    const res = await api.get('/api/auth/admins')
    admins.value = res.data.data || []
  } catch (e) { /* */ }
}

async function createNewAdmin () {
  const valid = await adminFormRef.value.validate()
  if (!valid) return

  adminSaving.value = true
  try {
    await api.post('/api/auth/admins', newAdminForm.value)
    $q.notify({ type: 'positive', message: 'حساب ادمین جدید ایجاد شد' })
    showAdminDialog.value = false
    newAdminForm.value = { full_name: '', username: '', password: '', role: 'admin' }
    loadAdmins()
  } catch (e) {
    $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در ایجاد ادمین' })
  } finally {
    adminSaving.value = false
  }
}

function confirmDeleteAdmin (a) {
  $q.dialog({
    title: 'حذف حساب ادمین',
    message: `آیا از حذف حساب "${a.full_name}" اطمینان دارید؟`,
    cancel: 'انصراف',
    ok: { label: 'حذف حساب', color: 'negative' },
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/api/auth/admins/${a.id}`)
      $q.notify({ type: 'positive', message: 'ادمین با موفقیت حذف شد' })
      loadAdmins()
    } catch (e) {
      $q.notify({ type: 'negative', message: e.response?.data?.message || 'خطا در حذف' })
    }
  })
}

onMounted(async () => {
  loadSiteSettings()
  try {
    const res = await api.get('/api/auth/profile')
    const p = res.data.data
    profileForm.value = {
      full_name: p.full_name || p.fullName || p.firstName || '',
      username: p.username || '',
      avatar: p.avatar || p.profileImage || null,
    }
  } catch (e) { /* */ }
  loadAdmins()
})

onBeforeUnmount(() => {
  stopCamera()
})
</script>

<style scoped>
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-in { animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) both; }

.admin-settings {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Top Hero Header */
.settings-top-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 28px 32px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 22px;
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04);
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  border-radius: 9999px;
  background: #fefce8;
  border: 1px solid #fef08a;
  font-size: 0.78rem;
  font-weight: 800;
  color: #a16207;
  margin-bottom: 10px;
}

.badge-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #eab308;
  box-shadow: 0 0 0 2px rgba(234, 179, 8, 0.25);
}

.settings-hero-titles h2 {
  font-size: 1.5rem;
  font-weight: 900;
  color: #0a0a0b;
  margin: 0 0 6px;
  letter-spacing: -0.02em;
}

.settings-hero-titles p {
  font-size: 0.88rem;
  color: #71717a;
  margin: 0;
  line-height: 1.6;
}

.btn-brand-dark {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 22px;
  border-radius: 9999px;
  background: #0a0a0b;
  color: #ffffff;
  border: 1.5px solid #262626;
  font-weight: 800;
  font-size: 0.88rem;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.25s ease;
  white-space: nowrap;
}

.btn-brand-dark:hover {
  border-color: #fed72b;
  color: #fed72b;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.2);
  transform: translateY(-1px);
}

/* Tabs Bar */
.settings-tabs-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.settings-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 22px;
  border-radius: 9999px;
  background: #ffffff;
  border: 1.5px solid #e2e8f0;
  color: #52525b;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  white-space: nowrap;
}

.settings-tab-btn:hover {
  border-color: #cbd5e1;
  color: #0a0a0b;
  background: #fbfbfe;
}

.settings-tab-btn.active {
  background: #0a0a0b;
  color: #fed72b;
  border-color: #0a0a0b;
  box-shadow: 0 4px 16px rgba(10, 10, 11, 0.15);
}

.settings-tab-btn.active .q-icon {
  color: #fed72b;
}

/* Bento Grid */
.settings-bento-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.settings-bento-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 22px;
  padding: 26px 28px;
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.03);
  transition: all 0.25s ease;
}

.settings-bento-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 8px 30px -4px rgba(15, 23, 42, 0.06);
}

.settings-bento-card.full-span {
  grid-column: span 2;
}

.bento-card-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 22px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
}

.bento-icon-bubble {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #0a0a0b;
  color: #fed72b;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  border: 1px solid #27272a;
}

.bento-card-header h4 {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0a0a0b;
  margin: 0 0 3px;
  letter-spacing: -0.01em;
}

.bento-card-header p {
  font-size: 0.8rem;
  color: #71717a;
  margin: 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* Action Bar */
.settings-action-bar {
  display: flex;
  justify-content: flex-start;
  margin-top: 20px;
}

/* Setting Toggle Card */
.setting-toggle-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #fafafa;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
}

.setting-toggle-card strong {
  font-size: 0.95rem;
  color: #0a0a0b;
  display: block;
  margin-bottom: 3px;
}

.setting-toggle-card p {
  font-size: 0.82rem;
  color: #71717a;
  margin: 0;
}

/* CMS Hub Styling */
.cms-hub-intro {
  margin-bottom: 20px;
}

.cms-hub-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  border-radius: 9999px;
  background: #f4f4f5;
  border: 1px solid #e4e4e7;
  font-size: 0.78rem;
  font-weight: 800;
  color: #0a0a0b;
  margin-bottom: 8px;
}

.cms-hub-intro h3 {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0a0a0b;
  margin: 0 0 6px;
}

.cms-hub-intro p {
  font-size: 0.88rem;
  color: #71717a;
  margin: 0;
}

.cms-cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.cms-card {
  display: flex;
  gap: 14px;
  padding: 22px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  transition: all 0.25s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
}

.cms-card:hover {
  border-color: #fed72b;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(254, 215, 43, 0.12);
}

.cms-card-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #0a0a0b;
  color: #fed72b;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.cms-card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.cms-card-content h4 {
  font-size: 0.98rem;
  font-weight: 800;
  color: #0a0a0b;
  margin: 0 0 4px;
}

.cms-card-content p {
  font-size: 0.78rem;
  color: #71717a;
  line-height: 1.65;
  margin: 0 0 14px;
  flex: 1;
}

.cms-card-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-cms-open {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  font-weight: 800;
  color: #0a0a0b;
  text-decoration: none;
  background: #f4f4f5;
  padding: 6px 14px;
  border-radius: 9999px;
  transition: all 0.2s ease;
}

.btn-cms-open:hover {
  background: #fed72b;
  color: #0a0a0b;
}

.btn-cms-link {
  font-size: 0.78rem;
  font-weight: 700;
  color: #71717a;
  text-decoration: none;
  transition: color 0.2s;
}

.btn-cms-link:hover {
  color: #0a0a0b;
}

/* Security Profile Styling */
.profile-avatar-row {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 22px;
  padding: 16px;
  background: #fafafa;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
}

.avatar-wrapper {
  position: relative;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  cursor: pointer;
  overflow: hidden;
  border: 2.5px solid #fed72b;
  background: #0a0a0b;
  flex-shrink: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: #fed72b;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  background: rgba(10, 10, 11, 0.6);
  color: #fed72b;
  display: grid;
  place-items: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.avatar-desc strong {
  display: block;
  font-size: 0.95rem;
  color: #0a0a0b;
}

.avatar-desc span {
  font-size: 0.8rem;
  color: #71717a;
}

/* Admins Grid */
.admins-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 14px;
}

.admin-item-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: #fafafa;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
}

.admin-item-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  overflow: hidden;
  background: #0a0a0b;
  color: #fed72b;
  display: grid;
  place-items: center;
  border: 2px solid #fed72b;
  flex-shrink: 0;
}

.admin-item-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.admin-item-details {
  flex: 1;
  min-width: 0;
}

.admin-item-details strong {
  display: block;
  font-size: 0.9rem;
  color: #0a0a0b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.admin-item-user {
  font-size: 0.78rem;
  color: #71717a;
  display: block;
  direction: ltr;
  text-align: right;
}

.role-pill {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 9999px;
  background: #f4f4f5;
  color: #52525b;
  margin-top: 3px;
}

.role-pill.main {
  background: #fefce8;
  color: #a16207;
}

/* Dialogs */
.dialog-card {
  width: 520px;
  max-width: 95vw;
  border-radius: 20px;
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid #f1f5f9;
}

.dialog-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 800;
  color: #0a0a0b;
}

.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px 24px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 10px;
}

.avatar-dialog {
  width: 440px;
  max-width: 95vw;
  border-radius: 20px;
}

.avatar-dialog-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
  align-items: center;
  padding: 20px 24px;
}

.avatar-options {
  display: flex;
  gap: 12px;
  width: 100%;
}

.avatar-options button {
  flex: 1;
}

.camera-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.camera-video {
  width: 100%;
  max-width: 320px;
  border-radius: 14px;
  background: #000;
}

.avatar-preview-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  width: 100%;
}

.avatar-preview-img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #fed72b;
}

.avatar-preview-actions {
  display: flex;
  gap: 12px;
}

@media (max-width: 1024px) {
  .cms-cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .settings-top-hero {
    flex-direction: column;
    align-items: stretch;
    padding: 20px;
    gap: 16px;
  }

  .btn-brand-dark {
    width: 100%;
    justify-content: center;
  }

  .settings-bento-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .settings-bento-card.full-span {
    grid-column: span 1;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .cms-cards-grid {
    grid-template-columns: 1fr;
  }

  .settings-action-bar {
    width: 100%;
  }

  .settings-action-bar .btn-pill-save-brand {
    width: 100%;
    justify-content: center;
    min-height: 42px;
  }

  .dialog-card,
  .avatar-dialog {
    width: 100vw !important;
    max-width: 100vw !important;
    min-width: 0 !important;
    height: 100vh !important;
    max-height: 100vh !important;
    border-radius: 0 !important;
    margin: 0 !important;
  }

  .admins-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .settings-tabs-bar {
    gap: 6px;
  }

  .settings-tab-btn {
    padding: 8px 14px;
    font-size: 0.8rem;
    gap: 6px;
  }

  .settings-bento-card {
    padding: 16px 14px;
    border-radius: 16px;
  }

  .bento-card-header {
    gap: 10px;
    margin-bottom: 16px;
    padding-bottom: 12px;
  }

  .bento-icon-bubble {
    width: 36px;
    height: 36px;
  }
}

@media (max-width: 320px) {
  .settings-top-hero {
    padding: 14px 10px;
  }

  .settings-top-hero h2 {
    font-size: 1.1rem;
  }

  .settings-tabs-bar {
    gap: 4px;
  }

  .settings-tab-btn {
    padding: 6px 10px;
    font-size: 0.72rem;
    gap: 4px;
  }

  .settings-bento-card {
    padding: 12px 10px;
    border-radius: 14px;
  }

  .profile-avatar-row {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 10px;
    padding: 12px;
  }

  .cms-card {
    padding: 14px 10px;
    flex-direction: column;
    gap: 10px;
  }

  .camera-video {
    max-width: 220px;
  }
}
</style>

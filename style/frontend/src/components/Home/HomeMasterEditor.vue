<template>
  <q-dialog
    v-model="isMasterEditorOpen"
    persistent
    maximized
    transition-show="slide-up"
    transition-hide="slide-down"
  >
    <div class="master-modal-root" data-lenis-prevent @wheel.stop>
      <!-- Top Bar -->
      <header class="master-header">
        <div class="header-brand">
          <div class="brand-badge">
            <span class="live-dot"></span>
            <span>ویرایشگر جامع و استاندارد کهکشان هوشمند</span>
          </div>
          <h2 class="header-title">مدیریت جامع محتوای وب‌سایت</h2>
        </div>

        <div class="header-actions">
          <button type="button" class="btn-head-ghost" @click="handleReset" title="بازنشانی تمام داده‌ها به حالت پیش‌فرض">
            <q-icon name="restart_alt" size="18px" />
            <span>بازنشانی پیش‌فرض</span>
          </button>

          <button type="button" class="btn-head-cancel" @click="closeMasterEditor">
            <span>انصراف</span>
          </button>

          <button type="button" class="btn-head-save" :disabled="isSaving" @click="handleSave">
            <q-spinner v-if="isSaving" size="18px" color="dark" />
            <q-icon v-else name="check_circle" size="18px" />
            <span>{{ isSaving ? 'در حال ذخیره‌سازی...' : 'ذخیره و انتشار تغییرات' }}</span>
          </button>
        </div>
      </header>

      <!-- Main Layout: Navigation Sidebar + Content Area -->
      <div class="master-body" data-lenis-prevent>
        <!-- Sidebar Navigation -->
        <aside class="master-sidebar" data-lenis-prevent>
          <div class="sidebar-label">بخش‌های وب‌سایت</div>
          <nav class="sidebar-nav">
            <button
              v-for="tab in TABS"
              :key="tab.id"
              type="button"
              class="nav-tab-btn"
              :class="{ active: activeTab === tab.id }"
              @click="activeTab = tab.id"
            >
              <span class="tab-icon-wrap">
                <q-icon :name="tab.icon" size="20px" />
              </span>
              <div class="tab-info">
                <span class="tab-title">{{ tab.label }}</span>
                <span class="tab-subtitle">{{ tab.desc }}</span>
              </div>
              <span class="tab-active-indicator" v-if="activeTab === tab.id"></span>
            </button>
          </nav>
        </aside>

        <!-- Main Form Panel -->
        <main class="master-content-panel" data-lenis-prevent>
          <div class="content-scrollable">

            <!-- TAB 1: HERO SECTION -->
            <div v-show="activeTab === 'hero'" class="tab-pane">
              <div class="pane-head">
                <h3>بخش هیرو و هویت بصری (Hero Section)</h3>
                <p>تنظیم عنوان شاخص، متن توضیحی، برچسب‌ها، دکمه‌های اقدام و تصویر سه‌بعدی هدر.</p>
              </div>

              <div class="form-grid">
                <div class="form-card full-width">
                  <label class="form-label">برچسب بالای عنوان (Badge)</label>
                  <q-input v-model="form.hero_badge" outlined dense placeholder="استودیو هوشمند معماری ابری و مهندسی نرم‌افزار" class="editor-input" />
                </div>

                <div class="form-card full-width">
                  <label class="form-label">عنوان اصلی صفحه (Hero Headline)</label>
                  <q-input v-model="form.hero_title" outlined type="textarea" autogrow placeholder="عنوان اصلی با اینتر برای شکست خط..." class="editor-input" />
                  <div class="form-hint">برای ایجاد سطر جدید، از دکمه Enter استفاده فرمایید.</div>
                </div>

                <div class="form-card full-width">
                  <label class="form-label">توضیحات هیرو (با ویرایشگر استاندارد)</label>
                  <RichTextEditor
                    v-model="form.hero_description"
                    :min-height="150"
                    placeholder="توضیح کامل توانمندی‌ها..."
                  />
                </div>

                <div class="form-card half-width">
                  <label class="form-label">تصویر یا ویدیوی سه‌بعدی هیرو (URL یا بارگذاری)</label>
                  <div class="image-uploader-row">
                    <video
                      v-if="form.hero_image_url && isVideoUrl(form.hero_image_url)"
                      :src="form.hero_image_url"
                      class="img-preview"
                      autoplay
                      muted
                      loop
                    />
                    <img v-else-if="form.hero_image_url" :src="form.hero_image_url" class="img-preview" alt="" />
                    <div v-else class="img-preview empty">
                      <q-icon name="image" size="24px" />
                    </div>
                    <div class="img-inputs">
                      <q-input v-model="form.hero_image_url" outlined dense placeholder="/images/herosection-video.mp4" class="editor-input mb-2" />
                      <label class="file-upload-btn">
                        <input type="file" accept="image/*,video/*" @change="onHeroFileChange" style="display:none;" />
                        <q-icon name="cloud_upload" size="16px" />
                        <span>انتخاب فایل تصویر یا ویدیو</span>
                      </label>
                    </div>
                  </div>
                </div>

                <div class="form-card half-width">
                  <label class="form-label">متن دکمه اسکرول راهنما</label>
                  <q-input v-model="form.hero_scroll_label" outlined dense placeholder="بررسی توانمندی‌های مهندسی" class="editor-input" />
                </div>

                <!-- Hero Buttons List -->
                <div class="form-card full-width">
                  <div class="sub-head-row">
                    <label class="form-label mb-0">دکمه‌های اقدام هیرو (Hero Action Buttons)</label>
                    <button type="button" class="btn-sub-add" @click="addHeroButton">
                      <q-icon name="add" size="14px" />
                      <span>افزودن دکمه</span>
                    </button>
                  </div>

                  <div class="buttons-editor-list">
                    <div
                      v-for="(btn, bIdx) in form.buttons"
                      :key="bIdx"
                      class="button-editor-row"
                    >
                      <q-input v-model="btn.label" outlined dense label="عنوان دکمه" class="editor-input flex-1" />
                      <q-input v-model="btn.link" outlined dense label="آدرس پیوند (Link)" class="editor-input flex-1" />
                      <q-select
                        v-model="btn.variant"
                        :options="['primary', 'secondary', 'ghost']"
                        outlined
                        dense
                        label="استایل"
                        class="editor-input"
                        style="width: 120px;"
                      />
                      <button type="button" class="btn-row-del" @click="removeHeroButton(bIdx)" title="حذف دکمه">
                        <q-icon name="delete_outline" size="18px" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- TAB 2: SERVICES SECTION -->
            <div v-show="activeTab === 'services'" class="tab-pane">
              <div class="pane-head">
                <h3>بخش خدمات و راهکارهای تخصصی (Services & Solutions)</h3>
                <p>مدیریت کارت‌های سه‌بعدی خدمات، عناوین و ویژگی‌های کلیدی مهندسی.</p>
              </div>

              <div class="form-grid">
                <div class="form-card half-width">
                  <label class="form-label">برچسب بخش خدمات</label>
                  <q-input v-model="form.why_badge" outlined dense class="editor-input" />
                </div>

                <div class="form-card half-width">
                  <label class="form-label">عنوان اصلی بخش خدمات</label>
                  <q-input v-model="form.why_title" outlined dense class="editor-input" />
                </div>

                <div class="form-card full-width">
                  <label class="form-label">توضیح کوتاه سربرگ خدمات</label>
                  <q-input v-model="form.why_description" outlined dense autogrow class="editor-input" />
                </div>

                <!-- 6 Service Cards -->
                <div class="form-card full-width">
                  <div class="sub-head-row">
                    <label class="form-label mb-0">کارت‌های خدمات تخصصی ({{ form.services.length }} کارت)</label>
                    <button type="button" class="btn-sub-add" @click="addServiceCard">
                      <q-icon name="add" size="14px" />
                      <span>افزودن خدمت جدید</span>
                    </button>
                  </div>

                  <div class="cards-accordion">
                    <div
                      v-for="(srv, sIdx) in form.services"
                      :key="sIdx"
                      class="nested-editor-card"
                    >
                      <div class="nested-card-head">
                        <div class="nested-title-badge">
                          <span class="nested-num">۰{{ sIdx + 1 }}</span>
                          <span class="nested-name">{{ srv.title || 'خدمت بدون نام' }}</span>
                        </div>
                        <button type="button" class="btn-row-del" @click="removeServiceCard(sIdx)" title="حذف کارت">
                          <q-icon name="delete_outline" size="18px" />
                        </button>
                      </div>

                      <div class="nested-grid">
                        <div>
                          <label class="nested-label">عنوان خدمت</label>
                          <q-input v-model="srv.title" outlined dense class="editor-input" />
                        </div>
                        <div class="full-width icon-uploader-block">
                          <label class="nested-label">آیکون سه‌بعدی خدمت (آپلود تصویر / آیکون)</label>
                          <div class="icon-uploader-row">
                            <div class="icon-preview-box">
                              <img
                                v-if="srv.iconSrc"
                                :src="srv.iconSrc"
                                alt="آیکون خدمت"
                                class="icon-preview-img"
                                @error="(e) => { e.target.src = '/assets/icons3d/cloud.svg' }"
                              />
                              <q-icon v-else name="image" size="24px" color="grey-6" />
                            </div>

                            <div class="icon-upload-actions">
                              <input
                                :ref="(el) => { if (el) serviceIconInputs[sIdx] = el }"
                                type="file"
                                accept="image/*,.svg"
                                style="display: none;"
                                @change="(e) => onServiceIconUpload(e, sIdx)"
                              />
                              <button
                                type="button"
                                class="btn-upload-icon"
                                :disabled="uploadingServiceIcon[sIdx]"
                                @click="triggerServiceIconUpload(sIdx)"
                              >
                                <q-spinner v-if="uploadingServiceIcon[sIdx]" size="14px" color="primary" />
                                <q-icon v-else name="cloud_upload" size="16px" />
                                <span>{{ uploadingServiceIcon[sIdx] ? 'در حال آپلود...' : 'آپلود آیکون یا تصویر' }}</span>
                              </button>

                              <q-select
                                v-model="srv.iconSrc"
                                :options="PRESET_ICONS"
                                emit-value
                                map-options
                                outlined
                                dense
                                label="انتخاب از آیکون‌های پیش‌فرض ۳D"
                                class="preset-icon-select"
                              />

                              <button
                                v-if="srv.iconSrc"
                                type="button"
                                class="btn-icon-clear"
                                @click="srv.iconSrc = ''"
                                title="حذف آیکون"
                              >
                                <q-icon name="close" size="14px" />
                              </button>
                            </div>
                          </div>
                        </div>
                        <div class="full-width">
                          <label class="nested-label">متن توضیحات کارت</label>
                          <q-input v-model="srv.text" outlined dense autogrow class="editor-input" />
                        </div>
                        <div class="full-width">
                          <label class="nested-label">ویژگی اول</label>
                          <q-input v-model="srv.features[0]" outlined dense class="editor-input mb-2" />
                          <label class="nested-label">ویژگی دوم</label>
                          <q-input v-model="srv.features[1]" outlined dense class="editor-input" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- TAB 3: PROJECTS SHOWCASE -->
            <div v-show="activeTab === 'projects'" class="tab-pane">
              <div class="pane-head">
                <h3>مدیریت بخش و صفحه پروژه‌ها (Projects Showcase)</h3>
                <p>تنظیم پیش‌عنوان (Eyebrow)، عنوان اصلی و متن توضیحات بخش پروژه‌ها، به همراه دسترسی به مدیریت کارت‌ها در پنل ادمین.</p>
              </div>

              <div class="form-grid">
                <div class="form-card half-width">
                  <label class="form-label">برچسب / پیش‌عنوان بخش پروژه‌ها (Eyebrow)</label>
                  <q-input v-model="form.works_eyebrow" outlined dense placeholder="پروژه‌های شاخص" class="editor-input" />
                </div>

                <div class="form-card half-width">
                  <label class="form-label">عنوان اصلی بخش پروژه‌ها</label>
                  <q-input v-model="form.works_title" outlined dense placeholder="معماری سیستم‌های پرترافیک و مقیاس‌پذیر" class="editor-input" />
                </div>

                <div class="form-card full-width">
                  <label class="form-label">متن توضیحات بخش پروژه‌ها</label>
                  <q-input v-model="form.works_description" outlined dense autogrow placeholder="سامانه‌های استراتژیک ملی و سازمانی که با تکیه بر پایداری، سرعت و بالاترین استانداردهای مهندسی نرم‌افزار خلق شده‌اند." class="editor-input" />
                </div>

                <div class="form-card full-width admin-redirect-action">
                  <router-link
                    to="/admin/products"
                    class="btn-admin-nav-brand"
                    @click="closeMasterEditor"
                  >
                    <q-icon name="dashboard" size="18px" />
                    <span>ورود به پنل مدیریت پروژه‌ها</span>
                    <q-icon name="arrow_back" size="16px" />
                  </router-link>
                </div>
              </div>
            </div>

            <!-- TAB 4: ABOUT US & TEAM -->
            <div v-show="activeTab === 'about'" class="tab-pane">
              <div class="pane-head">
                <h3>بخش درباره ما در صفحه اصلی (About Us Section)</h3>
                <p>ویرایش لیبل، عنوان اصلی، متن توضیحات، دکمه اقدام، تصویر سه‌بعدی موشن و نشان‌های شناور بخش درباره ما.</p>
              </div>

              <div class="form-grid">
                <div class="form-card half-width">
                  <label class="form-label">برچسب بالای عنوان (Badge / لیبل)</label>
                  <q-input v-model="form.about.badge" outlined dense placeholder="درباره کهکشان هوشمند" class="editor-input" />
                </div>

                <div class="form-card half-width">
                  <label class="form-label">عنوان اصلی بخش درباره ما (Title)</label>
                  <q-input v-model="form.about.title" outlined dense placeholder="اصالت مهندسی، انضباط سازمانی" class="editor-input" />
                </div>

                <div class="form-card full-width">
                  <label class="form-label">متن توضیحات بخش درباره ما (Text / Description)</label>
                  <RichTextEditor
                    v-model="form.about.desc"
                    :min-height="130"
                    placeholder="متن کامل معرفی، اهداف و رویکرد مهندسی..."
                  />
                </div>

                <div class="form-card half-width">
                  <label class="form-label">عنوان دکمه اقدام (Button Text)</label>
                  <q-input v-model="form.about.button_text" outlined dense placeholder="آشنایی بیشتر با کهکشان هوشمند" class="editor-input" />
                </div>

                <div class="form-card half-width">
                  <label class="form-label">لینک دکمه اقدام (Button Link)</label>
                  <q-input v-model="form.about.button_link" outlined dense placeholder="/about" class="editor-input" />
                </div>

                <!-- About Motion Graphic Image & Uploader -->
                <div class="form-card full-width">
                  <label class="form-label">تصویر سه‌بعدی / گرافیک موشن (Image URL یا بارگذاری فایل)</label>
                  <div class="image-uploader-row">
                    <img v-if="form.about.image" :src="form.about.image" class="img-preview" alt="" />
                    <div v-else class="img-preview empty">
                      <q-icon name="image" size="24px" />
                    </div>
                    <div class="img-inputs">
                      <q-input v-model="form.about.image" outlined dense placeholder="/Modern 3D Tech Dashboard Illustration(1).png" class="editor-input mb-2" />
                      <label class="file-upload-btn">
                        <input type="file" accept="image/*" @change="onAboutFileChange" style="display:none;" />
                        <q-icon name="cloud_upload" size="16px" />
                        <span>انتخاب فایل تصویر موشن</span>
                      </label>
                    </div>
                  </div>
                </div>

                <!-- HUD Floating Status Chips on Graphic -->
                <div class="form-card full-width">
                  <div class="sub-head-row">
                    <label class="form-label mb-0">نشان‌های شناور وضعیت موشن (HUD Chips)</label>
                  </div>
                  <div class="nested-grid q-mt-sm">
                    <div>
                      <label class="nested-label">نشان ۱ - عنوان</label>
                      <q-input v-model="form.about.chip1_label" outlined dense placeholder="معماری امنیتی" class="editor-input" />
                    </div>
                    <div>
                      <label class="nested-label">نشان ۱ - مقدار</label>
                      <q-input v-model="form.about.chip1_val" outlined dense placeholder="Zero-Trust Isolated" class="editor-input" />
                    </div>
                    <div>
                      <label class="nested-label">نشان ۲ - عنوان</label>
                      <q-input v-model="form.about.chip2_label" outlined dense placeholder="لتنسی لبه شبکه" class="editor-input" />
                    </div>
                    <div>
                      <label class="nested-label">نشان ۲ - مقدار</label>
                      <q-input v-model="form.about.chip2_val" outlined dense placeholder="< ۱۵ms Anycast" class="editor-input" />
                    </div>
                    <div>
                      <label class="nested-label">نشان ۳ - عنوان</label>
                      <q-input v-model="form.about.chip3_label" outlined dense placeholder="تضمین پایداری کتبی" class="editor-input" />
                    </div>
                    <div>
                      <label class="nested-label">نشان ۳ - مقدار</label>
                      <q-input v-model="form.about.chip3_val" outlined dense placeholder="SLA ۹۹.۹۹٪ رسمی" class="editor-input" />
                    </div>
                  </div>
                </div>


                <!-- Core Values / Pillars -->
                <div class="form-card full-width">
                  <div class="sub-head-row">
                    <label class="form-label mb-0">ارزش‌ها و ارکان فنی مهندسی ({{ (form.about.values || []).length }} مورد)</label>
                    <button type="button" class="btn-sub-add" @click="addValueItem">
                      <q-icon name="add" size="14px" />
                      <span>افزودن ارزش فنی</span>
                    </button>
                  </div>

                  <div class="cards-accordion">
                    <div
                      v-for="(val, vIdx) in (form.about.values || [])"
                      :key="vIdx"
                      class="nested-editor-card"
                    >
                      <div class="nested-card-head">
                        <span class="nested-name">{{ val.title || 'ارزش فنی' }}</span>
                        <button type="button" class="btn-row-del" @click="removeValueItem(vIdx)">
                          <q-icon name="delete_outline" size="18px" />
                        </button>
                      </div>
                      <div class="nested-grid">
                        <div>
                          <label class="nested-label">عنوان</label>
                          <q-input v-model="val.title" outlined dense class="editor-input" />
                        </div>
                        <div>
                          <label class="nested-label">آیکون متریال</label>
                          <q-input v-model="val.icon" outlined dense placeholder="dns, security, code..." class="editor-input" />
                        </div>
                        <div class="full-width">
                          <label class="nested-label">توضیحات</label>
                          <q-input v-model="val.desc" outlined dense autogrow class="editor-input" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Team Members -->
                <div class="form-card full-width">
                  <div class="sub-head-row">
                    <label class="form-label mb-0">اعضای تیم و معماران ارشد ({{ (form.about.team || []).length }} عضو)</label>
                    <button type="button" class="btn-sub-add" @click="addTeamItem">
                      <q-icon name="add" size="14px" />
                      <span>افزودن عضو تیم</span>
                    </button>
                  </div>

                  <div class="cards-accordion">
                    <div
                      v-for="(tm, tIdx) in (form.about.team || [])"
                      :key="tIdx"
                      class="nested-editor-card"
                    >
                      <div class="nested-card-head">
                        <span class="nested-name">{{ tm.name || 'عضو جدید' }} - {{ tm.role }}</span>
                        <button type="button" class="btn-row-del" @click="removeTeamItem(tIdx)">
                          <q-icon name="delete_outline" size="18px" />
                        </button>
                      </div>
                      <div class="nested-grid">
                        <div>
                          <label class="nested-label">نام و نام خانوادگی</label>
                          <q-input v-model="tm.name" outlined dense class="editor-input" />
                        </div>
                        <div>
                          <label class="nested-label">سمت سازمانی / نقش</label>
                          <q-input v-model="tm.role" outlined dense class="editor-input" />
                        </div>
                        <div>
                          <label class="nested-label">تصویر پرتره</label>
                          <q-input v-model="tm.image" outlined dense placeholder="/images/team/photo.jpg" class="editor-input" />
                        </div>
                        <div class="full-width">
                          <label class="nested-label">بیوگرافی و تخصص</label>
                          <q-input v-model="tm.bio" outlined dense autogrow class="editor-input" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

              </div>
            </div>

            <!-- TAB 5: ARTICLES & BLOG -->
            <div v-show="activeTab === 'articles'" class="tab-pane">
              <div class="pane-head">
                <h3>مدیریت بخش و صفحه مقالات فنی (Articles & Knowledge)</h3>
                <p>تنظیم برچسب (Badge)، عنوان اصلی و متن توضیحات بخش مقالات، به همراه دسترسی به انتشار و مدیریت مقالات در پنل ادمین.</p>
              </div>

              <div class="form-grid">
                <div class="form-card half-width">
                  <label class="form-label">برچسب بالای عنوان (Badge)</label>
                  <q-input v-model="form.articles.badge" outlined dense placeholder="دانش و وبلاگ" class="editor-input" />
                </div>

                <div class="form-card half-width">
                  <label class="form-label">عنوان اصلی بخش مقالات</label>
                  <q-input v-model="form.articles.title" outlined dense placeholder="تازه‌ترین مقالات مهندسی" class="editor-input" />
                </div>

                <div class="form-card full-width">
                  <label class="form-label">متن توضیحات بخش مقالات</label>
                  <q-input v-model="form.articles.desc" outlined dense autogrow placeholder="دیدگاه‌ها و مقالات فنی تیم مهندسی در حوزه‌های معماری ابری، امنیت، طراحی محصول و هوش مصنوعی." class="editor-input" />
                </div>

                <div class="form-card full-width admin-redirect-action">
                  <router-link
                    to="/admin/solutions"
                    class="btn-admin-nav-brand"
                    @click="closeMasterEditor"
                  >
                    <q-icon name="dashboard" size="18px" />
                    <span>ورود به پنل مدیریت مقالات</span>
                    <q-icon name="arrow_back" size="16px" />
                  </router-link>
                </div>
              </div>
            </div>

            <!-- TAB 6: CONTACT & CONSULTATION -->
            <div v-show="activeTab === 'contact'" class="tab-pane">
              <div class="pane-head">
                <h3>بخش تماس، مشاوره و پرسش‌های متداول (Contact & Consultation)</h3>
                <p>ویرایش اطلاعات تماس، آدرس دفتر، ساعات کاری، متن فرم درخواست و سوالات متداول FAQ.</p>
              </div>

              <div class="form-grid">
                <div class="form-card half-width">
                  <label class="form-label">برچسب صفحه تماس (Badge)</label>
                  <q-input v-model="form.contact.badge" outlined dense placeholder="ارتباط مستقیم و مشاوره تخصصی" class="editor-input" />
                </div>

                <div class="form-card half-width">
                  <label class="form-label">عنوان اصلی صفحه تماس</label>
                  <q-input v-model="form.contact.title" outlined dense placeholder="بیایید پروژه نرم‌افزاری و زیرساخت ابری شما را آغاز کنیم" class="editor-input" />
                </div>

                <div class="form-card full-width">
                  <label class="form-label">متن توضیحات صفحه تماس</label>
                  <q-input v-model="form.contact.description" outlined dense autogrow class="editor-input" />
                </div>

                <div class="form-card half-width">
                  <label class="form-label">آدرس ایمیل ارتباط مستقیم</label>
                  <q-input v-model="form.contact.email" outlined dense placeholder="contact@smartgalaxy.land" class="editor-input" />
                </div>

                <div class="form-card half-width">
                  <label class="form-label">شماره تلفن دفتر مهندسی</label>
                  <q-input v-model="form.contact.phone" outlined dense placeholder="۰۲۱ - ۸۸۹۰ ۱۲۳۴" class="editor-input" />
                </div>

                <div class="form-card full-width">
                  <label class="form-label">نشانی کامل دفتر مرکزی</label>
                  <q-input v-model="form.contact.address" outlined dense placeholder="تهران، نلسون ماندلا، بالاتر از میرداماد، برج کهکشان" class="editor-input" />
                </div>

                <div class="form-card half-width">
                  <label class="form-label">ساعات کاری و پاسخ‌گویی</label>
                  <q-input v-model="form.contact.workingHours" outlined dense placeholder="شنبه تا چهارشنبه: ۸:۰۰ الی ۱۸:۰۰" class="editor-input" />
                </div>

                <div class="form-card half-width">
                  <label class="form-label">تضمین زمان پاسخ‌دهی (SLA Response)</label>
                  <q-input v-model="form.contact.slaResponse" outlined dense placeholder="میانگین پاسخ کمتر از ۲ ساعت" class="editor-input" />
                </div>

                <div class="form-card half-width">
                  <label class="form-label">عنوان فرم مشاوره</label>
                  <q-input v-model="form.contact.formTitle" outlined dense placeholder="درخواست جلسه مشاوره و بررسی پروژه" class="editor-input" />
                </div>

                <div class="form-card half-width">
                  <label class="form-label">زیرعنوان فرم مشاوره</label>
                  <q-input v-model="form.contact.formSubtitle" outlined dense placeholder="مشخصات اولیه سازمان خود را ثبت کنید..." class="editor-input" />
                </div>

                <!-- FAQs Editor -->
                <div class="form-card full-width">
                  <div class="sub-head-row">
                    <label class="form-label mb-0">پرسش‌های متداول ({{ (form.contact.faqs || []).length }} پرسش)</label>
                    <button type="button" class="btn-sub-add" @click="addFaqItem">
                      <q-icon name="add" size="14px" />
                      <span>افزودن سوال جدید</span>
                    </button>
                  </div>

                  <div class="cards-accordion">
                    <div
                      v-for="(faq, fIdx) in (form.contact.faqs || [])"
                      :key="fIdx"
                      class="nested-editor-card"
                    >
                      <div class="nested-card-head">
                        <span class="nested-name">{{ faq.q || 'سوال بدون متن' }}</span>
                        <button type="button" class="btn-row-del" @click="removeFaqItem(fIdx)">
                          <q-icon name="delete_outline" size="18px" />
                        </button>
                      </div>
                      <div class="nested-grid">
                        <div class="full-width">
                          <label class="nested-label">متن پرسش</label>
                          <q-input v-model="faq.q" outlined dense class="editor-input" />
                        </div>
                        <div class="full-width">
                          <label class="nested-label">متن پاسخ تخصصی</label>
                          <q-input v-model="faq.a" outlined dense autogrow class="editor-input" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- CTA Banner on Home -->
                <div class="form-card full-width">
                  <label class="form-label">عنوان بنر اقدام در صفحه اصلی (Home CTA)</label>
                  <q-input v-model="form.cta_title" outlined dense class="editor-input" />
                </div>

                <div class="form-card full-width">
                  <label class="form-label">متن توضیحات بنر اقدام صفحه اصلی</label>
                  <RichTextEditor
                    v-model="form.cta_description"
                    :min-height="110"
                    placeholder="توضیحات مشاوره و شروع همکاری..."
                  />
                </div>
              </div>
            </div>

            <!-- TAB 7: BRAND & FOOTER -->
            <div v-show="activeTab === 'brand'" class="tab-pane">
              <div class="pane-head">
                <h3>تنظیمات برند، هدر و فوتر (Brand & Site Global)</h3>
                <p>تنظیم نام برند کهکشان هوشمند، دکمه اقدام هدر و متن کپی‌رایت انتهای سایت.</p>
              </div>

              <div class="form-grid">
                <!-- Site Brand & Footer Information -->
                <div class="form-card half-width">
                  <label class="form-label">نام برند تجاری (Site Brand Name)</label>
                  <q-input v-model="form.site_name" outlined dense placeholder="کهکشان هوشمند" class="editor-input" />
                  <div class="form-hint">عنوان نمایشی برند در هدر، لوگو و بخش بالایی فوتر</div>
                </div>

                <div class="form-card half-width">
                  <label class="form-label">زیرعنوان / شعار معرفی فوتر (Footer Tagline)</label>
                  <q-input v-model="form.footer_description" outlined dense placeholder="پلتفرم جامع مهندسی نرم‌افزار و معماری ابری" class="editor-input" />
                  <div class="form-hint">متن زیر عنوان برند در فوتر سایت</div>
                </div>

                <div class="form-card half-width">
                  <label class="form-label">متن کپی‌رایت فوتر (Copyright)</label>
                  <q-input v-model="form.footer_copyright" outlined dense placeholder="© ۱۴۰۵ تمامی حقوق مادی و معنوی متعلق به سرزمین کهکشان هوشمند است." class="editor-input" />
                  <div class="form-hint">متن کپی‌رایت نمایش‌داده شده در نوار انتهایی فوتر</div>
                </div>

                <div class="form-card half-width">
                  <label class="form-label">امضای فنی / متن انگلیسی فوتر (Footer Secondary Credit)</label>
                  <q-input v-model="form.footer_credit" outlined dense placeholder="Designed with precision & high standards." class="editor-input" />
                  <div class="form-hint">متن انگلیسی چپ‌چین در پایین فوتر</div>
                </div>

                <!-- Footer Social Links -->
                <div class="form-card full-width">
                  <div class="sub-head-row">
                    <label class="form-label mb-0">لینک‌های شبکه‌های اجتماعی فوتر (Social Media Links)</label>
                  </div>
                  <div class="nested-grid q-mt-sm">
                    <div>
                      <label class="nested-label">آدرس گیت‌هاب (GitHub URL)</label>
                      <q-input v-model="form.social_github" outlined dense placeholder="https://github.com/your-org" class="editor-input" />
                    </div>
                    <div>
                      <label class="nested-label">آدرس لینکدین (LinkedIn URL)</label>
                      <q-input v-model="form.social_linkedin" outlined dense placeholder="https://linkedin.com/company/your-company" class="editor-input" />
                    </div>
                    <div>
                      <label class="nested-label">کانال یا آیدی تلگرام (Telegram URL)</label>
                      <q-input v-model="form.social_telegram" outlined dense placeholder="https://t.me/your-channel" class="editor-input" />
                    </div>
                    <div>
                      <label class="nested-label">آدرس توییتر / ایکس (Twitter / X URL)</label>
                      <q-input v-model="form.social_twitter" outlined dense placeholder="https://x.com/your-handle" class="editor-input" />
                    </div>
                  </div>
                </div>

                <!-- Quick Access Floating Button Config -->
                <div class="form-card full-width">
                  <div class="sub-head-row">
                    <label class="form-label mb-0">تنظیمات دکمه دسترسی سریع شناور (Quick Access Widget)</label>
                  </div>
                  <div class="nested-grid q-mt-sm">
                    <div>
                      <label class="nested-label">شماره تلفن مستقیم تماس</label>
                      <q-input v-model="form.quick_phone" outlined dense placeholder="02188901234" class="editor-input" />
                    </div>
                    <div>
                      <label class="nested-label">عنوان دکمه تماس</label>
                      <q-input v-model="form.quick_phone_label" outlined dense placeholder="تماس تلفنی مستقیم" class="editor-input" />
                    </div>
                    <div>
                      <label class="nested-label">لینک یا آیدی تلگرام</label>
                      <q-input v-model="form.quick_telegram" outlined dense placeholder="https://t.me/yourusername" class="editor-input" />
                    </div>
                    <div>
                      <label class="nested-label">عنوان دکمه تلگرام</label>
                      <q-input v-model="form.quick_telegram_label" outlined dense placeholder="پشتیبانی تلگرام" class="editor-input" />
                    </div>
                    <div>
                      <label class="nested-label">شماره یا لینک واتس‌اپ</label>
                      <q-input v-model="form.quick_whatsapp" outlined dense placeholder="0912... یا https://wa.me/..." class="editor-input" />
                    </div>
                    <div>
                      <label class="nested-label">عنوان دکمه واتس‌اپ</label>
                      <q-input v-model="form.quick_whatsapp_label" outlined dense placeholder="پیام در واتس‌اپ" class="editor-input" />
                    </div>
                    <div>
                      <label class="nested-label">مسیر دکمه مشاوره (CTA)</label>
                      <q-input v-model="form.quick_cta_link" outlined dense placeholder="/contact یا #sec-contact" class="editor-input" />
                    </div>
                    <div>
                      <label class="nested-label">عنوان دکمه مشاوره</label>
                      <q-input v-model="form.quick_cta_label" outlined dense placeholder="درخواست مشاوره فوری" class="editor-input" />
                    </div>
                    <div class="full-width">
                      <q-toggle
                        v-model="quickEnabledBool"
                        label="نمایش دکمه دسترسی سریع برای کلیه کاربران در تمام صفحات"
                        color="primary"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </main>
      </div>
    </div>
  </q-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import RichTextEditor from 'src/components/common/RichTextEditor.vue'
import { useMasterEditor } from 'src/composables/useMasterEditor'
import { useHomeContent } from 'src/composables/useHomeContent'
import { useSiteContent } from 'src/composables/useSiteContent'
import { useCinematicMotion } from 'src/composables/useCinematicMotion'
import api from 'src/services/api'

const { stopLenis, startLenis } = useCinematicMotion()

const {
  isMasterEditorOpen,
  activeTab,
  isSaving,
  servicesState,
  projectsState,
  aboutState,
  articlesState,
  contactState,
  closeMasterEditor,
  saveAllContent,
  resetToDefaults,
} = useMasterEditor()

const { settings: homeSettings, buttons: homeButtons } = useHomeContent()
const { settings: siteSettings } = useSiteContent()

const TABS = [
  { id: 'hero', label: 'هیرو و بنر اصلی', desc: 'عنوان، توضیحات و دکمه‌ها', icon: 'auto_awesome' },
  { id: 'services', label: 'خدمات تخصصی', desc: '۶ کارت با آیکون‌های ۳D', icon: 'grid_view' },
  { id: 'projects', label: 'پروژه‌ها و نمونه‌کارها', desc: '۳ پروژه استراتژیک سازمانی', icon: 'layers' },
  { id: 'about', label: 'درباره ما و تیم', desc: 'بیانیه، ارزش‌ها، آمار و متخصصان', icon: 'corporate_fare' },
  { id: 'articles', label: 'دانش و مقالات', desc: 'مدیریت و انتشار مقالات فنی', icon: 'article' },
  { id: 'contact', label: 'تماس با ما و FAQ', desc: 'اطلاعات تماس، آدرس و فرم', icon: 'chat' },
  { id: 'brand', label: 'هدر و فوتر', desc: 'نام برند و کپی‌رایت', icon: 'language' },
]

// Working clone form state
const form = reactive({
  hero_badge: '',
  hero_title: '',
  hero_description: '',
  hero_image_url: '',
  hero_scroll_label: '',
  buttons: [],
  why_badge: '',
  why_title: '',
  why_description: '',
  services: [],
  works_eyebrow: '',
  works_title: '',
  works_description: '',
  projects: [],
  about: {},
  articles: {},
  cta_title: '',
  cta_description: '',
  contact: {},
  site_name: '',
  footer_description: '',
  footer_copyright: '',
  footer_credit: '',
  social_github: '',
  social_linkedin: '',
  social_telegram: '',
  social_twitter: '',
  quick_phone: '',
  quick_phone_label: '',
  quick_telegram: '',
  quick_telegram_label: '',
  quick_whatsapp: '',
  quick_whatsapp_label: '',
  quick_cta_link: '',
  quick_cta_label: '',
  quick_is_enabled: 'true',
})

const quickEnabledBool = computed({
  get: () => form.quick_is_enabled !== 'false',
  set: (val) => { form.quick_is_enabled = val ? 'true' : 'false' }
})

// Synchronize state when editor is opened
function syncFromState () {
  form.hero_badge = homeSettings.value.hero_badge || 'استودیو هوشمند معماری ابری و مهندسی نرم‌افزار'
  form.hero_title = homeSettings.value.hero_title || 'خلق پلتفرم‌های مقیاس‌پذیر،\nمهندسی سیستم‌های ابری پایدار'
  form.hero_description = homeSettings.value.hero_description || ''
  form.hero_image_url = homeSettings.value.hero_image_url || '/images/herosection-video.mp4'
  form.hero_scroll_label = homeSettings.value.hero_scroll_label || 'بررسی توانمندی‌های مهندسی'
  form.buttons = JSON.parse(JSON.stringify(homeButtons.value || []))

  form.why_badge = homeSettings.value.why_badge || 'خدمات ما'
  form.why_title = homeSettings.value.why_title || 'راهکارهای تخصصی مهندسی'
  form.why_description = homeSettings.value.why_description || ''
  form.services = JSON.parse(JSON.stringify(servicesState.value || []))

  form.works_eyebrow = homeSettings.value.works_eyebrow || 'پروژه‌های شاخص'
  form.works_title = homeSettings.value.works_title || 'معماری سیستم‌های پرترافیک و مقیاس‌پذیر'
  form.works_description = homeSettings.value.works_description || 'سامانه‌های استراتژیک ملی و سازمانی که با تکیه بر پایداری، سرعت و بالاترین استانداردهای مهندسی نرم‌افزار خلق شده‌اند.'
  form.projects = JSON.parse(JSON.stringify(projectsState.value || []))

  form.about = JSON.parse(JSON.stringify(aboutState.value || {}))
  if (!form.about.badge) form.about.badge = 'درباره کهکشان هوشمند'
  if (!form.about.title) form.about.title = 'اصالت مهندسی، انضباط سازمانی'
  if (!form.about.desc) form.about.desc = 'ما یک استودیوی پیشرو در معماری نرم‌افزارهای تجاری و زیرساخت‌های ابری هستیم که دقت فنی را با استانداردهای بین‌المللی سازمانی تلفیق می‌کنیم. رویکرد ما در مهندسی نرم‌افزار متکی بر شفافیت کد منبع، کاهش ریسک‌های عملیاتی و ایزولاسیون امنیتی Zero-Trust بنا شده است.'
  if (!form.about.button_text) form.about.button_text = 'آشنایی بیشتر با کهکشان هوشمند'
  if (!form.about.button_link) form.about.button_link = '/about'
  if (!form.about.image) form.about.image = '/Modern 3D Tech Dashboard Illustration(1).png'
  if (!form.about.chip1_label) form.about.chip1_label = 'معماری امنیتی'
  if (!form.about.chip1_val) form.about.chip1_val = 'Zero-Trust Isolated'
  if (!form.about.chip2_label) form.about.chip2_label = 'لتنسی لبه شبکه'
  if (!form.about.chip2_val) form.about.chip2_val = '< ۱۵ms Anycast'
  if (!form.about.chip3_label) form.about.chip3_label = 'تضمین پایداری کتبی'
  if (!form.about.chip3_val) form.about.chip3_val = 'SLA ۹۹.۹۹٪ رسمی'
  if (!form.about.values) form.about.values = []
  if (!form.about.team) form.about.team = []

  form.articles = JSON.parse(JSON.stringify(articlesState.value || {}))
  form.articles.badge = form.articles.badge || homeSettings.value.articles_badge || 'دانش و وبلاگ'
  form.articles.title = form.articles.title || homeSettings.value.articles_title || 'تازه‌ترین مقالات مهندسی'
  form.articles.desc = form.articles.desc || homeSettings.value.articles_description || 'دیدگاه‌ها و مقالات فنی تیم مهندسی در حوزه‌های معماری ابری، امنیت، طراحی محصول و هوش مصنوعی.'
  if (!form.articles.items) form.articles.items = []
  form.articles.items.forEach((art) => {
    if (!art.author || typeof art.author !== 'object') {
      art.author = { name: 'معمار ارشد سیستم', role: 'کهکشان هوشمند', avatar: '/Modern 3D Tech Dashboard Illustration(1).png' }
    }
  })

  form.cta_title = homeSettings.value.cta_title || 'آماده‌اید پروژه بعدی خود را با ما بسازید؟'
  form.cta_description = homeSettings.value.cta_description || ''
  form.contact = JSON.parse(JSON.stringify(contactState.value || {}))
  if (!form.contact.faqs) form.contact.faqs = []

  form.site_name = siteSettings.value.site_name || 'کهکشان هوشمند'
  form.footer_description = siteSettings.value.footer_description || 'پلتفرم جامع مهندسی نرم‌افزار و معماری ابری'
  form.footer_copyright = siteSettings.value.footer_copyright || '© ۱۴۰۵ تمامی حقوق مادی و معنوی متعلق به سرزمین کهکشان هوشمند است.'
  form.footer_credit = siteSettings.value.footer_credit || 'Designed with precision & high standards.'

  form.social_github = siteSettings.value.social_github || 'https://github.com'
  form.social_linkedin = siteSettings.value.social_linkedin || 'https://linkedin.com'
  form.social_telegram = siteSettings.value.social_telegram || 'https://t.me'
  form.social_twitter = siteSettings.value.social_twitter || 'https://x.com'

  form.quick_phone = siteSettings.value.quick_phone || siteSettings.value.footer_contact_phone || '02188901234'
  form.quick_phone_label = siteSettings.value.quick_phone_label || 'تماس تلفنی مستقیم'
  form.quick_telegram = siteSettings.value.quick_telegram || 'https://t.me'
  form.quick_telegram_label = siteSettings.value.quick_telegram_label || 'پشتیبانی تلگرام'
  form.quick_whatsapp = siteSettings.value.quick_whatsapp || ''
  form.quick_whatsapp_label = siteSettings.value.quick_whatsapp_label || 'پیام در واتس‌اپ'
  form.quick_cta_link = siteSettings.value.quick_cta_link || '/contact'
  form.quick_cta_label = siteSettings.value.quick_cta_label || 'درخواست مشاوره فوری'
  form.quick_is_enabled = siteSettings.value.quick_is_enabled || 'true'
}

function isVideoUrl (url) {
  if (!url || typeof url !== 'string') return false
  const lower = url.toLowerCase()
  return (
    lower.endsWith('.mp4') ||
    lower.endsWith('.webm') ||
    lower.endsWith('.ogg') ||
    lower.includes('gemini_generated_video') ||
    lower.includes('herosection-video')
  )
}

watch(isMasterEditorOpen, (open) => {
  if (open) {
    syncFromState()
  }
})

async function onHeroFileChange (e) {
  const file = e.target?.files?.[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const res = await api.post('/api/upload/general', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (res.data?.data?.url) {
      form.hero_image_url = res.data.data.url
    }
  } catch (err) {
    form.hero_image_url = URL.createObjectURL(file)
  }
}

async function onAboutFileChange (e) {
  const file = e.target?.files?.[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const res = await api.post('/api/upload/general', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (res.data?.data?.url) {
      form.about.image = res.data.data.url
    }
  } catch (err) {
    form.about.image = URL.createObjectURL(file)
  }
}

// Button manipulation
function addHeroButton () {
  form.buttons.push({
    label: 'دکمه جدید',
    link: '/contact',
    variant: 'primary',
  })
}

function removeHeroButton (idx) {
  form.buttons.splice(idx, 1)
}

// Preset 3D Icons
const PRESET_ICONS = [
  { label: 'رایانش ابری (Cloud)', value: '/assets/icons3d/cloud.svg' },
  { label: 'میکروسرویس (Microservices)', value: '/assets/icons3d/microservices.svg' },
  { label: 'هوش مصنوعی (AI & ML)', value: '/assets/icons3d/ai.svg' },
  { label: 'دیزاین و رابط کاربری (UI/UX)', value: '/assets/icons3d/ux.svg' },
  { label: 'امنیت چندسطحی (Security)', value: '/assets/icons3d/security.svg' },
  { label: 'کلان‌داده و توزیع‌شده (Big Data)', value: '/assets/icons3d/bigdata.svg' },
  { label: 'توسعه نرم‌افزار و کدنویسی (Code & Dev)', value: '/assets/icons3d/code.svg' },
]

const serviceIconInputs = ref({})
const uploadingServiceIcon = ref({})

function triggerServiceIconUpload (sIdx) {
  const el = serviceIconInputs.value[sIdx]
  if (el) el.click()
}

async function onServiceIconUpload (e, sIdx) {
  const file = e.target.files?.[0]
  if (!file) return
  uploadingServiceIcon.value[sIdx] = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('folder', 'solutions')
    const res = await api.post('/api/media/upload', formData)
    if (res.data?.data?.url) {
      form.services[sIdx].iconSrc = res.data.data.url
    } else {
      form.services[sIdx].iconSrc = URL.createObjectURL(file)
    }
  } catch (err) {
    console.error('Service icon upload failed', err)
    form.services[sIdx].iconSrc = URL.createObjectURL(file)
  } finally {
    uploadingServiceIcon.value[sIdx] = false
    // reset input so same file can be chosen again
    e.target.value = ''
  }
}

// Service card manipulation
function addServiceCard () {
  form.services.push({
    title: 'خدمت تخصصی جدید',
    text: 'توضیحات مربوط به خدمت مهندسی...',
    iconSrc: '/assets/icons3d/cloud.svg',
    features: ['ویژگی اول', 'ویژگی دوم'],
  })
}

function removeServiceCard (idx) {
  form.services.splice(idx, 1)
}

// Project card manipulation
function addProjectCard () {
  form.projects.push({
    num: `۰${form.projects.length + 1}`,
    category: 'توسعه نرم‌افزار سازمانی',
    title: 'سامانه مقیاس‌پذیر جدید',
    description: 'توضیح معماری و مقیاس سامانه...',
    metrics: [
      { val: '۹۹.۹٪', lbl: 'پایداری' },
      { val: '۱۰ms', lbl: 'پاسخ‌دهی' },
    ],
    tags: ['Microservices', 'Docker'],
    image: '/uploads/home/contact-datacenter.jpg',
    badge: 'استقرار فعال',
    link: '/contact',
  })
}

function removeProjectCard (idx) {
  form.projects.splice(idx, 1)
}

// Values manipulation
function addValueItem () {
  if (!form.about.values) form.about.values = []
  form.about.values.push({
    title: 'ارزش فنی جدید',
    desc: 'توضیحات مرتبط با ارزش مهندسی و انضباط سازمانی...',
    icon: 'verified',
  })
}

function removeValueItem (idx) {
  form.about.values.splice(idx, 1)
}

// Team manipulation
function addTeamItem () {
  if (!form.about.team) form.about.team = []
  form.about.team.push({
    name: 'عضو جدید',
    role: 'مهندس ارشد نرم‌افزار',
    bio: 'سوابق و تخصص‌های کلیدی در سیستم‌های ابری...',
    image: '/uploads/home/contact-programming.jpg',
    tags: ['Cloud', 'DevOps'],
  })
}

function removeTeamItem (idx) {
  form.about.team.splice(idx, 1)
}

// Articles manipulation
function addArticleItem () {
  if (!form.articles.items) form.articles.items = []
  form.articles.items.unshift({
    id: Date.now(),
    title: 'مقاله فنی جدید',
    category: 'رایانش ابری',
    readTime: '۵ دقیقه مطالعه',
    topic: 'معماری سیستم',
    image: '/assets/articles/edge-computing.jpg',
    date: 'امروز',
    author: {
      name: 'معمار ارشد سیستم',
      role: 'کهکشان هوشمند',
      avatar: '/Modern 3D Tech Dashboard Illustration(1).png',
    },
    excerpt: 'خلاصه مختصر از مفاهیم و الگوهای ارائه‌شده در این مقاله...',
    content: 'متن کامل مقاله و بررسی تکنیکال سناریوهای معماری...',
    tags: ['ابری', 'معماری'],
  })
}

function removeArticleItem (idx) {
  form.articles.items.splice(idx, 1)
}

function getAuthorName (art) {
  if (!art.author) art.author = {}
  return art.author.name || ''
}

function setAuthorName (art, val) {
  if (!art.author) art.author = {}
  art.author.name = val
}

function getAuthorRole (art) {
  if (!art.author) art.author = {}
  return art.author.role || ''
}

function setAuthorRole (art, val) {
  if (!art.author) art.author = {}
  art.author.role = val
}

// FAQ manipulation
function addFaqItem () {
  if (!form.contact.faqs) form.contact.faqs = []
  form.contact.faqs.push({
    q: 'پرسش فنی جدید؟',
    a: 'پاسخ مستند و شفاف به پرسش کارفرما...',
  })
}

function removeFaqItem (idx) {
  form.contact.faqs.splice(idx, 1)
}

async function handleSave () {
  await saveAllContent(form)
}

function handleReset () {
  if (confirm('آیا از بازنشانی کلیه داده‌ها به حالت پیش‌فرض اطمینان دارید؟')) {
    resetToDefaults()
    syncFromState()
  }
}

// Ensure smooth scroll doesn't hijack wheel events when the modal is open
watch(isMasterEditorOpen, (isOpen) => {
  if (isOpen) {
    stopLenis()
  } else {
    startLenis()
  }
})
</script>

<style scoped>
/* ==========================================================================
   MASTER CONTENT EDITOR STYLING (Standardized Light Theme UI)
   ========================================================================== */
.master-modal-root {
  background-color: #f8fafc;
  color: #0f172a;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  direction: rtl;
  font-family: inherit;
  overflow: hidden;
}

/* Header */
.master-header {
  height: 72px;
  background-color: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  z-index: 10;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
}

.header-brand {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.brand-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  font-weight: 700;
  color: #b45309;
  background: #fef3c7;
  padding: 3px 10px;
  border-radius: 9999px;
  border: 1px solid #fde68a;
  text-transform: uppercase;
}

.live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #eab308;
  box-shadow: 0 0 6px #eab308;
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.85); }
}

.header-title {
  margin: 0;
  font-size: 1.12rem;
  font-weight: 800;
  color: #0f172a;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-head-ghost {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  border: 1.5px solid #cbd5e1;
  color: #475569;
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-head-ghost:hover {
  background: #fefce8;
  border-color: #fed72b;
  color: #0a0a0b;
}

.btn-head-cancel {
  background: transparent;
  border: none;
  color: #64748b;
  padding: 8px 14px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: color 0.2s;
}

.btn-head-cancel:hover {
  color: #0f172a;
}

.btn-head-save {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #fed72b;
  color: #000000;
  border: 1.5px solid #eab308;
  padding: 9px 20px;
  border-radius: 10px;
  font-size: 0.88rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(254, 215, 43, 0.3);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-head-save:hover:not(:disabled) {
  background: #f59e0b;
  border-color: #d97706;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}

.btn-head-save:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Master Body */
.master-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* Sidebar */
.master-sidebar {
  width: 290px;
  background-color: #ffffff;
  border-left: 1px solid #e2e8f0;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}

.sidebar-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  padding: 0 8px;
  margin-bottom: 6px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.nav-tab-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 12px;
  color: #475569;
  cursor: pointer;
  text-align: right;
  position: relative;
  transition: all 0.2s ease;
}

.nav-tab-btn:hover {
  background: #f8fafc;
  color: #0f172a;
}

.nav-tab-btn.active {
  background: #fefce8;
  border-color: #fde047;
  color: #854d0e;
}

.tab-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  flex-shrink: 0;
  transition: all 0.2s;
}

.nav-tab-btn.active .tab-icon-wrap {
  background: #fed72b;
  color: #000000;
}

.tab-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.tab-title {
  font-size: 0.88rem;
  font-weight: 700;
}

.tab-subtitle {
  font-size: 0.72rem;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-tab-btn.active .tab-subtitle {
  color: #a16207;
}

.tab-active-indicator {
  position: absolute;
  left: 0;
  top: 14%;
  height: 72%;
  width: 3px;
  background-color: #eab308;
  border-radius: 0 4px 4px 0;
}

/* Content Panel */
.master-content-panel {
  flex: 1;
  background-color: #f8fafc;
  overflow-y: auto !important;
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
  padding: 32px 40px;
}

.content-scrollable {
  max-width: 960px;
  margin: 0 auto;
}

.tab-pane {
  display: flex;
  flex-direction: column;
  gap: 28px;
  animation: fadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

.pane-head h3 {
  margin: 0 0 6px 0;
  font-size: 1.35rem;
  font-weight: 800;
  color: #0f172a;
}

.pane-head p {
  margin: 0;
  font-size: 0.86rem;
  color: #64748b;
}

/* Form Grid */
.form-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.form-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}

.form-card.full-width {
  width: 100%;
}

.form-card.half-width {
  width: calc(50% - 10px);
}

@media (max-width: 900px) {
  .form-card.half-width {
    width: 100%;
  }
}

.form-label {
  font-size: 0.82rem;
  font-weight: 700;
  color: #1e293b;
}

.form-hint {
  font-size: 0.72rem;
  color: #64748b;
}

.sub-head-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.btn-sub-add {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #fefce8;
  color: #854d0e;
  border: 1px solid #fde047;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-sub-add:hover {
  background: #fed72b;
  color: #000000;
}

/* Custom Input Theming */
:deep(.editor-input .q-field__control) {
  background: #ffffff !important;
  border-color: #cbd5e1 !important;
  color: #0f172a !important;
  border-radius: 10px !important;
}

:deep(.editor-input .q-field__native) {
  color: #0f172a !important;
  font-family: inherit;
  font-size: 0.88rem;
}

:deep(.editor-input .q-field__label) {
  color: #64748b !important;
}

:deep(.editor-input.q-field--focused .q-field__control) {
  border-color: #eab308 !important;
  box-shadow: 0 0 0 2px rgba(234, 179, 8, 0.2) !important;
}

/* Image Uploader */
.image-uploader-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.img-preview {
  width: 76px;
  height: 76px;
  border-radius: 12px;
  object-fit: contain;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  padding: 4px;
}

.img-preview.empty {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}

.img-inputs {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.file-upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  border: 1.5px solid #cbd5e1;
  color: #1e293b;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  align-self: flex-start;
  transition: all 0.2s;
}

.file-upload-btn:hover {
  background: #fefce8;
  border-color: #fed72b;
  color: #000000;
}

/* Buttons Editor List */
.buttons-editor-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.button-editor-row {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f8fafc;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
}

.flex-1 {
  flex: 1;
}

.btn-row-del {
  background: transparent;
  border: none;
  color: #ef4444;
  padding: 6px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-row-del:hover {
  background: rgba(239, 68, 68, 0.12);
}

/* Cards Accordion */
.cards-accordion {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.nested-editor-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.nested-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 10px;
}

.nested-title-badge {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nested-num {
  background: #fed72b;
  color: #09090b;
  font-weight: 800;
  font-size: 0.72rem;
  padding: 2px 7px;
  border-radius: 6px;
}

.nested-name {
  font-size: 0.88rem;
  font-weight: 700;
  color: #0f172a;
}

.badge-cat {
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: 6px;
}

.nested-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.nested-grid .full-width {
  grid-column: span 2;
}

.nested-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 4px;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.metric-editor-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px;
}

.metric-box-head {
  font-size: 0.75rem;
  font-weight: 700;
  color: #b45309;
  margin-bottom: 8px;
}

.mb-2 {
  margin-bottom: 8px;
}

.mb-0 {
  margin-bottom: 0;
}

/* Icon Uploader Styles */
.icon-uploader-block {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 10px 12px;
}

.icon-uploader-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 6px;
}

.icon-preview-box {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  display: grid;
  place-items: center;
  overflow: hidden;
  flex-shrink: 0;
}

.icon-preview-img {
  width: 36px;
  height: 36px;
  object-fit: contain;
}

.icon-upload-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  flex-wrap: wrap;
}

.btn-upload-icon {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  color: #000000;
  border: 1.5px solid #fed72b;
  border-radius: 8px;
  padding: 7px 12px;
  font-size: 0.76rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-upload-icon:hover {
  background: #fed72b;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(254, 215, 43, 0.35);
}

.preset-icon-select {
  flex: 1;
  min-width: 200px;
}

.btn-icon-clear {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.25);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon-clear:hover {
  background: #ef4444;
  color: #ffffff;
}

/* Branded Admin Redirect Action (White / Black / Yellow - No Black Background!) */
.admin-redirect-action {
  margin-top: 8px;
  padding: 16px 0;
  display: flex;
  justify-content: flex-start;
}

.btn-admin-nav-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: #ffffff;
  color: #0a0a0b;
  border: 1.5px solid #0a0a0b;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 0.88rem;
  font-weight: 800;
  text-decoration: none;
  cursor: pointer;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.25s ease;
}

.btn-admin-nav-brand:hover {
  background: #fed72b;
  color: #000000;
  border-color: #eab308;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(254, 215, 43, 0.35);
}
</style>

<template>
  <footer class="site-footer">
    <div class="container">
      <div class="footer-inner">
        <!-- Brand -->
        <div class="footer-brand-wrap">
          <div class="brand-mark">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
          </div>
          <div>
            <div class="footer-brand-title">{{ settings.site_name || 'سرزمین کهکشان هوشمند' }}</div>
            <div class="footer-brand-sub">{{ settings.footer_description || 'پلتفرم جامع مهندسی نرم‌افزار و معماری ابری' }}</div>
          </div>
        </div>

        <!-- Links -->
        <ul class="footer-nav-links">
          <li><router-link to="/">خانه</router-link></li>
          <li><router-link to="/services">خدمات</router-link></li>
          <li><router-link to="/projects">پروژه‌ها</router-link></li>
          <li><router-link to="/articles">مقالات</router-link></li>
          <li><router-link to="/about">درباره ما</router-link></li>
          <li><router-link to="/contact">تماس با ما</router-link></li>
        </ul>

        <!-- Social Icons with circular badges -->
        <div class="footer-social-strip">
          <q-btn
            v-if="isAdmin"
            round
            dense
            size="sm"
            unelevated
            color="dark"
            icon="edit"
            class="footer-edit-btn"
            @click="openMasterEditor('brand')"
          >
            <q-tooltip>ویرایش فوتر و برند</q-tooltip>
          </q-btn>

          <a :href="settings.social_github || 'https://github.com'" target="_blank" rel="noopener noreferrer" class="footer-social-btn" title="GitHub" aria-label="GitHub">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
          </a>
          <a :href="settings.social_linkedin || 'https://linkedin.com'" target="_blank" rel="noopener noreferrer" class="footer-social-btn" title="LinkedIn" aria-label="LinkedIn">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
          </a>
          <a :href="settings.social_telegram || 'https://t.me'" target="_blank" rel="noopener noreferrer" class="footer-social-btn" title="Telegram" aria-label="Telegram">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.18-.357.295-.6.295-.002 0-.003 0-.005 0l.213-3.054 5.56-5.022c.24-.213-.054-.334-.373-.121l-6.869 4.326-2.96-.924c-.643-.204-.657-.643.136-.953l11.57-4.461c.536-.196 1.006.128.832.946z"/></svg>
          </a>
          <a :href="settings.social_twitter || 'https://x.com'" target="_blank" rel="noopener noreferrer" class="footer-social-btn" title="Twitter/X" aria-label="Twitter/X">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
          </a>
        </div>
      </div>

      <div class="footer-bottom-copy">
        <div>{{ settings.footer_copyright || '© ۱۴۰۵ تمامی حقوق مادی و معنوی متعلق به سرزمین کهکشان هوشمند است.' }}</div>
        <div style="font-family: var(--font-en, 'Outfit', sans-serif); font-weight: 600;">{{ settings.footer_credit || 'Designed with precision & high standards.' }}</div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { useAuth } from 'src/composables/useAuth'
import { useSiteContent } from 'src/composables/useSiteContent'
import { useMasterEditor } from 'src/composables/useMasterEditor'

const { isAdmin } = useAuth()
const { settings } = useSiteContent()
const { openMasterEditor } = useMasterEditor()
</script>

<style scoped>
/* ==========================================================================
   FOOTER (Design from index.html)
   ========================================================================== */
.site-footer {
  background: #ffffff;
  border-top: 1px solid var(--border-light, #e5e5e5);
  padding: 56px 0 32px 0;
  direction: rtl;
}

.container {
  width: min(1340px, 94vw);
  margin: 0 auto;
  padding: 0 16px;
  box-sizing: border-box;
}

.footer-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
  padding-bottom: 36px;
  border-bottom: 1px solid var(--border-light, #e5e5e5);
}

.footer-brand-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-mark {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #0a0a0a;
  display: grid;
  place-items: center;
  color: var(--yellow, #ffcc00);
  font-weight: 900;
  font-size: 0.95rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
}

.footer-brand-title {
  font-weight: 800;
  font-size: 1.05rem;
  color: var(--text-dark, #0a0a0a);
}

.footer-brand-sub {
  font-size: 0.78rem;
  color: var(--text-dark-muted, #737373);
}

.footer-nav-links {
  display: flex;
  align-items: center;
  gap: 22px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.footer-nav-links a {
  text-decoration: none;
  color: var(--text-dark, #0a0a0a);
  font-size: 0.9rem;
  font-weight: 600;
  transition: color 0.2s;
}

.footer-nav-links a:hover {
  color: var(--yellow, #ffcc00);
}

.footer-social-strip {
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-edit-btn {
  background: #ffd54a !important;
  color: #000000 !important;
  margin-left: 6px;
}

.footer-social-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-light-card, #f0f0f0);
  display: grid;
  place-items: center;
  color: var(--text-dark, #0a0a0a);
  text-decoration: none;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.footer-social-btn:hover {
  background: var(--yellow, #ffcc00);
  color: #000000;
  transform: translateY(-2px);
}

.footer-bottom-copy {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 24px;
  font-size: 0.8rem;
  color: var(--text-dark-muted, #737373);
}

@media (max-width: 900px) {
  .site-footer {
    padding: 40px 0 24px 0;
  }
  .footer-inner {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
    padding-bottom: 24px;
  }
  .footer-brand-title {
    font-size: 0.95rem;
  }
  .footer-brand-sub {
    font-size: 0.75rem;
  }
  .footer-nav-links {
    flex-wrap: wrap;
    gap: 14px;
  }
  .footer-nav-links a {
    font-size: 0.82rem;
  }
  .footer-social-btn {
    width: 38px;
    height: 38px;
  }
  .footer-bottom-copy {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
    font-size: 0.74rem;
    padding-top: 18px;
  }
}

@media (max-width: 480px) {
  .site-footer {
    padding: 32px 0 20px 0;
  }
  .footer-brand-title {
    font-size: 0.88rem;
  }
  .footer-brand-sub {
    font-size: 0.72rem;
  }
  .footer-nav-links {
    gap: 12px;
  }
  .footer-nav-links a {
    font-size: 0.78rem;
  }
  .footer-bottom-copy {
    font-size: 0.7rem;
    line-height: 1.6;
  }
}
</style>

const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: 'services', component: () => import('pages/SolutionsPage.vue') },
      { path: 'solutions', component: () => import('pages/SolutionsPage.vue') },
      { path: 'solutions/:slug', component: () => import('pages/SolutionDetailsPage.vue') },
      { path: 'projects', component: () => import('pages/ProductsPage.vue') },
      { path: 'products', component: () => import('pages/ProductsPage.vue') },
      { path: 'products/:slug', component: () => import('pages/ProductDetailsPage.vue') },
      { path: 'about', component: () => import('pages/AboutPage.vue') },
      { path: 'articles', component: () => import('pages/ArticlesPage.vue') },
      { path: 'articles/:slug', component: () => import('pages/SolutionDetailsPage.vue') },
      { path: 'article/:slug', component: () => import('pages/SolutionDetailsPage.vue') },
      { path: 'blog', component: () => import('pages/ArticlesPage.vue') },
      { path: 'blog/:slug', component: () => import('pages/SolutionDetailsPage.vue') },
      { path: 'contact', component: () => import('pages/ContactPage.vue') },
      { path: ':catchAll(.*)*', component: () => import('pages/IndexPage.vue') },
    ]
  },

  { path: '/login', redirect: '/admin/login' },
  { path: '/admin/login', component: () => import('pages/AdminLoginPage.vue') },

  {
    path: '/admin',
    component: () => import('layouts/AdminLayout.vue'),
    children: [
      { path: '', component: () => import('pages/admin/DashboardPage.vue') },
      { path: 'products', component: () => import('pages/admin/ProductsAdminPage.vue') },
      { path: 'categories', component: () => import('pages/admin/CategoriesAdminPage.vue') },
      { path: 'catalogs', component: () => import('pages/admin/CatalogsAdminPage.vue') },
      { path: 'consultations', component: () => import('pages/admin/ConsultationsAdminPage.vue') },
      { path: 'team', component: () => import('pages/admin/TeamMembersAdminPage.vue') },
      { path: 'solutions', component: () => import('pages/admin/SolutionsAdminPage.vue') },
      { path: 'articles', component: () => import('pages/admin/SolutionsAdminPage.vue') },
      { path: 'media', component: () => import('pages/admin/MediaAdminPage.vue') },
      { path: 'settings', component: () => import('pages/admin/SettingsPage.vue') },
      { path: ':catchAll(.*)*', redirect: '/admin' },
    ]
  },

  { path: '/:catchAll(.*)*', redirect: '/' }
]

export default routes


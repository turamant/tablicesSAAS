import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/core/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/modules/auth/views/LoginView.vue')
    },
    {
      path: '/dashboard',
      component: () => import('@/shared/layouts/UserLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/modules/user/views/DashboardView.vue')
        },
        {
          path: 'tables/:id',
          name: 'table',
          component: () => import('@/modules/user/views/TableView.vue')
        }
      ]
    }
  ]
})

// ЕДИНСТВЕННЫЙ ГЛОБАЛЬНЫЙ ГУАРД
router.beforeEach(async (to) => {
  const auth = useAuthStore()
  
  // 1. Инициализация если нужно
  if (!auth.initialized) {
    await auth.fetchMe()
  }
  
  // 2. Редирект с корня
  if (to.path === '/') {
    return auth.isAuthenticated ? '/dashboard' : '/login'
  }
  
  // 3. Защита авторизованных роутов
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return '/login'
  }
  
  // 4. Редирект с логина если уже авторизован
  if (to.path === '/login' && auth.isAuthenticated) {
    return '/dashboard'
  }
})

export default router
import { createRouter, createWebHistory } from 'vue-router'
import { authGuard, guestGuard } from '@/core/auth/guards'
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
      component: () => import('@/modules/auth/views/LoginView.vue'),
      beforeEnter: guestGuard
    },
    {
      path: '/dashboard',
      component: () => import('@/shared/layouts/UserLayout.vue'),
      beforeEnter: authGuard,
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

// Глобальная проверка
router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.initialized && !to.path.includes('/login')) {
    await auth.fetchMe()
  }
})

export default router









// import { createRouter, createWebHistory } from 'vue-router'
// import { authGuard, adminGuard, guestGuard } from '@/core/auth/guards'
// import { useAuthStore } from '@/core/stores/auth'

// const router = createRouter({
//   history: createWebHistory(),
//   routes: [
//     {
//       path: '/',
//       redirect: '/login'
//     },
//     {
//       path: '/login',
//       name: 'login',
//       component: () => import('@/modules/auth/views/LoginView.vue'),
//       beforeEnter: guestGuard
//     },
//     {
//       path: '/register',
//       name: 'register',
//       component: () => import('@/modules/auth/views/RegisterView.vue'),
//       beforeEnter: guestGuard
//     },
//     {
//       path: '/dashboard',
//       component: () => import('@/shared/layouts/UserLayout.vue'),
//       beforeEnter: authGuard,
//       children: [
//         {
//           path: '',
//           name: 'dashboard',
//           component: () => import('@/modules/user/views/DashboardView.vue')
//         }
//       ]
//     },
//     {
//       path: '/admin',
//       component: () => import('@/shared/layouts/AdminLayout.vue'),
//       beforeEnter: [authGuard, adminGuard],
//       children: [
//         {
//           path: '',
//           redirect: 'users'
//         },
//         {
//           path: 'users',
//           name: 'admin-users',
//           component: () => import('@/modules/admin/views/UsersView.vue')
//         }
//       ]
//     }
//   ]
// })

// // Глобальная проверка
// router.beforeEach(async (to) => {
//   const auth = useAuthStore()
//   if (!auth.initialized && !to.path.includes('/login') && !to.path.includes('/register')) {
//     await auth.fetchMe()
//   }
// })

// export default router
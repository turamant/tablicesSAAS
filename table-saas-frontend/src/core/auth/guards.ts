import type { NavigationGuard } from 'vue-router'
import { useAuthStore } from '@/core/stores/auth'

export const authGuard: NavigationGuard = async (to, from, next) => {
  const auth = useAuthStore()
  
  // Ждем инициализации
  if (!auth.initialized) {
    await auth.fetchMe()
  }
  
  if (!auth.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
}

export const adminGuard: NavigationGuard = async (to, from, next) => {
  const auth = useAuthStore()
  
  if (!auth.initialized) {
    await auth.fetchMe()
  }
  
  if (!auth.isSuperuser) {
    next('/dashboard')
  } else {
    next()
  }
}

export const guestGuard: NavigationGuard = async (to, from, next) => {
  const auth = useAuthStore()
  
  if (!auth.initialized) {
    await auth.fetchMe()
  }
  
  if (auth.isAuthenticated) {
    next(auth.isSuperuser ? '/admin' : '/dashboard')
  } else {
    next()
  }
}
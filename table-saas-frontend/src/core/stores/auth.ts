import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/core/api/auth'
import type { User, LoginPayload, RegisterPayload } from '@/core/types/auth.types'
import router from '@/core/router'

export const useAuthStore = defineStore('auth', () => {
  // Состояние
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const initialized = ref(false)

  // Геттеры
  const isAuthenticated = computed(() => !!user.value)
  const isSuperuser = computed(() => user.value?.is_superuser ?? false)

  // Действия
  async function fetchMe() {
    if (isLoading.value) return
    
    isLoading.value = true
    try {
      const { data } = await authApi.me()
      user.value = data
    } catch (error) {
      user.value = null
    } finally {
      isLoading.value = false
      initialized.value = true
    }
  }

  async function login(payload: LoginPayload) {
    isLoading.value = true
    try {
      await authApi.login(payload)
      await fetchMe() // после логина получаем юзера
      
      // Редирект в зависимости от роли
      if (isSuperuser.value) {
        await router.push('/admin')
      } else {
        await router.push('/dashboard')
      }
    } finally {
      isLoading.value = false
    }
  }

  async function register(payload: RegisterPayload) {
    isLoading.value = true
    try {
      await authApi.register(payload)
      await login({ email: payload.email, password: payload.password })
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      user.value = null
      await router.push('/login')
    }
  }

  return {
    // state
    user,
    isLoading,
    initialized,
    // getters
    isAuthenticated,
    isSuperuser,
    // actions
    fetchMe,
    login,
    register,
    logout,
  }
})
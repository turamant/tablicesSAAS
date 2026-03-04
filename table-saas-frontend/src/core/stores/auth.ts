import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/core/api/auth'
import type { User, LoginPayload, RegisterPayload } from '@/core/types/auth.types'
import router from '@/core/router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const initialized = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const isSuperuser = computed(() => user.value?.is_superuser ?? false)

  async function fetchMe() {
    isLoading.value = true
    try {
      const { data } = await authApi.me()
      user.value = data
      console.log('fetchMe got user:', data)
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
      await fetchMe()
      
      console.log('Login completed, user:', user.value)
      
      if (user.value?.is_superuser) {
        await router.replace('/admin')
      } else {
        await router.replace('/dashboard')
      }
      
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function register(payload: RegisterPayload) {
    isLoading.value = true
    try {
      await authApi.register(payload)
      await login({ email: payload.email, password: payload.password })
    } catch (error) {
      console.error('Register failed:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // ВОТ СУКА ЛОГАУТ - ВЕРНУЛ!
  async function logout() {
    try {
      await authApi.logout()
    } finally {
      user.value = null
      initialized.value = false
      await router.push('/login')
    }
  }

  return {
    user,
    isLoading,
    initialized,
    isAuthenticated,
    isSuperuser,
    fetchMe,
    login,
    register,
    logout,  // ← ВЕРНУЛ В ЭКСПОРТ
  }
})
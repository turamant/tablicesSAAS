import { apiClient } from './client'
import type { User, LoginPayload, RegisterPayload, AuthResponse } from '@/core/types/auth.types'

export const authApi = {
  // Проверка текущего пользователя (по куке)
  me: () => apiClient.get<User>('/auth/me'),
  
  // Вход
  login: (data: LoginPayload) => apiClient.post<AuthResponse>('/auth/login', data),
  
  // Регистрация
  register: (data: RegisterPayload) => apiClient.post<AuthResponse>('/auth/register', data),
  
  // Выход
  logout: () => apiClient.post<{ message: string }>('/auth/logout'),
}
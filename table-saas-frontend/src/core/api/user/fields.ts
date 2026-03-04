import { apiClient } from '@/core/api/client'
import type { Field } from './tables'

export interface CreateFieldDto {
  name: string
  display_name: string
  field_type: string
  is_required?: boolean
  is_unique?: boolean
  options?: any
  sort_order?: number
}

export interface UpdateFieldDto {
  name?: string
  display_name?: string
  is_required?: boolean
}

export const fieldsApi = {
  // Создать поле
  createField: (tableId: string, data: CreateFieldDto) => 
    apiClient.post<Field>(`/tables/${tableId}/fields`, data),
  
  // Удалить поле
  deleteField: (tableId: string, fieldId: string) => 
    apiClient.delete(`/tables/${tableId}/fields/${fieldId}`),
  
  // Обновить поле
  updateField: (tableId: string, fieldId: string, data: UpdateFieldDto) => 
    apiClient.patch<Field>(`/tables/${tableId}/fields/${fieldId}`, data),
  
  // Получить все поля таблицы
  getFields: (tableId: string) => 
    apiClient.get<Field[]>(`/tables/${tableId}/fields`),
}
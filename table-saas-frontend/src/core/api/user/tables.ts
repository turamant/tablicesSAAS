import { apiClient } from '@/core/api/client'

export interface Field {
  id: string
  name: string
  display_name: string
  field_type: string
  is_required: boolean
  is_unique: boolean
  options: any | null
  sort_order: number
}

export interface Table {
  id: string
  name: string
  description: string | null
  physical_name: string
  created_at: string
  updated_at: string
  owner_id: string
  fields: Field[]
}

export interface CreateFieldDto {
  name: string
  display_name: string
  field_type: 'text' | 'number' | 'date' | 'boolean' | 'select' | 'multiselect' | 'email'| 'formula'
  is_required?: boolean
  is_unique?: boolean
  options?: any
  sort_order?: number
}

export interface CreateTableDto {
  name: string
  description?: string
  fields: CreateFieldDto[]
}

export interface UpdateTableDto {
  name?: string
  description?: string
  // Поля таблицы редактируются отдельно
}

export const tablesApi = {
  getTables: () => apiClient.get<Table[]>('/tables'),
  getTable: (id: string) => apiClient.get<Table>(`/tables/${id}`),
  createTable: (data: CreateTableDto) => apiClient.post<Table>('/tables', data),
  updateTable: (id: string, data: UpdateTableDto) => apiClient.patch<Table>(`/tables/${id}`, data),
  deleteTable: (id: string) => apiClient.delete(`/tables/${id}`),
}
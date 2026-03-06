import { apiClient } from '@/core/api/client'

export type ViewType = 'grid' | 'kanban' | 'calendar' | 'gallery'

export interface ViewSettings {
  // Общие настройки
  hidden_fields?: string[]
  sort_field?: string
  sort_direction?: 'asc' | 'desc'
  filters?: any[]
  
  // Для Kanban
  kanban_group_field?: string  // поле для группировки (например, status)
  kanban_columns?: string[]     // значения колонок
  card_fields?: string[]        // поля, отображаемые в карточке
}

export interface View {
  id: string
  name: string
  type: ViewType
  table_id: string
  settings: ViewSettings
  is_default: boolean
  created_by: string
  created_at: string
  updated_at: string
}

export interface CreateViewDto {
  name: string
  type: ViewType
  table_id: string
  settings: ViewSettings
  is_default?: boolean
}

export interface UpdateViewDto {
    name?: string
    settings?: ViewSettings
    is_default?: boolean
  }

export const viewsApi = {
  // Получить все виды таблицы
  getViews: (tableId: string) => 
    apiClient.get<View[]>(`/tables/${tableId}/views`),
  
  // Создать вид
  createView: (tableId: string, data: CreateViewDto) => 
    apiClient.post<View>(`/tables/${tableId}/views`, data),
  
  // Обновить вид
  updateView: (tableId: string, viewId: string, data: Partial<CreateViewDto>) => 
    apiClient.put<View>(`/tables/${tableId}/views/${viewId}`, data),
  
  // Удалить вид
  deleteView: (tableId: string, viewId: string) => 
    apiClient.delete(`/tables/${tableId}/views/${viewId}`),
  
  // Получить вид по умолчанию
  getDefaultView: (tableId: string) => 
    apiClient.get<View>(`/tables/${tableId}/views/default`),
}
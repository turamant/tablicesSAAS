import { apiClient } from '@/core/api/client'

export interface FieldMapping {
  excel_column: string
  table_field: string
  skip: boolean
}

export interface ImportPreview {
  columns: string[]
  rows: Record<string, any>[]
  total_rows: number
  suggested_mappings: FieldMapping[]
}

export interface ImportResult {
  imported: number
  total: number
  errors: string[]
}

export const importApi = {
  // Предпросмотр файла
  preview: (tableId: string, formData: FormData) => 
    apiClient.post<ImportPreview>(`/tables/${tableId}/import/preview`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  
  // Импорт данных
  import: (tableId: string, formData: FormData) => 
    apiClient.post<ImportResult>(`/tables/${tableId}/import`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
}
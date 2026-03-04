import { apiClient } from '@/core/api/client'

export interface TableRecord {
  id: string
  _created_at: string
  _created_by: string
  _updated_at: string
  [key: string]: any
}

export interface CreateRecordDto {
  data: Record<string, any>
}

export interface UpdateRecordDto {
  data: Record<string, any>
}

export interface RecordsQueryParams {
  filters?: any[]
  order_by?: string
  order_direction?: 'asc' | 'desc'
  limit?: number
  offset?: number
}

export const recordsApi = {
  getRecords: (tableId: string, params?: RecordsQueryParams) => 
    apiClient.get<TableRecord[]>(`/tables/${tableId}/data`, { params }),
  
  getRecord: (tableId: string, recordId: string) => 
    apiClient.get<TableRecord>(`/tables/${tableId}/data/${recordId}`),
  
  createRecord: (tableId: string, data: CreateRecordDto) => 
    apiClient.post<TableRecord>(`/tables/${tableId}/data`, data),
  
  updateRecord: (tableId: string, recordId: string, data: UpdateRecordDto) => 
    apiClient.put<TableRecord>(`/tables/${tableId}/data/${recordId}`, data),
  
  deleteRecord: (tableId: string, recordId: string) => 
    apiClient.delete(`/tables/${tableId}/data/${recordId}`),
}
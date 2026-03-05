import { apiClient } from '@/core/api/client'

export interface GroupByField {
  field: string
  sort_direction?: 'asc' | 'desc'
}

export interface AggregateField {
  field: string
  function: 'sum' | 'avg' | 'count' | 'min' | 'max'
  alias?: string
}

export interface GroupRequest {
  group_by: GroupByField[]
  aggregates: AggregateField[]
  filters?: any[]
  limit?: number
  offset?: number
}

export interface GroupResult {
  groups: Record<string, any>[]
  total_groups: number
  grand_totals: Record<string, any>
}

export const groupApi = {
  groupData: (tableId: string, data: GroupRequest) => 
    apiClient.post<GroupResult>(`/tables/${tableId}/group`, data)
}
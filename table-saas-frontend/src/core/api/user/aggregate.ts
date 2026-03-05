import { apiClient } from '@/core/api/client'

export interface AggregateResponse {
  total_records: number
  sums: Record<string, number>
  averages: Record<string, number>
  mins: Record<string, number>
  maxs: Record<string, number>
}

export const aggregateApi = {
  getAggregations: (tableId: string, fields?: string[]) => {
    const params = fields?.length ? { fields: fields.join(',') } : {}
    return apiClient.get<AggregateResponse>(`/tables/${tableId}/aggregate`, { params })
  }
}
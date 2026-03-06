import { apiClient } from '@/core/api/client'

export interface KanbanColumn {
  id: string
  title: string
  cards: KanbanCard[]
  color?: string
  limit?: number
}

export interface KanbanCard {
  id: string
  title: string
  description?: string
  columnId: string
  data: Record<string, any>  // все поля записи
  order: number
}

export const kanbanApi = {
  // Получить данные для канбана
  getKanbanData: (tableId: string, groupField: string) => 
    apiClient.get<KanbanColumn[]>(`/tables/${tableId}/kanban`, {
      params: { group_field: groupField }
    }),
  
  // Переместить карточку
  moveCard: (tableId: string, cardId: string, targetColumnId: string, newOrder?: number) => 
    apiClient.post(`/tables/${tableId}/kanban/move`, {
      card_id: cardId,
      target_column_id: targetColumnId,
      order: newOrder
    }),
}
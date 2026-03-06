<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import type { Table, Field } from '@/core/api/user/tables'
import type { TableRecord } from '@/core/api/user/records'
import { useRecordsStore } from '@/modules/user/stores/records.store'

const props = defineProps<{
  table: Table
  records: TableRecord[]
  groupField: string
  cardFields?: string[]
}>()

const emit = defineEmits<{
  (e: 'cardClick', record: TableRecord): void
}>()

const recordsStore = useRecordsStore()
const draggedCard = ref<{ id: string; columnId: string; element: HTMLElement } | null>(null)

// Группируем записи по значению поля
const columns = ref<Array<{ id: string; title: string; cards: TableRecord[]; color: string; count: number }>>([])

function updateColumns() {
  const groups: Record<string, TableRecord[]> = {}
  
  const values = new Set(props.records.map(r => r[props.groupField]))
  
  values.forEach(val => {
    groups[val || 'Не указано'] = []
  })
  
  props.records.forEach(record => {
    const val = record[props.groupField] || 'Не указано'
    if (!groups[val]) {
      groups[val] = []
    }
    groups[val].push(record)
  })
  
  columns.value = Object.entries(groups).map(([title, cards]) => ({
    id: title,
    title,
    cards: [...cards],
    count: cards.length,
    color: getColumnColor(title)
  }))
}

watch(() => props.records, () => {
  updateColumns()
}, { deep: true, immediate: true })

function getColumnColor(title: string): string {
  const colors: Record<string, string> = {
    'active': 'bg-green-50 border-green-200',
    'inactive': 'bg-gray-50 border-gray-200',
    'pending': 'bg-yellow-50 border-yellow-200',
    'completed': 'bg-blue-50 border-blue-200',
    'Не указано': 'bg-gray-50 border-gray-200'
  }
  return colors[title] || 'bg-gray-50 border-gray-200'
}

function getCardTitle(record: TableRecord): string {
  const titleField = props.table.fields.find(f => 
    f.name.toLowerCase().includes('title') || 
    f.name.toLowerCase().includes('name') ||
    f.name.toLowerCase().includes('фамилия')
  )
  return titleField ? record[titleField.name] || 'Без названия' : record.id
}

// Drag & Drop функции (без изменений)
function onDragStart(event: DragEvent, card: TableRecord, columnId: string) {
  const target = event.target as HTMLElement
  draggedCard.value = { id: card.id, columnId, element: target }
  
  event.dataTransfer?.setData('text/plain', JSON.stringify({
    cardId: card.id,
    sourceColumnId: columnId
  }))
  
  event.dataTransfer!.effectAllowed = 'move'
  
  setTimeout(() => {
    target.classList.add('opacity-50')
  }, 0)
}

function onDragEnd(event: DragEvent) {
  const target = event.target as HTMLElement
  target.classList.remove('opacity-50')
  draggedCard.value = null
}

function onDragOver(event: DragEvent) {
  event.preventDefault()
  event.dataTransfer!.dropEffect = 'move'
}

function onDragEnter(event: DragEvent) {
  event.preventDefault()
  const target = event.currentTarget as HTMLElement
  target.classList.add('bg-blue-50', 'ring-2', 'ring-blue-200')
}

function onDragLeave(event: DragEvent) {
  const target = event.currentTarget as HTMLElement
  target.classList.remove('bg-blue-50', 'ring-2', 'ring-blue-200')
}

async function onDrop(event: DragEvent, targetColumnId: string) {
  event.preventDefault()
  
  const target = event.currentTarget as HTMLElement
  target.classList.remove('bg-blue-50', 'ring-2', 'ring-blue-200')
  
  const data = event.dataTransfer?.getData('text/plain')
  if (!data) return
  
  try {
    const { cardId, sourceColumnId } = JSON.parse(data)
    
    if (sourceColumnId === targetColumnId) return
    
    const sourceColumn = columns.value.find(c => c.id === sourceColumnId)
    
    if (sourceColumn && sourceColumn.cards.length === 1) {
      const confirmMove = confirm(
        `Вы перемещаете последнего сотрудника из отдела "${sourceColumnId}".\n` +
        `Отдел будет закрыт. Продолжить?`
      )
      if (!confirmMove) return
    }
    
    await recordsStore.updateRecord(props.table.id, cardId, {
      [props.groupField]: targetColumnId
    })
    
    await recordsStore.fetchRecords(props.table.id)
    
  } catch (error) {
    console.error('Drop error:', error)
  }
}
</script>

<template>
  <div class="kanban-container">
    <div class="kanban-board">
      <div
        v-for="column in columns"
        :key="column.id"
        class="kanban-column"
        :class="column.color"
        @dragover="onDragOver"
        @dragenter="onDragEnter"
        @dragleave="onDragLeave"
        @drop="onDrop($event, column.id)"
      >
        <!-- Минималистичный заголовок -->
        <div class="kanban-header">
          <span class="kanban-title">{{ column.title }}</span>
          <span class="kanban-badge">{{ column.count }}</span>
        </div>
        
        <!-- Карточки без лишних отступов -->
        <div class="kanban-cards">
          <div
            v-for="card in column.cards"
            :key="card.id"
            class="kanban-card"
            draggable="true"
            @dragstart="onDragStart($event, card, column.id)"
            @dragend="onDragEnd"
            @click="emit('cardClick', card)"
          >
            <div class="kanban-card-content">
              <div class="kanban-card-title">{{ getCardTitle(card) }}</div>
              
              <!-- Дополнительные поля одной строкой -->
              <div v-if="cardFields?.length" class="kanban-meta">
                <span 
                  v-for="fieldName in cardFields" 
                  :key="fieldName"
                  class="kanban-tag"
                >
                  {{ card[fieldName] || '—' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.kanban-container {
  width: 100%;
  overflow-x: auto;
  margin-top: 1rem;
  padding-bottom: 0.5rem;
}

.kanban-container::-webkit-scrollbar {
  height: 4px;
}

.kanban-container::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.kanban-container::-webkit-scrollbar-thumb {
  background: #94a3b8;
  border-radius: 2px;
}

.kanban-board {
  display: flex;
  gap: 0.75rem;
  min-width: min-content;
}

.kanban-column {
  flex: 0 0 220px; /* Уменьшил ширину */
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  max-height: calc(100vh - 200px);
}

.kanban-header {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: 0.5rem 0.5rem 0 0;
}

.kanban-title {
  font-weight: 600;
  font-size: 0.8125rem; /* Уменьшил */
  color: #1e293b;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.kanban-badge {
  font-size: 0.6875rem;
  background-color: white;
  padding: 0.125rem 0.375rem;
  border-radius: 9999px;
  color: #475569;
  border: 1px solid #e2e8f0;
  min-width: 1.25rem;
  text-align: center;
}

.kanban-cards {
  flex: 1;
  padding: 0.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.kanban-card {
  background-color: white;
  border-radius: 0.375rem;
  border: 1px solid #e2e8f0;
  transition: all 0.15s;
  cursor: move;
}

.kanban-card:hover {
  border-color: #94a3b8;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.kanban-card-content {
  padding: 0.5rem 0.625rem;
}

.kanban-card-title {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #0f172a;
  line-height: 1.4;
  word-break: break-word;
}

.kanban-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-top: 0.25rem;
}

.kanban-tag {
  font-size: 0.6875rem;
  background-color: #f1f5f9;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  color: #475569;
  white-space: nowrap;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Drag effects */
.opacity-50 {
  opacity: 0.5;
}

.bg-blue-50 {
  background-color: #eff6ff;
}

.ring-2 {
  box-shadow: 0 0 0 2px #bfdbfe;
}
</style>
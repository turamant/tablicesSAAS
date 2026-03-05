<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Table, Field } from '@/core/api/user/tables'
import { groupApi, type GroupResult } from '@/core/api/user/group'

const props = defineProps<{
  table: Table
}>()

const emit = defineEmits<{
  (e: 'grouped', data: GroupResult): void
  (e: 'close'): void
}>()

const groupByFields = ref<string[]>([])
const aggregates = ref<Array<{field: string, function: string}>>([])
const loading = ref(false)

// Все поля таблицы
const fields = computed(() => props.table.fields)

// Поля для группировки (можно группировать по текстовым полям, select, датам)
const groupableFields = computed(() => 
  fields.value.filter(f => 
    ['text', 'select', 'date'].includes(f.field_type)
  )
)

// Числовые поля для агрегаций
const numericFields = computed(() => 
  fields.value.filter(f => f.field_type === 'number')
)

// Функции агрегации
const aggFunctions = [
  { value: 'sum', label: 'Sum' },
  { value: 'avg', label: 'Average' },
  { value: 'count', label: 'Count' },
  { value: 'min', label: 'Minimum' },
  { value: 'max', label: 'Maximum' }
]

// Добавить группировку
function addGroupBy() {
  groupByFields.value.push('')
}

// Добавить агрегацию
function addAggregate() {
  aggregates.value.push({ field: '', function: 'sum' })
}

// Удалить группировку
function removeGroupBy(index: number) {
  groupByFields.value.splice(index, 1)
}

// Удалить агрегацию
function removeAggregate(index: number) {
  aggregates.value.splice(index, 1)
}

// Выполнить группировку
async function applyGroup() {
  if (groupByFields.value.length === 0 || aggregates.value.length === 0) return
  
  loading.value = true
  try {
    const response = await groupApi.groupData(props.table.id, {
      group_by: groupByFields.value.map(f => ({ field: f, sort_direction: 'asc' })),
      aggregates: aggregates.value.map(a => ({
        field: a.field,
        function: a.function as any,
        alias: `${a.field}_${a.function}`
      }))
    })
    emit('grouped', response.data)
  } catch (error) {
    console.error('Failed to group data:', error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
    <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
      <span>📊</span>
      Group By
    </h3>
    
    <!-- Group By fields -->
    <div class="space-y-3 mb-4">
      <div v-for="(_, index) in groupByFields" :key="index" class="flex gap-2">
        <select v-model="groupByFields[index]" class="flex-1 px-3 py-2 border rounded-lg">
          <option value="">Select field</option>
          <option v-for="field in groupableFields" :key="field.id" :value="field.name">
            {{ field.display_name }}
          </option>
        </select>
        <button @click="removeGroupBy(index)" class="text-red-500 hover:text-red-700">
          ✕
        </button>
      </div>
      
      <button
        @click="addGroupBy"
        class="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
      >
        + Add group by field
      </button>
    </div>
    
    <!-- Aggregations -->
    <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
      <span>∑</span>
      Aggregations
    </h3>
    
    <div class="space-y-3 mb-6">
      <div v-for="(agg, index) in aggregates" :key="index" class="flex gap-2">
        <select v-model="agg.field" class="flex-1 px-3 py-2 border rounded-lg">
          <option value="">Select field</option>
          <option v-for="field in numericFields" :key="field.id" :value="field.name">
            {{ field.display_name }}
          </option>
        </select>
        <select v-model="agg.function" class="w-32 px-3 py-2 border rounded-lg">
          <option v-for="fn in aggFunctions" :key="fn.value" :value="fn.value">
            {{ fn.label }}
          </option>
        </select>
        <button @click="removeAggregate(index)" class="text-red-500 hover:text-red-700">
          ✕
        </button>
      </div>
      
      <button
        @click="addAggregate"
        class="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
      >
        + Add aggregation
      </button>
    </div>
    
    <!-- Actions -->
    <div class="flex justify-end gap-3">
      <button
        @click="$emit('close')"
        class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
      >
        Cancel
      </button>
      <button
        @click="applyGroup"
        :disabled="loading || groupByFields.length === 0 || aggregates.length === 0"
        class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
      >
        <span v-if="loading" class="animate-spin">⏳</span>
        <span v-else>✓</span>
        {{ loading ? 'Applying...' : 'Apply Grouping' }}
      </button>
    </div>
  </div>
</template>
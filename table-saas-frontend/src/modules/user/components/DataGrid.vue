<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Table, Field } from '@/core/api/user/tables'
import type { TableRecord } from '@/core/api/user/records'
import { aggregateApi, type AggregateResponse } from '@/core/api/user/aggregate'
import { groupApi, type GroupResult } from '@/core/api/user/group'
import GroupPanel from './GroupPanel.vue'

const props = defineProps<{
  table: Table | null
  records: TableRecord[]
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'edit', record: TableRecord): void
  (e: 'delete', recordId: string): void
  (e: 'sort', field: string): void
}>()

// Состояния для агрегаций
const showAggregations = ref(false)
const aggregations = ref<AggregateResponse | null>(null)
const loadingAggs = ref(false)
const selectedAggFields = ref<Set<string>>(new Set())

// Состояния для группировок
const showGroupPanel = ref(false)
const groupedData = ref<GroupResult | null>(null)

// Сортировка
const sortField = ref('')
const sortDirection = ref<'asc' | 'desc'>('asc')

// Безопасный доступ к полям
const fields = computed(() => props.table?.fields || [])

// Числовые поля
const numericFields = computed(() => 
  fields.value.filter(f => f.field_type === 'number')
)

// Форматирование значений
function formatValue(value: any, field: Field): string {
  if (value === null || value === undefined) return '-'
  
  switch (field.field_type) {
    case 'boolean':
      return value ? '✓' : '✗'
    case 'date':
      return new Date(value).toLocaleDateString()
    case 'select':
    case 'multiselect':
      return Array.isArray(value) ? value.join(', ') : String(value)
    case 'number':
      return formatNumber(value)
    default:
      return String(value)
  }
}

// ФОРМАТИРОВАНИЕ ЧИСЕЛ (ИСПРАВЛЕНО)
function formatNumber(value: any): string {
  if (value === null || value === undefined) return '-'
  
  let num: number
  
  if (typeof value === 'string') {
    // Обработка экспоненциальной записи и запятых
    const cleaned = value.replace(',', '.').trim()
    num = parseFloat(cleaned)
  } else if (typeof value === 'number') {
    num = value
  } else {
    // Попытка преобразовать любой другой тип
    num = Number(value)
  }
  
  if (isNaN(num)) return String(value)
  
  // Для больших чисел — без дробной части
  if (Math.abs(num) >= 100000) {
    return Math.round(num).toLocaleString('ru-RU')
  }
  
  // Обычные числа — до 2 знаков после запятой
  return num.toLocaleString('ru-RU', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  })
}

// Форматирование валюты (если нужно)
function formatCurrency(value: number): string {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

function handleSort(fieldName: string) {
  if (sortField.value === fieldName) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = fieldName
    sortDirection.value = 'asc'
  }
  emit('sort', `${sortField.value}:${sortDirection.value}`)
}

// Переключение агрегаций
async function toggleAggregations() {
  showAggregations.value = !showAggregations.value
  groupedData.value = null // Скрываем группировки при включении итогов
  
  if (showAggregations.value) {
    await fetchAggregations()
  }
}

// Выбор поля для агрегации
function toggleAggField(fieldName: string) {
  if (selectedAggFields.value.has(fieldName)) {
    selectedAggFields.value.delete(fieldName)
  } else {
    selectedAggFields.value.add(fieldName)
  }
  
  if (showAggregations.value) {
    fetchAggregations()
  }
}

// Выбрать все числовые поля
function selectAllNumeric() {
  numericFields.value.forEach(f => selectedAggFields.value.add(f.name))
  if (showAggregations.value) {
    fetchAggregations()
  }
}

// Сбросить выбор
function clearSelection() {
  selectedAggFields.value.clear()
  if (showAggregations.value) {
    fetchAggregations()
  }
}

// Загрузка агрегаций
async function fetchAggregations() {
  if (!props.table) return
  
  loadingAggs.value = true
  try {
    const fields = selectedAggFields.value.size > 0 
      ? Array.from(selectedAggFields.value)
      : undefined
    
    const { data } = await aggregateApi.getAggregations(props.table.id, fields)
    aggregations.value = data
  } catch (error) {
    console.error('Failed to fetch aggregations:', error)
  } finally {
    loadingAggs.value = false
  }
}

// Обработка результатов группировки
function handleGroupedData(data: GroupResult) {
  groupedData.value = data
  showGroupPanel.value = false
  showAggregations.value = false // Скрываем итоги при показе группировок
}

// Следим за изменением таблицы
watch(() => props.table, () => {
  if (showAggregations.value) {
    fetchAggregations()
  }
})
</script>

<template>
  <div v-if="!table" class="text-center py-12 text-gray-500">
    Loading table structure...
  </div>
  <div v-else class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
    <!-- Панель управления -->
    <div class="border-b border-gray-200 bg-gray-50 px-4 py-2 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <!-- Кнопка Итоги -->
        <button
          @click="toggleAggregations"
          class="px-3 py-1.5 rounded-lg flex items-center gap-2 transition-colors"
          :class="showAggregations ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
        >
          <span class="text-lg">Σ</span>
          <span class="text-sm font-medium">{{ showAggregations ? 'Hide Totals' : 'Show Totals' }}</span>
        </button>
        
        <!-- Кнопка Группировка -->
        <button
          @click="showGroupPanel = !showGroupPanel"
          class="px-3 py-1.5 rounded-lg flex items-center gap-2 transition-colors"
          :class="showGroupPanel ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
        >
          <span class="text-lg">📊</span>
          <span class="text-sm font-medium">{{ showGroupPanel ? 'Hide Grouping' : 'Show Grouping' }}</span>
        </button>
        
        <!-- Панель выбора полей для агрегаций -->
        <div v-if="showAggregations && numericFields.length" class="flex items-center gap-2">
          <span class="text-xs text-gray-500">Fields:</span>
          <div class="flex items-center gap-2">
            <button
              @click="selectAllNumeric"
              class="text-xs px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50"
            >
              All
            </button>
            <button
              @click="clearSelection"
              class="text-xs px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50"
            >
              Clear
            </button>
          </div>
        </div>
      </div>
      
      <!-- Индикатор загрузки -->
      <div v-if="loadingAggs" class="flex items-center gap-2">
        <div class="animate-spin h-4 w-4 border-2 border-gray-300 border-t-blue-600 rounded-full"></div>
        <span class="text-xs text-gray-500">Calculating...</span>
      </div>
    </div>
    
    <!-- Панель группировки -->
    <GroupPanel
      v-if="showGroupPanel && table"
      :table="table"
      @grouped="handleGroupedData"
      @close="showGroupPanel = false"
    />
    
    <!-- Таблица сгруппированных данных -->
    <div v-if="groupedData" class="p-4 border-t border-gray-200">
      <div class="flex justify-between items-center mb-3">
        <h3 class="font-medium flex items-center gap-2">
          <span>📊</span>
          Grouped Results
        </h3>
        <button @click="groupedData = null" class="text-sm text-gray-500 hover:text-gray-700">
          ✕ Clear
        </button>
      </div>
      
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th v-for="col in Object.keys(groupedData.groups[0] || {})" 
                  :key="col"
                  class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                {{ col }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="(row, idx) in groupedData.groups" :key="idx">
              <td v-for="(val, key) in row" 
                  :key="key"
                  class="px-4 py-2 text-sm text-gray-900">
                {{ formatNumber(val) }}
              </td>
            </tr>
          </tbody>
          <tfoot v-if="groupedData.grand_totals && Object.keys(groupedData.grand_totals).length" 
                 class="bg-gray-50 border-t-2 border-gray-200">
            <tr>
              <td :colspan="Object.keys(groupedData.groups[0] || {}).length" 
                  class="px-4 py-2 text-sm font-medium">
                <div class="flex items-center gap-4">
                  <span class="text-lg">📊</span>
                  <span>Grand Totals:</span>
                  <span v-for="(val, key) in groupedData.grand_totals" :key="key">
                    {{ key }}: {{ typeof val === 'number' ? formatNumber(val) : val }}
                  </span>
                </div>
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
      
      <p class="text-xs text-gray-500 mt-2">
        Total groups: {{ groupedData.total_groups }}
      </p>
    </div>
    
    <!-- Основная таблица (показывается если нет группировки) -->
    <div v-if="!groupedData" class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <!-- Header -->
        <thead class="bg-gray-50">
          <tr>
            <th 
              v-for="field in fields" 
              :key="field.id"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              <div class="flex items-center gap-2">
                <!-- Чекбокс для числовых полей (только при включенных агрегациях) -->
                <input
                  v-if="showAggregations && field.field_type === 'number'"
                  type="checkbox"
                  :checked="selectedAggFields.has(field.name)"
                  @change="toggleAggField(field.name)"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                
                <!-- Заголовок с сортировкой -->
                <button
                  @click="handleSort(field.name)"
                  class="flex items-center gap-1 hover:text-gray-900"
                >
                  {{ field.display_name }}
                  <span v-if="field.is_required" class="text-red-500">*</span>
                  <span v-if="sortField === field.name" class="text-gray-400">
                    {{ sortDirection === 'asc' ? '↑' : '↓' }}
                  </span>
                </button>
              </div>
            </th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        
        <!-- Body -->
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-if="loading">
            <td :colspan="fields.length + 1" class="px-6 py-12 text-center text-gray-500">
              <div class="flex items-center justify-center gap-2">
                <div class="animate-spin h-5 w-5 border-2 border-gray-300 border-t-blue-600 rounded-full"></div>
                Loading records...
              </div>
            </td>
          </tr>
          
          <tr v-else-if="records.length === 0">
            <td :colspan="fields.length + 1" class="px-6 py-12 text-center text-gray-500">
              <div class="flex flex-col items-center gap-2">
                <span class="text-4xl">📭</span>
                <p>No records yet. Click "Add Record" to create one.</p>
              </div>
            </td>
          </tr>
          
          <tr v-else v-for="record in records" :key="record.id" class="hover:bg-gray-50">
            <td 
              v-for="field in fields" 
              :key="field.id"
              class="px-6 py-4 text-sm text-gray-900"
            >
              {{ formatValue(record[field.name], field) }}
            </td>
            <td class="px-6 py-4 text-right text-sm font-medium whitespace-nowrap">
              <button
                @click="emit('edit', record)"
                class="text-blue-600 hover:text-blue-900 mr-3"
              >
                Edit
              </button>
              <button
                @click="emit('delete', record.id)"
                class="text-red-600 hover:text-red-900"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
        
        <!-- Footer с итогами -->
        <tfoot v-if="showAggregations && aggregations" class="bg-gray-50 border-t-2 border-gray-200">
          <tr>
            <td :colspan="fields.length + 1" class="px-6 py-3">
              <div class="flex items-center gap-6 text-sm">
                <!-- Total Records -->
                <div class="flex items-center gap-2">
                  <span class="text-lg">📊</span>
                  <span class="font-medium">Total Records:</span>
                  <span class="text-gray-900">{{ aggregations.total_records }}</span>
                </div>
                
                <!-- Sums -->
                <div v-if="Object.keys(aggregations.sums).length" 
                     v-for="(value, fieldName) in aggregations.sums" 
                     :key="'sum-'+fieldName"
                     class="flex items-center gap-2"
                >
                  <span class="text-lg">Σ</span>
                  <span class="font-medium">{{ fieldName }}:</span>
                  <span class="text-gray-900">{{ formatNumber(value) }}</span>
                </div>
                
                <!-- Averages -->
                <div v-if="Object.keys(aggregations.averages).length" 
                     v-for="(value, fieldName) in aggregations.averages" 
                     :key="'avg-'+fieldName"
                     class="flex items-center gap-2"
                >
                  <span class="text-lg">∅</span>
                  <span class="font-medium">{{ fieldName }}:</span>
                  <span class="text-gray-900">{{ formatNumber(value) }}</span>
                </div>
                
                <!-- Mins -->
                <div v-if="Object.keys(aggregations.mins).length" 
                     v-for="(value, fieldName) in aggregations.mins" 
                     :key="'min-'+fieldName"
                     class="flex items-center gap-2"
                >
                  <span class="text-lg">↓</span>
                  <span class="font-medium">{{ fieldName }}:</span>
                  <span class="text-gray-900">{{ formatNumber(value) }}</span>
                </div>
                
                <!-- Maxs -->
                <div v-if="Object.keys(aggregations.maxs).length" 
                     v-for="(value, fieldName) in aggregations.maxs" 
                     :key="'max-'+fieldName"
                     class="flex items-center gap-2"
                >
                  <span class="text-lg">↑</span>
                  <span class="font-medium">{{ fieldName }}:</span>
                  <span class="text-gray-900">{{ formatNumber(value) }}</span>
                </div>
                
                <!-- Empty state -->
                <div v-if="!Object.keys(aggregations.sums).length && 
                          !Object.keys(aggregations.averages).length &&
                          !Object.keys(aggregations.mins).length &&
                          !Object.keys(aggregations.maxs).length"
                     class="text-gray-400 italic"
                >
                  No numeric fields selected for aggregation
                </div>
              </div>
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>
</template>
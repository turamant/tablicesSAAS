<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Table, Field } from '@/core/api/user/tables'
import type { TableRecord } from '@/core/api/user/records'

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

// Сортировка
const sortField = ref('')
const sortDirection = ref<'asc' | 'desc'>('asc')

// Безопасный доступ к полям
const fields = computed(() => props.table?.fields || [])

// Функция форматирования значений - ЭТО БЫЛО ПОТЕРЯНО!
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
    default:
      return String(value)
  }
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
</script>

<template>
  <div v-if="!table" class="text-center py-12 text-gray-500">
    Loading table structure...
  </div>
  <div v-else class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <!-- Header -->
        <thead class="bg-gray-50">
          <tr>
            <th 
              v-for="field in fields" 
              :key="field.id"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              @click="handleSort(field.name)"
            >
              <div class="flex items-center gap-1">
                {{ field.display_name }}
                <span v-if="field.is_required" class="text-red-500">*</span>
                <span v-if="sortField === field.name" class="text-gray-400">
                  {{ sortDirection === 'asc' ? '↑' : '↓' }}
                </span>
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
              Loading...
            </td>
          </tr>
          
          <tr v-else-if="records.length === 0">
            <td :colspan="fields.length + 1" class="px-6 py-12 text-center text-gray-500">
              No records yet. Click "Add Record" to create one.
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
            <td class="px-6 py-4 text-right text-sm font-medium">
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
      </table>
    </div>
  </div>
</template>
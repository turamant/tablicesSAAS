<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/core/stores/auth'
import { useTablesStore } from '@/modules/user/stores/tables.store'
import { useRecordsStore } from '@/modules/user/stores/records.store'
import DataGrid from '@/modules/user/components/DataGrid.vue'
import RecordModal from '@/modules/user/components/RecordModal.vue'
import EditFieldsModal from '@/modules/user/components/EditFieldsModal.vue'
import type { TableRecord } from '@/core/api/user/records'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const tablesStore = useTablesStore()
const recordsStore = useRecordsStore()

// Используем computed для tableId
const tableId = ref(route.params.id as string)
const showRecordModal = ref(false)
const showEditFieldsModal = ref(false)
const editingRecord = ref<TableRecord | null>(null)

// Функция загрузки всех данных
async function loadTableData() {
  console.log('Loading table data for:', tableId.value)
  
  try {
    await tablesStore.fetchTable(tableId.value)
    console.log('Table loaded:', tablesStore.currentTable)
    
    if (tablesStore.currentTable) {
      await recordsStore.fetchRecords(tableId.value)
    }
  } catch (error) {
    console.error('Failed to load:', error)
  }
}

onMounted(async () => {
  await loadTableData()
})

// Следим за изменением параметра в роуте
watch(() => route.params.id, async (newId) => {
  if (newId) {
    tableId.value = newId as string
    await loadTableData()
  }
})

function handleSort(sort: string) {
  const [field, direction] = sort.split(':')
  recordsStore.fetchRecords(tableId.value, {
    order_by: field,
    order_direction: direction as 'asc' | 'desc'
  })
}

function addRecord() {
  editingRecord.value = null
  showRecordModal.value = true
}

function editRecord(record: TableRecord) {
  editingRecord.value = record
  showRecordModal.value = true
}

async function saveRecord(data: Record<string, any>) {
  try {
    if (editingRecord.value) {
      await recordsStore.updateRecord(tableId.value, editingRecord.value.id, data)
    } else {
      await recordsStore.createRecord(tableId.value, data)
    }
    showRecordModal.value = false
    await recordsStore.fetchRecords(tableId.value)
  } catch (error) {
    console.error('Failed to save record:', error)
  }
}

async function deleteRecord(recordId: string) {
  if (confirm('Are you sure?')) {
    await recordsStore.deleteRecord(tableId.value, recordId)
  }
}

// После редактирования полей перезагружаем таблицу
async function handleFieldsUpdated() {
  console.log('Fields updated, reloading table...')
  await loadTableData()
  // Модалка закроется автоматически по @close
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <button 
          @click="router.back()" 
          class="text-gray-600 hover:text-gray-900 mb-2 flex items-center gap-1"
        >
          ← Back to Tables
        </button>
        <h1 class="text-2xl font-bold">{{ tablesStore.currentTable?.name }}</h1>
        <p v-if="tablesStore.currentTable?.description" class="text-gray-600 mt-1">
          {{ tablesStore.currentTable.description }}
        </p>
      </div>
      
      <div class="flex gap-2">
        <!-- Кнопка редактирования полей -->
        <button
          v-if="tablesStore.currentTable"
          @click="showEditFieldsModal = true"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          Edit Fields
        </button>
        
        <!-- Кнопка добавления записи -->
        <button
          v-if="tablesStore.currentTable"
          @click="addRecord"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Record
        </button>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="!tablesStore.currentTable" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"></div>
      <p class="mt-2 text-gray-600">Loading table...</p>
    </div>

    <!-- Data Grid -->
    <DataGrid
      v-else
      :table="tablesStore.currentTable"
      :records="recordsStore.records"
      :loading="recordsStore.isLoading"
      @edit="editRecord"
      @delete="deleteRecord"
      @sort="handleSort"
    />

    <!-- Record Modal -->
    <RecordModal
      :show="showRecordModal"
      :table="tablesStore.currentTable"
      :record="editingRecord"
      @close="showRecordModal = false"
      @save="saveRecord"
    />

    <!-- Edit Fields Modal -->
    <EditFieldsModal
      :show="showEditFieldsModal"
      :table="tablesStore.currentTable"
      @close="showEditFieldsModal = false"
      @updated="handleFieldsUpdated"
    />
  </div>
</template>
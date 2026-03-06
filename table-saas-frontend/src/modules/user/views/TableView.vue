<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/core/stores/auth'
import { useTablesStore } from '@/modules/user/stores/tables.store'
import { useRecordsStore } from '@/modules/user/stores/records.store'
import { useViewsStore } from '@/modules/user/stores/views.store'
import DataGrid from '@/modules/user/components/DataGrid.vue'
import RecordModal from '@/modules/user/components/RecordModal.vue'
import EditFieldsModal from '@/modules/user/components/EditFieldsModal.vue'
import ImportExcelModal from '@/modules/user/components/ImportExcelModal.vue'
import ViewSwitcher from '@/modules/user/components/ViewSwitcher.vue'
import KanbanView from '@/modules/user/components/KanbanView.vue'
import type { TableRecord } from '@/core/api/user/records'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const tablesStore = useTablesStore()
const recordsStore = useRecordsStore()
const viewsStore = useViewsStore()

const tableId = ref(route.params.id as string)
const showRecordModal = ref(false)
const showEditFieldsModal = ref(false)
const showImportModal = ref(false)
const editingRecord = ref<TableRecord | null>(null)

// Загрузка всех данных
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

// Экспорт в Excel
async function exportToExcel() {
  const url = `${import.meta.env.VITE_API_URL}/tables/${tableId.value}/export/excel?include_aggregations=true`
  window.open(url, '_blank')
}

// Инициализация
onMounted(async () => {
  // Сначала загружаем таблицу
  await tablesStore.fetchTable(tableId.value)
  
  // Потом загружаем виды
  await viewsStore.fetchViews(tableId.value)
  
  // Если видов нет - создаем дефолтные
  if (viewsStore.views.length === 0 && tablesStore.currentTable) {
    // Создаем Grid вид
    await viewsStore.createView(tableId.value, {
      name: 'Grid',
      type: 'grid',
      table_id: tableId.value,
      settings: {},
      is_default: true
    })
    
    // Находим select поле для канбана
    const statusField = tablesStore.currentTable.fields.find(
      f => f.field_type === 'select' || f.name.toLowerCase().includes('status')
    )
    
    if (statusField) {
      await viewsStore.createView(tableId.value, {
        name: 'Kanban',
        type: 'kanban',
        table_id: tableId.value,
        settings: {
          kanban_group_field: statusField.name,
          card_fields: ['title', 'description'].filter(f => 
            tablesStore.currentTable?.fields.some(fld => fld.name === f)
          )
        },
        is_default: false
      })
    }
    
    // Перезагружаем виды
    await viewsStore.fetchViews(tableId.value)
  }
  
  // Загружаем записи
  if (tablesStore.currentTable) {
    await recordsStore.fetchRecords(tableId.value)
  }
})

// Следим за изменением параметра
watch(() => route.params.id, async (newId) => {
  if (newId) {
    tableId.value = newId as string
    await viewsStore.fetchViews(tableId.value)
    await loadTableData()
  }
})

// Сортировка
function handleSort(sort: string) {
  const [field, direction] = sort.split(':')
  recordsStore.fetchRecords(tableId.value, {
    order_by: field,
    order_direction: direction as 'asc' | 'desc'
  })
}

// CRUD записей
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

// После редактирования полей
async function handleFieldsUpdated() {
  console.log('Fields updated, reloading table...')
  await loadTableData()
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
        <!-- Edit Fields -->
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
        
        <!-- Add Record -->
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

        <!-- Export Excel -->
        <button
          @click="exportToExcel"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Export Excel
        </button>

        <!-- Import Excel -->
        <button
          @click="showImportModal = true"
          class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          Import Excel
        </button>
      </div>
    </div>

    <!-- View Switcher - показываем всегда, если есть таблица -->
    <ViewSwitcher
      v-if="tablesStore.currentTable"
      :table-id="tableId"
      :table-fields="tablesStore.currentTable.fields"
    />

    <!-- Loading state -->
    <div v-if="!tablesStore.currentTable" class="text-center py-12">
      <div class="animate-spin h-8 w-8 border-4 border-gray-300 border-t-blue-600 rounded-full mx-auto"></div>
      <p class="mt-2 text-gray-600">Loading table...</p>
    </div>

    <!-- Grid View -->
    <DataGrid
      v-else-if="viewsStore.currentView?.type === 'grid' || !viewsStore.currentView"
      :table="tablesStore.currentTable"
      :records="recordsStore.records"
      :loading="recordsStore.isLoading"
      @edit="editRecord"
      @delete="deleteRecord"
      @sort="handleSort"
    />

    <!-- Kanban View -->
    <KanbanView
      v-else-if="viewsStore.currentView?.type === 'kanban'"
      :key="viewsStore.currentView?.id"  
      :table="tablesStore.currentTable"
      :records="recordsStore.records"
      :group-field="viewsStore.currentView.settings.kanban_group_field || 'status'"
      :card-fields="viewsStore.currentView.settings.card_fields"
      @card-click="editRecord"
    />

    <!-- Calendar View (заглушка) -->
    <div v-else-if="viewsStore.currentView?.type === 'calendar'" class="text-center py-12 text-gray-500">
      Calendar view coming soon...
    </div>

    <!-- Gallery View (заглушка) -->
    <div v-else-if="viewsStore.currentView?.type === 'gallery'" class="text-center py-12 text-gray-500">
      Gallery view coming soon...
    </div>

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

    <!-- Import Modal -->
    <ImportExcelModal
      :show="showImportModal"
      :table="tablesStore.currentTable"
      @close="showImportModal = false"
      @imported="loadTableData"
    />
  </div>
</template>
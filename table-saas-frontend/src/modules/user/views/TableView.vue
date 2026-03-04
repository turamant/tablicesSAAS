<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/core/stores/auth'
import { useTablesStore } from '@/modules/user/stores/tables.store'
import { useRecordsStore } from '@/modules/user/stores/records.store'
import DataGrid from '@/modules/user/components/DataGrid.vue'
import RecordModal from '@/modules/user/components/RecordModal.vue'
import type { TableRecord } from '@/core/api/user/records'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const tablesStore = useTablesStore()
const recordsStore = useRecordsStore()

const tableId = route.params.id as string
const showRecordModal = ref(false)
const editingRecord = ref<TableRecord | null>(null)

onMounted(async () => {
  console.log('Loading table:', tableId)
  console.log('Current user:', authStore.user)
  
  try {
    await tablesStore.fetchTable(tableId)
    console.log('Table loaded:', tablesStore.currentTable)
    
    if (tablesStore.currentTable) {
      await recordsStore.fetchRecords(tableId)
    }
  } catch (error) {
    console.error('Failed to load:', error)
  }
})

function handleSort(sort: string) {
  const [field, direction] = sort.split(':')
  recordsStore.fetchRecords(tableId, {
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
      await recordsStore.updateRecord(tableId, editingRecord.value.id, data)
    } else {
      await recordsStore.createRecord(tableId, data)
    }
    showRecordModal.value = false
    await recordsStore.fetchRecords(tableId)
  } catch (error) {
    console.error('Failed to save record:', error)
  }
}

async function deleteRecord(recordId: string) {
  if (confirm('Are you sure?')) {
    await recordsStore.deleteRecord(tableId, recordId)
  }
}
</script>

<template>
  <div>
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

    <div v-if="!tablesStore.currentTable" class="text-center py-12">
      Loading table...
    </div>

    <DataGrid
      v-else
      :table="tablesStore.currentTable"
      :records="recordsStore.records"
      :loading="recordsStore.isLoading"
      @edit="editRecord"
      @delete="deleteRecord"
      @sort="handleSort"
    />

    <RecordModal
      :show="showRecordModal"
      :table="tablesStore.currentTable"
      :record="editingRecord"
      @close="showRecordModal = false"
      @save="saveRecord"
    />
  </div>
</template>
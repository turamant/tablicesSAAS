<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/core/stores/auth'
import { useTablesStore } from '@/modules/user/stores/tables.store'
import { RouterLink } from 'vue-router'
import CreateTableModal from '@/modules/user/components/CreateTableModal.vue'
import EditTableModal from '@/modules/user/components/EditTableModal.vue'
import type { Table } from '@/core/api/user/tables'

const auth = useAuthStore()
const tablesStore = useTablesStore()
const showCreateModal = ref(false)
const tableToDelete = ref<string | null>(null)
const showDeleteConfirm = ref(false)
const showEditModal = ref(false)
const editingTable = ref<Table | null>(null)

onMounted(() => {
  tablesStore.fetchTables()
})

function confirmDelete(tableId: string, tableName: string) {
  tableToDelete.value = tableId
  showDeleteConfirm.value = true
}

async function handleDelete() {
  if (!tableToDelete.value) return
  
  try {
    await tablesStore.deleteTable(tableToDelete.value)
    showDeleteConfirm.value = false
    tableToDelete.value = null
  } catch (error) {
    console.error('Failed to delete table:', error)
  }
}

function editTable(table: Table) {
  editingTable.value = table
  showEditModal.value = true
}

async function handleEditSave(data: { name: string; description: string }) {
  if (!editingTable.value) return
  
  try {
    await tablesStore.updateTable(editingTable.value.id, data)
    showEditModal.value = false
    editingTable.value = null
  } catch (error) {
    console.error('Failed to update table:', error)
  }
}
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">Your Tables</h1>
      <button
        @click="showCreateModal = true"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
      >
        + New Table
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="tablesStore.isLoading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"></div>
      <p class="mt-2 text-gray-600">Loading tables...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="tablesStore.tables.length === 0" class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No tables</h3>
      <p class="mt-1 text-sm text-gray-500">Get started by creating your first table.</p>
      <button
        @click="showCreateModal = true"
        class="mt-4 inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
      >
        Create your first table
      </button>
    </div>

    <!-- Tables Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="table in tablesStore.tables"
        :key="table.id"
        class="block bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200"
      >
        <RouterLink
          :to="`/dashboard/tables/${table.id}`"
          class="block p-4"
        >
          <h3 class="text-lg font-semibold mb-2">{{ table.name }}</h3>
          <p class="text-gray-600 text-sm mb-3 line-clamp-2">{{ table.description || 'No description' }}</p>
          <div class="flex justify-between text-xs text-gray-500">
            <span>{{ table.fields?.length || 0 }} fields</span>
            <span>{{ new Date(table.created_at).toLocaleDateString() }}</span>
          </div>
        </RouterLink>
        
        <!-- Actions -->
        <div class="border-t border-gray-200 px-4 py-2 flex justify-end gap-2">
          <button
            @click="editTable(table)"
            class="text-sm text-blue-600 hover:text-blue-800"
          >
            Edit
          </button>
          <button
            @click="confirmDelete(table.id, table.name)"
            class="text-sm text-red-600 hover:text-red-800"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Create Table Modal -->
    <CreateTableModal
      :show="showCreateModal"
      @close="showCreateModal = false"
      @created="tablesStore.fetchTables()"
    />

    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 overflow-y-auto">
        <div class="fixed inset-0 bg-black/50" @click="showDeleteConfirm = false"></div>
        <div class="relative min-h-screen flex items-center justify-center p-4">
          <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-md p-6">
            <h3 class="text-lg font-semibold mb-2">Delete Table</h3>
            <p class="text-gray-600 mb-6">
              Are you sure you want to delete this table? All data will be permanently lost.
            </p>
            <div class="flex justify-end gap-3">
              <button
                @click="showDeleteConfirm = false"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                @click="handleDelete"
                class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Edit Table Modal -->
    <EditTableModal
      :show="showEditModal"
      :table="editingTable"
      @close="showEditModal = false"
      @save="handleEditSave"
    />
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/core/stores/auth'
import { useTablesStore } from '@/modules/user/stores/tables.store'
import { RouterLink } from 'vue-router'
import CreateTableModal from '@/modules/user/components/CreateTableModal.vue'

const auth = useAuthStore()
const tablesStore = useTablesStore()
const showCreateModal = ref(false)

onMounted(() => {
  tablesStore.fetchTables()
})
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
      <RouterLink
        v-for="table in tablesStore.tables"
        :key="table.id"
        :to="`/dashboard/tables/${table.id}`"
        class="block p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200"
      >
        <h3 class="text-lg font-semibold mb-2">{{ table.name }}</h3>
        <p class="text-gray-600 text-sm mb-3 line-clamp-2">{{ table.description || 'No description' }}</p>
        <div class="flex justify-between text-xs text-gray-500">
          <span>{{ table.fields?.length || 0 }} fields</span>
          <span>{{ new Date(table.created_at).toLocaleDateString() }}</span>
        </div>
      </RouterLink>
    </div>

    <!-- Create Table Modal -->
    <CreateTableModal
      :show="showCreateModal"
      @close="showCreateModal = false"
      @created="tablesStore.fetchTables()"
    />
  </div>
</template>
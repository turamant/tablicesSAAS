<script setup lang="ts">
import { computed, ref } from 'vue'
import { useViewsStore } from '@/modules/user/stores/views.store'
import type { ViewType, View } from '@/core/api/user/views'
import CreateViewModal from './CreateViewModal.vue'

const props = defineProps<{
  tableId: string
  tableFields?: any[]
}>()

const viewsStore = useViewsStore()
const showCreateModal = ref(false)

const viewTypes: { value: ViewType; label: string; icon: string }[] = [
  { value: 'grid', label: 'Grid', icon: '⊞' },
  { value: 'kanban', label: 'Kanban', icon: '📋' },
  { value: 'calendar', label: 'Calendar', icon: '📅' },
  { value: 'gallery', label: 'Gallery', icon: '🖼️' },
]

function changeView(viewId: string) {
  const view = viewsStore.views.find(v => v.id === viewId)
  if (view) {
    viewsStore.setCurrentView(view)
  }
}

async function deleteView(view: View) {
  if (!confirm(`Удалить вид "${view.name}"?`)) return
  
  try {
    await viewsStore.deleteView(props.tableId, view.id)
    // Вид удалится, store обновится автоматически
  } catch (error) {
    console.error('Failed to delete view:', error)
    alert('Ошибка при удалении вида')
  }
}

function openCreateModal(type: ViewType) {
  showCreateModal.value = true
}

function handleViewCreated() {
  viewsStore.fetchViews(props.tableId)
}

console.log('Views in switcher:', viewsStore.views)
console.log('Current view:', viewsStore.currentView)
</script>

<template>
  <div class="flex items-center gap-2 border-b border-gray-200 px-4">
    <!-- Существующие виды -->
    <div class="flex gap-1">
      <div
        v-for="view in viewsStore.views"
        :key="view.id"
        class="relative group"
      >
        <button
          @click="changeView(view.id)"
          class="px-3 py-2 text-sm font-medium rounded-t-lg transition-colors pr-8"
          :class="view.id === viewsStore.currentView?.id 
            ? 'bg-white text-blue-600 border-t border-l border-r border-gray-200 -mb-px' 
            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'"
        >
          <span class="mr-1">{{ viewTypes.find(t => t.value === view.type)?.icon }}</span>
          {{ view.name }}
        </button>
        
        <!-- Кнопка удаления -->
        <button
          v-if="viewsStore.views.length > 1"
          @click.stop="deleteView(view)"
          class="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-4 h-4 flex items-center justify-center text-xs transition-opacity"
          :class="view.id === viewsStore.currentView?.id 
            ? 'opacity-100'  // всегда виден для активного
            : 'opacity-0 group-hover:opacity-100'"
        >
          ×
        </button>
      </div>
    </div>
    
    <!-- Кнопка добавления нового вида -->
    <div class="relative group">
      <button class="px-2 py-2 text-gray-400 hover:text-gray-600">
        +
      </button>
      <div class="absolute left-0 top-full mt-1 bg-white shadow-lg rounded-lg border border-gray-200 hidden group-hover:block z-10 min-w-[150px]">
        <div class="py-1">
          <button
            v-for="type in viewTypes"
            :key="type.value"
            @click="openCreateModal(type.value)"
            class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center gap-2"
          >
            <span>{{ type.icon }}</span>
            {{ type.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <CreateViewModal
      :show="showCreateModal"
      :table-id="tableId"
      :table-fields="tableFields || []"
      @close="showCreateModal = false"
      @created="handleViewCreated"
    />
  </div>
</template>

<style scoped>
.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}

.transition-opacity {
  transition: opacity 0.2s ease-in-out;
}
</style>
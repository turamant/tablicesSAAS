<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Table } from '@/core/api/user/tables'

const props = defineProps<{
  show: boolean
  table: Table | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', data: { name: string; description: string }): void
}>()

const form = ref({
  name: '',
  description: ''
})

watch(() => props.table, (newTable) => {
  if (newTable) {
    form.value = {
      name: newTable.name,
      description: newTable.description || ''
    }
  }
}, { immediate: true })

watch(() => props.show, (newVal) => {
  if (!newVal) {
    form.value = { name: '', description: '' }
  }
})

function handleSubmit() {
  emit('save', form.value)
  emit('close')
}

function closeModal() {
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="fixed inset-0 bg-black/50" @click="closeModal"></div>
      <div class="relative min-h-screen flex items-center justify-center p-4">
        <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-md">
          <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-xl font-semibold">Edit Table</h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-500 text-2xl">&times;</button>
          </div>
          
          <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Table Name *</label>
              <input
                v-model="form.name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="form.description"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div class="flex justify-end gap-3 pt-4">
              <button
                type="button"
                @click="closeModal"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
              >
                Save Changes
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </Teleport>
</template>
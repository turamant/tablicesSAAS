<script setup lang="ts">
import { ref, computed } from 'vue'
import { useViewsStore } from '@/modules/user/stores/views.store'
import type { ViewType } from '@/core/api/user/views'

const props = defineProps<{
  show: boolean
  tableId: string
  tableFields: any[] // поля таблицы
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'created'): void
}>()

const viewsStore = useViewsStore()

const step = ref(1)
const form = ref({
  name: '',
  type: 'kanban' as ViewType,
  settings: {
    kanban_group_field: '',
    card_fields: [] as string[],
    show_empty_columns: true
  }
})

// Поля для группировки (select, text с небольшим количеством уникальных значений)
const groupableFields = computed(() => 
  props.tableFields.filter(f => 
    ['select', 'text', 'number', 'date'].includes(f.field_type)
  )
)

// Все поля для отображения в карточке
const allFields = computed(() => props.tableFields)

function nextStep() {
  if (step.value === 1 && form.value.name && form.value.type) {
    step.value = 2
  }
}

function prevStep() {
  step.value = 1
}

async function createView() {
  try {
    await viewsStore.createView(props.tableId, {
      name: form.value.name,
      type: form.value.type,
      table_id: props.tableId,
      settings: form.value.settings,
      is_default: false
    })
    emit('created')
    closeModal()
  } catch (error) {
    console.error('Failed to create view:', error)
  }
}

function closeModal() {
  step.value = 1
  form.value = {
    name: '',
    type: 'kanban',
    settings: {
      kanban_group_field: '',
      card_fields: [],
      show_empty_columns: true
    }
  }
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="fixed inset-0 bg-black/50" @click="closeModal"></div>
      <div class="relative min-h-screen flex items-center justify-center p-4">
        <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-2xl">
          
          <!-- Header -->
          <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-xl font-semibold">Create New View</h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-500">&times;</button>
          </div>

          <!-- Step 1: Basic Info -->
          <div v-if="step === 1" class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">View Name *</label>
              <input
                v-model="form.name"
                type="text"
                class="w-full px-3 py-2 border rounded-lg"
                placeholder="e.g. Sales Pipeline"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">View Type *</label>
              <div class="grid grid-cols-2 gap-2">
                <button
                  @click="form.type = 'kanban'"
                  class="p-4 border rounded-lg text-left"
                  :class="form.type === 'kanban' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'"
                >
                  <div class="text-2xl mb-1">📋</div>
                  <div class="font-medium">Kanban</div>
                  <div class="text-xs text-gray-500">Drag and drop board</div>
                </button>
                <button
                  @click="form.type = 'calendar'"
                  class="p-4 border rounded-lg text-left opacity-50 cursor-not-allowed"
                  disabled
                >
                  <div class="text-2xl mb-1">📅</div>
                  <div class="font-medium">Calendar</div>
                  <div class="text-xs text-gray-500">Coming soon</div>
                </button>
              </div>
            </div>
          </div>

          <!-- Step 2: Kanban Settings -->
          <div v-else-if="step === 2 && form.type === 'kanban'" class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Group By Field *</label>
              <select
                v-model="form.settings.kanban_group_field"
                class="w-full px-3 py-2 border rounded-lg"
              >
                <option value="">Select field</option>
                <option v-for="field in groupableFields" :key="field.id" :value="field.name">
                  {{ field.display_name }}
                </option>
              </select>
              <p class="text-xs text-gray-400 mt-1">Cards will be grouped by this field</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Card Fields</label>
              <div class="space-y-2 border rounded-lg p-3 max-h-60 overflow-y-auto">
                <div v-for="field in allFields" :key="field.id" class="flex items-center">
                  <input
                    type="checkbox"
                    :id="field.id"
                    :value="field.name"
                    v-model="form.settings.card_fields"
                    class="mr-2"
                  />
                  <label :for="field.id">{{ field.display_name }}</label>
                </div>
              </div>
              <p class="text-xs text-gray-400 mt-1">Fields to show on cards</p>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
            <button
              v-if="step === 2"
              @click="prevStep"
              class="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              ← Back
            </button>
            <button
              @click="closeModal"
              class="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              v-if="step === 1"
              @click="nextStep"
              :disabled="!form.name || !form.type"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              Next →
            </button>
            <button
              v-else
              @click="createView"
              :disabled="form.type === 'kanban' && !form.settings.kanban_group_field"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create View
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
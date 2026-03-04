<script setup lang="ts">
import { ref, watch } from 'vue'
import { useTablesStore } from '@/modules/user/stores/tables.store'
import type { CreateFieldDto, CreateTableDto } from '@/core/api/user/tables'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'created'): void
}>()

const tablesStore = useTablesStore()

// Типы полей
const fieldTypes = [
  { value: 'text', label: 'Text' },
  { value: 'number', label: 'Number' },
  { value: 'date', label: 'Date' },
  { value: 'boolean', label: 'Yes/No' },
  { value: 'select', label: 'Select (dropdown)' },
  { value: 'multiselect', label: 'Multi Select' },
  { value: 'email', label: 'Email' },
]

// Начальная форма
const createEmptyField = (): CreateFieldDto => ({
  name: '',
  display_name: '',
  field_type: 'text',
  is_required: false,
  is_unique: false,
  options: null,
  sort_order: 0
})

const form = ref<CreateTableDto>({
  name: '',
  description: '',
  fields: [createEmptyField()]
})

// Сброс формы при закрытии
watch(() => props.show, (newVal) => {
  if (!newVal) {
    form.value = {
      name: '',
      description: '',
      fields: [createEmptyField()]
    }
  }
})

// Генерация технического имени из отображаемого
function generateFieldName(index: number) {
  const field = form.value.fields[index]
  if (field.display_name && !field.name) {
    field.name = field.display_name
      .toLowerCase()
      .replace(/[^a-zа-яё0-9]+/gi, '_')
      .replace(/^_|_$/g, '')
      .substring(0, 50)
  }
}

// Добавить поле
function addField() {
  form.value.fields.push(createEmptyField())
  // Auto-scroll to new field after DOM update
  setTimeout(() => {
    const fieldsContainer = document.querySelector('.fields-container')
    if (fieldsContainer) {
      fieldsContainer.scrollTop = fieldsContainer.scrollHeight
    }
  }, 100)
}

// Удалить поле
function removeField(index: number) {
  if (form.value.fields.length > 1) {
    form.value.fields.splice(index, 1)
  }
}

// Отправка формы
async function handleSubmit() {
  try {
    await tablesStore.createTable(form.value)
    emit('created')
    emit('close')
  } catch (error) {
    console.error('Failed to create table:', error)
  }
}

// Закрытие
function closeModal() {
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-black/50 transition-opacity" @click="closeModal"></div>
      
      <!-- Modal -->
      <div class="relative min-h-screen flex items-center justify-center p-4">
        <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col">
          
          <!-- Header -->
          <div class="flex-shrink-0 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-xl font-semibold text-gray-900">Create New Table</h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-500">
              <span class="text-2xl">&times;</span>
            </button>
          </div>
          
          <!-- Form (теперь включает весь контент И кнопки) -->
          <form @submit.prevent="handleSubmit" class="flex-1 flex flex-col overflow-hidden">
            <!-- Body (scrollable) -->
            <div class="flex-1 overflow-y-auto px-6 py-4">
              <!-- Basic Info -->
              <div class="space-y-4 mb-8">
                <h4 class="font-medium text-gray-700 border-b pb-2">Table Information</h4>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Table Name <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="form.name"
                    type="text"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g. Customers, Products, Orders"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    v-model="form.description"
                    rows="2"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="What is this table for?"
                  />
                </div>
              </div>
              
              <!-- Fields Section -->
              <div class="space-y-4">
                <!-- STICKY HEADER с кнопкой Add Field -->
                <div class="sticky top-0 bg-white z-10 py-2 -mx-6 px-6 border-b border-gray-200" style="top: -1px;">
                  <div class="flex justify-between items-center">
                    <div>
                      <h4 class="font-medium text-gray-700">Fields</h4>
                      <p class="text-xs text-gray-500 mt-0.5">{{ form.fields.length }} field{{ form.fields.length !== 1 ? 's' : '' }} defined</p>
                    </div>
                    <button
                      type="button"
                      @click="addField"
                      class="inline-flex items-center gap-1 text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
                    >
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                      </svg>
                      Add Field
                    </button>
                  </div>
                </div>
                
                <!-- Fields List -->
                <div class="space-y-4 fields-container">
                  <div
                    v-for="(field, index) in form.fields"
                    :key="index"
                    class="bg-gray-50 p-4 rounded-lg border border-gray-200 relative group"
                  >
                    <!-- Remove button (visible on hover) -->
                    <button
                      v-if="form.fields.length > 1"
                      type="button"
                      @click="removeField(index)"
                      class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity shadow-lg hover:bg-red-600"
                      title="Remove field"
                    >
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                    
                    <div class="flex items-center gap-2 mb-3">
                      <span class="text-xs font-medium text-gray-500 bg-gray-200 px-2 py-0.5 rounded-full">
                        Field #{{ index + 1 }}
                      </span>
                      <span v-if="field.is_required" class="text-xs text-red-500 bg-red-50 px-2 py-0.5 rounded-full">
                        Required
                      </span>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <!-- Display Name -->
                      <div>
                        <label class="block text-xs text-gray-500 mb-1">Display Name <span class="text-red-500">*</span></label>
                        <input
                          v-model="field.display_name"
                          type="text"
                          required
                          @input="generateFieldName(index)"
                          class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
                          placeholder="e.g. Customer Name"
                        />
                      </div>
                      
                      <!-- Technical Name -->
                      <div>
                        <label class="block text-xs text-gray-500 mb-1">Technical Name <span class="text-red-500">*</span></label>
                        <input
                          v-model="field.name"
                          type="text"
                          required
                          class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 font-mono"
                          placeholder="customer_name"
                        />
                        <p class="text-xs text-gray-400 mt-1">Used in API, lowercase with underscores</p>
                      </div>
                      
                      <!-- Field Type -->
                      <div>
                        <label class="block text-xs text-gray-500 mb-1">Field Type <span class="text-red-500">*</span></label>
                        <select
                          v-model="field.field_type"
                          class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
                        >
                          <option v-for="type in fieldTypes" :key="type.value" :value="type.value">
                            {{ type.label }}
                          </option>
                        </select>
                      </div>
                      
                      <!-- Required Checkbox -->
                      <div class="flex items-center pt-5">
                        <label class="flex items-center gap-2 text-sm">
                          <input
                            v-model="field.is_required"
                            type="checkbox"
                            class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          Required field
                        </label>
                      </div>
                    </div>
                    
                    <!-- Options for Select/Multiselect -->
                    <div v-if="field.field_type === 'select' || field.field_type === 'multiselect'" class="mt-3 pt-3 border-t border-gray-200">
                      <label class="block text-xs text-gray-500 mb-1">Options (comma separated)</label>
                      <input
                        type="text"
                        class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
                        placeholder="active, inactive, pending"
                        @input="(e) => {
                          const val = (e.target as HTMLInputElement).value
                          field.options = { choices: val.split(',').map(s => s.trim()).filter(s => s) }
                        }"
                      />
                      <p class="text-xs text-gray-400 mt-1">Enter options separated by commas</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Footer (ВНУТРИ ФОРМЫ) -->
            <div class="flex-shrink-0 px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-end gap-3">
              <button
                type="button"
                @click="closeModal"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="tablesStore.isCreating"
                class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <svg v-if="tablesStore.isCreating" class="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                {{ tablesStore.isCreating ? 'Creating...' : 'Create Table' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
/* Smooth scrolling for fields container */
.fields-container {
  scroll-behavior: smooth;
  max-height: none;
}

/* Better sticky header */
.sticky {
  position: sticky;
  z-index: 20;
  background-color: white;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

/* Hover effects */
.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}

/* Transitions */
.transition-opacity {
  transition: opacity 0.2s ease-in-out;
}
</style>
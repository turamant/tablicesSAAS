<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Table, Field } from '@/core/api/user/tables'
import { fieldsApi } from '@/core/api/user/fields'

const props = defineProps<{
  show: boolean
  table: Table | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'updated'): void
}>()

// Состояния
const newField = ref({
  name: '',
  display_name: '',
  field_type: 'text',
  is_required: false,
  options: null as { choices: string[] } | null
})

const loading = ref(false)
const deletingFieldId = ref<string | null>(null)
const editingField = ref<Field | null>(null)
const editForm = ref({
  display_name: '',
  is_required: false,
  optionsText: ''
})

// Типы полей с иконками и описаниями
const fieldTypes = [
  { 
    value: 'text', 
    label: 'Text',
    icon: '📝',
    description: 'Single line text'
  },
  { 
    value: 'number', 
    label: 'Number',
    icon: '🔢',
    description: 'Numeric values'
  },
  { 
    value: 'date', 
    label: 'Date',
    icon: '📅',
    description: 'Date picker'
  },
  { 
    value: 'boolean', 
    label: 'Yes/No',
    icon: '✅',
    description: 'Checkbox'
  },
  { 
    value: 'email', 
    label: 'Email',
    icon: '📧',
    description: 'Email address'
  },
  { 
    value: 'select', 
    label: 'Select',
    icon: '▼',
    description: 'Dropdown list'
  },
  { 
    value: 'multiselect', 
    label: 'Multi Select',
    icon: '☑️',
    description: 'Multiple choices'
  },
]

// Сортировка полей по sort_order
const sortedFields = computed(() => {
  return [...(props.table?.fields || [])].sort((a, b) => a.sort_order - b.sort_order)
})

// Валидация
const canAddField = computed(() => {
  return newField.value.display_name.trim() !== ''
})

// Генерация технического имени
function generateTechnicalName(displayName: string): string {
  return displayName
    .toLowerCase()
    .replace(/[^a-zа-яё0-9]+/gi, '_')
    .replace(/^_|_$/g, '')
    .substring(0, 50)
}

// Обновить техническое имя при вводе
function onDisplayNameInput() {
  if (!newField.value.name) {
    newField.value.name = generateTechnicalName(newField.value.display_name)
  }
}

// Добавить поле
async function addField() {
  if (!props.table || !canAddField.value) return
  
  loading.value = true
  try {
    const fieldData: any = {
      name: newField.value.name || generateTechnicalName(newField.value.display_name),
      display_name: newField.value.display_name,
      field_type: newField.value.field_type,
      is_required: newField.value.is_required
    }
    
    // Добавляем options для select/multiselect
    if (newField.value.field_type === 'select' || newField.value.field_type === 'multiselect') {
      fieldData.options = newField.value.options
    }
    
    await fieldsApi.createField(props.table.id, fieldData)
    
    // Сброс формы
    newField.value = {
      name: '',
      display_name: '',
      field_type: 'text',
      is_required: false,
      options: null
    }
    
    emit('updated')
  } catch (error) {
    console.error('Failed to add field:', error)
    alert('Failed to add field. Please try again.')
  } finally {
    loading.value = false
  }
}

// Обновить опции для нового поля
function updateNewFieldOptions(event: Event) {
  const val = (event.target as HTMLInputElement).value
  const choices = val.split(',').map(s => s.trim()).filter(s => s)
  newField.value.options = { choices }
}

// Начать редактирование
function startEdit(field: Field) {
  editingField.value = field
  editForm.value = {
    display_name: field.display_name,
    is_required: field.is_required,
    optionsText: field.options?.choices?.join(', ') || ''
  }
}

// Обновить опции при редактировании
function updateEditOptions(event: Event) {
  const val = (event.target as HTMLInputElement).value
  editForm.value.optionsText = val
}

// Сохранить редактирование
async function saveEdit() {
  if (!props.table || !editingField.value) return
  
  loading.value = true
  try {
    const updateData: any = {
      display_name: editForm.value.display_name,
      is_required: editForm.value.is_required
    }
    
    // Добавляем options для select/multiselect
    if (editingField.value.field_type === 'select' || editingField.value.field_type === 'multiselect') {
      const choices = editForm.value.optionsText
        .split(',')
        .map(s => s.trim())
        .filter(s => s)
      
      updateData.options = { choices }
    }
    
    await fieldsApi.updateField(props.table.id, editingField.value.id, updateData)
    
    editingField.value = null
    emit('updated')
  } catch (error) {
    console.error('Failed to update field:', error)
    alert('Failed to update field. Please try again.')
  } finally {
    loading.value = false
  }
}

// Отмена редактирования
function cancelEdit() {
  editingField.value = null
}

// Удалить поле
async function deleteField(field: Field) {
  if (!props.table) return
  
  const hasData = confirm(
    `Are you sure you want to delete "${field.display_name}"?\n\n` +
    `This will permanently remove this field and all its data from your table.`
  )
  
  if (!hasData) return
  
  deletingFieldId.value = field.id
  try {
    await fieldsApi.deleteField(props.table.id, field.id)
    emit('updated')
  } catch (error) {
    console.error('Failed to delete field:', error)
    alert('Failed to delete field. Please try again.')
  } finally {
    deletingFieldId.value = null
  }
}

// Закрыть модалку
function closeModal() {
  if (loading.value) return
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
      <!-- Backdrop -->
      <div 
        class="fixed inset-0 bg-black/50 transition-opacity" 
        :class="{ 'cursor-wait': loading }"
        @click="!loading && closeModal()"
      ></div>
      
      <!-- Modal -->
      <div class="relative min-h-screen flex items-center justify-center p-4">
        <div 
          class="relative bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col"
          :class="{ 'opacity-75': loading }"
        >
          <!-- Header -->
          <div class="flex-shrink-0 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <div>
              <h3 class="text-xl font-semibold text-gray-900">
                Edit Fields - {{ table?.name }}
              </h3>
              <p class="text-sm text-gray-500 mt-1">
                Add, remove or modify fields in your table
              </p>
            </div>
            <button 
              @click="closeModal" 
              :disabled="loading"
              class="text-gray-400 hover:text-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span class="text-2xl">&times;</span>
            </button>
          </div>
          
          <!-- Body (scrollable) -->
          <div class="flex-1 overflow-y-auto px-6 py-4">
            <!-- Loading overlay -->
            <div v-if="loading" class="absolute inset-0 bg-white/50 flex items-center justify-center">
              <div class="flex flex-col items-center">
                <div class="animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"></div>
                <p class="mt-2 text-sm text-gray-600">Saving changes...</p>
              </div>
            </div>
            
            <!-- Current Fields Section -->
            <div class="space-y-4 mb-8">
              <div class="flex justify-between items-center">
                <h4 class="font-medium text-gray-700">Current Fields</h4>
                <span class="text-xs text-gray-500">{{ sortedFields.length }} fields</span>
              </div>
              
              <div v-if="sortedFields.length === 0" class="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed">
                <p class="text-gray-500">No fields yet. Add your first field below.</p>
              </div>
              
              <div v-else class="space-y-2">
                <!-- Field items -->
                <div
                  v-for="field in sortedFields"
                  :key="field.id"
                  class="group relative bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                >
                  <!-- Edit mode -->
                  <div v-if="editingField?.id === field.id" class="p-4">
                    <div class="space-y-3">
                      <!-- Display Name -->
                      <div>
                        <label class="block text-xs text-gray-500 mb-1">Display Name</label>
                        <input
                          v-model="editForm.display_name"
                          type="text"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          placeholder="Field display name"
                        />
                      </div>
                      
                      <!-- Options for Select/Multiselect -->
                      <div v-if="editingField?.field_type === 'select' || editingField?.field_type === 'multiselect'">
                        <label class="block text-xs text-gray-500 mb-1">Options (comma separated)</label>
                        <input
                          :value="editForm.optionsText"
                          @input="updateEditOptions"
                          type="text"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          placeholder="option1, option2, option3"
                        />
                        <p class="text-xs text-gray-400 mt-1">Enter options separated by commas</p>
                      </div>
                      
                      <!-- Required Checkbox -->
                      <div class="flex items-center">
                        <label class="flex items-center gap-2 text-sm">
                          <input
                            v-model="editForm.is_required"
                            type="checkbox"
                            class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          Required field
                        </label>
                      </div>
                      
                      <!-- Buttons -->
                      <div class="flex justify-end gap-2 pt-2">
                        <button
                          @click="cancelEdit"
                          class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
                        >
                          Cancel
                        </button>
                        <button
                          @click="saveEdit"
                          class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                          Save
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  <!-- View mode -->
                  <div v-else class="p-4">
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <div class="flex items-center gap-2">
                          <span class="font-medium">{{ field.display_name }}</span>
                          <span class="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full">
                            {{ field.field_type }}
                          </span>
                          <span v-if="field.is_required" class="text-xs text-red-500 bg-red-50 px-2 py-0.5 rounded-full">
                            required
                          </span>
                        </div>
                        <p class="text-xs text-gray-400 mt-1 font-mono">{{ field.name }}</p>
                        
                        <!-- Show options for select/multiselect -->
                        <div v-if="field.options?.choices?.length" class="mt-2 text-xs text-gray-500">
                          Options: {{ field.options.choices.join(', ') }}
                        </div>
                      </div>
                      
                      <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          @click="startEdit(field)"
                          class="p-1 text-gray-400 hover:text-blue-600"
                          title="Edit field"
                        >
                          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          @click="deleteField(field)"
                          :disabled="deletingFieldId === field.id"
                          class="p-1 text-gray-400 hover:text-red-600 disabled:opacity-50"
                          title="Delete field"
                        >
                          <svg v-if="deletingFieldId === field.id" class="w-5 h-5 animate-spin" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                          <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Add New Field Section -->
            <div class="border-t border-gray-200 pt-6">
              <h4 class="font-medium text-gray-700 mb-4">Add New Field</h4>
              
              <div class="space-y-4">
                <!-- Display Name -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Display Name <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="newField.display_name"
                    @input="onDisplayNameInput"
                    type="text"
                    placeholder="e.g. Customer Name"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <!-- Technical Name (optional) -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Technical Name
                    <span class="text-xs text-gray-400 ml-1">(optional - auto-generated)</span>
                  </label>
                  <input
                    v-model="newField.name"
                    type="text"
                    placeholder="customer_name"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono"
                  />
                  <p class="text-xs text-gray-400 mt-1">Used in API, lowercase with underscores</p>
                </div>
                
                <!-- Field Type -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Field Type <span class="text-red-500">*</span>
                  </label>
                  <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
                    <button
                      v-for="type in fieldTypes"
                      :key="type.value"
                      type="button"
                      @click="newField.field_type = type.value"
                      class="p-3 border rounded-lg text-left hover:border-blue-500 transition-colors"
                      :class="{
                        'border-blue-500 ring-2 ring-blue-200': newField.field_type === type.value,
                        'border-gray-200': newField.field_type !== type.value
                      }"
                    >
                      <div class="text-2xl mb-1">{{ type.icon }}</div>
                      <div class="font-medium text-sm">{{ type.label }}</div>
                      <div class="text-xs text-gray-400">{{ type.description }}</div>
                    </button>
                  </div>
                </div>
                
                <!-- Options for Select/Multiselect -->
                <div v-if="newField.field_type === 'select' || newField.field_type === 'multiselect'">
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Options <span class="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    @input="updateNewFieldOptions"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="option1, option2, option3"
                  />
                  <p class="text-xs text-gray-400 mt-1">Enter options separated by commas</p>
                </div>
                
                <!-- Required Checkbox -->
                <div class="flex items-center pt-2">
                  <label class="flex items-center gap-2 text-sm">
                    <input
                      v-model="newField.is_required"
                      type="checkbox"
                      class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    Required field - users must fill this
                  </label>
                </div>
                
                <!-- Add Button -->
                <button
                  @click="addField"
                  :disabled="!canAddField || loading || (newField.field_type === 'select' && !newField.options?.choices?.length)"
                  class="w-full bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                >
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Add Field
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}

.transition-opacity {
  transition: opacity 0.2s ease-in-out;
}
</style>
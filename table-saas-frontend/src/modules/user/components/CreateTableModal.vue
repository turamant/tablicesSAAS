<script setup lang="ts">
import { ref, watch, computed } from 'vue'
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

// Состояния
const currentStep = ref(1) // 1: Basic Info, 2: Fields
const errors = ref<Record<string, string>>({})
const touched = ref<Record<string, boolean>>({})

// Типы полей с иконками и описаниями
const fieldTypes = [
  { 
    value: 'text', 
    label: 'Text',
    icon: '📝',
    description: 'Single line text',
    color: 'bg-blue-50 text-blue-700 border-blue-200'
  },
  { 
    value: 'number', 
    label: 'Number',
    icon: '🔢',
    description: 'Numeric values',
    color: 'bg-green-50 text-green-700 border-green-200'
  },
  { 
    value: 'date', 
    label: 'Date',
    icon: '📅',
    description: 'Date picker',
    color: 'bg-purple-50 text-purple-700 border-purple-200'
  },
  { 
    value: 'boolean', 
    label: 'Yes/No',
    icon: '✅',
    description: 'Checkbox',
    color: 'bg-yellow-50 text-yellow-700 border-yellow-200'
  },
  { 
    value: 'select', 
    label: 'Select',
    icon: '▼',
    description: 'Dropdown list',
    color: 'bg-pink-50 text-pink-700 border-pink-200'
  },
  { 
    value: 'multiselect', 
    label: 'Multi Select',
    icon: '☑️',
    description: 'Multiple choices',
    color: 'bg-orange-50 text-orange-700 border-orange-200'
  },
  { 
    value: 'email', 
    label: 'Email',
    icon: '📧',
    description: 'Email address',
    color: 'bg-indigo-50 text-indigo-700 border-indigo-200'
  },
  { 
    value: 'formula', 
    label: 'Formula',
    icon: 'ƒ',
    description: 'Calculated field',
    color: 'bg-purple-50 text-purple-700 border-purple-200'
  },
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

// Валидация формы
const isBasicInfoValid = computed(() => {
  return form.value.name.trim() !== ''
})

const isFieldsValid = computed(() => {
  return form.value.fields.every((field, index) => {
    if (!field.display_name.trim()) return false
    if (!field.name.trim()) return false
    if (field.field_type === 'select' || field.field_type === 'multiselect') {
      return field.options?.choices?.length > 0
    }
        // 👇 ДЛЯ FORMULA - проверка что формула есть
        if (field.field_type === 'formula') {
      return field.options?.formula?.trim() !== ''
    }
    return true
  })
})

const canProceed = computed(() => {
  if (currentStep.value === 1) return isBasicInfoValid.value
  return isFieldsValid.value
})

// Сброс формы при закрытии
watch(() => props.show, (newVal) => {
  if (!newVal) {
    form.value = {
      name: '',
      description: '',
      fields: [createEmptyField()]
    }
    currentStep.value = 1
    errors.value = {}
    touched.value = {}
  }
})

// Маркировка поля как touched
function markAsTouched(field: string) {
  touched.value[field] = true
}

// Генерация технического имени
function generateTechnicalName(displayName: string): string {
  return displayName
    .toLowerCase()
    .replace(/[^a-zа-яё0-9]+/gi, '_')
    .replace(/^_|_$/g, '')
    .substring(0, 50)
}

// Генерация имени поля
function generateFieldName(index: number) {
  const field = form.value.fields[index]
  if (field.display_name && !field.name) {
    field.name = generateTechnicalName(field.display_name)
  }
}

// Добавить поле
function addField() {
  form.value.fields.push(createEmptyField())
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

// Обновление опций для select/multiselect
function updateOptions(field: CreateFieldDto, event: Event) {
  const val = (event.target as HTMLInputElement).value
  const choices = val.split(',').map(s => s.trim()).filter(s => s)
  field.options = { choices }
}

// Отправка формы
async function handleSubmit() {
  if (!isFieldsValid.value) return
  
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
  if (tablesStore.isCreating) return
  emit('close')
}

// Навигация по шагам
function nextStep() {
  if (currentStep.value === 1 && isBasicInfoValid.value) {
    currentStep.value = 2
  }
}

function prevStep() {
  if (currentStep.value === 2) {
    currentStep.value = 1
  }
}

// Получить иконку для типа поля
function getFieldIcon(type: string): string {
  return fieldTypes.find(t => t.value === type)?.icon || '📄'
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
      <!-- Backdrop с анимацией -->
      <div 
        class="fixed inset-0 bg-black/50 transition-opacity duration-300"
        :class="{ 'opacity-0': !show, 'opacity-100': show }"
        @click="!tablesStore.isCreating && closeModal()"
      ></div>
      
      <!-- Modal с анимацией -->
      <div class="relative min-h-screen flex items-center justify-center p-4">
        <div 
          class="relative bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col transform transition-all duration-300"
          :class="{
            'scale-95 opacity-0': !show,
            'scale-100 opacity-100': show,
            'opacity-75': tablesStore.isCreating
          }"
        >
          <!-- Header с градиентом -->
          <div class="flex-shrink-0 px-6 py-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 rounded-t-xl flex justify-between items-center">
            <div>
              <h3 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <span class="text-2xl">➕</span>
                Create New Table
              </h3>
              <p class="text-sm text-gray-600 mt-1">
                Step {{ currentStep }} of 2: {{ currentStep === 1 ? 'Basic Information' : 'Define Fields' }}
              </p>
            </div>
            <button 
              @click="closeModal" 
              :disabled="tablesStore.isCreating"
              class="text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/50"
            >
              <span class="text-2xl">&times;</span>
            </button>
          </div>
          
          <!-- Progress Bar -->
          <div class="px-6 pt-4">
            <div class="flex gap-2">
              <div 
                class="h-2 flex-1 rounded-full transition-all duration-300"
                :class="currentStep >= 1 ? 'bg-blue-600' : 'bg-gray-200'"
              ></div>
              <div 
                class="h-2 flex-1 rounded-full transition-all duration-300"
                :class="currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-200'"
              ></div>
            </div>
          </div>
          
          <!-- Loading Overlay -->
          <div v-if="tablesStore.isCreating" class="absolute inset-0 bg-white/80 flex items-center justify-center z-10 rounded-xl">
            <div class="flex flex-col items-center">
              <div class="animate-spin rounded-full h-12 w-12 border-4 border-gray-200 border-t-blue-600"></div>
              <p class="mt-3 text-sm font-medium text-gray-700">Creating your table...</p>
            </div>
          </div>
          
          <!-- Form -->
          <form @submit.prevent="handleSubmit" class="flex-1 flex flex-col overflow-hidden">
            <!-- Body (scrollable) -->
            <div class="flex-1 overflow-y-auto px-6 py-4">
              <!-- Step 1: Basic Info -->
              <div v-if="currentStep === 1" class="space-y-6">
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 flex gap-3">
                  <span class="text-2xl">💡</span>
                  <div>
                    <h4 class="font-medium text-blue-900">Getting Started</h4>
                    <p class="text-sm text-blue-700">First, give your table a name and description. This helps you identify it later.</p>
                  </div>
                </div>
                
                <div class="space-y-4">
                  <div>
                    <label class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
                      <span>📋</span>
                      Table Name <span class="text-red-500">*</span>
                    </label>
                    <input
                      v-model="form.name"
                      @blur="markAsTouched('name')"
                      type="text"
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                      :class="{ 'border-red-300 bg-red-50': touched.name && !form.name }"
                      placeholder="e.g. Customers, Products, Orders"
                    />
                    <p v-if="touched.name && !form.name" class="text-xs text-red-600 mt-1 flex items-center gap-1">
                      <span>⚠️</span>
                      Table name is required
                    </p>
                  </div>
                  
                  <div>
                    <label class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
                      <span>📝</span>
                      Description
                    </label>
                    <textarea
                      v-model="form.description"
                      rows="3"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all resize-y"
                      placeholder="What is this table for? e.g., 'Store customer information', 'Track product inventory'"
                    />
                  </div>
                </div>
              </div>
              
              <!-- Step 2: Fields -->
              <div v-else class="space-y-6">
                <div class="bg-green-50 border border-green-200 rounded-lg p-4 flex gap-3">
                  <span class="text-2xl">🎯</span>
                  <div>
                    <h4 class="font-medium text-green-900">Define Your Fields</h4>
                    <p class="text-sm text-green-700">Add fields to store different types of data. Each field becomes a column in your table.</p>
                  </div>
                </div>
                
                <!-- Fields Section -->
                <div class="space-y-4">
                  <!-- Fields List -->
                  <div class="space-y-4 fields-container">
                    <div
                      v-for="(field, index) in form.fields"
                      :key="index"
                      class="bg-white border border-gray-200 rounded-lg p-4 relative group hover:shadow-md transition-all"
                    >
                      <!-- Field Header -->
                      <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center gap-2">
                          <span class="text-lg">{{ getFieldIcon(field.field_type) }}</span>
                          <span class="text-sm font-medium text-gray-700">Field #{{ index + 1 }}</span>
                          <span 
                            v-if="field.is_required" 
                            class="text-xs px-2 py-0.5 bg-red-50 text-red-600 rounded-full"
                          >
                            required
                          </span>
                        </div>
                        
                        <!-- Remove button -->
                        <button
                          v-if="form.fields.length > 1"
                          type="button"
                          @click="removeField(index)"
                          class="opacity-0 group-hover:opacity-100 transition-opacity text-red-500 hover:text-red-700"
                          title="Remove field"
                        >
                          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                      
                      <!-- Field Grid -->
                      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- Display Name -->
                        <div>
                          <label class="block text-xs text-gray-500 mb-1">Display Name *</label>
                          <input
                            v-model="field.display_name"
                            type="text"
                            required
                            @input="generateFieldName(index)"
                            class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 transition-all"
                            :class="{ 'border-red-300 bg-red-50': !field.display_name }"
                            placeholder="e.g. Customer Name"
                          />
                        </div>
                        
                        <!-- Technical Name -->
                        <div>
                          <label class="block text-xs text-gray-500 mb-1">Technical Name *</label>
                          <input
                            v-model="field.name"
                            type="text"
                            required
                            class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 font-mono transition-all"
                            :class="{ 'border-red-300 bg-red-50': !field.name }"
                            placeholder="customer_name"
                          />
                        </div>
                        
                        <!-- Field Type -->
                        <div class="col-span-2">
                          <label class="block text-xs text-gray-500 mb-2">Field Type *</label>
                          <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                            <button
                              v-for="type in fieldTypes"
                              :key="type.value"
                              type="button"
                              @click="field.field_type = type.value"
                              class="p-2 border rounded-lg text-left hover:border-blue-500 transition-all"
                              :class="[
                                field.field_type === type.value 
                                  ? 'border-blue-500 ring-2 ring-blue-200 bg-blue-50' 
                                  : 'border-gray-200',
                                type.color
                              ]"
                            >
                              <div class="text-xl mb-1">{{ type.icon }}</div>
                              <div class="font-medium text-xs">{{ type.label }}</div>
                            </button>
                          </div>
                        </div>
                        
                        <!-- Options for Select/Multiselect -->
                        <div v-if="field.field_type === 'select' || field.field_type === 'multiselect'" class="col-span-2">
                          <label class="block text-xs text-gray-500 mb-1">Options *</label>
                          <input
                            type="text"
                            class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 transition-all"
                            :class="{ 'border-red-300 bg-red-50': !field.options?.choices?.length }"
                            placeholder="option1, option2, option3"
                            @input="(e) => updateOptions(field, e)"
                          />
                          <p class="text-xs text-gray-400 mt-1">Enter options separated by commas</p>
                        </div>
                        
                        <!-- Required Checkbox -->
                        <div class="col-span-2 flex items-center">
                          <label class="flex items-center gap-2 text-sm cursor-pointer group">
                            <input
                              v-model="field.is_required"
                              type="checkbox"
                              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 transition-colors"
                            />
                            <span class="text-gray-600 group-hover:text-gray-900">Required field - users must fill this</span>
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Add Field Button -->
                  <button
                    type="button"
                    @click="addField"
                    class="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-blue-500 hover:text-blue-600 transition-all flex items-center justify-center gap-2"
                  >
                    <span class="text-xl">➕</span>
                    Add Another Field
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Footer с навигацией -->
            <div class="flex-shrink-0 px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-xl flex justify-between gap-3">
              <div>
                <button
                  v-if="currentStep === 2"
                  type="button"
                  @click="prevStep"
                  :disabled="tablesStore.isCreating"
                  class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors flex items-center gap-2"
                >
                  <span>←</span>
                  Back
                </button>
              </div>
              
              <div class="flex gap-3">
                <button
                  type="button"
                  @click="closeModal"
                  :disabled="tablesStore.isCreating"
                  class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors flex items-center gap-2"
                >
                  <span>❌</span>
                  Cancel
                </button>
                
                <button
                  v-if="currentStep === 1"
                  type="button"
                  @click="nextStep"
                  :disabled="!canProceed || tablesStore.isCreating"
                  class="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 shadow-lg hover:shadow-xl"
                >
                  <span>→</span>
                  Next Step
                </button>
                
                <button
                  v-else
                  type="submit"
                  :disabled="!canProceed || tablesStore.isCreating"
                  class="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-green-600 to-emerald-600 rounded-lg hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 shadow-lg hover:shadow-xl"
                >
                  <span v-if="tablesStore.isCreating" class="animate-spin">⏳</span>
                  <span v-else>✅</span>
                  {{ tablesStore.isCreating ? 'Creating...' : 'Create Table' }}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.fields-container {
  scroll-behavior: smooth;
  max-height: none;
}

/* Кастомный скроллбар */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 8px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 8px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}

.transition-opacity {
  transition: opacity 0.2s ease-in-out;
}
</style>
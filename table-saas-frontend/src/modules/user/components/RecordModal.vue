<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { Table, Field } from '@/core/api/user/tables'
import type { TableRecord } from '@/core/api/user/records'

const props = defineProps<{
  show: boolean
  table: Table | null
  record: TableRecord | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', data: Record<string, any>): void
}>()

// Состояния
const form = ref<Record<string, any>>({})
const errors = ref<Record<string, string>>({})
const isSubmitting = ref(false)
const touched = ref<Record<string, boolean>>({})

// Иконки для типов полей
const fieldIcons: Record<string, string> = {
  text: '📝',
  number: '🔢',
  date: '📅',
  boolean: '✅',
  email: '📧',
  select: '▼',
  multiselect: '☑️',
  formula: 'ƒ',  
}

// Следим за record
watch(() => props.record, (newRecord) => {
  console.log('Record changed:', newRecord)
  if (newRecord) {
    form.value = { ...newRecord }
  } else {
    form.value = {}
  }
  errors.value = {}
  touched.value = {}
}, { immediate: true, deep: true })

// Следим за открытием модалки
watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.record) {
      form.value = { ...props.record }
    }
    // Сбрасываем touched при открытии
    touched.value = {}
  } else {
    form.value = {}
    errors.value = {}
    touched.value = {}
    isSubmitting.value = false
  }
})

// Следим за обновлением таблицы
watch(() => props.table, () => {
  if (props.show && props.record) {
    form.value = { ...props.record }
  }
})

// Валидация поля
function validateField(field: Field, value: any): string | null {
  if (field.is_required && (value === undefined || value === null || value === '')) {
    return `${field.display_name} is required`
  }
  
  if (value === undefined || value === null || value === '') return null
  
  switch (field.field_type) {
    case 'email':
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(value)) {
        return 'Invalid email format'
      }
      break
    case 'number':
      if (isNaN(Number(value))) {
        return 'Must be a valid number'
      }
      break
    case 'date':
      if (isNaN(Date.parse(value))) {
        return 'Must be a valid date'
      }
      break
  }
  
  return null
}

// Отметить поле как touched при потере фокуса
function markAsTouched(fieldName: string) {
  touched.value[fieldName] = true
}

// Валидация всей формы
function validateForm(): boolean {
  const newErrors: Record<string, string> = {}
  
  for (const field of props.table?.fields || []) {
    const error = validateField(field, form.value[field.name])
    if (error) {
      newErrors[field.name] = error
    }
  }
  
  errors.value = newErrors
  return Object.keys(newErrors).length === 0
}

// Проверка нужно ли показывать ошибку для поля
function shouldShowError(fieldName: string): boolean {
  const isTouched = touched.value[fieldName] === true
  const hasError = !!errors.value[fieldName]
  return isTouched && hasError
}

// Подготовка данных
function prepareSubmitData(): Record<string, any> {
  const submitData = { ...form.value }
  
  for (const field of props.table?.fields || []) {
    const value = submitData[field.name]
    
    if (value === undefined || value === null) continue
    
    switch (field.field_type) {
      case 'number':
        submitData[field.name] = Number(value)
        break
      case 'boolean':
        submitData[field.name] = !!value
        break
    }
  }
  
  return submitData
}

// Отправка
async function handleSubmit() {
  if (!validateForm()) {
    // Отмечаем все поля как touched чтобы показать ошибки
    for (const field of props.table?.fields || []) {
      touched.value[field.name] = true
    }
    return
  }
  
  isSubmitting.value = true
  try {
    const submitData = prepareSubmitData()
    emit('save', submitData)
  } catch (error) {
    console.error('Failed to submit:', error)
  } finally {
    isSubmitting.value = false
  }
}

// Закрытие
function closeModal() {
  if (isSubmitting.value) return
  emit('close')
}

// Получить цвет для типа поля
function getFieldTypeColor(type: string): string {
  const colors: Record<string, string> = {
    text: 'bg-blue-50 text-blue-700',
    number: 'bg-green-50 text-green-700',
    date: 'bg-purple-50 text-purple-700',
    boolean: 'bg-yellow-50 text-yellow-700',
    email: 'bg-indigo-50 text-indigo-700',
    select: 'bg-pink-50 text-pink-700',
    multiselect: 'bg-orange-50 text-orange-700',
    formula: 'bg-purple-100 text-purple-700',
  }
  return colors[type] || 'bg-gray-50 text-gray-700'
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
      <!-- Backdrop с анимацией -->
      <div 
        class="fixed inset-0 bg-black/50 transition-opacity duration-300"
        :class="{ 'opacity-0': !show, 'opacity-100': show }"
        @click="!isSubmitting && closeModal()"
      ></div>
      
      <!-- Modal с анимацией -->
      <div class="relative min-h-screen flex items-center justify-center p-4">
        <div 
          class="relative bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col transform transition-all duration-300"
          :class="{
            'scale-95 opacity-0': !show,
            'scale-100 opacity-100': show,
            'opacity-75': isSubmitting
          }"
        >
          <!-- Header с градиентом -->
          <div class="flex-shrink-0 px-6 py-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 rounded-t-xl flex justify-between items-center">
            <div>
              <h3 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <span class="text-2xl">{{ record ? '✏️' : '➕' }}</span>
                {{ record ? 'Edit Record' : 'New Record' }}
              </h3>
              <p v-if="table" class="text-sm text-gray-600 mt-1 flex items-center gap-1">
                <span>📊</span>
                {{ table.name }}
              </p>
            </div>
            <button 
              @click="closeModal" 
              :disabled="isSubmitting"
              class="text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/50"
            >
              <span class="text-2xl">&times;</span>
            </button>
          </div>
          
          <!-- Loading Overlay -->
          <div v-if="isSubmitting" class="absolute inset-0 bg-white/80 flex items-center justify-center z-10 rounded-xl">
            <div class="flex flex-col items-center">
              <div class="animate-spin rounded-full h-12 w-12 border-4 border-gray-200 border-t-blue-600"></div>
              <p class="mt-3 text-sm font-medium text-gray-700">Saving your data...</p>
            </div>
          </div>
          
          <!-- Form -->
          <form @submit.prevent="handleSubmit" class="flex-1 flex flex-col overflow-hidden">
            <!-- Body (scrollable) -->
            <div class="flex-1 overflow-y-auto px-6 py-4">
              <div v-if="!table?.fields.length" class="text-center py-12">
                <div class="text-6xl mb-4">📭</div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">No Fields Defined</h3>
                <p class="text-gray-500">This table doesn't have any fields yet.</p>
              </div>
              
              <div v-else class="space-y-5">
                <div 
                  v-for="field in table.fields" 
                  :key="field.id"
                  class="space-y-1 transition-all duration-200"
                  :class="{ 'animate-pulse': isSubmitting }"
                >
                  <!-- Label с иконкой и типом -->
                  <div class="flex items-center justify-between">
                    <label class="flex items-center gap-2 text-sm font-medium text-gray-700">
                      <span class="text-lg">{{ fieldIcons[field.field_type] || '📄' }}</span>
                      <span>{{ field.display_name }}</span>
                      <span v-if="field.is_required" class="text-red-500">*</span>
                    </label>
                    <span 
                      class="text-xs px-2 py-1 rounded-full font-medium"
                      :class="getFieldTypeColor(field.field_type)"
                    >
                      {{ field.field_type }}
                    </span>
                  </div>
                  
                  <!-- Error message с анимацией -->
                  <div v-if="shouldShowError(field.name)" class="overflow-hidden">
                    <p class="text-xs text-red-600 bg-red-50 px-3 py-2 rounded-lg animate-slideDown">
                      ⚠️ {{ errors[field.name] }}
                    </p>
                  </div>
                  
                  <!-- Boolean (checkbox) -->
                  <div v-if="field.field_type === 'boolean'" class="flex items-center mt-2">
                    <label class="flex items-center gap-3 text-sm cursor-pointer group">
                      <input
                        type="checkbox"
                        v-model="form[field.name]"
                        @blur="markAsTouched(field.name)"
                        class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 transition-colors"
                      />
                      <span class="text-gray-600 group-hover:text-gray-900">Yes / No</span>
                    </label>
                  </div>
                  
                  <!-- Date picker -->
                  <input
                    v-else-if="field.field_type === 'date'"
                    type="date"
                    v-model="form[field.name]"
                    @blur="markAsTouched(field.name)"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                    :class="{ 'border-red-300 bg-red-50': shouldShowError(field.name) }"
                  />
                  
                  <!-- Select dropdown -->
                  <select
                    v-else-if="field.field_type === 'select'"
                    v-model="form[field.name]"
                    @blur="markAsTouched(field.name)"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all appearance-none bg-white"
                    :class="{ 'border-red-300 bg-red-50': shouldShowError(field.name) }"
                  >
                    <option value="" class="text-gray-400">— Select an option —</option>
                    <option 
                      v-for="option in field.options?.choices || []" 
                      :key="option"
                      :value="option"
                      class="text-gray-900"
                    >
                      {{ option }}
                    </option>
                  </select>
                  
                  <!-- Multi-select -->
                  <select
                    v-else-if="field.field_type === 'multiselect'"
                    v-model="form[field.name]"
                    @blur="markAsTouched(field.name)"
                    multiple
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all min-h-[100px]"
                    :class="{ 'border-red-300 bg-red-50': shouldShowError(field.name) }"
                  >
                    <option 
                      v-for="option in field.options?.choices || []" 
                      :key="option"
                      :value="option"
                    >
                      {{ option }}
                    </option>
                  </select>
                  <!-- Formula field (readonly) -->
<div v-else-if="field.field_type === 'formula'">
  <div class="relative">
    <input
      :value="form[field.name]"
      readonly
      disabled
      class="w-full px-3 py-2 bg-gray-100 border border-gray-300 rounded-lg text-gray-600"
    />
    <span class="absolute right-3 top-2 text-xs text-gray-400">ƒ</span>
  </div>
  <p class="text-xs text-gray-400 mt-1">Автоматически рассчитывается</p>
</div>
                  
                  <!-- Textarea for long text -->
                  <textarea
                    v-else-if="field.field_type === 'text' && field.name.toLowerCase().includes('description')"
                    v-model="form[field.name]"
                    @blur="markAsTouched(field.name)"
                    rows="4"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all resize-y"
                    :class="{ 'border-red-300 bg-red-50': shouldShowError(field.name) }"
                    :placeholder="`Enter ${field.display_name.toLowerCase()}...`"
                  />
                  
                  <!-- Number input -->
                  <input
                    v-else-if="field.field_type === 'number'"
                    type="number"
                    step="any"
                    v-model="form[field.name]"
                    @blur="markAsTouched(field.name)"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                    :class="{ 'border-red-300 bg-red-50': shouldShowError(field.name) }"
                    placeholder="0"
                  />
                  
                  <!-- Email input -->
                  <input
                    v-else-if="field.field_type === 'email'"
                    type="email"
                    v-model="form[field.name]"
                    @blur="markAsTouched(field.name)"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                    :class="{ 'border-red-300 bg-red-50': shouldShowError(field.name) }"
                    placeholder="name@example.com"
                  />
                  
                  <!-- Default text input -->
                  <input
                    v-else
                    type="text"
                    v-model="form[field.name]"
                    @blur="markAsTouched(field.name)"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                    :class="{ 'border-red-300 bg-red-50': shouldShowError(field.name) }"
                    :placeholder="`Enter ${field.display_name.toLowerCase()}...`"
                  />
                </div>
              </div>
            </div>
            
            <!-- Footer -->
            <div class="flex-shrink-0 px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-xl flex justify-end gap-3">
              <button
                type="button"
                @click="closeModal"
                :disabled="isSubmitting"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                <span>❌</span>
                Cancel
              </button>
              <button
                type="submit"
                :disabled="isSubmitting"
                class="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 shadow-lg hover:shadow-xl"
              >
                <span v-if="isSubmitting" class="animate-spin">⏳</span>
                <span v-else>{{ record ? '✏️' : '➕' }}</span>
                {{ isSubmitting ? 'Saving...' : (record ? 'Update Record' : 'Create Record') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slideDown {
  animation: slideDown 0.2s ease-out;
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
</style>
<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Table, Field } from '@/core/api/user/tables'
import type { Record } from '@/core/api/user/records'

const props = defineProps<{
  show: boolean
  table: Table | null
  record: Record | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', data: Record<string, any>): void
}>()

// Форма
const form = ref<Record<string, any>>({})

// Заполняем форму при редактировании
watch(() => props.record, (newRecord) => {
  if (newRecord) {
    form.value = { ...newRecord }
  } else {
    form.value = {}
  }
}, { immediate: true })

// Сброс при закрытии
watch(() => props.show, (newVal) => {
  if (!newVal) {
    form.value = {}
  }
})

// Получить поле по имени
function getField(fieldName: string): Field | undefined {
  return props.table?.fields.find(f => f.name === fieldName)
}

// Валидация
function validateField(field: Field, value: any): string | null {
  if (field.is_required && (value === undefined || value === null || value === '')) {
    return `${field.display_name} is required`
  }
  
  switch (field.field_type) {
    case 'email':
      if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        return 'Invalid email format'
      }
      break
    case 'number':
      if (value && isNaN(Number(value))) {
        return 'Must be a number'
      }
      break
  }
  
  return null
}

// Сохранить
function handleSubmit() {
  // Валидация
  for (const field of props.table?.fields || []) {
    const error = validateField(field, form.value[field.name])
    if (error) {
      alert(error)
      return
    }
  }
  
  emit('save', form.value)  // ← отправляет просто объект с полями
}

// Закрыть
function closeModal() {
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-black/50" @click="closeModal"></div>
      
      <!-- Modal -->
      <div class="relative min-h-screen flex items-center justify-center p-4">
        <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-2xl">
          
          <!-- Header -->
          <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-xl font-semibold text-gray-900">
              {{ record ? 'Edit Record' : 'New Record' }}
            </h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-500">
              <span class="text-2xl">&times;</span>
            </button>
          </div>
          
          <!-- Form -->
          <form @submit.prevent="handleSubmit">
            <div class="p-6 space-y-4">
              <div 
                v-for="field in table?.fields || []" 
                :key="field.id"
                class="space-y-1"
              >
                <label class="block text-sm font-medium text-gray-700">
                  {{ field.display_name }}
                  <span v-if="field.is_required" class="text-red-500">*</span>
                </label>
                
                <!-- Boolean (checkbox) -->
                <div v-if="field.field_type === 'boolean'" class="flex items-center">
                  <input
                    type="checkbox"
                    v-model="form[field.name]"
                    class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                </div>
                
                <!-- Select dropdown -->
                <select
                  v-else-if="field.field_type === 'select'"
                  v-model="form[field.name]"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">-- Select --</option>
                  <option 
                    v-for="option in field.options?.choices || []" 
                    :key="option"
                    :value="option"
                  >
                    {{ option }}
                  </option>
                </select>
                
                <!-- Textarea for long text -->
                <textarea
                  v-else-if="field.field_type === 'text' && field.name.toLowerCase().includes('description')"
                  v-model="form[field.name]"
                  rows="3"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                
                <!-- Default input -->
                <input
                  v-else
                  :type="field.field_type === 'number' ? 'number' : 
                         field.field_type === 'email' ? 'email' : 'text'"
                  v-model="form[field.name]"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <!-- Footer -->
            <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
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
                {{ record ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </Teleport>
</template>
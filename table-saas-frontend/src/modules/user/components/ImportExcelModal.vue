<script setup lang="ts">
import { ref } from 'vue'
import type { Table } from '@/core/api/user/tables'
import { importApi } from '@/core/api/user/import_data'

const props = defineProps<{
  show: boolean
  table: Table | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'imported'): void
}>()

// Состояния
const step = ref(1) // 1: загрузка файла, 2: маппинг полей
const file = ref<File | null>(null)
const preview = ref<any>(null)
const mappings = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const importResult = ref<any>(null)

// Загрузка файла
async function handleFileUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const files = input.files
  if (!files || files.length === 0) return
  
  // Принудительное приведение к File
  file.value = files[0] as File
  error.value = ''
  
  await uploadAndPreview()
}

async function uploadAndPreview() {
  if (!file.value || !props.table) return
  
  loading.value = true
  error.value = ''
  
  try {
    const formData = new FormData()
    formData.append('file', file.value)
    
    const response = await importApi.preview(props.table.id, formData)
    preview.value = response.data
    mappings.value = response.data.suggested_mappings
    step.value = 2
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to preview file'
  } finally {
    loading.value = false
  }
}

// Обновление маппинга
function updateMapping(index: number, field: string) {
  mappings.value[index].table_field = field
}

function toggleSkip(index: number) {
  mappings.value[index].skip = !mappings.value[index].skip
}

// Выполнить импорт
async function doImport() {
  if (!file.value || !props.table) return
  
  loading.value = true
  error.value = ''
  
  try {
    const formData = new FormData()
    formData.append('file', file.value)
    
    // Отправляем mappings как JSON строку
    formData.append('mappings', JSON.stringify(mappings.value))
    formData.append('skip_first_row', 'true')
    formData.append('create_missing_fields', 'false')
    
    const response = await importApi.import(props.table.id, formData)
    importResult.value = response.data
    step.value = 3  // добавить step 3 для результатов
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to import'
    console.error('Import error:', err.response?.data)
  } finally {
    loading.value = false
  }
}

// Закрыть и сбросить
function closeModal() {
  step.value = 1
  file.value = null
  preview.value = null
  mappings.value = []
  error.value = ''
  importResult.value = null
  emit('close')
}

// Завершить импорт
function finishImport() {
  emit('imported')
  closeModal()
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-black/50" @click="!loading && closeModal()"></div>
      
      <!-- Modal -->
      <div class="relative min-h-screen flex items-center justify-center p-4">
        <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col">
          
          <!-- Header -->
          <div class="flex-shrink-0 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <div>
              <h3 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <span>📥</span>
                Import Excel - {{ table?.name }}
              </h3>
              <p class="text-sm text-gray-500 mt-1">
                Step {{ step }} of 2: {{ step === 1 ? 'Upload file' : 'Map fields' }}
              </p>
            </div>
            <button 
              @click="closeModal" 
              :disabled="loading"
              class="text-gray-400 hover:text-gray-500 disabled:opacity-50"
            >
              <span class="text-2xl">&times;</span>
            </button>
          </div>
          
          <!-- Progress bar -->
          <div class="px-6 pt-4">
            <div class="flex gap-2">
              <div class="h-2 flex-1 rounded-full" :class="step >= 1 ? 'bg-blue-600' : 'bg-gray-200'"></div>
              <div class="h-2 flex-1 rounded-full" :class="step >= 2 ? 'bg-blue-600' : 'bg-gray-200'"></div>
            </div>
          </div>
          
          <!-- Body -->
          <div class="flex-1 overflow-y-auto px-6 py-4">
            <!-- Loading -->
            <div v-if="loading" class="text-center py-12">
              <div class="animate-spin h-8 w-8 border-4 border-gray-300 border-t-blue-600 rounded-full mx-auto"></div>
              <p class="mt-2 text-gray-600">Processing...</p>
            </div>
            
            <!-- Error -->
            <div v-else-if="error" class="bg-red-50 text-red-600 p-4 rounded-lg mb-4">
              {{ error }}
            </div>
            
            <!-- Step 1: Upload -->
            <div v-else-if="step === 1" class="text-center py-8">
              <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 hover:border-blue-500 transition-colors">
                <input
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  @change="handleFileUpload"
                  class="hidden"
                  id="file-upload"
                />
                <label for="file-upload" class="cursor-pointer">
                  <div class="text-5xl mb-4">📎</div>
                  <p class="text-lg font-medium mb-2">Click to upload Excel file</p>
                  <p class="text-sm text-gray-500">.xlsx, .xls or .csv</p>
                </label>
              </div>
            </div>
            
            <!-- Step 2: Mapping -->
            <div v-else-if="step === 2 && preview" class="space-y-6">
              <!-- Preview data -->
              <div>
                <h4 class="font-medium mb-2">Preview (first 5 rows)</h4>
                <div class="overflow-x-auto border rounded-lg">
                  <table class="min-w-full text-sm">
                    <thead class="bg-gray-50">
                      <tr>
                        <th v-for="col in preview.columns" :key="col" class="px-3 py-2 text-left">
                          {{ col }}
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, idx) in preview.rows" :key="idx" class="border-t">
                        <td v-for="col in preview.columns" :key="col" class="px-3 py-2">
                          {{ row[col] }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p class="text-xs text-gray-500 mt-1">Total rows: {{ preview.total_rows }}</p>
              </div>
              
              <!-- Field mapping -->
              <div>
                <h4 class="font-medium mb-2">Map columns to fields</h4>
                <div class="space-y-2">
                  <div v-for="(m, index) in mappings" :key="index" 
                       class="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                    <input
                      type="checkbox"
                      :checked="!m.skip"
                      @change="toggleSkip(index)"
                      class="rounded border-gray-300"
                    />
                    <span class="w-1/3 font-mono text-sm">{{ m.excel_column }}</span>
                    <span class="text-gray-400">→</span>
                    <select
                      v-model="m.table_field"
                      :disabled="m.skip"
                      class="flex-1 px-2 py-1 border rounded-lg text-sm"
                    >
                      <option value="">— Skip —</option>
                      <option v-for="field in table?.fields" :key="field.id" :value="field.name">
                        {{ field.display_name }} ({{ field.name }})
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Import result -->
            <div v-else-if="importResult" class="text-center py-8">
              <div class="text-5xl mb-4">✅</div>
              <h3 class="text-lg font-medium mb-2">Import Complete!</h3>
              <p class="text-gray-600">
                Imported {{ importResult.imported }} of {{ importResult.total }} rows
              </p>
              <div v-if="importResult.errors?.length" class="mt-4 text-left">
                <p class="text-sm font-medium text-red-600">Errors:</p>
                <ul class="text-xs text-red-500 list-disc pl-4">
                  <li v-for="err in importResult.errors" :key="err">{{ err }}</li>
                </ul>
              </div>
            </div>
          </div>
          
          <!-- Footer -->
          <div class="flex-shrink-0 px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-end gap-3">
            <button
              v-if="step === 2 && !importResult"
              @click="step = 1"
              :disabled="loading"
              class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
            >
              ← Back
            </button>
            
            <button
              @click="closeModal"
              :disabled="loading"
              class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            
            <button
              v-if="step === 2 && !importResult"
              @click="doImport"
              :disabled="loading"
              class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {{ loading ? 'Importing...' : 'Import Data' }}
            </button>
            
            <button
              v-if="importResult"
              @click="finishImport"
              class="px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
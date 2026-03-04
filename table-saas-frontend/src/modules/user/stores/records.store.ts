import { defineStore } from 'pinia'
import { ref } from 'vue'
import { recordsApi, type TableRecord, type RecordsQueryParams } from '@/core/api/user/records'

export const useRecordsStore = defineStore('records', () => {
  const records = ref<TableRecord[]>([])
  const currentRecord = ref<TableRecord | null>(null)
  const isLoading = ref(false)
  const totalCount = ref(0)

  async function fetchRecords(tableId: string, params?: RecordsQueryParams) {
    isLoading.value = true
    try {
      const { data } = await recordsApi.getRecords(tableId, params)
      records.value = data
      totalCount.value = data.length
    } catch (error) {
      console.error('Failed to fetch records:', error)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchRecord(tableId: string, recordId: string) {
    isLoading.value = true
    try {
      const { data } = await recordsApi.getRecord(tableId, recordId)
      currentRecord.value = data
    } catch (error) {
      console.error('Failed to fetch record:', error)
    } finally {
      isLoading.value = false
    }
  }

  async function createRecord(tableId: string, data: Record<string, any>) {
    try {
      const { data: newRecord } = await recordsApi.createRecord(tableId, { data })
      records.value.push(newRecord)
      return newRecord
    } catch (error) {
      console.error('Failed to create record:', error)
      throw error
    }
  }

  async function updateRecord(tableId: string, recordId: string, formData: Record<string, any>) {
    try {
      // Убираем лишние поля (id, _created_at, _created_by, _updated_at)
      const { id, _created_at, _created_by, _updated_at, ...cleanData } = formData
      
      const payload = { data: cleanData }
      const { data: updatedRecord } = await recordsApi.updateRecord(tableId, recordId, payload)
      
      const index = records.value.findIndex(r => r.id === recordId)
      if (index !== -1) {
        records.value[index] = updatedRecord
      }
      return updatedRecord
    } catch (error) {
      console.error('Failed to update record:', error)
      throw error
    }
  }

  async function deleteRecord(tableId: string, recordId: string) {
    try {
      await recordsApi.deleteRecord(tableId, recordId)
      records.value = records.value.filter(r => r.id !== recordId)
    } catch (error) {
      console.error('Failed to delete record:', error)
      throw error
    }
  }

  return {
    records,
    currentRecord,
    isLoading,
    totalCount,
    fetchRecords,
    fetchRecord,
    createRecord,
    updateRecord,
    deleteRecord,
  }
})
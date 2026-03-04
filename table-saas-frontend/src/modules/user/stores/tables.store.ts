import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tablesApi, type Table, type CreateTableDto } from '@/core/api/user/tables'

export const useTablesStore = defineStore('tables', () => {
  const tables = ref<Table[]>([])
  const currentTable = ref<Table | null>(null)
  const isLoading = ref(false)
  const isCreating = ref(false)

  async function fetchTables() {
    isLoading.value = true
    try {
      const { data } = await tablesApi.getTables()
      tables.value = data
    } catch (error) {
      console.error('Failed to fetch tables:', error)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTable(id: string) {
    isLoading.value = true
    try {
      const { data } = await tablesApi.getTable(id)
      currentTable.value = data
    } catch (error) {
      console.error('Failed to fetch table:', error)
    } finally {
      isLoading.value = false
    }
  }

  async function createTable(data: CreateTableDto) {
    isCreating.value = true
    try {
      const { data: newTable } = await tablesApi.createTable(data)
      tables.value.push(newTable)
      return newTable
    } catch (error) {
      console.error('Failed to create table:', error)
      throw error
    } finally {
      isCreating.value = false
    }
  }

  return {
    tables,
    currentTable,
    isLoading,
    isCreating,
    fetchTables,
    fetchTable,
    createTable,
  }
})
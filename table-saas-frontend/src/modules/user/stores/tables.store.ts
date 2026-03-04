import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tablesApi, type Table, type CreateTableDto, type UpdateTableDto } from '@/core/api/user/tables'

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
      return data
    } catch (error) {
      console.error('Failed to fetch table:', error)
      throw error
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

  // НОВЫЙ МЕТОД: обновление таблицы
  async function updateTable(id: string, data: UpdateTableDto) {
    isLoading.value = true
    try {
      const { data: updatedTable } = await tablesApi.updateTable(id, data)
      
      // Обновляем в списке
      const index = tables.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tables.value[index] = updatedTable
      }
      
      // Обновляем текущую таблицу если это она
      if (currentTable.value?.id === id) {
        currentTable.value = updatedTable
      }
      
      return updatedTable
    } catch (error) {
      console.error('Failed to update table:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // НОВЫЙ МЕТОД: удаление таблицы
  async function deleteTable(id: string) {
    isLoading.value = true
    try {
      await tablesApi.deleteTable(id)
      
      // Удаляем из списка
      tables.value = tables.value.filter(t => t.id !== id)
      
      // Очищаем текущую таблицу если это она
      if (currentTable.value?.id === id) {
        currentTable.value = null
      }
    } catch (error) {
      console.error('Failed to delete table:', error)
      throw error
    } finally {
      isLoading.value = false
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
    updateTable,
    deleteTable,
  }
})
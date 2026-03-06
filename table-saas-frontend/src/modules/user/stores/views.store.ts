import { defineStore } from 'pinia'
import { ref } from 'vue'
import { viewsApi, type View, type ViewType, type CreateViewDto, type UpdateViewDto } from '@/core/api/user/views'

export const useViewsStore = defineStore('views', () => {
  const views = ref<View[]>([])
  const currentView = ref<View | null>(null)
  const isLoading = ref(false)

  async function fetchViews(tableId: string) {
    isLoading.value = true
    try {
      const { data } = await viewsApi.getViews(tableId)
      views.value = data
      
      if (data.length > 0) {
        // Ищем дефолтный вид
        const defaultView = data.find(v => v.is_default)
        
        // Явно проверяем на undefined и присваиваем
        if (defaultView) {
          currentView.value = defaultView
        } else {
          // data[0] точно существует, но TS тупит - используем !
          currentView.value = data[0]!
        }
      } else {
        currentView.value = null
      }
    } catch (error) {
      console.error('Failed to fetch views:', error)
      currentView.value = null
    } finally {
      isLoading.value = false
    }
  }

  async function createView(tableId: string, data: CreateViewDto) {
    try {
      const { data: newView } = await viewsApi.createView(tableId, data)
      views.value.push(newView)
      return newView
    } catch (error) {
      console.error('Failed to create view:', error)
      throw error
    }
  }

  async function updateView(tableId: string, viewId: string, data: UpdateViewDto) {
    try {
      const { data: updatedView } = await viewsApi.updateView(tableId, viewId, data)
      const index = views.value.findIndex(v => v.id === viewId)
      if (index !== -1) {
        views.value[index] = updatedView
      }
      if (currentView.value?.id === viewId) {
        currentView.value = updatedView
      }
      return updatedView
    } catch (error) {
      console.error('Failed to update view:', error)
      throw error
    }
  }

  async function deleteView(tableId: string, viewId: string) {
    try {
      await viewsApi.deleteView(tableId, viewId)
      views.value = views.value.filter(v => v.id !== viewId)
      if (currentView.value?.id === viewId) {
        currentView.value = views.value[0] || null
      }
    } catch (error) {
      console.error('Failed to delete view:', error)
      throw error
    }
  }

  function setCurrentView(view: View | null) {
    currentView.value = view
  }

  return {
    views,
    currentView,
    isLoading,
    fetchViews,
    createView,
    updateView,
    deleteView,
    setCurrentView,
  }
})
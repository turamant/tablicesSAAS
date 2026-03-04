<script setup lang="ts">
import { useAuthStore } from '@/core/stores/auth'

const auth = useAuthStore()
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Шапка -->
    <header class="bg-white shadow-sm border-b">
      <div class="mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="text-xl font-bold text-gray-900">
            Table SaaS
          </div>
          
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-600">
              {{ auth.user?.full_name || auth.user?.email }}
            </span>
            <button
              @click="auth.logout"
              class="px-3 py-1 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
    
    <!-- Основной контент -->
    <main class="mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <router-view />
    </main>
  </div>
</template>
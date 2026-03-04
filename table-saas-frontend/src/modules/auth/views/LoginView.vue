<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/core/stores/auth'

const auth = useAuthStore()
const email = ref('')
const password = ref('')
const error = ref('')

async function handleSubmit() {
  try {
    error.value = ''
    await auth.login({
      email: email.value,
      password: password.value,
    })
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Login failed'
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg">
      <div>
        <h2 class="text-3xl font-bold text-center text-gray-900">
          Table SaaS
        </h2>
        <p class="mt-2 text-center text-gray-600">
          Sign in to your account
        </p>
      </div>
      
      <form @submit.prevent="handleSubmit" class="mt-8 space-y-6">
        <div v-if="error" class="bg-red-50 text-red-600 p-3 rounded-lg text-sm">
          {{ error }}
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              v-model="email"
              type="email"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="user@example.com"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              v-model="password"
              type="password"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
            />
          </div>
        </div>

        <button
          type="submit"
          :disabled="auth.isLoading"
          class="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ auth.isLoading ? 'Loading...' : 'Sign in' }}
        </button>
        
        <p class="text-center text-sm text-gray-600">
          Don't have an account?
          <router-link to="/register" class="text-blue-600 hover:underline">
            Register
          </router-link>
        </p>
      </form>
    </div>
  </div>
</template>
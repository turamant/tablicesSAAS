export interface User {
    id: string
    email: string
    full_name: string | null
    is_active: boolean
    is_superuser: boolean
    tier?: string  // добавим позже
  }
  
  export interface LoginPayload {
    email: string
    password: string
  }
  
  export interface RegisterPayload extends LoginPayload {
    full_name?: string
  }
  
  export interface AuthResponse {
    message: string
    user?: string  // email
  }
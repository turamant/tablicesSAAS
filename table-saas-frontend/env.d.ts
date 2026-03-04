/// <reference types="vite/client" />


interface ImportMetaEnv {
    readonly VITE_API_URL: string
    // добавь другие переменные если есть
  }
  
  interface ImportMeta {
    readonly env: ImportMetaEnv
  }
  
  declare module '*.vue' {
    import type { DefineComponent } from 'vue'
    const component: DefineComponent<{}, {}, any>
    export default component
  }
#!/bin/bash

# Создаем корневую структуру
mkdir -p src/core/{api/{user,admin},auth,router,stores,types}
mkdir -p src/shared/{ui,composables,layouts,utils}
mkdir -p src/modules/{auth,user/{router,views,components,stores},admin/{router,views,components,stores}}

# ========== CORE ==========

# API
touch src/core/api/client.ts
touch src/core/api/auth.ts
touch src/core/api/user/index.ts
touch src/core/api/user/tables.ts
touch src/core/api/user/records.ts
touch src/core/api/user/fields.ts
touch src/core/api/admin/index.ts
touch src/core/api/admin/users.ts
touch src/core/api/admin/stats.ts

# Auth
touch src/core/auth/guards.ts
touch src/core/auth/composables/useAuth.ts

# Router
touch src/core/router/index.ts
touch src/core/router/routes.ts

# Stores
touch src/core/stores/auth.ts

# Types
touch src/core/types/api.types.ts
touch src/core/types/auth.types.ts

# ========== SHARED ==========

# UI-kit
touch src/shared/ui/Button/index.ts
touch src/shared/ui/Button/Button.vue
touch src/shared/ui/Input/Input.vue
touch src/shared/ui/Modal/Modal.vue
touch src/shared/ui/Table/Table.vue
touch src/shared/ui/Select/Select.vue
touch src/shared/ui/Toast/Toast.vue

# Composables
touch src/shared/composables/useTableSort.ts
touch src/shared/composables/useTableFilter.ts
touch src/shared/composables/usePagination.ts

# Layouts
touch src/shared/layouts/AuthLayout.vue
touch src/shared/layouts/UserLayout.vue
touch src/shared/layouts/AdminLayout.vue

# Utils
touch src/shared/utils/date.ts
touch src/shared/utils/validators.ts

# ========== MODULES ==========

# Auth
touch src/modules/auth/views/LoginView.vue
touch src/modules/auth/views/RegisterView.vue
touch src/modules/auth/stores/index.ts

# User
touch src/modules/user/router/index.ts
touch src/modules/user/views/DashboardView.vue
touch src/modules/user/views/TableView.vue
touch src/modules/user/views/DataView.vue
touch src/modules/user/components/TableList.vue
touch src/modules/user/components/FieldEditor.vue
touch src/modules/user/components/DataGrid.vue
touch src/modules/user/components/RecordModal.vue
touch src/modules/user/stores/tables.store.ts
touch src/modules/user/stores/records.store.ts

# Admin
touch src/modules/admin/router/index.ts
touch src/modules/admin/views/UsersView.vue
touch src/modules/admin/views/StatsView.vue
touch src/modules/admin/components/UserTable.vue
touch src/modules/admin/components/UserEditModal.vue
touch src/modules/admin/stores/users.store.ts

# ========== КОРНЕВЫЕ ФАЙЛЫ (если нет) ==========
touch src/App.vue
touch src/main.ts
touch src/style.css
touch src/env.d.ts
touch postcss.config.js
touch tailwind.config.js
touch vite.config.ts
touch tsconfig.json
touch tsconfig.app.json
touch tsconfig.node.json
touch index.html
touch .env
touch .env.example
touch .gitignore

echo "✅ Структура проекта создана!"
echo ""
echo "📁 Проверь результат:"
echo "   ls -la src/"
echo "   ls -la src/core/api/"
echo "   ls -la src/modules/"
echo ""
echo "🚀 Запусти проект:"
echo "   npm run dev"
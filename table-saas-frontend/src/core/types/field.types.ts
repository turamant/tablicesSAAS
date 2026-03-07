// ДОЛЖНО СОВПАДАТЬ С БЭКОМ 1 В 1!
export type FieldType = 
  | 'text'
  | 'number'
  | 'date'
  | 'boolean'
  | 'select'
  | 'multiselect'
  | 'email'
  | 'formula'  // ← ДОБАВЛЕНО!

// Для компонентов (с человеческими названиями и иконками)
export const FIELD_TYPES: { value: FieldType; label: string; icon: string; description: string }[] = [
  { value: 'text', label: 'Text', icon: '📝', description: 'Single line text' },
  { value: 'number', label: 'Number', icon: '🔢', description: 'Numeric values' },
  { value: 'date', label: 'Date', icon: '📅', description: 'Date picker' },
  { value: 'boolean', label: 'Yes/No', icon: '✅', description: 'Checkbox' },
  { value: 'select', label: 'Select', icon: '▼', description: 'Dropdown list' },
  { value: 'multiselect', label: 'Multi Select', icon: '☑️', description: 'Multiple choices' },
  { value: 'email', label: 'Email', icon: '📧', description: 'Email address' },
  { value: 'formula', label: 'Formula', icon: 'ƒ', description: 'Calculated field' },
]

// Конфигурация для рендеринга полей
export const FIELD_TYPE_CONFIG: {
  [key in FieldType]: {
    component: 'input' | 'select' | 'checkbox' | 'textarea' | 'div'
    inputType?: string
    readonly?: boolean
  }
} = {
  text: { component: 'input', inputType: 'text', readonly: false },
  number: { component: 'input', inputType: 'number', readonly: false },
  date: { component: 'input', inputType: 'date', readonly: false },
  boolean: { component: 'checkbox', readonly: false },
  select: { component: 'select', readonly: false },
  multiselect: { component: 'select', readonly: false },
  email: { component: 'input', inputType: 'email', readonly: false },
  formula: { component: 'div', readonly: true },  // formula только для чтения
}

// Тип для опций поля (включая формулу)
export interface FieldOptions {
  choices?: string[]  // для select/multiselect
  formula?: string    // для formula
  return_type?: 'number' | 'string' | 'boolean'  // для formula
  dependencies?: string[]  // поля, от которых зависит формула
}

// Расширенный тип поля для создания
export interface CreateFieldDto {
  name: string
  display_name: string
  field_type: FieldType
  is_required?: boolean
  is_unique?: boolean
  options?: FieldOptions
  sort_order?: number
}
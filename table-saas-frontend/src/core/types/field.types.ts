// ДОЛЖНО СОВПАДАТЬ С БЭКОМ 1 В 1!
export type FieldType = 
  | 'text'
  | 'number'
  | 'date'
  | 'boolean'
  | 'select'
  | 'multiselect'
  | 'email'

// Для компонентов (с человеческими названиями)
export const FIELD_TYPES: { value: FieldType; label: string }[] = [
  { value: 'text', label: 'Text' },
  { value: 'number', label: 'Number' },
  { value: 'date', label: 'Date' },
  { value: 'boolean', label: 'Yes/No' },
  { value: 'select', label: 'Select (dropdown)' },
  { value: 'multiselect', label: 'Multi Select' },
  { value: 'email', label: 'Email' },
]

// ИСПРАВЛЕНО: убираем Record, делаем простой объект с типами
export const FIELD_TYPE_CONFIG: {
  [key in FieldType]: {
    component: 'input' | 'select' | 'checkbox' | 'textarea'
    inputType?: string
  }
} = {
  text: { component: 'input', inputType: 'text' },
  number: { component: 'input', inputType: 'number' },
  date: { component: 'input', inputType: 'date' },
  boolean: { component: 'checkbox' },
  select: { component: 'select' },
  multiselect: { component: 'select' }, // multiple=true добавим в компоненте
  email: { component: 'input', inputType: 'email' },
}
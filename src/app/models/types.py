import enum

class SharePermission(str, enum.Enum):
    READ = "read"
    EDIT = "edit"
    ADMIN = "admin"

class FieldType(str, enum.Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    SELECT = "select"
    MULTISELECT = "multiselect"
    EMAIL = "email"
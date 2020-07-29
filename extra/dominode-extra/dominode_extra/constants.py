from enum import Enum


class DepartmentName(Enum):
    PPD = 'ppd'
    LSD = 'lsd'


class UserRole(str, Enum):
    REGULAR_DEPARTMENT_USER = 'regular_department_user'
    EDITOR = 'editor'

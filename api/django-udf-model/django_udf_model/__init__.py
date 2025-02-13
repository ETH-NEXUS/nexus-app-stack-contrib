from enum import Enum


class Command(Enum):
    SELECT = 'select'
    INSERT = 'insert'
    UPDATE = 'update'
    DELETE = 'delete'

from dataclasses import dataclass
from enum import Enum

class UserStatusEnum(Enum):
    BLOCK = 'Заблокирован'
    ACTIVE = 'Активен'

#Классы-сущности
@dataclass
class User:
    fio : str
    login : str
    password : str
    stat : UserStatusEnum

@dataclass
class Operator:
    note : str
    user: User

@dataclass
class UnloadingOperator:
    unload_place : str
    note : str
    user: User

@dataclass
class ScaleOperator:
    primary_weight : float
    secondary_weight : float
    user : User

@dataclass
class Laborant:
    primary_check : str
    secondary_check : str
    user : User

@dataclass
class TE:
    vendor_item: str
    sugarbeet_condition: str
    registration_number: str
    note: str
    operator : Operator = None
    unloading_operator : UnloadingOperator = None
    scale_operator : ScaleOperator = None
    laborant : Laborant = None

@dataclass
class AcceptingAct:
    te: TE
    accept_info : str
    weighting_result : float

@dataclass
class DistrReport:
    te : TE
    destination : str

@dataclass
class UnloadingReport:
    te : TE
    unload_info : str
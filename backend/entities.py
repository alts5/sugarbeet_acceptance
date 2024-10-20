from dataclasses import dataclass
from enum import Enum


class UserStatusEnum(Enum):
    BLOCK = 'Заблокирован'
    ACTIVE = 'Активен'

@dataclass
class User:
    fio: str
    login: str
    password: str
    stat: UserStatusEnum


@dataclass
class Operator:
    note: str
    user: User


@dataclass
class UnloadingOperator:
    unload_place: str
    note: str
    user: User


@dataclass
class ScaleOperator:
    user: User
    primary_weight: float = 0
    secondary_weight: float = 0


@dataclass
class Laborant:
    primary_check: str
    secondary_check: str
    user: User


@dataclass
class TE:
    vendor_item: str
    sugarbeet_condition: str
    registration_number: str
    note: str
    operator: Operator = None
    unloading_operator: UnloadingOperator = None
    scale_operator: ScaleOperator = None
    laborant: Laborant = None

@dataclass
class AcceptingAct:
    te: TE
    accept_info: str
    weighting_result: float = 0

@dataclass
class DistrReport:
    te: TE
    destination: str

@dataclass
class UnloadingReport:
    te: TE
    unload_info: str

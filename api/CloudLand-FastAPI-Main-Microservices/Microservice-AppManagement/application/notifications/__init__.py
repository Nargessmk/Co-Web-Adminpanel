from uuid import UUID
from dataclasses import dataclass

from core.mediator import Notification
from Schema.AppManagement.constant import ConstantDTO


@dataclass
class ConstantAddedNotification(Notification):
    constant: ConstantDTO
    user_id: UUID


@dataclass
class ConstantUpdatedNotification(Notification):
    constant: ConstantDTO
    user_id: UUID


@dataclass
class ConstantDeletedNotification(Notification):
    constant: ConstantDTO | None
    user_id: UUID
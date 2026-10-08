from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ScheduleSyncResponse(BaseModel):
    added: list[ScheduleResponse]
    updated: list[ScheduleResponse]
    deleted: list[ScheduleResponse]


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # разрешение на создание модели из объекта с атрибутами(Schedule)

    id: UUID
    group_name: str
    date: date
    week_type: int
    lesson_number: int
    start_time: time
    end_time: time
    discipline: str
    teacher: str
    classroom: str
    is_lection: bool
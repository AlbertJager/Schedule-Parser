from datetime import date, time
from uuid import UUID, uuid7

from sqlalchemy import Date, SmallInteger, String, Time, Uuid, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.app.services.db.database import Base

class Schedule(Base):
    __tablename__ = "schedule"
    
    __table_args__ = (  # комбинация group_name + date + lesson_number должна быть уникальной
        UniqueConstraint(
            "group_name",
            "date",
            "lesson_number",
            name="uq_schedule_group_date_lesson",
        ),
    )
    
    
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    group_name: Mapped[str] = mapped_column(String)
    date: Mapped[date] = mapped_column(Date)
    week_type: Mapped[int] = mapped_column(SmallInteger)
    lesson_number: Mapped[int] = mapped_column(SmallInteger)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    discipline: Mapped[str] = mapped_column(String)
    teacher: Mapped[str] = mapped_column(String)
    classroom: Mapped[str] = mapped_column(String)
    is_lection: Mapped[bool] = mapped_column(Boolean)
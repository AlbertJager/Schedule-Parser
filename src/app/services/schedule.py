from src.app.services.kubsau_schedule_scraper import get_schedule
from src.app.services.db.models import Schedule
from sqlalchemy import select
from datetime import date as date_type, time as time_type

def add_schedule_of_group(group_name: str, db):
    '''Получает расписание группы с обработкой ошибок'''
    try:
        schedule_of_group = get_schedule(group_name)
    except ValueError:
        return None
    
    for weeks in schedule_of_group: 
        week_type = weeks["week"]
        for day, schedule_of_day in weeks["schedules"].items(): 
            for lesson_number, subject in schedule_of_day["schedule"].items():
                lesson_number = int(lesson_number)
                date = date_type.fromisoformat(day)  # преобразуем дату из строки в дату
                start_time = time_type.fromisoformat(subject["time_start"])
                end_time = time_type.fromisoformat(subject["time_end"])
                
                existing_schedule = db.scalar(
                select(Schedule).where(
                    Schedule.group_name == group_name,
                    Schedule.date == date,
                    Schedule.lesson_number == lesson_number,
                )
            )
                if existing_schedule:
                    continue
                
                schedule = Schedule(
                group_name = group_name,
                date = date,
                week_type = week_type,
                lesson_number = lesson_number,
                start_time = start_time,
                end_time = end_time,
                discipline = subject["discipline"],
                teacher = subject["teacher"],
                classroom = subject["classroom"],
                is_lection = subject["is_lection"]
                )
                
                db.add(schedule)
    db.commit()
    return schedule_of_group


def get_schedule_from_db(group_name: str, db):
    return db.scalars(
        select(Schedule).where(
            Schedule.group_name == group_name
        )
    ).all()
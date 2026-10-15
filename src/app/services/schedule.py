from src.app.services.kubsau_schedule_scraper import get_schedule
from src.app.services.db.models import Schedule
from src.app.schemas.schedule import SchedulePeriod
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from datetime import date as date_type, time as time_type, timedelta


def add_schedule_of_group(group_name: str, db) -> dict[str, list[Schedule]] | None:
    '''Получает расписание группы с обработкой ошибок и записывает в БД'''
    try:
        schedule_of_group = get_schedule(group_name)
    except ValueError:
        return None
    
    entries_info = {"added": [], "updated": [], "deleted": []}  # Для уведомления пользователя об изменениях
    
    today = date_type.today()

    if today.weekday() == 0:  # понедельник
        previous_monday = today - timedelta(days=7)
        previous_sunday = today - timedelta(days=1)

        old_entries = db.scalars(
            select(Schedule).where(
                Schedule.group_name == group_name,
                Schedule.date.between(previous_monday, previous_sunday),
            )
        ).all()

        for entry in old_entries:
            entries_info["deleted"].append(entry)
            db.delete(entry)
            
    for weeks in schedule_of_group: 
        for day, schedule_of_day in weeks["schedules"].items(): 
            for lesson_number, subject in schedule_of_day["schedule"].items():
                data_for_entry = {}  # словарь из полей для записи в БД
                
                data_for_entry["lesson_number"] = int(lesson_number)
                data_for_entry["week_type"] = weeks["week"]
                data_for_entry["date"] = date_type.fromisoformat(day)  # преобразуем дату из строки в дату
                data_for_entry["group_name"] = group_name
                
                existing_schedule: Schedule = db.scalar(
                select(Schedule).where(
                    Schedule.group_name == data_for_entry["group_name"],
                    Schedule.date == data_for_entry["date"],
                    Schedule.lesson_number == data_for_entry["lesson_number"],
                )
            )
                if not subject:
                    if existing_schedule:
                        entries_info["deleted"].append(existing_schedule)
                        db.delete(existing_schedule)  # удаление записи о занятии из БД, если оно исчезло из сайта КубГАУ
                    continue
                            
                data_for_entry["start_time"] = time_type.fromisoformat(subject["time_start"])
                data_for_entry["end_time"] = time_type.fromisoformat(subject["time_end"])
                data_for_entry["discipline"] = subject["discipline"]
                data_for_entry["teacher"] = subject["teacher"]
                data_for_entry["classroom"] = subject["classroom"]
                data_for_entry["is_lection"] = subject["is_lection"]
                
                if existing_schedule:  # проверка на наличие записи по занятию
                    changes = (
                        existing_schedule.classroom != data_for_entry["classroom"] or
                        existing_schedule.start_time != data_for_entry["start_time"] or
                        existing_schedule.end_time != data_for_entry["end_time"] or
                        existing_schedule.teacher != data_for_entry["teacher"] or 
                        existing_schedule.discipline != data_for_entry["discipline"] or
                        existing_schedule.is_lection != data_for_entry["is_lection"]
                    )
                    
                    if changes:  # проверка, изменилось ли что-то для существующей записи
                        entry = add_entry(existing_schedule, **data_for_entry, update=True)

                        entries_info["updated"].append(entry)
                    else:
                        continue
                
                else:  # добавление новой записи в БД
                    entry = add_entry(existing_schedule, **data_for_entry)

                    entries_info["added"].append(entry)
                
                db.add(entry)
                
    db.commit()
    return entries_info
    
    
def add_entry(entry: Schedule, update=False, **kwargs) -> Schedule | None:
    '''Добавляет или обновляет запись расписания для БД и возвращает запись'''
    if not update:
        entry = Schedule()
        entry.date = kwargs["date"]
        entry.lesson_number = kwargs["lesson_number"]
        entry.group_name = kwargs["group_name"]
        entry.week_type = kwargs["week_type"]
    
    entry.start_time = kwargs["start_time"]
    entry.end_time = kwargs["end_time"]
    entry.discipline = kwargs["discipline"]
    entry.teacher = kwargs["teacher"]
    entry.classroom = kwargs["classroom"]
    entry.is_lection = kwargs["is_lection"]
    return entry


def get_schedule_from_db(group_name: str, db: Session, period: SchedulePeriod | None = None) -> list[Schedule]:
    """Возвращает выборку расписания для группы"""
    today = date_type.today()

    query = select(Schedule).where(
        Schedule.group_name == group_name
    )

    if period is not None:
        if period == SchedulePeriod.TODAY:
            date_from = today
            date_to = today
        elif period == SchedulePeriod.TOMORROW:
            date_from = today + timedelta(days=1)
            date_to = date_from
        else:
            date_from = today - timedelta(days=today.weekday())

            if period == SchedulePeriod.NEXT_WEEK:
                date_from += timedelta(days=7)

            date_to = date_from + timedelta(days=6)

        query = query.where(
            Schedule.date.between(date_from, date_to)
        )

        query = query.where(Schedule.date.between(date_from, date_to))

    return db.scalars(query).all()
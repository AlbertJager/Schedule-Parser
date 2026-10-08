from src.app.services.kubsau_schedule_scraper import get_schedule
from src.app.services.db.models import Schedule
from sqlalchemy import select
from datetime import date as date_type, time as time_type

def add_schedule_of_group(group_name: str, db) -> dict:
    '''Получает расписание группы с обработкой ошибок и записывает в БД'''
    try:
        schedule_of_group = get_schedule(group_name)
    except ValueError:
        return None
    
    entries_info = {"added": [], "updated": [], "deleted": []}
    
    for weeks in schedule_of_group: 
        for day, schedule_of_day in weeks["schedules"].items(): 
            for lesson_number, subject in schedule_of_day["schedule"].items():
                lesson_number = int(lesson_number)
                week_type = weeks["week"]
                date = date_type.fromisoformat(day)  # преобразуем дату из строки в дату
                
                existing_schedule: Schedule = db.scalar(
                select(Schedule).where(
                    Schedule.group_name == group_name,
                    Schedule.date == date,
                    Schedule.lesson_number == lesson_number,
                )
            )
                if not subject:
                    if existing_schedule:
                        entries_info["deleted"].append(existing_schedule)
                        db.delete(existing_schedule)  # удаление записи о занятии из БД, если оно исчезло из сайта КубГАУ
                    continue
                            
                start_time = time_type.fromisoformat(subject["time_start"])
                end_time = time_type.fromisoformat(subject["time_end"])
                discipline = subject["discipline"]
                teacher = subject["teacher"]
                classroom = subject["classroom"]
                is_lection = subject["is_lection"]
                
                if existing_schedule:  # проверка на наличие записи по занятию
                    changes = (
                        existing_schedule.classroom != classroom or
                        existing_schedule.start_time != start_time or
                        existing_schedule.end_time != end_time or
                        existing_schedule.teacher != teacher or 
                        existing_schedule.discipline != discipline or
                        existing_schedule.week_type != week_type or
                        existing_schedule.is_lection != is_lection
                    )
                    
                    if changes:  # проверка, изменилось ли что-то для существующей записи
                        entry = add_entry(existing_schedule, classroom=classroom, discipline=discipline, teacher=teacher, 
                        start_time=start_time, end_time=end_time, is_lection=is_lection, 
                        lesson_number=lesson_number, week_type=week_type, date=date, update=True)

                        entries_info["updated"].append(entry)
                    else:
                        continue
                
                else:  # добавление новой записи в БД
                    entry = add_entry(existing_schedule, group_name=group_name, week_type=week_type, lesson_number=lesson_number, 
                    classroom=classroom, teacher=teacher, start_time=start_time, discipline=discipline, 
                    end_time=end_time, is_lection=is_lection, date=date)

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


def get_schedule_from_db(group_name: str, db) -> list[Schedule]:
    """Возвращает выборку расписания(на 2 недели) для группы"""
    return db.scalars(
        select(Schedule).where(
            Schedule.group_name == group_name
        )
    ).all()
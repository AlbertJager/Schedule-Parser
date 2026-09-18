from collections.abc import Generator
from requests import get
from bs4 import BeautifulSoup, Tag
from re import compile
from fake_useragent import UserAgent
from datetime import datetime, timezone, timedelta
import json


def get_souped_page(group: str) -> BeautifulSoup | None:
    '''Отдает страницу в виде экземпляра BS'''
    headers = {"User-Agent": UserAgent().random, "Accept-Language": "ru-RU,ru;q=0.9"}  # генерирует случайную строку User-Agent    

    response = get(f"https://s.kubsau.ru/?type_schedule=1&val={group}", headers=headers).text

    soup = BeautifulSoup(response, "lxml")

    group_exists = soup.find('h2', class_='h2-responsive')

    if not group_exists:
        raise ValueError("Такой группы нет.")    
    return soup


def get_days(week: Tag) -> Generator[Tag, None, None]:
    '''Поочередно выдает блоки дней недели(пн-сб)'''
    yield from week.find_all("div", class_= compile("^card-block day-"))


def get_page_of_week(souped_page: BeautifulSoup, week: str) -> Tag | None:
    '''Возвращает блок html-кода с конкретной неделей, принимает week(first, second)'''
    page = souped_page.find("div", class_=compile(f"schedule-{week}-week"))  # страница конкретной недели
    return page


def get_schedule_of_week(souped_page, week: str):
    '''Возвращает расписание конкретной недели в виде словаря с днями'''    
    page_of_week = get_page_of_week(souped_page, week)
    
    schedule_of_week = {
        "week": week,
        "schedules": {
            # здесь будут словари с расписаниями дней 
        }
    }

    for page_of_day in get_days(page_of_week):  # перебор веб-страниц дней
        schedule_of_day = extract_schedule_from_day(page_of_day)
        
        day = schedule_of_day["day"]  # дата в формате yyyy-mm-dd
        schedule_of_week["schedules"][day] = schedule_of_day
        
    with open(f"schedule_of_weeks.json", "w", encoding="utf-8") as f:
        json.dump(schedule_of_week, f, ensure_ascii=False, indent=4)
        
    return schedule_of_week


def extract_schedule_from_day(page_of_day: Tag) -> dict:
    '''Возвращает расписание дня в виде словаря'''    
    
    # словарь данных для каждого предмета
    schedule_of_day = {
       "day": page_of_day.get("class")[1][4:],  # дата в формате yyyy-mm-dd
        "schedule": {  
            # здесь ключ это number - порядковый номер пары(начиная с 1)
        }
    }

    # перебор каждого занятия
    for number, subject in enumerate(page_of_day.find("table", class_= "table").find_all("tr"), start=1):  
        discipline_tag = subject.find("td", class_="diss")  # в нем содержится дисциплина и преподаватель
        
        is_lection = True if subject.find("td", class_="lection yes") else False
        if is_lection:
            discipline = discipline_tag.find("strong").text.strip()
        else:
            discipline = discipline_tag.find(string=True).text.strip()
        
        if not discipline:  # пропуск пустых занятий
            continue
        
        entry = schedule_of_day["schedule"][number] = {}  # хранилище данных предмета    
        
        teacher = discipline_tag.find("span", class_="diss-info").text.strip()
        teacher = " | ".join([i.strip() for i in teacher.split("\r\n") if i.strip() and i.strip() != ","])
        
        time_start, time_end = subject.find("td", class_="time").text.strip().split() 
        classroom = subject.find("a", class_="room-link").text.strip()
        
        # заполнение хранилища предмета
        if not classroom:
            link = subject.find("a", class_="webex")["href"]
            entry["classroom"] = link
        else:
            entry["classroom"] = classroom
        
        entry["discipline"] = discipline    
        entry["teacher"] = teacher
        entry["is_lection"] = is_lection
        entry["time_start"] = time_start    
        entry["time_end"] = time_end    
        
    return schedule_of_day
        

def schedule_of_weeks(souped_page: Tag):
    '''Создает расписания сразу для двух недель'''
    weeks = []
    
    for week in ("first", "second"):
        weeks.append(get_schedule_of_week(souped_page, week))
    
    with open(f"schedule_of_weeks.json", "w", encoding="utf-8") as f:
        json.dump(weeks, f, ensure_ascii=False, indent=4)
            

def main(group: str) -> None:
    '''Пока для теста функций получения расписания дня и недели'''
    souped_page = get_souped_page(group)
    if not souped_page:
        print('Такой группы нет')
        return
    
    # get_schedule_of_week(souped_page, "second")
    schedule_of_weeks(souped_page)

    
if __name__ == "__main__":
    main('ЮФО2201')
    
    
    
    
# def get_schedule_of_day(souped_page: BeautifulSoup, day: str) -> dict:
#     ''' Вызывается для поиска расписания сегодняшнего или завтрашнего дня.
#     Параметр day - строка даты в формате in (today, tomorrow). 
    
#     Находит блок(div) с форматом даты в виде yyyy-mm-dd'''
    
#     day = day.lower().strip()
#     if day == "today":
#         day = (datetime.now(timezone.utc)).strftime("%Y-%m-%d")  # перевод даты в строку в формате yyyy-mm-dd
#     elif day == "tomorrow":
#         day = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")  # перевод даты в строку в формате yyyy-mm-dd
#     else:
#         raise ValueError(f"Выберите today/tomorrow. Сейчас: {day}")
    
#     page_of_day = souped_page.find("div", class_= compile(f"^card-block day-{day}"))
#     if not page_of_day:
#         return "Такого дня нет"

#     schedule_of_day = extract_schedule_from_day(page_of_day)  # пока просто
#     with open(f"schedule_of_day_{day}.json", "w", encoding="utf-8") as f:
#             json.dump(schedule_of_day, f, ensure_ascii=False, indent=4)
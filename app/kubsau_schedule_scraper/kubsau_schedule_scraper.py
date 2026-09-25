from collections.abc import Generator
from requests import get
from bs4 import BeautifulSoup, Tag
from re import compile
from fake_useragent import UserAgent
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


def get_page_of_week(souped_page: BeautifulSoup, week: int) -> Tag | None:
    '''Возвращает блок html-кода с конкретной неделей, принимает week(first, second)'''
    week = 'first' if week == 1 else 'second'
    page = souped_page.find("div", class_=compile(f"schedule-{week}-week"))  # страница конкретной недели
    return page


def get_schedule_of_week(souped_page, week: int) -> dict:
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
        

def schedule_of_weeks(souped_page: Tag) -> list[dict]:
    '''Создает расписания сразу для двух недель'''
    weeks = []
    
    for week in range(1, 3):
        weeks.append(get_schedule_of_week(souped_page, week))
    
    return weeks
            

def get_schedule(group: str) -> list[dict]:
    '''Основная функция для получения расписания на 2 недели для конкретной группы
    Получает группу в виде 'ИТ2304', парсит сайт КубГАУ, 
    формирует список словарей с двумя неделями и возвращает его
    '''
    
    souped_page = get_souped_page(group)  # Получаем страницу в виде экземпляра beautiful soup
    
    return schedule_of_weeks(souped_page)  # Получаем список словарей(2 недели)

    
if __name__ == "__main__":
    '''Мои тесты'''
    group = input("Введите группу. Например: ИТ2304\n> ")
    schedule = get_schedule(group)
    with open(f"schedule_{group}.json", "w", encoding="utf-8") as f:
        json.dump(schedule, f, ensure_ascii=False, indent=4)
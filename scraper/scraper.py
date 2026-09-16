# ИТОГОВАЯ ФУНКЦИЯ get_schedule
from collections.abc import Generator
from requests import get
from bs4 import BeautifulSoup, Tag
from re import compile
from fake_useragent import UserAgent
from datetime import datetime, timezone, timedelta


def get_souped_page(group: str) -> BeautifulSoup | None:

    headers = {"User-Agent": UserAgent().random, "Accept-Language": "ru-RU,ru;q=0.9"}  # генерирует случайную строку User-Agent    

    response = get(f"https://s.kubsau.ru/?type_schedule=1&val={group}", headers=headers).text

    soup = BeautifulSoup(response, "lxml")

    group_exists = soup.find('h2', class_='h2-responsive')

    if group_exists:
        return soup


def get_days(week: Tag) -> Generator[Tag, None, None]:
    '''Поочередно выдает блоки с днями недели(пн-сб)'''
    yield from week.find_all("div", class_= compile("^card-block day-"))


def get_page_of_week(souped_page: BeautifulSoup, week: str) -> Tag | None:
    '''Возвращает блок html-кода с конкретной неделей, принимает week(first, second)'''

    page = souped_page.find("div", class_=compile(f"schedule-{week}-week"))  # страница конкретной недели
    return page


def get_schedule_of_week(souped_page, week: str):
    '''Возвращает расписание конкретной недели в виде словаря с днями'''
    page_of_week = get_page_of_week(souped_page, week)

    for page_of_day in get_days(page_of_week):  # перебор страниц дней
        pass

    # словарь куда будут передаваться дни
    schedule_of_week = {

    }
    return page_of_week

    
def get_schedule_of_day(souped_page: BeautifulSoup, day: str) -> dict:
    '''Возвращает расписание сегодняшнего или завтрашнего дня в виде словаря. day in (today, tomorrow). Нужно найти блок с форматом даты в виде day-2026-09-19'''

    page_of_day = souped_page.find("div", class_= compile(f"^card-block day-{day}"))
    if not page_of_day:
        return "Такого дня нет"

    extract_schedule_from_day(page_of_day)
    

def extract_schedule_from_day(page_of_day: Tag):
    schedule_of_day = {
       "day": page_of_day.find("h4", class_= "card-title"),
        "schedule": {  # тут заполнить табличную часть с каждым предметом
            
        }
    }

    for subject in page_of_day.find("table", class_= "table").find_all("tr"):  # перебор каждого занятия
        discipline = subject.find("td", class_="diss").text.strip()
        if not discipline:  # пропуск пустых занятий
            continue

        time_start, time_end = subject.find("td", class_="time").text.strip().split() 
        lection_yes = True if subject.find("div", class_="lection yes") else False
        print(discipline, time_start, time_end, lection_yes)
        
        
        

def main(group: str):
    souped_page = get_souped_page(group)
    if not souped_page:
        print('Такой группы нет')
        return
    # day = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
    day = (datetime.now(timezone.utc)).strftime("%Y-%m-%d")

    get_schedule_of_day(souped_page, day)

    # print(get_schedule_of_week(souped_page, 'second'))
main('ИТ2304')

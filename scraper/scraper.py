# ИТОГОВАЯ ФУНКЦИЯ get_schedule
from collections.abc import Generator
from requests import get
from bs4 import BeautifulSoup, Tag
from re import compile
from fake_useragent import UserAgent
from datetime import datetime, timezone, timedelta


def get_souped_page(group: str) -> BeautifulSoup | None:

    headers = {"User-Agent": UserAgent().random, "Accept-Language": "ru-RU,ru;q=0.9"}

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

    page = souped_page.find("div", id=week)  # страница конкретной недели
    return page


def get_schedule_of_week(souped_page):
    '''Возвращает расписание конкретной недели в виде словаря с днями'''
    week = get_page_of_week(souped_page)
    # словарь куда будут передаваться дни
    schedule_of_week = {

    }

    
def get_schedule_of_day(souped_page: BeautifulSoup, day: str) -> dict:
    '''Возвращает расписание дня в виде словаря. day in (today, tomorrow). Нужно найти блок с форматом даты в виде day-2026-09-19'''
    schedule_of_day = {

    }

    block_of_day = souped_page.find("div", class_= compile(f"^card-block day-{day}"))
    if not block_of_day:
        return "Такого дня нет"
    return block_of_day.find('h4', class_='card-title').text.strip()
    

def main(group: str):
    souped_page = get_souped_page(group)
    day = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
    if not souped_page:
        print('Такой группы нет')
        return
    print(get_schedule_of_day(souped_page, day))


main('ИТ2304')

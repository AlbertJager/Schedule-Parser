from fastapi import APIRouter, HTTPException, status
from src.app.services.kubsau_schedule_scraper import get_schedule


router = APIRouter()


@router.get("")
def root():
    return "Здесь апишка парсера расписания, она возвращает расписание группы на 2 недели"


@router.get("/{group_name}")
def schedule_for_group(group_name: str):
    '''Возвращает расписание целиком'''
    try:
        schedule = get_schedule(group_name)
        return schedule
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(error)
        )
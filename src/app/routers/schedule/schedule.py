from fastapi import APIRouter, HTTPException, status
from fastapi import Depends

from src.app.services.schedule import add_schedule_of_group, get_schedule_from_db
from src.app.services.db.database import get_db
from src.app.schemas.schedule import ScheduleSyncResponse, ScheduleResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

router = APIRouter()


@router.get("")
def root():
    return "Здесь апишка парсера расписания, она возвращает расписание группы на 2 недели"


@router.get("/{group_name}", response_model=ScheduleResponse)
def get_schedule_for_group(group_name: str, db: Session = Depends(get_db)):
    try:
        schedule = get_schedule_from_db(group_name, db)
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="База данных недоступна")
    
    if not schedule:
        try:
            result = add_schedule_of_group(group_name, db)
        except OperationalError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="База данных недоступна"
            )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Группа не найдена"
            )

        schedule = get_schedule_from_db(group_name, db)    
    return schedule


@router.post("/{group_name}", response_model=ScheduleSyncResponse, status_code=status.HTTP_201_CREATED)
def add_schedule_for_group(group_name: str, db: Session = Depends(get_db)):
    try:
        result = add_schedule_of_group(group_name, db)
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="База данных недоступна")
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена")
    
    return result
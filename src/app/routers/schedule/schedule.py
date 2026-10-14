from fastapi import APIRouter, HTTPException, status
from fastapi import Depends

from src.app.services.schedule import add_schedule_of_group, get_schedule_from_db
from src.app.services.db.database import get_db
from src.app.services.db.models import Schedule
from src.app.schemas.schedule import ScheduleSyncResponse, ScheduleResponse, SchedulePeriod
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

router = APIRouter()


@router.get("", response_model=list[ScheduleResponse])
def get_schedule_for_group(group_name: str, period: SchedulePeriod = SchedulePeriod.TODAY, db: Session = Depends(get_db)) -> list[Schedule]:
    try:
        schedule = get_schedule_from_db(group_name, db, period)

        if not schedule:  # Если для выбранного периода нет расписания, загружаем его
            result = add_schedule_of_group(group_name, db)
            if result is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Группа не найдена",
                )
            
            schedule = get_schedule_from_db(group_name, db, period)

    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="База данных недоступна")
         
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
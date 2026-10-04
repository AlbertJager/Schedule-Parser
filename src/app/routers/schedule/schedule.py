from fastapi import APIRouter, HTTPException, status
from src.app.services.schedule import get_schedule_of_group
from fastapi import Depends

from sqlalchemy.orm import Session
from src.app.services.db.database import get_db
router = APIRouter()


@router.get("")
def root():
    return "Здесь апишка парсера расписания, она возвращает расписание группы на 2 недели"


@router.get("/{group_name}")
def schedule_for_group(
    group_name: str,
    db: Session = Depends(get_db),
):
    schedule = get_schedule_of_group(group_name, db)

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена",
        )

    return schedule
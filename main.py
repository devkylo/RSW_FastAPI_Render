from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# 서버 측에서 임시로 JSON 데이터를 저장할 변수 (예: 메모리)
stored_data = {}

# pydantic 모델 예시
class ScheduleData(BaseModel):
    date: str
    day_shift: list
    night_shift: list
    vacation_shift: list

@app.post("/receive-json")
async def receive_data(team: str, data: ScheduleData):
    """
    JSON 데이터를 받아 서버 측에 임시 저장합니다.
    실제 운용 시 파일 또는 DB에 저장하고,
    에러 처리 로직을 추가하는 것을 권장합니다.
    """
    # team별로 해당 데이터를 저장 (메모리)
    stored_data[team] = data.dict()
    return {"detail": f"데이터가 저장되었습니다: {team} - {data.date}"}

@app.get("/get-schedule")
async def get_schedule(team: str):
    """
    저장된 JSON 데이터를 팀 단위로 조회합니다.
    """
    if team not in stored_data:
        raise HTTPException(status_code=404, detail="데이터 없음")
    return {"data": stored_data[team]}

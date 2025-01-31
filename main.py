from fastapi import FastAPI
from pydantic import BaseModel
import os
import json

app = FastAPI()

# 데이터 모델 정의
class ScheduleData(BaseModel):
    date: str
    day_shift: list
    night_shift: list
    vacation_shift: list

@app.get("/")
def root():
    return {"message": "Hello, this is the FastAPI server!"}

@app.get("/get-schedule", response_model=ScheduleData)
def get_schedule(team: str, date: str):
    # JSON 파일 경로 설정
    json_file_path = os.path.join("team_today_schedules", team, date[:7], f"{date}_schedule.json")
    
    if not os.path.exists(json_file_path):
        return {"date": date, "day_shift": [], "night_shift": [], "vacation_shift": []}
    
    with open(json_file_path, "r", encoding="utf-8") as f:
        schedule_data = json.load(f)
    
    return schedule_data

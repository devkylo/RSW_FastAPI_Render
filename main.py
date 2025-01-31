from fastapi import FastAPI, Query, HTTPException
from typing import Optional
import os
import json

app = FastAPI()

# JSON 파일 경로 생성 함수
def get_json_file_path(date: str, team: str) -> str:
    today_schedules_root_dir = "team_today_schedules"
    today_team_folder_path = os.path.join(today_schedules_root_dir, team)
    month_folder = os.path.join(today_team_folder_path, date[:7])
    json_file_path = os.path.join(month_folder, f"{date}_schedule.json")
    return json_file_path

# JSON 데이터 로드 함수
def load_json_data(file_path: str):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return None

# 날짜 형식 검증 함수 (간단한 유효성 체크)
def validate_date_format(date_str: str) -> bool:
    try:
        from datetime import datetime
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# API 엔드포인트 정의
@app.get("/get-schedule")
async def get_schedule(team: str = Query(...), date: str = Query(...)):
    # 날짜 형식 검증
    if not validate_date_format(date):
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다. 'YYYY-MM-DD' 형식이어야 합니다.")
    
    # JSON 파일 경로 생성
    json_file_path = get_json_file_path(date, team)
    
    # JSON 데이터 로드
    schedule_data = load_json_data(json_file_path)
    
    if schedule_data:
        return {"data": schedule_data}
    else:
        raise HTTPException(status_code=404, detail=f"{date} ({team})에 해당하는 데이터를 찾을 수 없습니다.")

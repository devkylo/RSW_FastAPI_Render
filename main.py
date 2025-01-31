from fastapi import FastAPI, Query, HTTPException
from typing import Optional
import os, json, subprocess
from datetime import datetime

app = FastAPI()
REPO_PATH = os.path.abspath(".")

def pull_specific_file(file_path: str):
    ...

@app.get("/get-schedule")
def get_schedule(
    team: Optional[str] = Query(None),
    date: Optional[str] = Query(None)
):
    if not team or not date:
        raise HTTPException(status_code=400, detail="team과 date를 모두 입력해야 합니다.")

    # 날짜 형식 유효성 확인
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다. 'YYYY-MM-DD' 형식으로 전달하세요.")

    json_file_path = os.path.join("team_today_schedules", team, date[:7], f"{date}_schedule.json")
    absolute_json_path = os.path.join(REPO_PATH, json_file_path)

    if not os.path.exists(absolute_json_path):
        pull_specific_file(json_file_path)

    if not os.path.exists(absolute_json_path):
        return {"date": date, "day_shift": [], "night_shift": [], "vacation_shift": []}

    with open(absolute_json_path, "r", encoding="utf-8") as f:
        schedule_data = json.load(f)

    return schedule_data

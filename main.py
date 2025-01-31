from fastapi import FastAPI, Query
from typing import Optional
import os
import json
import subprocess

app = FastAPI()

def pull_specific_file(file_path):
    try:
        subprocess.run(["git", "fetch", "origin"], check=True)
        subprocess.run(["git", "checkout", f"origin/main -- {file_path}"], check=True)
        print(f"✅ {file_path} 파일이 성공적으로 동기화되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 명령어 실행 중 오류 발생: {e}")

@app.get("/get-schedule")
def get_schedule(
    team: Optional[str] = Query(None),
    date: Optional[str] = Query(None)
):
    if not team or not date:
        return {"message": "team과 date를 모두 입력해야 합니다."}

    json_file_path = os.path.join("team_today_schedules", team, date[:7], f"{date}_schedule.json")
    if not os.path.exists(json_file_path):
        pull_specific_file(json_file_path)

    if not os.path.exists(json_file_path):
        return {"date": date, "day_shift": [], "night_shift": [], "vacation_shift": []}

    with open(json_file_path, "r", encoding="utf-8") as f:
        schedule_data = json.load(f)
    return schedule_data

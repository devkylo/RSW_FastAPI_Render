import os
import json
import subprocess
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ScheduleData(BaseModel):
    date: str
    day_shift: list
    night_shift: list
    vacation_shift: list

def pull_specific_file(file_path):
    try:
        subprocess.run(["git", "fetch", "origin"], check=True)
        subprocess.run(["git", "checkout", f"origin/main -- {file_path}"], check=True)
        print(f"✅ {file_path} 파일이 성공적으로 동기화되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 명령어 실행 중 오류 발생: {e}")

@app.get("/")
def root():
    return {"message": "Hello, this is the FastAPI server!"}

@app.get("/get-schedule", response_model=ScheduleData)
def get_schedule(team: str, date: str):
    json_file_path = os.path.join("team_today_schedules", team, date[:7], f"{date}_schedule.json")
    print(f"JSON 파일 경로: {json_file_path}")

    # JSON 파일이 없으면 Git에서 최신 파일을 pull 시도
    if not os.path.exists(json_file_path):
        print("JSON 파일이 존재하지 않습니다. Git에서 최신 파일을 가져옵니다.")
        pull_specific_file(json_file_path)

    # 다시 확인했는데도 없으면 빈 데이터 반환
    if not os.path.exists(json_file_path):
        print("최신 파일을 가져와도 JSON 파일이 없으므로 기본값을 반환합니다.")
        return {"date": date, "day_shift": [], "night_shift": [], "vacation_shift": []}

    with open(json_file_path, "r", encoding="utf-8") as f:
        schedule_data = json.load(f)

    return schedule_data

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
    return {"message":"Hello, this is the FastAPI server!"}

@app.get("/get-schedule", response_model=ScheduleData)
def get_schedule(team: str, date: str):
    json_file_path = os.path.join("team_today_schedules", team, date[:7], f"{date}_schedule.json")
    print(f"JSON 파일 경로: {json_file_path}")
    
    if not os.path.exists(json_file_path):
        print("❌ JSON 파일이 존재하지 않습니다.")
        return {"date": date, "day_shift": [], "night_shift": [], "vacation_shift": []}
    
    with open(json_file_path, "r", encoding="utf-8") as f:
        schedule_data = json.load(f)
    
    return schedule_data

def pull_specific_file(file_path):
    """
    원격 Git 저장소에서 특정 파일을 가져옵니다.
    """
    try:
        subprocess.run(["git", "fetch", "origin"], check=True)
        subprocess.run(["git", "checkout", f"origin/main -- {file_path}"], check=True)
        print(f"✅ {file_path} 파일이 성공적으로 동기화되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 명령어 실행 중 오류 발생: {e}")

@app.get("/get-schedule")
def get_schedule(team: str, date: str):
    # JSON 파일 경로 설정
    json_file_path = os.path.join("team_today_schedules", team, date[:7], f"{date}_schedule.json")

    # JSON 파일이 없으면 Git에서 Pull 시도
    if not os.path.exists(json_file_path):
        pull_specific_file(json_file_path)

    # JSON 데이터 반환 (파일이 존재하지 않으면 기본값 반환)
    if not os.path.exists(json_file_path):
        return {"date": date, "day_shift": [], "night_shift": [], "vacation_shift": []}

    with open(json_file_path, "r", encoding="utf-8") as f:
        schedule_data = json.load(f)

    return schedule_data

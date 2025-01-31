from fastapi import FastAPI, Query
from typing import Optional
import os
import json
import subprocess

app = FastAPI()

# Git 저장소가 있는 디렉터리(예: /home/render/app). 적절히 변경하세요.
REPO_PATH = os.path.abspath(".")

def pull_specific_file(file_path):
    full_path = os.path.join(REPO_PATH, file_path)
    try:
        # 1) 원격에서 최신 내용 가져오기
        fetch_result = subprocess.run(
            ["git", "fetch", "origin"],
            cwd=REPO_PATH,
            check=True,
            capture_output=True,
            text=True
        )
        print("fetch stdout:", fetch_result.stdout)
        print("fetch stderr:", fetch_result.stderr)

        # 2) 특정 파일만 origin/main 브랜치 버전으로 체크아웃
        checkout_result = subprocess.run(
            ["git", "checkout", "origin/main", "--", full_path],
            cwd=REPO_PATH,
            check=True,
            capture_output=True,
            text=True
        )
        print("checkout stdout:", checkout_result.stdout)
        print("checkout stderr:", checkout_result.stderr)

        print(f"✅ {file_path} 파일이 성공적으로 동기화되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 명령어 실행 중 오류 발생: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")

@app.get("/get-schedule")
def get_schedule(
    team: Optional[str] = Query(None),
    date: Optional[str] = Query(None)
):
    if not team or not date:
        return {"message": "team과 date를 모두 입력해야 합니다."}

    # JSON 파일 경로
    json_file_path = os.path.join("team_today_schedules", team, date[:7], f"{date}_schedule.json")

    # 파일이 없으면 원격에서 가져오기 시도
    if not os.path.exists(os.path.join(REPO_PATH, json_file_path)):
        pull_specific_file(json_file_path)

    # 다시 확인
    target_json = os.path.join(REPO_PATH, json_file_path)
    if not os.path.exists(target_json):
        # 파일이 없으면 기본 빈 데이터 반환
        return {
            "date": date,
            "day_shift": [],
            "night_shift": [],
            "vacation_shift": []
        }

    with open(target_json, "r", encoding="utf-8") as f:
        schedule_data = json.load(f)
    return schedule_data

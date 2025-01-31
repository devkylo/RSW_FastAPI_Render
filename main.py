from fastapi import FastAPI, Query
from typing import Optional
import os
import json
import subprocess
from datetime import datetime
from datetime import datetime

app = FastAPI()

# --------------------------------------------------------------------------
# 1) GitHub 저장소 연동 (파일 동기화 함수)
# --------------------------------------------------------------------------
# 예: Render 서버에서 /home/render/app 경로에 repo가 있다고 가정하면,
# 아래 REPO_PATH = os.path.abspath(".")는 현재 디렉토리를 기준으로 잡는다.
REPO_PATH = os.path.abspath(".")

def pull_specific_file(file_path: str):
    """
    GitHub에서 origin/main 브랜치의 특정 파일만 가져온다.
    1) git fetch origin
    2) git checkout origin/main -- file_path
    """
    full_path = os.path.join(REPO_PATH, file_path)

    try:
        # 최신 내용 먼저 가져오기
        fetch_result = subprocess.run(
            ["git", "fetch", "origin"],
            cwd=REPO_PATH,
            check=True,
            capture_output=True,
            text=True
        )
        print("fetch stdout:", fetch_result.stdout)
        print("fetch stderr:", fetch_result.stderr)

        # 특정 파일만 origin/main 기준으로 체크아웃
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

# --------------------------------------------------------------------------
# 2) /get-schedule 엔드포인트
# --------------------------------------------------------------------------
@app.get("/get-schedule")
def get_schedule(
    team: Optional[str] = Query(None),
    date: Optional[str] = Query(None)
):
    """
    /get-schedule?team=예시팀&date=YYYY-MM-DD
    요청 시, team_today_schedules/TEAM/YYYY-MM/ 아래의 date_schedule.json을 로드 후 반환한다.
    파일이 없으면 GitHub 저장소에서 동기화 시도 후 재확인한다.
    """
    if not team or not date:
        return {"message": "team과 date를 모두 입력해야 합니다."}

    # team, date 형식에 맞춰 JSON 파일 경로를 구성
    # 예: team_today_schedules/관제SO팀/2025-01/2025-01-31_schedule.json
    json_file_path = os.path.join(
        "team_today_schedules", team, date[:7], f"{date}_schedule.json"
    )
    absolute_json_path = os.path.join(REPO_PATH, json_file_path)

    # 파일이 미리 없다면 GitHub에서 가져오기 시도
    if not os.path.exists(absolute_json_path):
        pull_specific_file(json_file_path)

    # 동기화 후에도 없다면 빈 데이터를 반환
    if not os.path.exists(absolute_json_path):
        return {
            "date": date,
            "day_shift": [],
            "night_shift": [],
            "vacation_shift": []
        }

    # 파일 존재 시 로드
    with open(absolute_json_path, "r", encoding="utf-8") as f:
        schedule_data = json.load(f)

    return schedule_data

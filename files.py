import json
import os

DATA_FILE = 'data.json'

#채널에 교육청 코드 & 학교 코드 등록 (json에 저장장)
async def saveIds(channel_id: int, office_of_education_code: str, school_code: str):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r+') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    data[str(channel_id)] = {"office_of_education_code" : office_of_education_code, "school_code" : school_code}

    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

#채널에 등록된 교육청 코드 & 학교 코드 불러오기
async def loadIds():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

#채널에 등록된 교육청 코드 & 학교 코드 삭제
async def deleteIds(channel_id):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r+') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
    else:
        return False

    if str(channel_id) in data:
        del data[str(channel_id)]
        with open(DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    return False
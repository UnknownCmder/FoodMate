#중요한 변수들
token = 0 #디스코드 봇 토큰
NEIS_API_KEY = '' # NEIS API 키

# 파일에서 읽어오기  
def get_important_value(file_path):  
    with open(file_path, 'r') as file:  
        return file.read().strip()  # 불필요한 공백을 제거
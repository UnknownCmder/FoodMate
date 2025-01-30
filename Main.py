import discord
from discord import app_commands
from discord.ext import commands  
import requests

# 토큰을 파일에서 읽어오기  
def get_token(file_path):  
    with open(file_path, 'r') as file:  
        return file.read().strip()  # 불필요한 공백을 제거  

# 토큰 파일 경로  
token_file_path = 'token.txt'  
token = get_token(token_file_path)  

# Bot 객체 생성  
bot = commands.Bot(command_prefix="!", intents= discord.Intents.all()) #접두사 '!' or '/'

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("테스트중"))



#테스트
@bot.tree.command(name= "hello", description= "welcome")
async def hello(ctx: discord.Interaction):  
    await ctx.response.send_message(f'Hello!')
    await ctx.followup.send("hi")


NEIS_API_KEY = '2ba1e0e538ba4082984d45933c3e015e' # NEIS API 키
ATPT_OFCDC_SC_CODE = 'S10' # 교육청 코드(경남)
SD_SCHUL_CODE = 9010050 # 학교 코드(명신고)
MMEAL_SC_CODE = 2 # 급식 종류 코드(중식)

@bot.tree.command(name="school_meals", description="Get information about school meals")
async def school_meals(ctx: discord.Interaction):
    MLSV_YMD = 20240405 # 날짜(YYYYMMDD) / 2025년 3월 5일(나중에는 오늘 날짜로 변경)

    api_url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={NEIS_API_KEY}&Type=json&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}&SD_SCHUL_CODE={SD_SCHUL_CODE}&MMEAL_SC_CODE={MMEAL_SC_CODE}&MLSV_YMD={MLSV_YMD}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
            #await ctx.response.send_message(f'School meals: {meals_info}')
        print(data)
        if 'mealServiceDietInfo' in data:
            meals_info = data['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
            meals_info = meals_info.replace('<br/>', '\n')
            await ctx.response.send_message(f'<학교 급식(중식)>\n{meals_info}')
        else:
            await ctx.response.send_message(f'No meal information available')
    else:
        await ctx.response.send_message(f'Failed to retrieve information')


# 봇 실행  
bot.run(token)  # 'your_token_here'를 실제 봇 토큰으로 교체

import discord
from discord import app_commands
from discord.ext import commands, tasks
import requests
from datetime import datetime

import MealInfo as mi
import files as f

import importentValue as iv

#중요한 값 초기화
iv.token = iv.get_important_value('token.txt')
iv.NEIS_API_KEY = iv.get_important_value('NEIS_API_KEY.txt')

# Bot 객체 생성  
bot = commands.Bot(command_prefix='/', intents= discord.Intents.all()) #접두사  '/'

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("급식메뉴 전파하는 중"))
    alertMealInfo.start()

#7시마다 등록된 학교 급식 정보 알림림
@tasks.loop(seconds=1)
async def alertMealInfo():
    now = datetime.now()
    current_date = now.strftime("%Y%m%d")
    current_time = now.strftime("%H:%M:%S")
    if current_time == "16:26:00":
        try:
            codes = await f.loadIds()
            for channel_id in codes:
                code = codes[channel_id]
                channel = bot.get_channel(int(channel_id))
                embed = await mi.getMealInfo(code["office_of_education_code"], code["school_code"], current_date)
                await channel.send(embed= embed)
        except:
            print("none of json file")

#도움말 명령어
@bot.tree.command(name= "help", description="명령어 사용법법")
async def help(ctx: discord.Interaction):
    embed = discord.Embed(title="도움말", description="", color=0xff0000)
    embed.add_field(name="/schoolmealinfo [교육청 코드] [학교 코드]", value="학교 급식 정보를 확인합니다", inline=False)
    embed.add_field(name="/register [교육청 코드] [학교 코드]", value="현재 채널에서 7시마다 급식 정보가 나오게 합니다\n[정확도 높음] (채널 1개당 1 학교)", inline=False)
    embed.add_field(name="/registerschoolname [학교 이름]", value="현재 채널에서 7시마다 급식 정보가 나오게 합니다\n[정확도 낮음] (채널 1개당 1 학교 / 같은 이름의 학교가 존재할 경우 의도와 다른 학교가 등록될 수 있음)", inline=False)
    embed.add_field(name="/unregister", value="더 이상 7시마다 급식 정보가 나오지 않게 합니다", inline=False)
    embed.add_field(name="/ping", value="봇의 핑을 확인합니다", inline=False)

    embed.add_field(name="", value="\n", inline=False)

    embed.add_field(name="교육청 & 학교 코드 찾기", value="1. 아래 링크 클릭 후 sheet에서 \"시도교육청코드\"와 \"학교명\"만 입력 후 검색\n2. 검색 결과로 나온 시드에서 \"시도교육청코드(교육청 코드)\"와 \"행정표준코드(학교 코드)\" 확인", inline=False)
    await ctx.response.send_message(embed=embed)

    channel = bot.get_channel(ctx.channel.id)
    await channel.send("링크 : https://open.neis.go.kr/portal/data/service/selectServicePage.do?page=1&sortColumn=&sortDirection=&infId=OPEN17320190722180924242823&infSeq=1&searchWord=%EA%B8%89%EC%8B%9D")

#급식 정보 명령어
@bot.tree.command(name= "schoolmealinfo", description="급식 정보 확인 명령어어")
@app_commands.describe(office_of_education_code="교육청 코드", school_code="학교 코드")
async def schoolMealInfo(ctx: discord.Interaction, office_of_education_code: str, school_code: str):
    now = datetime.now()
    current_date = now.strftime("%Y%m%d")

    embed = await mi.getMealInfo(office_of_education_code, school_code, current_date)
    if embed == False:
        await ctx.response.send_message("급식정보가 불러와지지 않습니다. (학교 코드나 교육청 코드를 확인해주세요)")
    else:
        await ctx.response.send_message(embed=embed)

#학교 등록 명령어 (교육청 코드와 학교 코드로)
@bot.tree.command(name= "register", description="원하는 학교 등록하는 명령어")
@app_commands.describe(office_of_education_code="교육청 코드", school_code="학교 코드")
async def register(ctx: discord.Interaction, office_of_education_code: str, school_code: str):
    if not ctx.user.guild_permissions.administrator:
        await ctx.response.send_message("관리자 권한이 있어야 이 명령어를 사용할 수 있습니다.", ephemeral=True)
        return
    
    channel_id = ctx.channel.id

    apiUrlForTitle = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={iv.NEIS_API_KEY}&Type=json&ATPT_OFCDC_SC_CODE={office_of_education_code}&SD_SCHUL_CODE={school_code}"
    responseForTitle = requests.get(apiUrlForTitle)
    dataForTitle = responseForTitle.json()

    if 'RESULT' not in dataForTitle: #급식정보가 불러와지면
        SCHOOL_NAME = dataForTitle['mealServiceDietInfo'][1]['row'][0]['SCHUL_NM']
        await f.saveIds(channel_id, office_of_education_code, school_code)
        await ctx.response.send_message("등록되었습니다! (등록된 학교 : " + SCHOOL_NAME + ")")
    else: #급식정보가 불러와지지 않으면
        await ctx.response.send_message("급식정보가 불러와지지 않습니다. (학교 코드나 교육청 코드를 확인해주세요)")

#학교 등록 명령어 (학교 이름으로 / 정확도 낮음)
@bot.tree.command(name="registerschoolname", description="학교 이름으로 등록하는 명령어")
@app_commands.describe(school_name="학교 이름")
async def registerschoolname(ctx: discord.Interaction, school_name: str):
    if not ctx.user.guild_permissions.administrator:
        await ctx.response.send_message("관리자 권한이 있어야 이 명령어를 사용할 수 있습니다.", ephemeral=True)
        return

    channel_id = ctx.channel.id

    office_of_education_code = ""
    school_code = 0

    getCodeAPI = f"https://open.neis.go.kr/hub/schoolInfo?KEY={iv.NEIS_API_KEY}&Type=json&pIndex=1&SCHUL_NM={school_name}"
    responseForSchool = requests.get(getCodeAPI)
    dataForSchool = responseForSchool.json()
    if 'RESULT' not in dataForSchool:
        office_of_education_code = dataForSchool['schoolInfo'][1]['row'][0]['ATPT_OFCDC_SC_CODE']
        school_code = dataForSchool['schoolInfo'][1]['row'][0]['SD_SCHUL_CODE']
    else:
        await ctx.response.send_message("존재하지 않는 학교이거나 OPEN API 오류가 발생했습니다.")
        return


    apiUrlForTitle = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={iv.NEIS_API_KEY}&Type=json&ATPT_OFCDC_SC_CODE={office_of_education_code}&SD_SCHUL_CODE={school_code}"
    responseForTitle = requests.get(apiUrlForTitle)
    dataForTitle = responseForTitle.json()

    if 'RESULT' not in dataForTitle:  # 급식정보가 불러와지면
        SCHOOL_NAME = dataForTitle['mealServiceDietInfo'][1]['row'][0]['SCHUL_NM']
        await f.saveIds(channel_id, office_of_education_code, school_code)
        await ctx.response.send_message("등록되었습니다! (등록된 학교 : " + SCHOOL_NAME + ")")
    else:  # 급식정보가 불러와지지 않으면
        await ctx.response.send_message("급식정보가 불러와지지 않습니다. (학교 코드나 교육청 코드를 확인해주세요)")

#학교 등록 해제 명령어
@bot.tree.command(name= "unregister", description="그 채널에 등록되어있는 학교 해제하는 명령어")
async def unregister(ctx: discord.Interaction):
    if not ctx.user.guild_permissions.administrator:
        await ctx.response.send_message("관리자 권한이 있어야 이 명령어를 사용할 수 있습니다.", ephemeral=True)
        return
    
    channel_id = ctx.channel.id
    result = await f.deleteIds(channel_id)
    if result:
        await ctx.response.send_message("등록이 취소되었습니다")
    else:
        await ctx.response.send_message("이 채널에는 등록되어있는 학교가 없습니다")

#핑 확인 명령어
@bot.tree.command(name= "ping", description="봇의 핑 확인 명령어")
async def ping(ctx: discord.Interaction):
    await ctx.response.send_message(f'Ping : {round(bot.latency * 1000)}ms')


# 봇 실행  
bot.run(iv.token)  # 'your_token_here'를 실제 봇 토큰으로 교체

import discord
import requests
import importentValue as iv

#급식 정보 가져오기
async def getMealInfo(office_of_education_code: str, school_code: str, day: int):
    apiUrlForTitle = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={iv.NEIS_API_KEY}&Type=json&ATPT_OFCDC_SC_CODE={office_of_education_code}&SD_SCHUL_CODE={school_code}"
    responseForTitle = requests.get(apiUrlForTitle)
    dataForTitle = responseForTitle.json()

    if 'RESULT' in dataForTitle: return False #급식정보가 불러와지지 않으면 False 반환

    SCHOOL_NAME = dataForTitle['mealServiceDietInfo'][1]['row'][0]['SCHUL_NM']
    embed = discord.Embed(title=f"<{SCHOOL_NAME} 급식  ({day})>", color=0xff0000)

    for mealTypeNum in range(1, 4):  # 1: 조식, 2: 중식, 3: 석식
        api_url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={iv.NEIS_API_KEY}&Type=json&ATPT_OFCDC_SC_CODE={office_of_education_code}&SD_SCHUL_CODE={school_code}&MMEAL_SC_CODE={mealTypeNum}&MLSV_YMD={day}"
        response = requests.get(api_url)

        mealTypeName = ""
        if mealTypeNum == 1: mealTypeName = "조식"
        elif mealTypeNum == 2: mealTypeName = "중식"
        elif mealTypeNum == 3: mealTypeName = "석식"
            
        if response.status_code == 200:
            data = response.json()

            if 'mealServiceDietInfo' in data: #급식정보가 불러와지면
                meals_info = data['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
                meals_info = meals_info.replace('<br/>', '\n')

                embed.add_field(name=mealTypeName, value=meals_info, inline=False)
            else: #급식정보가 불러와지지 않으면
                embed.add_field(name=mealTypeName, value="없음", inline=False)
        else:
            embed.add_field(name='', value= '알 수 없는 오류가 발생했습니다')
            return embed
    return embed
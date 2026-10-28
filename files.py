import sqlite3

DATABASE_FILE = "database.db"


def _connect():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def _initialize_database():
    with _connect() as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS school (
                channel_id INTEGER PRIMARY KEY,
                office_of_education_code TEXT NOT NULL,
                school_code INTEGER NOT NULL
            )"""
        )

_initialize_database()


# 채널에 교육청 코드와 학교 코드를 등록
async def saveIds(channel_id: int, office_of_education_code: str, school_code: str):
    with _connect() as connection:
        connection.execute(
            """INSERT INTO school (channel_id, office_of_education_code, school_code)
                VALUES (?, ?, ?)
                ON CONFLICT(channel_id) DO UPDATE SET
                office_of_education_code = excluded.office_of_education_code,
                school_code = excluded.school_code""",
            (channel_id, office_of_education_code, int(school_code)),
        )


# 채널에 등록된 교육청 코드와 학교 코드를 불러오기
async def loadIds(bot=None):
    with _connect() as connection:
        rows = connection.execute(
            "SELECT channel_id, office_of_education_code, school_code FROM school"
        ).fetchall()

    ids = {}
    for row in rows:
        channel_id = int(row["channel_id"])

        if bot is not None:
            # 캐시에서 찾을 수 없는 경우에만 API로 확인한다.
            # NotFound 응답을 받은 경우에만 해당 등록을 삭제한다.
            if bot.get_channel(channel_id) is None:
                try:
                    await bot.fetch_channel(channel_id)
                except Exception as error:
                    import discord

                    if isinstance(error, discord.NotFound):
                        await deleteIds(channel_id)
                        continue
                    print(f"채널 ID {channel_id} 확인 중 오류 발생: {error}")
                    raise

        ids[str(channel_id)] = {
            "office_of_education_code": row["office_of_education_code"],
            "school_code": int(row["school_code"]),
        }

    return ids


# 채널에 등록된 교육청 코드와 학교 코드를 삭제
async def deleteIds(channel_id):
    with _connect() as connection:
        cursor = connection.execute(
            "DELETE FROM school WHERE channel_id = ?", (channel_id,)
        )
    return cursor.rowcount > 0


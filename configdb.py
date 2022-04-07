from datetime import datetime, time, date
import asyncio
import aiomysql

USER_DATA = {}
loop = asyncio.get_event_loop()
USER_ID = dict()
USER_PACK = ['STANDART', 'PREMIUM']


async def sql_add_command(USER_DATA5, USER_ID, USER_PACK):
    USER_DATA5['user_id'] = USER_ID['id']
    USER_DATA5['user_pack'] = USER_PACK
    conn = await aiomysql.connect(host="localhost", user="test", password="1234", db="testdb", loop=loop)
    cur = await conn.cursor()
    await cur.execute("""INSERT INTO table1 (Name,Inst_Name,Phone,Date,time,id_User,Packet) 
    VALUES  (%s,%s,%s,%s,%s,%s,%s)""", tuple(USER_DATA5.values()))
    await conn.commit()
    conn.close()


async def sql_replace_commands(USER_DATA):
    conn1 = await aiomysql.connect(host="localhost", user="test", password="1234", db="testdb", loop=loop)
    cur = await conn1.cursor()
    data = USER_DATA['date']
    data_replace = datetime.strptime(data, '%d.%m.%Y').date()
    await cur.execute("""UPDATE datareg SET DATAREGcol='1' WHERE idDATAREG = '%s' """ % data_replace)
    await conn1.commit()
    conn1.close()


async def sql_select_freedate(User_text):
    conn2 = await aiomysql.connect(host="localhost", user="test", password="1234", db="testdb", loop=loop)
    cur = await conn2.cursor()
    await cur.execute("""SELECT idDATAREG FROM datareg WHERE idDATAREG > CURRENT_DATE() and DATAREGcol < 1 limit 4;""")
    r = await cur.fetchall()
    result_date = []
    for row in r:
        date = row[0].strftime('%d.%m.%Y')
        result_date.append(date)
    await cur.close()
    conn2.close()
    return result_date


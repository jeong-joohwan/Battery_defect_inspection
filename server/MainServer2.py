import asyncio
from random import random
import sqlite3 as sqlite
import time

_host = '192.168.0.118'
_port = 9000

clients = []
async def handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):

    no = 0
    IS_IMG = False
    client = {
        'reader' : reader,
        'writer' : writer
    }
    clients.append(client)
    print('Con One')
    StringImg = b''
    Model=''
    Date=''
    while True:
        if IS_IMG == True:
            while True:
                try:
                    data : bytes = await reader.read(1024)
                    if not data:
                        break
                    StringImg += data
                    if b'<eof>' in StringImg:
                        IS_IMG = False
                        for i in clients:
                            if i==client:
                                continue
                            i['writer'].write(StringImg)
                            await i['writer'].drain()
                        
                        StringImg = b''
                        break

                        #StringImg = StringImg.replace(b'<eof>',b'')
                        #StringImg = StringImg.replace(b'<sof>',b'')
                        #저장용으로 바꿀 공간=
                except:
                    print('image error')
        else:
            data: bytes = await reader.read(1024)
            if data != None:
                if b'<sof>' in data:
                    StringImg += data
                    IS_IMG = True
                    data = b''
                    continue
                peername = writer.get_extra_info('peername')
                print(f"[S] received: {len(data)} bytes from {peername}")

                cli_mes = data.decode('UTF-8') #client에서 보내준 data를 decode
                print(cli_mes)
                if cli_mes.startswith('TOC'): # Rasp에서 C#으로 보내줄 data 서버에 출력
                    print("[Rasp_Client] message: {}".format(cli_mes[3:]))

                elif cli_mes.startswith('TOR'): # C#에서 Rasp로 보내줄 data 서버에 출력
                    print("[C#_Client] message: {}".format(cli_mes[3:]))

                no+=1 
                #해당 index에 값을 넣어주기 위해 추가

                conn = sqlite.connect("DB.db")  # DB파일에 연결
                c = conn.cursor()  # 커서획득 
                if cli_mes.startswith('TEMPS'):
                    sendf = cli_mes.encode('UTF-8')
                    writer.write(sendf)
                    await writer.drain()
                if cli_mes.startswith('TORDatesStand'):
                    
                    payload = cli_mes.encode('UTF-8')
                    for i in clients:
                        await asyncio.sleep(0.3)
                        if i==client:
                            continue
                        print(payload)
                        i['writer'].write(payload) 
                        await i['writer'].drain()

                        print("[Server] sent: {}".format(cli_mes))

                    insert_cli_mes = cli_mes.replace('TORDatesStand,','').split(',')
                    index_cli_mes = insert_cli_mes[1]
                    Model = insert_cli_mes[0]
                    Date = insert_cli_mes[4]

                    print(insert_cli_mes)
                    for no in range(1, int(index_cli_mes)+1): #로트 크기만큼 Unit_date 값 넣어주기
                        c.execute('''INSERT INTO Unit_factory(Model, Unit_no, Unit_Date)
                                    VALUES('%s', %s, %s)''' % (Model, no, Date))

                    c.execute('''INSERT INTO Result(Model, hStandard, vStandard, ResultDate)
                                VALUES('%s', %s, %s, %s)''' % (insert_cli_mes[0], insert_cli_mes[2], insert_cli_mes[3], Date ) )

                elif cli_mes.startswith('TOCUnit_no'):
                    insert_cli_mes = cli_mes.replace('TOC','').split(',')

                    for k in insert_cli_mes:
                        k = 'TOC'+k
                        payload = k.encode('UTF-8')
                        for i in clients:
                            i['writer'].write(payload)
                            await i['writer'].drain()
                            time.sleep(0.1)
                    print("[Server] sent: {}".format(cli_mes))
                    print(insert_cli_mes)
                    #DB파일에 저장

                    c.execute('''UPDATE Unit_factory SET  
                                Unit_horizon = %s, Unit_vertical = %s, 
                                Unit_hpass = %s, Unit_vpass = %s,
                                Unit_temp = %s
                                WHERE Unit_no = %s and Unit_date = %s'''
                                % (insert_cli_mes[1][12:],insert_cli_mes[2][13:],
                                insert_cli_mes[3][10:],insert_cli_mes[4][10:],
                                insert_cli_mes[5][4:],
                                insert_cli_mes[0][7:],insert_cli_mes[6][9:]) )

                elif cli_mes.startswith('TOCAQL_hpass'):
                    print("[Server] sent1: {}".format(cli_mes))
                    thenTOC = cli_mes.replace('TOC','Last')
                    print(thenTOC)
                    ttl = thenTOC.encode('UTF-8')
                    for i in clients:
                        if i==client:
                            continue
                        i['writer'].write(ttl)
                        await i['writer'].drain()
                    
                    insert_cli_mes = cli_mes.replace('TOC','').split(',')
                    time.sleep(0.3)
                    print("[Server] sent: {}".format(cli_mes))
                    try:
                        c.execute('''UPDATE Result SET
                                AQL_hpass = %s, AQL_vpass = %s,
                                hSigma = %s, vSigma = %s,
                                hMean = %s, vMean = %s,
                                hCp = %s, vCp = %s,
                                hunpassCount = %s, vunpassCount = %s,
                                hDefectrate = %s, vDefectrate = %s,
                                Hadjust = '%s', Vadjust = '%s',
                                TotalunpassCount = %s, TotalDefectrate = %s,
                                Result_dateGap= '%s', Result_LOT = %s
                                WHERE Resultdate = %s and Model = "%s"'''
                                % (insert_cli_mes[0][9:],insert_cli_mes[1][9:], 
                                insert_cli_mes[2][6:],insert_cli_mes[3][6:],
                                insert_cli_mes[4][5:], insert_cli_mes[5][5:],
                                insert_cli_mes[6][3:], insert_cli_mes[7][3:],
                                insert_cli_mes[8][12:], insert_cli_mes[9][12:],
                                insert_cli_mes[10][11:], insert_cli_mes[11][11:],
                                insert_cli_mes[12][7:], insert_cli_mes[13][7:],
                                insert_cli_mes[14][16:], insert_cli_mes[15][15:],
                                insert_cli_mes[17][7:], insert_cli_mes[18][3:], 
                                insert_cli_mes[16][4:], insert_cli_mes[19][5:]) )
                        

                    except Exception as e:
                        print('update exception'+ e)
                    time.sleep(4)
                
                elif cli_mes.startswith('start'):
                    payload = cli_mes.encode('UTF-8')
                    for i in clients:
                        i['writer'].write(payload)
                        await writer.drain()
                    
                    print("[Server] sent: {}".format(cli_mes))
                conn.commit()  # 트랜젝션의 내용을 DB에 반영함
                conn.close()  # 커서닫기


                await asyncio.sleep(1.5) #대기

                serv_mes = 'Success'
                for i in clients:
                    i['writer'].write(serv_mes.encode('UTF-8'))
                    await writer.drain()
                #writer.write(serv_mes.encode('UTF-8'))
                #await writer.drain()
                print("[Server] sent: {}".format(serv_mes))
        IS_IMG = False
        
        

async def run_server():
    # 서버를 생성하고 실행
    print('Server Start....')
    server = await asyncio.start_server(handler, host=_host, port=_port)
    async with server:
        await server.serve_forever()


async def main():
    # await asyncio.wait([run_server(), run_client(_host, _port)])
    await asyncio.wait([run_server()])


if __name__ == "__main__":
    asyncio.run(main())
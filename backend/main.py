import os
import hashlib
import mysql.connector
from fastapi import *
from uuid import uuid4
from datetime import date
from dotenv import load_dotenv
from starlette.responses import JSONResponse, RedirectResponse
from starlette.middleware.cors import CORSMiddleware

load_dotenv()


def mysql_query(query):
    with mysql.connector.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
    ) as db:
        cursor = db.cursor(dictionary=True) #Включает возврат в виде массива словарей
        cursor.execute(query)
        sql_return_data = cursor.fetchall()
        db.commit()
    return sql_return_data or None

def get_user(token: str):
    return mysql_query(f"SELECT user, login, fio FROM usertbl WHERE token = '{token}'")


app = FastAPI()
app.add_middleware(CORSMiddleware,
               allow_origins=['*'],
               allow_headers=['*'],
               allow_methods=['*'],
               allow_credentials=True)


@app.post('/authenticate')
def authenticate(user_login = Form(), user_password = Form()):
    user = mysql_query(f"SELECT user FROM usertbl WHERE login = '{user_login}' AND password = (SELECT md5('{user_password}'))") #escape_string не нужен, делается автоматически
    if user is None:
        raise HTTPException(status_code=403, detail="Неверный логин или пароль")

    ''' Если успешно прошли проверку'''
    login_hash = hashlib.md5(str(uuid4()).encode()).hexdigest()
    mysql_query(f"UPDATE usertbl SET token = '{login_hash}' WHERE login = '{user_login}'")
    return {"token" : login_hash}


@app.get('/user-info')
def userInfo(token : str = Header(embed=True)):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")

    ''' Если успешно прошли проверку'''
    return JSONResponse(content=user[0])


@app.get('/dashboard-indicators')
def dashboardIndicators(token : str):
    result = {}

    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")


    result["totalAccept"] = mysql_query(f"SELECT COUNT(*) AS 'count' FROM te WHERE accept_stat = 1")[0]['count']
    result["totalReject"] = mysql_query(f"SELECT COUNT(*) AS 'count' FROM te WHERE reject_stat = 1")[0]['count']
    result["totalScale"] = mysql_query(f"SELECT SUM(info_primary_weighted- info_secondary_weighted) as summ FROM scale_operator INNER JOIN te ON scale_operator.staff_soid = te.staff_soid")[0]['summ']
    result["dayAccept"] = mysql_query(f"SELECT COUNT(*) AS 'count' FROM te WHERE accept_stat = 1 AND time BETWEEN '{date.today()} 00:00:00' AND '{date.today()} 23:59:59'")[0]['count']
    result["dayReject"] = mysql_query(f"SELECT COUNT(*) AS 'count' FROM te WHERE reject_stat = 1 AND time BETWEEN '{date.today()} 00:00:00' AND '{date.today()} 23:59:59'")[0]['count']
    result["dayScale"] = mysql_query(f"SELECT SUM(info_primary_weighted- info_secondary_weighted) as summ FROM scale_operator INNER JOIN te ON scale_operator.staff_soid = te.staff_soid WHERE te.time BETWEEN '{date.today()} 00:00:00' AND '{date.today()} 23:59:59'")[0]['summ']
    return JSONResponse(content=result)

import hashlib
from datetime import datetime
from http import HTTPStatus

from fastapi import *
from passlib.handlers.md5_crypt import md5_crypt
from starlette.middleware.cors import CORSMiddleware
import mysql.connector
import os
from dotenv import load_dotenv

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

def get_user(ubid: str):
    temp_ubid = hashlib.md5(ubid.encode()).hexdigest()
    return mysql_query(f"SELECT id FROM usertbl WHERE ubid = {temp_ubid}")


app = FastAPI()
app.add_middleware(CORSMiddleware,
               allow_origins=['http://127.0.0.1', 'http://localhost'],
               allow_headers=['*'],
               allow_methods=['*'],
               allow_credentials=True)


@app.post('/authenticate')
def authenticate(request : Request, user_login = Form(), user_password = Form(), ubid = Body(embed=True)):
    user = mysql_query(f"SELECT user FROM usertbl WHERE login = '{user_login}' AND password = (SELECT md5('{user_password}'))") #escape_string не нужен, делается автоматически
    if user is None:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    ''' Если успешно прошли проверку'''
    login_hash = hashlib.md5(ubid.encode()).hexdigest()
    mysql_query(f"UPDATE usertbl SET ubid = '{login_hash}' WHERE login = '{user_login}'")

@app.post('/')

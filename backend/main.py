from fastapi import *
from starlette.middleware.cors import CORSMiddleware
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def mysql_query(query):
    sql_return_data = set()
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
    return sql_return_data


app = FastAPI()
app.add_middleware(CORSMiddleware,
               allow_origins=['http://127.0.0.1', 'http://localhost'],
               allow_headers=['*'],
               allow_methods=['*'],
               allow_credentials=True)

@app.post('/authenticate')
def authenticate(user_login = Form(), user_password = Form()):
    sql = mysql_query(f"SELECT id FROM usertbl WHERE login = '{user_login}' AND password = '(SELECT MD5({user_password}))'") #escape_string не нужен, делается автоматически
    if sql
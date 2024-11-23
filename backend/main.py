import os
import hashlib

import mysql.connector
from fastapi import *
from uuid import uuid4
from datetime import date, datetime
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
    return mysql_query(f"SELECT user, login, fio FROM usertbl WHERE token = '{token}' LIMIT 1")


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
def user_info(token : str = Header(embed=True)):
    if token is not None:
        user = get_user(token)
        if user is None:
            raise HTTPException(status_code=401, detail="Клиент не авторизован")

    ''' Если успешно прошли проверку'''
    return JSONResponse(content=user[0])


@app.get('/dashboard-indicators')
def dashboard_indicators(token : str):
    result = {}

    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")


    result["totalAccept"] = mysql_query(f"SELECT COUNT(*) AS 'count' FROM te WHERE accept_stat = 1")[0]['count']
    result["totalReject"] = mysql_query(f"SELECT COUNT(*) AS 'count' FROM te WHERE reject_stat = 1")[0]['count']
    result["totalScale"] = mysql_query(f"SELECT IFNULL(SUM(info_primary_weighted-info_secondary_weighted), 0) as summ FROM scale_operator INNER JOIN te ON scale_operator.staff_soid = te.staff_soid")[0]['summ']
    result["dayAccept"] = mysql_query(f"SELECT COUNT(*) AS 'count' FROM te WHERE accept_stat = 1 AND time BETWEEN '{date.today()} 00:00:00' AND '{date.today()} 23:59:59'")[0]['count']
    result["dayReject"] = mysql_query(f"SELECT COUNT(*) AS 'count' FROM te WHERE reject_stat = 1 AND time BETWEEN '{date.today()} 00:00:00' AND '{date.today()} 23:59:59'")[0]['count']
    result["dayScale"] = mysql_query(f"SELECT IFNULL(SUM(info_primary_weighted- info_secondary_weighted), 0) as summ FROM scale_operator INNER JOIN te ON scale_operator.staff_soid = te.staff_soid WHERE te.time BETWEEN '{date.today()} 00:00:00' AND '{date.today()} 23:59:59'")[0]['summ']

    result["totalAgrofirms"] = mysql_query(f"SELECT SUM(info_primary_weighted-info_secondary_weighted) as summ, vendor_item AS vendor FROM scale_operator INNER JOIN te ON scale_operator.staff_soid = te.staff_soid GROUP BY vendor_item")
    result["dayAgrofirms"] = mysql_query(f"SELECT SUM(info_primary_weighted-info_secondary_weighted) as summ, vendor_item AS vendor FROM scale_operator INNER JOIN te ON scale_operator.staff_soid = te.staff_soid WHERE te.time BETWEEN '{date.today()} 00:00:00' AND '{date.today()} 23:59:59' GROUP BY vendor_item")

    return JSONResponse(content=result)


@app.get('/te-list')
def TE_list(token : str):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")

    result = mysql_query(f'''
    SELECT te.id_te, transport_reg_num as regnum, vendor_item as vendor, time, sugar_beet_charact as characts, destination, primary_checking_info as result FROM te 
    LEFT JOIN scale_operator ON te.staff_soid = scale_operator.staff_soid 
    LEFT JOIN distr_report ON te.id_te = distr_report.id_te 
    LEFT JOIN laborant ON te.staff_lid = laborant.staff_lid 
    WHERE reject_stat = '0' and accept_stat = '0' 
    and (distr_report.destination = 'Анализ показателей, вызвавших сомнение, в сырьевой лаборатории' or distr_report.destination is NULL or (
    info_secondary_weighted <> 0 and unload_stat = 1))
    ORDER BY time DESC
    ''')
    if result is not None:
        for elem in result:
            elem["time"] = elem["time"].strftime('%d.%m.%Y %H:%M:%S')
            elem["status"] = mysql_query(f'''
            SELECT IF (scale_operator.info_secondary_weighted != 0, 'Ожидает подтверждения', 'Прибыла в свёклопункт') AS 'result'
            FROM te LEFT JOIN scale_operator ON te.staff_soid = scale_operator.staff_soid WHERE id_te = "{elem['id_te']}"''')[0]['result']
            if mysql_query(f"SELECT id_te FROM te WHERE id_te = {elem["id_te"]} and distr_stat = '0'") is not None:
                elem["new"] = 1
    return JSONResponse(content=result)


@app.post('/add-te')
def add_te(token = Form(), vendor = Form(), regnum = Form(), characts = Form(), note = Form()):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")
    if token == "" or regnum == "" or vendor == "" or characts == "":
        raise HTTPException(status_code=422, detail="Не заполнены поля формы")

    mysql_query(f"INSERT INTO te(vendor_item, transport_reg_num, sugar_beet_charact, note) VALUES ('{vendor}', '{regnum}', '{characts}', '{note}')")
    te = mysql_query(f"SELECT id_te FROM te ORDER BY id_te DESC LIMIT 1")[0]["id_te"]
    mysql_query(f"INSERT INTO operator(accepting_data,user) VALUES ('Прибыла с свёклопункт','{user[0]["user"]}')")
    operator = mysql_query(f"SELECT staff_id FROM operator ORDER BY staff_id DESC LIMIT 1")[0]["staff_id"]
    mysql_query(f"INSERT INTO operator_te(staff_id,id_te) VALUES ('{operator}','{te}')")


@app.post('/reject-te')
def reject_te(token = Form(), reject_comment = Form(), id_te = Form()):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")
    if token == "" or reject_comment == "" or id_te == "":
        raise HTTPException(status_code=422, detail="Не заполнены поля формы")
    
    mysql_query(f"UPDATE te SET reject_stat = '1' WHERE id_te = '{id_te}'")
    mysql_query(f"INSERT INTO accepting_act(id_te,accept_info) VALUES ('{id_te}','{reject_comment}')")

@app.post('/accept-te')
def accept_te(token = Form(), accept_comment = Form(), id_te = Form()):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")
    if token == "" or accept_comment == "" or id_te == "":
        raise HTTPException(status_code=422, detail="Не заполнены поля формы")

    mysql_query(f"UPDATE te SET accept_stat = '1' WHERE id_te = '{id_te}'")
    mysql_query(f"INSERT INTO accepting_act(id_te,accept_info) VALUES ('{id_te}','{accept_comment}')")

@app.post('/distr-te')
def distr_te(token = Form(), distr_place = Form(), distr_comment = Form(), id_te = Form()):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")
    if token == "" or distr_place == "" or id_te == "":
        raise HTTPException(status_code=422, detail="Не заполнены поля формы")

    check_dest_query = mysql_query(f"SELECT destination FROM distr_report WHERE id_te = '{id_te}' ORDER by rep_id DESC LIMIT 1")
    if check_dest_query is None:
        mysql_query(f"UPDATE te SET distr_stat = '1' WHERE id_te = '{id_te}'")
        mysql_query(f"INSERT INTO distr_report(id_te,destination,note) VALUES ('{id_te}','{distr_place}','{distr_comment}')")
    else:
        mysql_query(f"UPDATE distr_report SET id_te = '{id_te}',destination = '{distr_place}', note = '{distr_comment}' WHERE id_te = '{id_te}'")


@app.get('/te-list-unchecked-lab')
def TE_list_unchecked_in_lab(token : str):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")

    result = mysql_query(f'''SELECT te.id_te, transport_reg_num as regnum 
    FROM te INNER JOIN distr_report ON te.id_te = distr_report.id_te 
    WHERE reject_stat = '0' and accept_stat = '0'
    AND (distr_report.destination = 'Анализ показателей, вызвавших сомнение, в сырьевой лаборатории' and primary_check_stat = '0'
        OR distr_report.destination = 'Взвешивание и последующий лабораторный контроль' and secondary_check_stat = '0') 
    ORDER BY time ASC''')
    return JSONResponse(content=result)

@app.post('/lab-add-result')
def add_lab_result(token = Form(), id_te = Form(), type_control = Form(), result = Form()):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")

    if token == "" or type_control == "" or result == "" or id_te == "":
        raise HTTPException(status_code=422, detail="Не заполнены поля формы")

    check_query = mysql_query(f"SELECT staff_lid, primary_check_stat, secondary_check_stat FROM te WHERE id_te = '{id_te}'")[0]
    check_dest_query = mysql_query(f"SELECT destination FROM distr_report WHERE id_te = '{id_te}' ORDER by rep_id DESC LIMIT 1")[0]

    if (check_dest_query["destination"] == "Анализ показателей, вызвавших сомнение, в сырьевой лаборатории" and type_control == "primary") or \
            (check_dest_query["destination"] == "Взвешивание и последующий лабораторный контроль" and type_control == "secondary"):
        if check_query["staff_lid"] is None:
            mysql_query(f"INSERT INTO laborant({type_control}_checking_info, user) VALUES ('{result}','{user[0]['user']}')")
            staff_lid = mysql_query(f"SELECT staff_lid FROM laborant ORDER by staff_lid DESC LIMIT 1")[0]["staff_lid"]
            mysql_query(f"UPDATE te SET staff_lid = '{staff_lid}', {type_control}_check_stat = '1' WHERE id_te = '{id_te}'")
        elif check_query[f"secondary_check_stat"] == '0':
            mysql_query(f"UPDATE te SET secondary_check_stat = '1' WHERE id_te = '{id_te}'")
            staff_lid = mysql_query(f"SELECT staff_lid FROM te WHERE id_te = '{id_te}'")[0]["staff_lid"]
            mysql_query(f"UPDATE laborant SET {type_control}_checking_info = '{result}', user_final = {user[0]["user"]} WHERE staff_lid = '{staff_lid}'")
        else:
            raise HTTPException(status_code=422, detail="Результаты данного вида контроля для ТЕ уже внесены")
    else:
        raise HTTPException(status_code=422, detail="Неверный вид контроля для распределения ТЕ")


@app.get('/lab-list')
def lab_list(token : str):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")

    result = mysql_query(f'''SELECT usertbl.user, te.id_te, primary_checking_info AS prima, secondary_checking_info AS 'secondary', transport_reg_num as regnum, destination as stat, fio, laborant.user_final FROM distr_report 
                            INNER JOIN te ON distr_report.id_te = te.id_te
                            LEFT JOIN laborant ON te.staff_lid = laborant.staff_lid
                            LEFT JOIN usertbl ON  usertbl.user = laborant.user
                            WHERE (destination = "Анализ показателей, вызвавших сомнение, в сырьевой лаборатории" OR destination = "Взвешивание и последующий лабораторный контроль")
                            AND reject_stat = '0' AND accept_stat = '0'
                            ORDER BY te.time DESC;
                            ''')
    if result is not None:
        for elem in result:
            if elem["user_final"] is not None:
                elem["user_final"] = mysql_query(f"SELECT fio FROM usertbl WHERE user = '{elem["user_final"]}'")[0]["fio"]
        return JSONResponse(content=result)

@app.get('/te-list-unweighted-scale')
def TE_list_unweighted_in_scale(token : str):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")

    result = mysql_query(f'''SELECT te.id_te, transport_reg_num as regnum 
    FROM te INNER JOIN distr_report ON te.id_te = distr_report.id_te 
    WHERE reject_stat = '0' and accept_stat = '0' AND info_secondary_weighted = 0
    AND (distr_report.destination = 'Взвешивание' OR distr_report.destination = 'Взвешивание и последующий лабораторный контроль') 
    ORDER BY time ASC''')
    return JSONResponse(content=result)


@app.post('/scale-add-result')
def add_scale_result(token = Form(), id_te = Form(), stage = Form(), result = Form()):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")

    if token == "" or stage == "" or float(result) <= 0 or id_te == "":
        raise HTTPException(status_code=422, detail="Не заполнены поля формы")

    check_query = mysql_query(f"SELECT staff_soid, primary_weighted_stat FROM te WHERE id_te = '{id_te}'")[0]
    check_dest_query = mysql_query(f"SELECT destination FROM distr_report WHERE id_te = '{id_te}' ORDER by rep_id DESC LIMIT 1")[0]
    check_scale_query = mysql_query(f"SELECT info_primary_weighted as fst, info_secondary_weighted as snd FROM scale_operator INNER JOIN te ON scale_operator.staff_soid = te.staff_soid WHERE te.id_te = '{id_te}'")

    if (check_dest_query["destination"] == "Взвешивание" or check_dest_query["destination"] == "Взвешивание и последующий лабораторный контроль") :
        if check_query["staff_soid"] is None and stage == "primary":
            mysql_query(f"INSERT INTO scale_operator(info_{stage}_weighted, user) VALUES ({float(result)},'{user[0]['user']}')")
            staff_soid = mysql_query(f"SELECT staff_soid FROM scale_operator ORDER by staff_soid DESC LIMIT 1")[0]["staff_soid"]
            mysql_query(f"UPDATE te SET staff_soid = '{staff_soid}', primary_weighted_stat = '1' WHERE id_te = '{id_te}'")
        elif check_query[f"primary_weighted_stat"] == '1' and stage == "secondary" and check_scale_query[0]["snd"] == 0 and float(result) > 0 and \
                check_scale_query[0]["fst"] > check_scale_query[0]["snd"] :
            staff_soid = mysql_query(f"SELECT staff_soid FROM te WHERE id_te = '{id_te}'")[0]["staff_soid"]
            mysql_query(f"UPDATE `scale_operator` SET info_secondary_weighted = {float(result)}, user_final = {user[0]["user"]}  WHERE staff_soid = '{staff_soid}'")
        else:
            raise HTTPException(status_code=422, detail="Результаты указанного этапа для ТЕ уже внесены")
    else:
        raise HTTPException(status_code=422, detail="Неверный этап для распределения ТЕ")

@app.get('/scale-list')
def Scale_list(token : str):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")

    result = mysql_query(f'''SELECT usertbl.user, te.id_te, info_primary_weighted as fst, info_secondary_weighted as snd, transport_reg_num as regnum, destination, fio, scale_operator.user_final FROM te 
                            LEFT JOIN distr_report ON te.id_te = distr_report.id_te
                            INNER JOIN scale_operator ON te.staff_soid = scale_operator.staff_soid
                            LEFT JOIN usertbl ON  usertbl.user = scale_operator.user
                            WHERE (destination = "Взвешивание" OR destination = "Взвешивание и последующий лабораторный контроль")
                            AND reject_stat = '0' AND accept_stat = '0' AND info_secondary_weighted = 0
                            ORDER BY te.time DESC;
                            ''')
    if result is not None:
        for elem in result:
            if elem["user_final"] is not None:
                elem["user_final"] = mysql_query(f"SELECT fio FROM usertbl WHERE user = '{elem["user_final"]}'")[0]["fio"]
        return JSONResponse(content=result)

@app.get('/unload-list')
def unload_list(token : str):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")

    result = mysql_query(f'''SELECT transport_reg_num as regnum, vendor_item FROM te
                            WHERE primary_weighted_stat = '1' and accept_stat = '0' and reject_stat = '0' and unload_stat = '0'
                            ORDER BY te.time DESC;
                            ''')
    if result is not None:
        return JSONResponse(content=result)

@app.post('/unload-add-result')
def add_unload_result(token=Form(), id_te=Form(), place=Form(), info_unloaded=Form(), unload_info = Form()):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")

    if token == "" or info_unloaded == "" or place == "" or id_te == "":
        raise HTTPException(status_code=422, detail="Не заполнены поля формы")

    check_query = mysql_query(f"SELECT staff_uoid, secondary_check_stat, primary_weighted_stat FROM te WHERE id_te = '{id_te}'")[0]
    check_dest_query = \
    mysql_query(f"SELECT destination FROM distr_report WHERE id_te = '{id_te}' ORDER by rep_id DESC LIMIT 1")[0]

    if (check_query["primary_weighted_stat"] == '1' and (check_dest_query["destination"] == "Взвешивание" or (check_dest_query[
        "destination"] == "Взвешивание и последующий лабораторный контроль" and check_query["secondary_check_stat"] == '1'))):
        if check_query["staff_uoid"] is None:
            mysql_query(f"INSERT INTO unloading_operator(info_unloaded, unload_place, user) VALUES ('{info_unloaded}','{place}',{user[0]['user']})")
            staff_uoid = mysql_query(f"SELECT staff_uoid FROM unloading_operator ORDER by staff_uoid DESC LIMIT 1")[0][
                "staff_uoid"]

            mysql_query(f"UPDATE te SET staff_uoid = '{staff_uoid}', unload_stat = '1' WHERE id_te = '{id_te}'")
            mysql_query(f"INSERT INTO unloading_report(unload_info, id_te) VALUES ('{unload_info}','{id_te}')")


        else:
            raise HTTPException(status_code=422, detail="Результаты указанного этапа для ТЕ уже внесены")
    else:
        raise HTTPException(status_code=422, detail="Невозможно разгрузить данную ТЕ. Не все этапы процесса пройдены/неверный этап для распределения ТЕ")

@app.get('/te-list-ununload')
def TE_list_ununload_in_scale(token : str):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")

    result = mysql_query(f'''SELECT te.id_te, transport_reg_num as regnum 
    FROM te 
    WHERE primary_weighted_stat = '1' and accept_stat = '0' and reject_stat = '0' and unload_stat = '0'
    ORDER BY time ASC''')
    return JSONResponse(content=result)


@app.get('/reports-list')
def TE_list_reports(token : str, date: str = None, regnum: str = None):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")


    expression = ""
    if date is not None and date != "":
        expression += f" and creating_date BETWEEN '{date} 00:00:00' AND '{date} 23:59:59.999'"
    if regnum is not None and regnum != "":
        expression += f" and transport_reg_num = '{regnum}'"

    result = mysql_query(f'''SELECT te.id_te, accepting_act.creating_date, te.transport_reg_num as regnum, vendor_item 
    FROM te 
    INNER JOIN accepting_act ON te.id_te = accepting_act.id_te
    WHERE (accept_stat = '1' or reject_stat = '1') {expression}
    ORDER BY id_te DESC''')
    if result is not None:
        for elem in result:
            elem["creating_date"] = elem["creating_date"].strftime('%d.%m.%Y %H:%M:%S')
    print(result)
    return JSONResponse(content=result)

@app.delete('/delete-te')
def delete_te(token : str, id_te : int):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")

    result = mysql_query(f'''SELECT id_te FROM te WHERE distr_stat = '0' and id_te = {id_te} ORDER BY id_te DESC''')
    if result is not None:
        mysql_query(f'''DELETE FROM te WHERE id_te = {id_te}''')


@app.get('/accepting-act')
def accepting_act(token : str, id_te: int):
    user = get_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Клиент не авторизован")

    result = mysql_query(f'''SELECT rep_id, creating_date, accept_info, transport_reg_num as regnum, vendor_item as vendor, time, te.id_te, usertbl.fio
    FROM accepting_act
    LEFT JOIN te ON accepting_act.id_te = te.id_te 
    LEFT JOIN operator_te ON te.id_te = operator_te.id_te 
    LEFT JOIN operator ON operator_te.staff_id  = operator.staff_id 
    LEFT JOIN usertbl ON operator.user  = usertbl.user 
    WHERE (accept_stat = '1' or reject_stat = '1') AND te.id_te = '{id_te}'
    ''')
    for elem in result:
        elem["creating_date"] = elem["creating_date"].strftime('%d.%m.%Y %H:%M:%S')
        elem["time"] = elem["time"].strftime('%d.%m.%Y %H:%M:%S')

    result[0]["stages"] = []
    temp = result[0]["stages"]
    temp_dict = {}

    #Сведения о регистрации
    sql = mysql_query(f'''SELECT * FROM te 
    INNER JOIN operator_te ON te.id_te = operator_te.id_te 
    INNER JOIN operator ON operator_te.staff_id = operator.staff_id
    INNER JOIN usertbl ON operator.user = usertbl.user
    WHERE te.id_te = \'{id_te}\'
    ''')
    if sql is not None:
        temp_dict["stage_name"] = "Регистрация ТЕ"
        temp_dict["staff"] = sql[0]["fio"]
        temp_dict["result"] = sql[0]["accepting_data"] + ". Состояние корнеплодов: " + sql[0]["sugar_beet_charact"]
        temp.append(temp_dict)

    temp_dict = {}

    # Сведения о распределении
    sql = mysql_query(f'''SELECT * FROM distr_report
    INNER JOIN te ON distr_report.id_te = te.id_te
    INNER JOIN operator_te ON te.id_te = operator_te.id_te 
    INNER JOIN operator ON operator_te.staff_id = operator.staff_id
    INNER JOIN usertbl ON operator.user = usertbl.user
    WHERE te.id_te =  \'{id_te}\'
        ''')

    if sql is not None:
        temp_dict["stage_name"] = "Распределение ТЕ"
        temp_dict["staff"] = sql[0]["fio"]
        temp_dict["result"] = sql[0]["destination"]
        temp.append(temp_dict)

    temp_dict = {}
    # Сведения об анализе
    sql = mysql_query(f'''SELECT * FROM laborant 
        INNER JOIN te ON laborant.staff_lid = te.staff_lid
        INNER JOIN usertbl ON laborant.user = usertbl.user
        WHERE te.id_te = \'{id_te}\'
        ''')
    sql2 = mysql_query(f'''SELECT * FROM laborant 
            INNER JOIN te ON laborant.staff_lid = te.staff_lid
            INNER JOIN usertbl ON laborant.user_final = usertbl.user
            WHERE te.id_te = \'{id_te}\'
            ''')

    if sql is not None or sql2 is not None:
        t2 = t3 = " "
        if sql2 is not None:
            t2 = sql2[0]["fio"]
            t3 = sql2[0]["secondary_checking_info"]
        temp_dict["stage_name"] = "Лабораторный контроль ТЕ"
        temp_dict["staff"] = sql[0]["fio"]  + " / " +  t2
        temp_dict["result"] = sql[0]["primary_checking_info"]  + " / " + t3
        temp.append(temp_dict)

    temp_dict = {}
    # Сведения об взвешивании
    sql = mysql_query(f'''SELECT * FROM scale_operator 
        INNER JOIN te ON scale_operator.staff_soid = te.staff_soid
        INNER JOIN usertbl ON scale_operator.user = usertbl.user
        WHERE te.id_te = \'{id_te}\'
        ''')
    sql2 = mysql_query(f'''SELECT * FROM scale_operator 
            INNER JOIN te ON scale_operator.staff_soid = te.staff_soid
            INNER JOIN usertbl ON scale_operator.user_final = usertbl.user
            WHERE te.id_te = \'{id_te}\'
            ''')

    if sql is not None or sql2 is not None:
        t2 = t3 = " "
        if sql2 is not None:
            t2 = sql2[0]["fio"]
            t3 = sql2[0]["info_secondary_weighted"]
        temp_dict["stage_name"] = "Взвешивание ТЕ"
        temp_dict["staff"] = sql[0]["fio"] + " / " + t2
        temp_dict["result"] = f"Вес брутто: {sql[0]["info_primary_weighted"]} кг. / Вес тары: {t3} кг."
        temp.append(temp_dict)

    temp_dict = {}
    # Сведения об отгрузке
    sql = mysql_query(f'''SELECT * FROM unloading_operator 
            INNER JOIN te ON unloading_operator.staff_uoid = te.staff_uoid
            INNER JOIN usertbl ON unloading_operator.user = usertbl.user
            INNER JOIN unloading_report ON te.id_te = unloading_report.id_te
            WHERE te.id_te = \'{id_te}\'
            ''')
    if sql is not None:
        temp_dict["stage_name"] = "Разрузка ТЕ"
        temp_dict["staff"] = sql[0]["fio"]
        temp_dict["result"] = sql[0]["info_unloaded"] + ". Место разгрузки: " + sql[0]["unload_place"] + ". Результат: " + sql[0]["unload_info"]
        temp.append(temp_dict)

    temp_dict = {}
    # Приёмка
    sql = mysql_query(f'''SELECT * FROM scale_operator
            RIGHT JOIN te ON scale_operator.staff_soid = te.staff_soid
            INNER JOIN operator_te ON te.id_te = operator_te.id_te 
            INNER JOIN operator ON operator_te.staff_id = operator.staff_id
            INNER JOIN usertbl ON operator.user = usertbl.user
            WHERE te.id_te = \'{id_te}\'
            ''')
    if sql is not None:
        temp_dict["stage_name"] = "Формирование акта приёмки ТЕ"
        temp_dict["staff"] = sql[0]["fio"]
        if sql[0]["accept_stat"] == '1':
            wei = float(sql[0]["info_primary_weighted"]) - float(sql[0]["info_secondary_weighted"])
            temp_dict["result"] = f"Результат: Принята. Итоговый вес: {wei} кг."
        else:
            temp_dict["result"] = "Результат: Отбракована"
        temp.append(temp_dict)

    return JSONResponse(content=result)


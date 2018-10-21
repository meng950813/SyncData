#-*-coding:utf-8-*-
import pymysql

# from helper import DBconfig as config
config = {
    "host" : "localhost",
    "port" : "3306",
    "DBname" : "nsfc",
    "user" : "cm",
    "pwd" : "chenmeng"
}

def getInsertSQL(context,dic):
    '''
    :param context: type list
    :param dic: type dict, with approve_id
    :return: list
    '''
    sql = ""
    for item in context:
        if not item[0] in dic:
            sql += '("%s","%s","%s","%s","%s","%s","%s","%s","%s"),' % tuple(item)
    if sql == "":
        return  sql
    sql =  '''insert into info_list values ''' + sql[:-1]
    return sql

def save_to_db(context):
    if context == []:
        return

    try:
        db = pymysql.connect(config['host'],config['user'],config['pwd'],config['DBname'])
    except Exception as e:
        print("connect error and the detail is : ",e)
    cursor = db.cursor()

    sql = "select approve_id from info_list where type=%s and approve_year=%s" % (context[0][-1],context[0][-2])
    try:
        cursor.execute(sql)
        dic = {str(x[0]) for x in list(cursor.fetchall())}

        sql = getInsertSQL(context,dic)

        print("sql : ",sql)

        # 需要插入
        if sql:
            cursor.execute(sql)
        else:
            print("nothing new to insert")
        db.commit()
    except Exception as e:
        # 数据库回滚
        db.rollback()
        print("opreation error : ",e)
    finally:
        db.close()

# 通过输入类型和年份获取数据
def getInfo(type,year):
    try:
        db = pymysql.connect(config['host'],config['user'],config['pwd'],config['DBname'])
    except Exception as e:
        print("connect error and the detail is : ",e)
    cursor = db.cursor()

    sql = "SELECT * from info_list where type =%s and year = %s " % (type,year)

    try:
        cursor.execute(sql)
        return list(cursor.fetchall())
    except Exception as e:
        print("getInfo,error msg: ",e)
    finally:
        db.close()

# 通过负责人名字和支持单位(可选)获取信息
def getInfoByName(name,support_unit=""):
    try:
        db = pymysql.connect(config['host'], config['user'], config['pwd'], config['DBname'])
    except Exception as e:
        print("connect error and the detail is : ", e)
    cursor = db.cursor()

    sql = "SELECT * from info_list where charge_man='%s'" % name
    if support_unit:
        sql += " and support_unit='%s'" % support_unit
    sql += " order by approve_year"
    print(sql)
    try:
        cursor.execute(sql)
        ls = list(cursor.fetchall())
        print("result : ", ls)
        return ls
    except Exception as e:
        print("getInfoByName, the error msg is : ",e)
    finally:
        db.close()

# TODO too time consuming,Low cost performance
def getUnit():
    try:
        db = pymysql.connect(config['host'], config['user'], config['pwd'], config['DBname'])
    except Exception as e:
        print("getUnit connect error : ", e)
    cursor = db.cursor()
    sql = "select support_unit from info_list group by support_unit"

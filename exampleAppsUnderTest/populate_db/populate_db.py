import MySQLdb as my
import random as rnd
import configparser

parser = configparser.ConfigParser()
parser.read("data_source_config.txt")

user = parser.get("config", "userDB")
password = parser.get("config", "passwordDB")
host = parser.get("config", "hostDB")
database = parser.get("config", "databaseName")

db = my.connect(host=host,
                user=user,
                passwd=password
                )

cursor = db.cursor()

linhas = 50000

operators = "+-*/"
db_creation_statement = "create database if not exists {}; use {};".format(database, database)

table_creation_statement = '''
create table if not exists calculations_data (
    id int auto_increment primary key,
    first_number decimal(10,2) not null,
    second_number decimal(10,2) not null,
    operator char(1) not null,
    expected_result decimal(12,4) not null
 );
''' 
cursor.execute(db_creation_statement)
cursor.execute(table_creation_statement)

for i in range(linhas):
    sql = "insert into calculations_data values (NULL, %s, %s, %s, %s)"
    val1 = str(rnd.randint(1,1000))
    val2 = str(rnd.randint(1,1000))
    oper = rnd.choice(operators)
    res = ""
    if oper == "+":
        res = str(int(val1) + int(val2))
    elif oper == "-":
        res = str(int(val1) - int(val2))
    elif oper =="*":
        res = str(int(val1) * int(val2))
    else:
        res = str(int(val1) / int(val2))
    val = (val1, val2, oper, res)
    
    cursor.execute(sql, val)

db.commit()
db.close()

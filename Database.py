import mysql.connector

conobj = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd = 'admin',
    database = 'UNOproject'
)
cur = conobj.cursor()
def Databaseinit():
    cur.execute('Create Database if not exists UNOProject')
    cur.execute('Use UNOProject')
    try:
        cur.execute('Create Table Playerdata (Serial integer NOT NULL PRIMARY KEY, Username VARCHAR(20))')
    except mysql.connector.Error as error:
        pass
    conobj.commit()
def addusername(username,clientno):
    try:
        cur.execute('Insert IGNORE into Playerdata values(%s,%s)',(clientno,username))
        print('done')
    except mysql.connector.Error as error:
        print(error)
    conobj.commit()




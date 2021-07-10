import secret
import pymysql
db = pymysql.connect(
    host="freetrainer.cryiqqx3x1ub.us-west-2.rds.amazonaws.com",
    user="sasha",
    password=secret.password
)
cursor = db.cursor()

def findDataMatch(table, column, searchText, exactMatch):
    if(exactMatch):
        sql = f"SELECT * FROM sasha_mackowiak.{table} WHERE {column}='{searchText}'"
    else:
        sql = f"SELECT * FROM sasha_mackowiak.{table} WHERE {column} LIKE '%{searchText}%'"
    return getRows(sql)


def getRows(script):
    result = []
    cursor.execute(script)
    while(True):
        row = cursor.fetchone()
        if(row == None):
            break
        # raise Exception(row)
        result.append(row)
    db.close
    return result


# cursor.execute("SELECT * FROM sasha_mackowiak.quantum_powers")
# while(True):
#     row = cursor.fetchone()
#     if row == None:
#         break;
#     print(row)
# db.close()


# def printRows(table, limit):
#     sql = f'SELECT * FROM sasha_mackowiak.{table} LIMIT {limit}'
#     cursor.execute(sql)
#     while(True):
#         row = cursor.fetchone()
#         if row == None:
#             break;
#         for cell in row:
#             print(cell)
#     db.close()


# tableName = input("Which table?")
# rows = int(input("How many rows?"))
# printRows(tableName, rows)
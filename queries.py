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


def getView(viewName, clearance):
    data = {}
    if(viewName == "animal-data"):
        tableName = "Current Patients"
        columns = "CONCAT_WS(' ', a.firstName, a.lastName), a.type, a.breed, a.age, a.admitted, CONCAT_WS(', ', d.lastName, d.firstName)"
        columnNames = ["Name", "Type", "Breed", "Age", "Date Admitted", "Assigned Doctor"]
        if clearance:
            columns += (", IF(a.quantum, 'yes', 'no')")
            columnNames.append("Quantum Abilities")
        primaryTable = "animals a"
        innerJoin = "doctors d ON d.doctor_id = a.doctor_id"
        orderBy = "a.type"
    sql = f"""
            SELECT {columns}
            FROM sasha_mackowiak.{primaryTable}
            INNER JOIN sasha_mackowiak.{innerJoin}
            ORDER BY {orderBy}
        """
    data["tableName"] = tableName
    data["columnNames"] = columnNames
    data["tableRows"] = getRows(sql)
    return data



def getRows(script):
    cursor = db.cursor()
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
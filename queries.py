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
    union = {}
    if(viewName == "animal-data"):
        tableName = "Current Patients"
        columns = "CONCAT_WS(' ', a.firstName, a.lastName), a.type, a.breed, a.age, a.admitted, CONCAT_WS(', ', d.lastName, d.firstName)"
        columnNames = ["Name", "Type", "Breed", "Age", "Date Admitted", "Assigned Doctor"]
        if clearance:
            columns += (", IF(a.quantum, 'yes', 'no')")
            columnNames.append("Quantum Abilities")
        primaryTable = "animals a"
        innerJoin = "doctors d ON d.doctor_id = a.doctor_id"
        orderGroupBy = "ORDER BY a.type"
    elif(viewName == "doctor-data"):
        tableName = "Hospital Staff"
        columns = "CONCAT_WS(', ', d.lastName, d.firstName) `name`, d.specialty, COUNT(*)"
        columnNames = ["Name", "Specialty", "Assigned Patients"]
        if clearance:
            columns += (", IF(d.quantum_clearance, 'yes', 'no'), IF(d.quantum, 'yes', 'no'), d.alias")
            columnNames.extend(["Quantum Clearance", "Quantum Powers", "Alias"])
        primaryTable = "doctors d"
        innerJoin = "animals a ON d.doctor_id = a.doctor_id"
        orderGroupBy = """GROUP BY `name` 
                            ORDER BY `name`"""
    elif(viewName == "hero-data"):
        if(clearance == False):
            return None
        tableName = "Resident Heroes"
        columns = "d.alias `alias`, CONCAT_WS(', ', d.lastName, d.firstName) `name`, 'human' `type`, qp.name `power`"
        columnNames = ["Alias", "Real Name", "Type", "Quantum Power"]
        primaryTable = "doctors d"
        innerJoin = """doctor_powers dp ON d.doctor_id = dp.doctor_id 
                        INNER JOIN sasha_mackowiak.quantum_powers qp ON dp.power_id = qp.power_id"""
        union['columns'] = "a.alias `alias`, CONCAT_WS(', ', a.lastName, a.firstName) `name`, a.type, qp.name `power`"
        union['primaryTable'] = "animals a"
        union['innerJoin'] = """animal_powers ap ON a.animal_id = ap.animal_id
                                INNER JOIN sasha_mackowiak.quantum_powers qp ON ap.power_id = qp.power_id"""
        orderGroupBy = "ORDER BY `alias`"
    elif(viewName == "malady-data"):
        tableName = "Known Maladies"
        columns = "m.name, m.description, COUNT(*)"
        columnNames = ["Malady Name", "Description", "Number of Patients"]
        primaryTable = "maladies m"
        innerJoin = """animal_maladies am ON m.malady_id = am.malady_id
                        INNER JOIN sasha_mackowiak.animals a ON am.animal_id = a.animal_id"""
        orderGroupBy = "GROUP BY name"
    else:
        return None
    sql = f"""
            SELECT {columns}
            FROM sasha_mackowiak.{primaryTable}
            INNER JOIN sasha_mackowiak.{innerJoin}

        """
    if union:
        sql += f"""
                UNION
                SELECT {union['columns']} 
                FROM sasha_mackowiak.{union['primaryTable']}
                INNER JOIN sasha_mackowiak.{union['innerJoin']}
                {orderGroupBy}
                """
    else:
        sql += orderGroupBy
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
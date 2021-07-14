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
        columns = "a.animal_id, CONCAT_WS(' ', a.firstName, a.lastName), a.type, a.breed, a.age, a.admitted, CONCAT_WS(', ', d.lastName, d.firstName)"
        columnNames = ["ID", "Name", "Type", "Breed", "Age", "Date Admitted", "Assigned Doctor"]
        if clearance:
            columns += (", IF(a.quantum, 'yes', 'no')")
            columnNames.append("Quantum Abilities")
        primaryTable = "animals a"
        innerJoin = "doctors d ON d.doctor_id = a.doctor_id"
        orderGroupBy = "ORDER BY a.type"
        data['realName'] = "animals"
        data['realID'] = "animal_id"
    elif(viewName == "doctor-data"):
        tableName = "Hospital Staff"
        columns = "d.doctor_id, CONCAT_WS(', ', d.lastName, d.firstName) `name`, d.specialty, COUNT(*)"
        columnNames = ["ID", "Name", "Specialty", "Assigned Patients"]
        if clearance:
            columns += (", IF(d.quantum_clearance, 'yes', 'no'), IF(d.quantum, 'yes', 'no'), d.alias")
            columnNames.extend(["Quantum Clearance", "Quantum Powers", "Alias"])
        primaryTable = "doctors d"
        innerJoin = "animals a ON d.doctor_id = a.doctor_id"
        orderGroupBy = """GROUP BY `name` 
                            ORDER BY `name`"""
        data['realName'] = "doctors"
        data['realID'] = "doctor_id"
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


def getIDData(tablesArray, clearance):
    dataDict = {}
    for tableName in tablesArray:
        if(tableName == "doctors"):
            columns = "doctor_id, CONCAT_WS(' ', firstName, lastName)"
        elif(tableName == "animals"):
            columns = "animal_id, CONCAT_WS(' ', firstName, lastName)"
        elif(tableName == "maladies"):
            columns = "malady_id, name"
        elif(clearance == False):
            continue
        elif(tableName == "quantum_powers"):
            columns = "power_id, name"
        else:
            continue
        sql = f"SELECT {columns} FROM sasha_mackowiak.{tableName}"
        dataDict[tableName] = getRows(sql)
    return dataDict


def deleteRow(table, column, columnMatch, name):
    sql = f"DELETE FROM sasha_mackowiak.{table} WHERE {column}='{columnMatch}'"
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    db.close
    return f"Deleted {name} from {table}"


def addRow(rowType, data):
    if(rowType == "animal"):
        animalData = {}
        animalData['columns'] = "firstName, lastName, type, doctor_id"
        animalData['values'] = f"'{data['firstName']}', '{data['lastName']}', '{data['type']}', {data['doctor_id']}"
        if(data['quantum']):
            animalData['columns'] += ", quantum"
            animalData['values'] += f", {data['quantum']}"
        animalData = addValueIfPresent('breed', animalData, data)
        animalData = addValueIfPresent('age', animalData, data)
        animalData = addValueIfPresent('admitted', animalData, data)
        animalData = addValueIfPresent('alias', animalData, data)
        newAnimalID = sendRowData("animals", animalData['columns'], animalData['values'])
        if 'malady_id' in data:
            maladyColumns = "animal_id, malady_id"
            maladyValues = f"{newAnimalID}, {data['malady_id']}"
            sendRowData("animal_maladies", maladyColumns, maladyValues)
        if 'power_id' in data:
            quantumColumns = "animal_id, power_id"
            quantumValues = f"{newAnimalID}, {data['power_id']}"
            sendRowData("animal_powers", quantumColumns, quantumValues)
    elif(rowType == "doctor"):
        doctorData = {}
        doctorData['columns'] = "firstName, lastName, quantum_clearance"
        doctorData['values'] = f"'{data['firstName']}', '{data['lastName']}'"
        if(data['quantum_clearance']):
            doctorData['values'] += f", True"
        else:
            doctorData['values'] += f", False"
        if(data['quantum']):
            doctorData['columns'] += ", quantum"
            doctorData['values'] += f", {data['quantum']}"
        doctorData = addValueIfPresent('specialty', doctorData, data)
        doctorData = addValueIfPresent('alias', doctorData, data)
        doctorData = addValueIfPresent('power_id', doctorData, data)
        newDoctorID = sendRowData("doctors", doctorData['columns'], doctorData['values'])
        if 'power_id' in data:
            quantumColumns = "doctor_id, power_id"
            quantumValues = f"{newDoctorID}, {data['power_id']}"
            sendRowData("animal_powers", quantumColumns, quantumValues)
    elif(rowType == "malady"):
        maladyData = {}
        maladyData['columns'] = "name"
        maladyData['values'] = f"'{data['name']}'"
        maladyData = addValueIfPresent('description', maladyData, data)
        newMaladyID = sendRowData(maladies, maladyData['columns'], maladyData['values'])
        if 'animal_id' in data:
            maladyColumns = "animal_id, malady_id"
            maladyValues = f"{data['animal_id']}, {newMaladyID}"
            sendRowData("animal_maladies", maladyColumns, maladyValues)
    elif(rowType == "power"):
        powerData = {}
        powerData['columns'] = "name"
        powerData['values'] = f"'{data['name']}'"
        powerData = addValueIfPresent('description', powerData, data)
        newPowerID = sendRowData('quantum_powers', powerData['columns'], powerData['values'])
        if 'animal_id' in data:
            animalColumns = "animal_id, power_id"
            animalValues = f"{data['animal_id']}, {newPowerID}"
            sendRowData("animal_powers", animalColumns, animalValues)
        if 'doctor_id' in data:
            doctorColumns = "doctor_id, power_id"
            doctorValues = f"{data['doctor_id']}, {newPowerID}"
            sendRowData("doctor_powers", doctorColumns, doctorValues)
    return


def addValueIfPresent(valueName, currentStrings, dataDict):
    if dataDict[valueName]:
        currentStrings['columns'] += f", {valueName}"
        currentStrings['values'] += f", '{dataDict[valueName]}'"
    return currentStrings


def sendRowData(tableName, columnString, valueString):
    script = f"INSERT INTO sasha_mackowiak.{tableName}({columnString}) VALUES ({valueString})"
    # if tableName == "quantum_powers":
    #     raise Exception(script)
    db = pymysql.connect(
        host="freetrainer.cryiqqx3x1ub.us-west-2.rds.amazonaws.com",
        user="sasha",
        password=secret.password
    )
    cursor = db.cursor()
    cursor.execute(script)
    db.commit()
    cursor.execute("SELECT LAST_INSERT_ID()")
    db.commit()
    result = cursor.fetchone()
    db.close()
    return result[0]


def changeRow(tableName, keyColumn, rowKey, newData):
    columnsList = newData.keys()
    columns = ", ".join(columnsList)
    valuesList = newData.values()
    values = "', '".join(valuesList)
    values = f"'{values}'"
    updatesList = []
    for name in columnsList:
        updatesList.append(f"{name} = '{newData[name]}'")
    updatesList = ", ".join(updatesList)
    sql = f"""INSERT INTO sasha_mackowiak.{tableName}({columns}, {keyColumn})
                VALUES ({values}, {rowKey}) 
                ON DUPLICATE KEY UPDATE {updatesList}"""
    # raise Exception(sql)
    db = pymysql.connect(
        host="freetrainer.cryiqqx3x1ub.us-west-2.rds.amazonaws.com",
        user="sasha",
        password=secret.password
    )
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    db.close
    return


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
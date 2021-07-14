# To start:
# export FLASK_APP=main.py
# export FLASK_ENV=development
# flask run

from flask import Flask, session, redirect, url_for, request, render_template
app = Flask(__name__)
import secret
import queries
app.secret_key = secret.sessionKey

@app.route("/", methods=['GET'])
def login():
    if("userName" in session):
        session.pop('userName', None)
        session.pop('clearance', None)
    message = "Please log in to view data"
    return render_template('login.html', message=message)


@app.route("/home/<userType>", methods=['GET', 'POST'])
def main(userType="unknown"):
    if("userName" in session):
        userName = session['userName']
        return render_template('home.html', userName=userName, message=f"Viewing data as {userName}", clearance=session['clearance'])
    message = "Welcome!"
    if(userType == "guest"):
        session['userName'] = "guest"
        session['clearance'] = False
        return render_template('home.html', userName="Guest", message=message, clearance=False)
    elif(userType == "registered"):
        name = request.form.get('lastName')
        userID = int(request.form.get('doctor_id'))
        userData = verifyLogin(name, userID)
        if(userData == None):
            return render_template('login.html', message="User data not found")
        userName = userData[1]
        clearance = bool(userData[4])
        session['userName'] = userName
        session['clearance'] = clearance
        return render_template('home.html', userName=userName, message=message, clearance=clearance)
    else:
        message = "Please log in to view data"
        return render_template('login.html', message=message)

@app.route("/home")
def goHome():
    if('userName' in session):
        if(session['userName'] == "guest"):
            userType = "guest"
        else:
            userType = "registered"
    else:
        userType = "unknown"
    return redirect(url_for('main', userType=userType))

@app.route("/data/<view>", methods=['GET'])
def showTable(view):
    if 'clearance' in session:
        doctorClearance = session['clearance']
    else:
        doctorClearance = False
    tableData = queries.getView(view, doctorClearance)
    if(tableData == None):
        return render_template('home.html', userName=(session['userName']), clearance=doctorClearance, message="Requested Data not found")
    return render_template('data_display.html', userName=(session['userName']), tableData=tableData)

@app.route("/search", methods=['GET'])
def showSearch():
    return render_template('search.html', userName=(session['userName']), clearance=(session['clearance']))


@app.route("/search-results", methods=['POST'])
def showResults():
    results = {}
    query = request.form.get('query')
    results['doctors'] = queries.findDataMatch("doctors", "lastName", query, False)
    # raise Exception(results['doctors'])
    results['doctors'].extend(queries.findDataMatch("doctors", "firstName", query, False))
    results['animals'] = queries.findDataMatch("animals", "lastName", query, False)
    results['animals'].extend(queries.findDataMatch("animals", "firstName", query, False))
    results['maladies'] = queries.findDataMatch("maladies", "name", query, False)
    results['maladies'].extend(queries.findDataMatch("maladies", "description", query, False))
    results['powers'] = queries.findDataMatch("quantum_powers", "name", query, False)
    results['powers'].extend(queries.findDataMatch("quantum_powers", "description", query, False))
    if results:
        message = "found these results"
    else:
        message = "no results found"
    return render_template('results.html', userName=(session['userName']), clearance=(session['clearance']), message=message, results=results)


@app.route("/delete/<table>/<columName>/<rowID>/<displayName>")
def deleteData(table, columName, rowID, displayName):
    message = queries.deleteRow(table, columName, rowID, displayName)
    return render_template('home.html', userName=session['userName'], message=message, clearance=session['clearance'])


@app.route("/update/<table>/<columnName>/<rowID>")
def updateData(table, columnName, rowID):
    existingRow = queries.findDataMatch(table, columnName, rowID, True)[0]
    idData = queries.getIDData(["animals", "doctors", "maladies", "quantum_powers"], session['clearance'])
    message = "Edit any fields you want to change, then submit"
    return render_template('update.html', existingRow=existingRow, idData=idData, table=table, columnName=columnName, userName=session['userName'], message=message, clearance=session['clearance'])

@app.route("/change/<table>/<columnName>/<rowID>", methods=['POST'])
def sendDataUpdate(table, columnName, rowID):
    updatedData = request.form
    queries.changeRow(table, columnName, rowID, updatedData)
    message = f"Updated {table}"
    return render_template('home.html', userName=session['userName'], message=message, clearance=session['clearance'])

@app.route("/new/<entryType>")
def showAddForm(entryType):
    idData = queries.getIDData(["animals", "doctors", "maladies", "quantum_powers"], session['clearance'])
    return render_template("add-form.html", idData=idData, entryType=entryType, userName=session['userName'], clearance=session['clearance'])


@app.route("/add/<entryType>", methods=['POST'])
def addEntry(entryType):
    entryData = request.form
    queries.addRow(entryType, entryData)
    message = f"Added {entryType} to records"
    return render_template('home.html', userName=session['userName'], message=message, clearance=session['clearance'])


def verifyLogin(doctorName, doctorID):
    doctorData = queries.findDataMatch("doctors", "lastName", doctorName, True)
    if (len(doctorData) == 0):
        return None
    else:
        for row in doctorData:
            if((row[0] == doctorID) and (row[2] == doctorName)):
                return row
        return None

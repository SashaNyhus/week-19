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
    tableData = queries.getView(view, True)
    return render_template('data_display.html', userName="Guest", tableData=tableData)


def verifyLogin(doctorName, doctorID):
    doctorData = queries.findDataMatch("doctors", "lastName", doctorName, True)
    if (len(doctorData) == 0):
        return None
    else:
        for row in doctorData:
            if((row[0] == doctorID) and (row[2] == doctorName)):
                return row
        return None

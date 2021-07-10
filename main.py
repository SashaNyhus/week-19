# To start:
# export FLASK_APP=main.py
# export FLASK_ENV=development
# flask run

from flask import Flask, request, render_template
app = Flask(__name__)
import queries

@app.route("/", methods=['GET'])
def login():
    message = "Please log in to view data"
    return render_template('login.html', message=message)


@app.route("/home/<userType>", methods=['POST'])
def main(userType):
    message = "Welcome!"
    if(userType == "guest"):
        return render_template('home.html', userName="Guest", message=message)
    elif(userType == "registered"):
        name = request.form.get('lastName')
        userID = int(request.form.get('doctor_id'))
        userData = verifyLogin(name, userID)
        if(userData == None):
            return render_template('login.html', message="User data not found")
        return render_template('home.html', userName=(userData[1]), message=message)


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

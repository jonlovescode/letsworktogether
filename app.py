import googlemaps
import sqlite3
from flask import g, Flask, request, jsonify, render_template, redirect, session, flash, url_for

import re
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'xyz'
app.config['HOST'] = 'localhost'
app.config['USER'] = 'root'
app.config['PASSWORD'] = 'password'
app.config['DATABASE'] = 'schema'

DATABASE = './schema.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db
def get_db_connection():
    conn = sqlite3.connect('schema.db')
    conn.row_factory = sqlite3.Row
    return conn
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        print(email,password)

        conn= get_db_connection()
        account = conn.execute("SELECT * FROM user WHERE email = ? AND password = ?", (email, password)).fetchone()
        print(account,'acc')
        if account:
            result = conn.execute("SELECT firstName, lastName FROM user WHERE email = ?", [email]).fetchone()

            print("result", result)


            session['loggedin'] = True
            session['lid'] = account['lID']
            session['email'] = account['email']
            session['name'] = result['firstName'] +" "+ result['lastName']
            print(session['name'])

            return redirect('/home')
        else:
            msg = 'Incorrect username/password!'
        return render_template("login.html",msg=msg)
    else:
        return render_template("login.html", msg=msg)



@app.route('/register', methods=['GET','POST'])
def register():
    msg = ''
        # read the posted values from the UI
    if request.method == "POST":
        #
        print('debugging purpose')
        details = request.form
        firstName = details['Firstname']
        lastName = details['Lastname']
        emailAddress = details['email']
        password = details['password']
        passwordRepeat = details['RepeatPassword']
        date = datetime.now()
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO user(email, password, firstName, lastName, lID, lastLogin,pChange) VALUES (?,?,?,?,?,?,?)",
            (emailAddress, password, firstName, lastName, 0, date,0))
        conn.commit()
        msg = "Successful"
        return render_template("register.html", msg=msg)
    else:
        return render_template("register.html", msg=msg)

@app.route('/join_group/', methods=['GET','POST'])
def join_group():
    msg = {
        'name': session['name']
    }
    conn = get_db_connection()
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    result = conn.execute("SELECT gName FROM groupC").fetchall()
    msg['result'] = [r['gName'] for r in result]
    # account = conn.execute("SELECT * FROM user WHERE email = ? AND password = ?", (email, password,)).fetchone()
    print(session['email'])
    joined = conn.execute("SELECT gName FROM groupMember WHERE email = ?", [session['email']]).fetchall()
    msg['joined'] = [j['gName'] for j in joined]

    if request.method == 'POST':
        j = request.form['b']
        conn.execute("INSERT INTO groupMember (gName, email, userStatus) VALUES (?, ?, ?)", (j, session['email'], 'pending'))
        conn.commit()
        result = conn.execute("SELECT gName FROM groupC").fetchall()
        msg['result'] = [r['gName'] for r in result]
        joined = conn.execute("SELECT gName FROM groupMember WHERE email = ?", [session['email']]).fetchall()
        msg['joined'] = [j['gName'] for j in joined]
        return render_template('join_groups.html', msg=msg)

    return render_template('join_groups.html',msg = msg)


@app.route('/create_group', methods=['GET','POST'])
def create_group():

    msg = {
        'name': session['name']
    }
    if request.method == 'POST':
        info = request.form
        gName = info['gName']
        d = info['description']
        conn = get_db_connection()
        result = conn.execute("SELECT gName FROM groupC").fetchall()
        gnames = [r['gName'] for r in result]
        print(gnames,gName)
        if gName not in gnames:
            print("in")
            conn.execute("INSERT INTO groupC (gName, gDescription) VALUES (?, ?)", (gName, d))
            conn.execute("INSERT INTO groupMember (gName, email, userStatus) VALUES (?, ?, ?)", (gName, session['email'], 'Approved'))
            conn.commit()
            msg['comment'] = "Successfully created a group!"
            print(msg)
            return render_template('create_group.html', msg=msg)
        else:
            msg['comment'] = "A group with a same name already exist. Please try again!"
            return render_template('create_group.html', msg=msg)

    return render_template('create_group.html', msg=msg)


@app.route('/change_password', methods=['GET','POST'])
def change_password():
    msg = ''
    if request.method == 'POST':
        info = request.form
        old_password = info['old_password']
        new_password = info['password']
        confirm_password = info['password1']
        cursor = get_db_connection().cursor()
        cursor.execute("SELECT password FROM User WHERE email = ?", [session['email']] )
        result = cursor.fetchone()
        if new_password == confirm_password and old_password == result['password']:
            cursor.execute("UPDATE User SET password = %s WHERE email = ?", [new_password, session['email']])
            cursor.commit()
            msg['msg'] = " You have successfully updated your password!"
            return render_template('change_password.html', msg = msg)
        return render_template('change_password.html', msg = msg)
    else:
        conn = get_db_connection()
        result = conn.execute("SELECT firstName, lastName FROM user WHERE email = ?", [session['email']]).fetchone()
        msg = result


        return render_template('change_password.html',msg=dict(msg))

@app.route('/create_location', methods=['GET','POST'])
def create_location():
    msg = {
        'name': session['name']
    }

    if request.method == 'POST':
        info = request.form 
        lName = info['lName']
        longitude = info['longitude']
        latitude = info['latitude']
        conn = get_db_connection()
        result = conn.execute("SELECT lName FROM location").fetchall()
        lNames = [r['lName'] for r in result]
        if lName not in lNames:

            conn.execute("INSERT INTO Location(lName, lID, longitude, latitude) VALUES (?,?,?,?)", [lName,0, longitude, latitude])
            conn.commit()
            msg['comment'] = "Successfully created a location!"
            return render_template('create_location.html', msg=msg)
        else:
            msg['comment'] = "The location already exists. Please try again!"
            return render_template('create_location.html', msg=msg)

    return render_template('create_location.html', msg=msg)
@app.route('/convert_location/', methods=['GET','POST'])
def convert_location():
    msg = {
        'name': session['name']
    }
    if request.method == 'POST':
        API_key = "AIzaSyB8BW2LAGsTx_euACkA-z4eiG1YDkRtB3k"
        gmaps = googlemaps.Client(key=API_key)
        info = request.form
        user_location = info['user-location']
        geocode_result = gmaps.geocode(user_location)

        
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']

        return  "Longitude: " + str(lng) + '\n Latitude: ' + str(lat)
    return render_template('convert_location.html',msg = msg)
@app.route('/find_location/', methods=['GET','POST'])
def find_location():
    msg = {
        'name': session['name']
    }
    return render_template('find_location.html',msg = msg)


@app.route('/group_page/<string:gName>', methods=['GET','POST'])
def create_event(gName):
    msg = {}
    msg['gName'] = gName
    conn = get_db_connection()
    if request.method == 'POST':
        info = request.form
        lID = info["lID"]
        eventDescription = info["description"]
        eventDate = info["eDate"]
        conn.execute("INSERT INTO Event(gName, lID, eventDescription, eventDate) VALUES (?,?,?,?)", (gName, lID, eventDescription, eventDate))
        conn.commit()
    
    result = conn.execute("SELECT * FROM Event WHERE gName = ?", [gName]).fetchall()
    msg['events'] = result

    result = conn.execute("select lastName, firstName from groupMember join User on User.email = groupMember.email where gName = ? and userStatus = \'approved\'", [msg['gName']]).fetchall();
    msg['people'] = result

    result = conn.execute("SELECT * FROM Location").fetchall()
    msg['result'] = result



    return render_template('group_page.html', msg=msg)





@app.route('/profile', methods=['GET','POST'])
def profile():
    msg = {
        'name': session['name']
    }
    conn = get_db_connection()
    result = conn.execute("SELECT gName FROM groupMember WHERE email = ?", [session['email']]).fetchall()
    msg['result'] = result

    g = conn.execute("SELECT COUNT(DISTINCT gName) FROM groupMember WHERE email = ?", [session['email']]).fetchone()
    msg['g_c'] = g['COUNT(DISTINCT gName)']

    result = conn.execute("SELECT * FROM groupMember WHERE userStatus = \"pending\" AND email != ?", [session['email']]).fetchall()
    msg['pending_num'] = len(result)
    if request.method == 'POST':
        l = request.form['b']
        print(l)
        conn = get_db_connection()
        conn.execute("DELETE FROM groupMember WHERE email = %s AND gName = ?", [session['email'], l])
        conn.commit()
        result = conn.execute("SELECT gName FROM groupMember WHERE email = ?", [session['email']]).fetchall()
        msg['result'] = result

        return render_template('profile.html', msg=msg)
    return render_template('profile.html', msg=msg)


@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')

@app.route('/pending_request', methods=['GET','POST'])
def pending_request():
    msg={
        'name': session['name']
    }
    conn = get_db_connection()
    if request.method == "POST":        
        info = request.form
        form_gName = info["gName"]
        form_email = info["email"]
        conn.execute("UPDATE groupMember SET userStatus = \"approved\" WHERE email = ? AND gName = ?", [form_email, form_gName])
        conn.commit()

    result = conn.execute("SELECT * FROM groupMember WHERE userStatus = \"pending\" AND email != ?", [session['email']]).fetchall()
    msg['result'] = result

    return render_template('pending_request.html', msg = msg)

@app.route('/people_nearby', methods=['GET','POST'])

def people_nearby():
    msg = {
        'email': session['email']
    }
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":        
        info = request.form
        email = info["person_email"]
        group = info["group"]
        conn.execute("INSERT INTO groupMember(gName, email, userStatus) VALUES (%s, %s, %s)", (group, email, "Approved"))
        conn.commit()

    result = conn.execute("SELECT * FROM user where lID = ?", [session['lid']]).fetchall()
    msg['people'] = result
    dictrows = [dict(result) for r in cursor]
    for i in dictrows:
        result = conn.execute("SELECT gName FROM groupC where gName not in (SELECT gName FROM groupMember where email = ?)", [i['email']]).fetchall()
        # dictrows = [dict(results) for r in cursor]
        i['groups'] = result
        # for i in dictrows:
        #     num = cursor.execute("SELECT COUNT(email) as c FROM groupMember where gName = ?", [i['gName']]).fetchone()
        #     print(num['c'])
        #     print(i['num'])
        #     print(i['num'])
        #     i['num'] = num['c']

    return render_template('people_nearby.html', msg = msg)

@app.route('/logout')
def logout():
    msg = "You have logged out!"
    return render_template('logout.html', msg=msg)

@app.route('/nopage')
def nopage():
    return render_template('404.html')




@app.route('/home', methods=['GET','POST']) #url should contain the username or some identifier to make sure we are pulling out the users info
def home():
    msg = {
        'name': session['name']
    }
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select * from groupC where gName in (select distinct gName from groupMember where gname not in (select gName from groupMember where email=?))", [session['email']])

    results = cursor.fetchall()
    msg['result'] = results
    dictrows = [dict(results) for r in cursor]
    for i in dictrows:
        num = cursor.execute("SELECT COUNT(email) as c FROM groupMember where gName = ?", [i['gName']]).fetchone()
        print(num['c'])
        print(i['num'])
        print(i['num'])
        i['num']=num['c']
        # format(r['amount'], '%.2f')
    result = cursor.execute("SELECT * FROM groupMember WHERE userStatus = \"pending\" AND email != ?", [session['email']]).fetchall()
    msg['pending_num'] = len(result)
    g = cursor.execute("SELECT COUNT(DISTINCT gName) FROM groupC").fetchone()
    msg['g_c'] = g['COUNT(DISTINCT gName)']
    # cursor.execute(
    #     'select Event.gName, Event.eventDescription, Event.eventDate, Location.lID, Location.longitude, Location.latitude '
    #     'from Event INNER JOIN Location on Event.lID = Location.lID')
    # lids = cursor.fetchall()
    #
    msg['lid'] = 0
    print(msg['lid'])

    # cursor.execute('SELECT *  FROM Event where lID in %s', [msg['lid']['lID']]);
    # events = cursor.fetchall()
    # print(events)

    if request.method == 'POST':
        b = request.form['b_home']
        cursor.execute("INSERT INTO groupMember (gName, email, userStatus) VALUES (?,?,?)",
                       [b, session['email'], 'Pending'])
        mysql.connection.commit()
        cursor.execute(
            "select * from groupC where gName in (select distinct gName from groupMember where gname not in (select gName from groupMember where email=?))",
            [session['email']])
        results = cursor.fetchall()
        msg['result'] = results

        for i in range(len(results)):
            cursor.execute("SELECT COUNT(email) as c FROM groupMember where gName = ?", [results[i]['gName']])
            num = cursor.fetchone()
            results[i]['num'] = num['c']


        return render_template('index.html', msg=msg)
    else:
        print("inside")
        return render_template('index.html', msg=msg)




# def executeScriptsFromFile(filename):
#     # Open and read the file as a single buffer
#     fd = open(filename, 'r')
#     sqlFile = fd.read()
#     fd.close()
#
#     # all SQL commands (split on ';')
#     sqlCommands = sqlFile.split(';')
#
#     # Execute every command from the input file
#     for command in sqlCommands:
#         # This will skip and report errors
#         # For example, if the tables do not yet exist, this will skip over
#         # the DROP TABLE commands
#         try:
#             cursor.execute(command)
#         except:
#             print ("Command skipped: ")
if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000, debug=True)



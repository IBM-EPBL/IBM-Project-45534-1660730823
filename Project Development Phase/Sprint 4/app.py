import json
import unicodedata
import os
import pathlib
from random import randint

import google.auth.transport.requests
import ibm_db
import requests
from flask import Flask, abort, redirect, render_template, request, session
from flask_mail import Mail, Message
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol

connectionstring = "DATABASE=bludb;HOSTNAME=21fecfd8-47b7-4937-840d-d791d0218660.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31864;PROTOCOL=TCPIP;UID=mzh43207;PWD=pLYMGfSprZntFyaz;SECURITY=SSL;"

connection = ibm_db.connect(connectionstring, '', '')
app = Flask(__name__)
app.debug = True


def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")


mail = Mail(app)
app.secret_key = "HireMe.com"

first_name = ""
last_name = ""
password = ""


app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = '2k19cse052@kiot.ac.in'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


GOOGLE_CLIENT_ID = ""
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


@app.route("/signup")
@app.route("/")
def signup():
    return render_template("signup.html")


@app.route('/verification', methods=["POST", "GET"])
def verify():
    global first_name
    global last_name
    global password
    global otp

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        useremail = request.form.get('email')
        sql = "SELECT * FROM User WHERE email =?"
        stmt = ibm_db.prepare(connection, sql)
        ibm_db.bind_param(stmt, 1, useremail)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if (account):
            return render_template('signup.html', msg="You are already a member, please login using your details")
        else:
            session['regmail'] = useremail
            otp = randint(000000, 999999)
            msg = Message(subject='OTP', sender='hackjacks@gmail.com',
                          recipients=[session['regmail']])
            msg.body = "You have succesfully registered for Hire Me!\nUse the OTP given below to verify your email ID.\n\t\t" + \
                str(otp)
            mail.send(msg)
            return render_template('verification.html')

    elif ("regmail" in session):
        if request.method == 'GET':
            otp = randint(000000, 999999)
            msg = Message(subject='OTP', sender='hackjacks@gmail.com',
                          recipients=[session['regmail']])
            msg.body = "You have succesfully registered for Hire Me!\nUse the OTP given below to verify your email ID.\n\t\t" + \
                str(otp)
            mail.send(msg)
            return render_template('verification.html', resendmsg="OTP has been resent")
    else:
        return redirect('/')


@app.route('/validate', methods=['POST', 'GET'])
def validate():
    if ('regmail' in session):
        global first_name
        global last_name
        global password
        user_otp = request.form['otp']
        if otp == int(user_otp):
            insert_sql = "INSERT INTO User(first_name,last_name,email,pass) VALUES (?,?,?,?)"
            prep_stmt = ibm_db.prepare(connection, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, first_name)
            ibm_db.bind_param(prep_stmt, 2, last_name)
            ibm_db.bind_param(prep_stmt, 3, session['regmail'])
            ibm_db.bind_param(prep_stmt, 4, password)
            ibm_db.execute(prep_stmt)
            return render_template('signin.html')
        else:
            return render_template('verification.html', msg="OTP is invalid. Please enter a valid OTP")
    else:
        return redirect('/')


@app.route("/googlelogin")
def googlelogin():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID,
        clock_skew_in_seconds=5
    )

    session["useremail"] = id_info.get("email")
    session["first_name"] = id_info.get("given_name")
    session["last_name"] = id_info.get("family_name")

    global first_name
    global last_name
    global useremail
    global password

    first_name = session['first_name']
    last_name = session['last_name']
    useremail = session['useremail']
    password = ""

    usersql = "SELECT * FROM User WHERE email =?"
    userstmt = ibm_db.prepare(connection, usersql)
    ibm_db.bind_param(userstmt, 1, useremail)
    ibm_db.execute(userstmt)
    useraccount = ibm_db.fetch_assoc(userstmt)
    if useraccount:
        session['newuser'] = useraccount['NEWUSER']
        if (session['newuser'] == 1):
            print(session['newuser'])
            return redirect('/profile')
        prosql = "SELECT * FROM profile WHERE email_id =?"
        prostmt = ibm_db.prepare(connection, prosql)
        ibm_db.bind_param(prostmt, 1, useremail)
        ibm_db.execute(prostmt)
        proaccount = ibm_db.fetch_assoc(prostmt)
        session['skill'] = proaccount['SKILL']
        return redirect('/home')

    else:

        insert_sql = "INSERT INTO User(first_name,last_name,email,pass) VALUES (?,?,?,?)"
        prep_stmt = ibm_db.prepare(connection, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, first_name)
        ibm_db.bind_param(prep_stmt, 2, last_name)
        ibm_db.bind_param(prep_stmt, 3, useremail)
        ibm_db.bind_param(prep_stmt, 4, password)
        ibm_db.execute(prep_stmt)
        return redirect("/profile")


@app.route("/logout")
def logout():
    session.clear()
    session.pop('useremail', None)
    session.pop('regmail', None)
    session.pop('newuser', None)
    session.pop('skill', None)
    session.pop('userid', None)
    session.pop('mailcompany', None)
    session.pop('appliedjobid', None)
    session.pop('state', None)
    return redirect("/login")


@app.route("/home", methods=['POST', 'GET'])
def home():
    if "useremail" in session:
        if request.method == 'POST':
            user_search = request.form.get(
                'search').replace(" ", "").casefold()
            arr = []
            sql = "SELECT * FROM COMPANY"
            stmt = ibm_db.exec_immediate(connection, sql)
            dictionary = ibm_db.fetch_assoc(stmt)
            while dictionary != False:
                if dictionary['COMPANY_NAME'].replace(" ", "").casefold() == user_search or dictionary['ROLE'].replace(" ", "").casefold() == user_search or dictionary['SKILL_1'].replace(" ", "").casefold() == user_search or dictionary['SKILL_2'].replace(" ", "").casefold() == user_search or dictionary['SKILL_3'].replace(" ", "").casefold() == user_search:
                    dict = {
                        'jobid': dictionary['JOB_ID'], 'cname': dictionary['COMPANY_NAME'], 'role': dictionary['ROLE'], 'ex': dictionary['EXPERIENCE'], 'skill_1': dictionary['SKILL_1'], 'skill_2': dictionary['SKILL_2'], 'skill_3': dictionary['SKILL_3'], 'vacancy': dictionary['VACANCY'], 'stream': dictionary['STREAM'], 'job_location': dictionary['JOB_LOCATION'], 'salary': dictionary['SALARY'], 'link': dictionary['WEBSITE'], 'logo': dictionary['LOGO'], 'description': remove_control_characters(dictionary['DESCRIPTION'])
                    }
                    arr.append(dict)
                dictionary = ibm_db.fetch_assoc(stmt)
            companies = json.dumps(arr)

            return render_template("index.html", companies=companies, arr=arr)
        else:
            arr = []
            sql = "SELECT * FROM COMPANY where skill_1 = ? or skill_2 = ? or skill_3 = ?"
            stmt = ibm_db.prepare(connection, sql)
            ibm_db.bind_param(stmt, 1, session['skill'])
            ibm_db.bind_param(stmt, 2, session['skill'])
            ibm_db.bind_param(stmt, 3, session['skill'])
            ibm_db.execute(stmt)
            dictionary = ibm_db.fetch_assoc(stmt)
            while dictionary != False:
                dict = {
                    'jobid': dictionary['JOB_ID'], 'cname': dictionary['COMPANY_NAME'], 'role': dictionary['ROLE'], 'ex': dictionary['EXPERIENCE'], 'skill_1': dictionary['SKILL_1'], 'skill_2': dictionary['SKILL_2'], 'skill_3': dictionary['SKILL_3'], 'vacancy': dictionary['VACANCY'], 'stream': dictionary['STREAM'], 'job_location': dictionary['JOB_LOCATION'], 'salary': dictionary['SALARY'], 'link': dictionary['WEBSITE'], 'logo': dictionary['LOGO'], 'description': remove_control_characters(dictionary['DESCRIPTION'])
                }
                print(dictionary['DESCRIPTION'].replace("\n", ""))
                arr.append(dict)
                dictionary = ibm_db.fetch_assoc(stmt)
            arr.reverse()
            companies = json.dumps(arr)
            # msg = getattr(session, 'msg', "")
            # print(session)
            # print("msg = ", msg)
            # if(getattr(session, 'msg', None) is not None):
            #     session.pop('msg')
            msg = ''
            if (session.get('msg') is not None):
                msg = session.get('msg')
                session.pop('msg')
            return render_template("index.html", companies=companies, arr=arr, msg=msg)
    else:
        return redirect('/login')


@app.route('/like', methods=['POST', 'GET'])
def store_like():
    session['jobid'] = request.form.get('jobid')
    print(session['jobid'])
    insert_sql = "INSERT INTO LIKES(USERID,JOBID) VALUES(?,?)"
    prep_stmt = ibm_db.prepare(connection, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, session['userid'])
    ibm_db.bind_param(prep_stmt, 2, session['jobid'])
    ibm_db.execute(prep_stmt)
    return None


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        useremail = request.form.get('email')
        password = request.form.get('password')
        sql = "SELECT * FROM user WHERE email =?"
        stmt = ibm_db.prepare(connection, sql)
        ibm_db.bind_param(stmt, 1, useremail)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            session["useremail"] = useremail
            session["newuser"] = account['NEWUSER']
            session['userid'] = account['USERID']
            if (password == str(account['PASS']).strip()):
                if (session['newuser'] == 1):
                    return redirect('/profile')
                else:
                    sql = "SELECT * FROM profile WHERE email_id =?"
                    stmt = ibm_db.prepare(connection, sql)
                    ibm_db.bind_param(stmt, 1, useremail)
                    ibm_db.execute(stmt)
                    account = ibm_db.fetch_assoc(stmt)
                    session['skill'] = account['SKILL']
                    return redirect('/home')
            else:
                return render_template('signin.html', msg="Password is invalid")
        else:
            return render_template('signin.html', msg="Email is invalid")
    else:
        if "useremail" in session:
            return redirect('/home')
        else:
            return render_template('signin.html')


@app.route("/profile", methods=["POST", "GET"])
def profile():
    if "useremail" in session:
        if (session['newuser'] == 1 and request.method == 'POST'):
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            mobile_no = request.form.get('mobile_no')
            address_line_1 = request.form.get('address_line_1')
            address_line_2 = request.form.get('address_line_2')
            zipcode = request.form.get('zipcode')
            city = request.form.get('city')
            education = request.form.get('education')
            country = request.form.get('countries')
            state = request.form.get('states')
            experience = request.form.get('experience')
            skill = request.form.get('skill')

            insert_sql = "INSERT INTO profile VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"

            prep_stmt = ibm_db.prepare(connection, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, first_name)
            ibm_db.bind_param(prep_stmt, 2, last_name)
            ibm_db.bind_param(prep_stmt, 3, mobile_no)
            ibm_db.bind_param(prep_stmt, 4, address_line_1)
            ibm_db.bind_param(prep_stmt, 5, address_line_2)
            ibm_db.bind_param(prep_stmt, 6, zipcode)
            ibm_db.bind_param(prep_stmt, 7, city)
            ibm_db.bind_param(prep_stmt, 8, session['useremail'])
            ibm_db.bind_param(prep_stmt, 9, education)
            ibm_db.bind_param(prep_stmt, 10, country)
            ibm_db.bind_param(prep_stmt, 11, state)
            ibm_db.bind_param(prep_stmt, 12, experience)
            ibm_db.bind_param(prep_stmt, 13, skill)
            ibm_db.execute(prep_stmt)

            insert_sql = "UPDATE USER SET newuser = false WHERE email=?"
            session['newuser'] = 0
            prep_stmt = ibm_db.prepare(connection, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, session['useremail'])
            ibm_db.execute(prep_stmt)
            session['skill'] = skill
            return redirect('/home')

        elif (session['newuser'] == 0 and request.method == "GET"):
            sql = "SELECT * FROM profile WHERE email_id =?"
            stmt = ibm_db.prepare(connection, sql)
            ibm_db.bind_param(stmt, 1, session['useremail'])
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            first_name = account['FIRST_NAME']
            last_name = account['LAST_NAME']
            mobile_no = account['MOBILE_NUMBER']
            address_line_1 = account['ADDRESS_LINE_1']
            address_line_2 = account['ADDRESS_LINE_2']
            zipcode = account['ZIPCODE']
            education = account['EDUCATION']
            countries = account['COUNTRY']
            states = account['STATEE']
            city = account['CITY']
            experience = account['EXPERIENCE']
            skill = account['SKILL']
            return render_template('profile.html', email=session['useremail'], newuser=session['newuser'], first_name=first_name, last_name=last_name, address_line_1=address_line_1, address_line_2=address_line_2, zipcode=zipcode, education=education, countries=countries, states=states, experience=experience, skill=skill, mobile_no=mobile_no, city=city)

        elif (session['newuser'] == 0 and request.method == "POST"):
            mobile_no = request.form.get('mobile_no')
            address_line_1 = request.form.get('address_line_1')
            address_line_2 = request.form.get('address_line_2')
            zipcode = request.form.get('zipcode')
            city = request.form.get('city')
            country = request.form.get('countries')
            state = request.form.get('states')
            experience = request.form.get('experience')
            skill = request.form.get('skill')
            sql = "UPDATE profile SET(mobile_number,address_line_1,address_line_2,zipcode,city,country,statee,experience,skill)=(?,?,?,?,?,?,?,?,?) where email_id =?"
            stmt = ibm_db.prepare(connection, sql)
            ibm_db.bind_param(stmt, 1, mobile_no)
            ibm_db.bind_param(stmt, 2, address_line_1)
            ibm_db.bind_param(stmt, 3, address_line_2)
            ibm_db.bind_param(stmt, 4, zipcode)
            ibm_db.bind_param(stmt, 5, city)
            ibm_db.bind_param(stmt, 6, country)
            ibm_db.bind_param(stmt, 7, state)
            ibm_db.bind_param(stmt, 8, experience)
            ibm_db.bind_param(stmt, 9, skill)
            ibm_db.bind_param(stmt, 10, session['useremail'])
            ibm_db.execute(stmt)
            session['skill'] = skill
            return redirect("/home")
        else:
            return render_template('profile.html', newuser=session['newuser'], email=session['useremail'])
    else:
        return redirect("/login")


@app.route("/forgotpass", methods=["POST", "GET"])
def forgotpass():
    global i
    global otp
    global email

    if request.method == 'POST':
        useremail = request.form.get('email')
        user_otp = request.form.get('OTP')
        password = request.form.get('password')

        sql = "SELECT * FROM User WHERE email =?"
        stmt = ibm_db.prepare(connection, sql)
        ibm_db.bind_param(stmt, 1, useremail)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if i == 1:
            if otp == int(user_otp):
                i = 2
                return render_template('forgotpass.html', i=i)
            else:
                return render_template('forgotpass.html', msg="OTP is invalid. Please enter a valid OTP", i=i)

        elif i == 2:
            sql = "UPDATE USER SET pass=? WHERE email=?"
            stmt = ibm_db.prepare(connection, sql)
            ibm_db.bind_param(stmt, 1, password)
            ibm_db.bind_param(stmt, 2, email)
            ibm_db.execute(stmt)
            i = 1
            return render_template('signin.html')

        elif i == 0:
            if (account):
                otp = randint(000000, 999999)
                email = request.form['email']
                msg = Message(subject='OTP', sender='hackjacks@gmail.com',
                              recipients=[email])
                msg.body = "Forgot your password?\n\nWe received a request to reset the password for your account.Use the OTP given below to reset the password.\n\n" + \
                    str(otp)
                mail.send(msg)
                i = 1
                return render_template('forgotpass.html', i=i)
            else:
                return render_template('forgotpass.html', msg="It looks like you are not yet our member!")
    i = 0
    return render_template('forgotpass.html')


@app.route("/apply/<string:jobid>", methods=["POST", "GET"])
def apply(jobid):
    if "useremail" in session:
        if request.method == "POST":
            session['appliedjobid'] = json.loads(jobid)
            stmt = ibm_db.prepare(
                connection, "select * from appliedcompany where userid=?")
            ibm_db.bind_param(stmt, 1, session['userid'])
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            while (account != False):
                if (session['appliedjobid'] == account["JOBID"]):
                    session['msg'] = "You have already applied for this job!"
                    session['error'] = True
                    # return render_template("index.html", msg="You have already applied for this job!")
                    return redirect("/home")
                account = ibm_db.fetch_assoc(stmt)

            # return redirect("/apply")
        elif (jobid == "profile"):
            return redirect('/profile')
        # else:
        jobsql = "SELECT * FROM company WHERE job_id =?"
        jobstmt = ibm_db.prepare(connection, jobsql)
        ibm_db.bind_param(jobstmt, 1, jobid)
        ibm_db.execute(jobstmt)
        appliedcompany = ibm_db.fetch_assoc(jobstmt)
        session['mailcompany'] = appliedcompany['COMPANY_NAME']
        sql = "SELECT * FROM profile WHERE email_id =?"
        stmt = ibm_db.prepare(connection, sql)
        ibm_db.bind_param(stmt, 1, session['useremail'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        first_name = account['FIRST_NAME']
        last_name = account['LAST_NAME']
        mobile_no = account['MOBILE_NUMBER']
        zipcode = account['ZIPCODE']
        education = account['EDUCATION']
        countries = account['COUNTRY']
        states = account['STATEE']
        city = account['CITY']
        experience = account['EXPERIENCE']
        return render_template('apply.html', email=session['useremail'], first_name=first_name, last_name=last_name, zipcode=zipcode, education=education, countries=countries, states=states, experience=experience, mobile_no=mobile_no, city=city)
    else:
        return redirect('/login')


@app.route("/applysuccess", methods=["POST", 'GET'])
def applysuccess():
    if "useremail" in session:
        if request.method == "POST":
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            mobile_no = request.form.get('mobile_no')
            zipcode = request.form.get('zipcode')
            city = request.form.get('city')
            education = request.form.get('education')
            country = request.form.get('countries')
            state = request.form.get('states')
            experience = request.form.get('experience')
            insert_sql = "INSERT INTO appliedcompany(userid,jobid,first_name,last_name,mobile_number,zipcode,city,email,education,country,state,experience) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(connection, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, session['userid'])
            ibm_db.bind_param(prep_stmt, 2, session['appliedjobid'])
            ibm_db.bind_param(prep_stmt, 3, first_name)
            ibm_db.bind_param(prep_stmt, 4, last_name)
            ibm_db.bind_param(prep_stmt, 5, mobile_no)
            ibm_db.bind_param(prep_stmt, 6, zipcode)
            ibm_db.bind_param(prep_stmt, 7, city)
            ibm_db.bind_param(prep_stmt, 8, session['useremail'])
            ibm_db.bind_param(prep_stmt, 9, education)
            ibm_db.bind_param(prep_stmt, 10, country)
            ibm_db.bind_param(prep_stmt, 11, state)
            ibm_db.bind_param(prep_stmt, 12, experience)

            ibm_db.execute(prep_stmt)
            msg = Message(subject='Job Application Notification', sender='hackjacks@gmail.com',
                          recipients=[session['useremail']])
            msg.body = "You have applied for the job posted by " + \
                session['mailcompany']+"\nBest of Luck!!!"
            mail.send(msg)
            return redirect('/applysuccess')
        else:
            return render_template('applysuccess.html'), {"Refresh": "5; url=/home"}

    else:
        return redirect('/home')


@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        adminmail = request.form.get('email')
        password = request.form.get('password')
        sql = "SELECT * FROM admin WHERE email =?"
        stmt = ibm_db.prepare(connection, sql)
        ibm_db.bind_param(stmt, 1, adminmail)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            session["adminmail"] = adminmail
            if (password == str(account['PASSWORD']).strip()):
                return render_template('adminhome.html')
            else:
                return render_template('adminlogin.html', msg="Password is invalid")
        else:
            return render_template('adminlogin.html', msg="Email is invalid")
    else:
        return render_template('adminlogin.html')


@app.route("/adminhome", methods=['GET', 'POST'])
def adminhome():
    if "adminmail" in session:
        if request.method == 'POST':
            company_name = request.form.get('company_name')
            role = request.form.get('role')
            skill_1 = request.form.get('skill_1')
            skill_2 = request.form.get('skill_2')
            skill_3 = request.form.get('skill_3')
            vacancy = request.form.get('vacancy')
            stream = request.form.get('stream')
            job_location = request.form.get('job_location')
            salary = request.form.get('salary')
            experience = request.form.get('experience')
            link = request.form.get('link')
            logo = request.form.get('logo')
            description = request.form.get('description')

            insert_sql = "INSERT INTO company (company_name, role, experience, skill_1, skill_2, skill_3, vacancy, stream, job_location, salary, website, logo,description) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"

            prep_stmt = ibm_db.prepare(connection, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, company_name)
            ibm_db.bind_param(prep_stmt, 2, role)
            ibm_db.bind_param(prep_stmt, 3, experience)
            ibm_db.bind_param(prep_stmt, 4, skill_1)
            ibm_db.bind_param(prep_stmt, 5, skill_2)
            ibm_db.bind_param(prep_stmt, 6, skill_3)
            ibm_db.bind_param(prep_stmt, 7, vacancy)
            ibm_db.bind_param(prep_stmt, 8, stream)
            ibm_db.bind_param(prep_stmt, 9, job_location)
            ibm_db.bind_param(prep_stmt, 10, salary)
            ibm_db.bind_param(prep_stmt, 11, link)
            ibm_db.bind_param(prep_stmt, 12, logo)
            ibm_db.bind_param(prep_stmt, 13, description)
            ibm_db.execute(prep_stmt)

            sql = 'SELECT email_id from profile Where skill = ? or skill = ? or skill = ?'
            stmt = ibm_db.prepare(connection, sql)
            ibm_db.bind_param(stmt, 1, skill_1)
            ibm_db.bind_param(stmt, 2, skill_2)
            ibm_db.bind_param(stmt, 3, skill_3)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            while account != False:
                msg = Message(subject='Job Posting', sender='hackjacks@gmail.com',
                              recipients=[account['EMAIL_ID']])
                msg.body = company_name+"has posted a new job. We are sending you this mail since you chose one of this company's required skill as your preferred skill"
                mail.send(msg)
                account = ibm_db.fetch_assoc(stmt)
            return render_template('adminhome.html')

        return render_template('adminhome.html')
    else:
        return redirect('/adminlogin')


@app.route("/adminlogout")
def adminlogout():
    session.pop('adminmail', None)
    return redirect("/adminlogin")
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
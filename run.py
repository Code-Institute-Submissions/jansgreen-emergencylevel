import pymongo
import mainClass
import json
import os
import bcrypt
import smtplib 
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_materialize import Material  
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from flask_pymongo import PyMongo  
from decouple import config
from flask_toastr import Toastr



app = Flask(__name__)
Material(app)
toastr = Toastr(app)


# MONGODB CONNECTION
if 'ENVIROMENT' in os.environ:
    s1_handler = os.environ['User_key']
    s2_handler = os.environ['Access_key']
else:
    s1_handler = config('User_key')
    s2_handler = config('Access_key')

client = pymongo.MongoClient("mongodb+srv://"+s1_handler+":"+s2_handler+"@cluster0-ajilk.mongodb.net/test?retryWrites=true&w=majority")
db = client["userRecord"]
dbColl = db["userRecord"]


# SETTING 
if 'ENVIROMENT' in os.environ:
    app.secret_key = os.environ.get('SECRET_KEY')
else:
    app.secret_key = config('SECRET_KEY')

imgFolder = os.path.join('static','img')
app.config['UPLOAD_FOLDER']=imgFolder

#dbColl = os.environ.get('dbColl')
#print(dbColl)

@app.route('/')
def index():
    homeImg= os.path.join(app.config['UPLOAD_FOLDER'], 'homeimg.jpg')
    return render_template("index.html", homeImg=homeImg)

#======================================================================================= PATIENT AREA


@app.route("/logout")
def logout():
    if 'Username' in session:
        session.pop('Username', None)
        flash(u'you did logout success', 'info')
        return redirect(url_for('index'))

@app.route('/PatientScreem')
def PatientScreem():
    UserLog = mainClass.UserLog(request.form)
    Seach = mainClass.Seach(request.form)
    PatientDataOut =[]
    return render_template("PatientScreem.html", form=UserLog, Seach=Seach, PatientDataOut = PatientDataOut)

@app.route('/PatientRegister')
def PatientRegister():
    Seach = mainClass.Seach(request.form)
    Register = mainClass.Register(request.form)
    visit = {
        "Category":"Patient",
        "FirstName": "name",
        "userAccount": " ",
        }
    _id = dbColl.insert_one(visit)
    id = _id.inserted_id 
    user = dbColl.find({'_id':id})   
    return render_template("register.html", form=Register, seach=Seach, id = id, User=user)

@app.route('/register/<string:id>', methods = ['GET'])
def register(id):
    Seach = mainClass.AllSeach(request.form)
    Register = mainClass.Register(request.form)
    user = dbColl.find_one({'_id':ObjectId(id)})
    if user:
        if user['Category']== 'DirectorDoctor':
            return render_template("register.html", form=Register, seach=Seach, id = id, User=user)
        elif user['Category']== 'Patient':
            flash(u'you did singup success', 'info')
            return render_template("register.html", form=Register, id = id)
    else:
        return render_template("register.html", form=Register, id = id)
    return render_template("index.html")

@app.route('/addRegister/<string:id>', methods = ['GET', 'POST'])
def addRegister(id):
    Register = mainClass.Register(request.form)
    if request.method == 'POST' and Register.validate:
        name = request.form['firstname']
        lastName = request.form['LastName']
        BOD = request.form['BOD']
        Address = request.form['address']
        Email = request.form['email']
        numPhone = request.form['telephone']
        if 'Username' in session:
            Userdata = dbColl.find_one({'_id':ObjectId(id)})

            if Userdata:
                Category = Userdata['Category']

                if Category=="DirectorDoctor":
                    New_Category = request.form['SeachSelect']
                    specialty = request.form['specialty']
                    dataPost = {
                        "Category": New_Category,
                        "FirstName": name,
                        "LastName": lastName,
                        "BOD": BOD,
                        "Address": Address,
                        "Email": Email,
                        "Phone": numPhone,
                        "userAccount": " ",
                        "Specialty"   : specialty
                        
                    }
                    _id = dbColl.insert_one(dataPost)
                    id = _id.inserted_id
                    if id: 
                        return redirect(url_for("AutoEmail", id=id))
        else:
            _id = dbColl.update({"_id":ObjectId(id)}, {'$set':{"FirstName": name, "LastName": lastName, "BOD": BOD, "Address": Address, "Email": Email, "Phone": numPhone }})
            patientId = id
            if patientId:
                return redirect(url_for("AutoEmail", id=id))
    return redirect(url_for("board", id=id))

        

#=============================================================================================================================
# API 
#=============================================================================================================================
@app.route('/AutoEmail/<string:id>') 
def AutoEmail(id):
    for user in dbColl.find({'_id': ObjectId(id)}):
        pass
        patienFirstName = user['FirstName']
        patienLastName = user['LastName']
        patienEmail = user['Email']
        patienCategory = user['Category']

    if patienFirstName:
        if patienCategory == "Patient": 
            EmailMessage = patienFirstName+" "+patienLastName+" We have information that you have registered at the emergency level, if you have been your favor, visit the following url to continue with the registration process. "+'https://emergencylevel.herokuapp.com/singup/'+id
            subject= 'Emergency, Continue your singup'
            Email = 'Subject: {}\n\n{}'.format(subject, EmailMessage)

            EmailSystem = smtplib.SMTP('smtp.googlemail.com', 587)
            EmailSystem.starttls()
            if 'ENVIROMENT' in os.environ:
                EmailSystem.login('emergencylebel@gmail.com', os.environ.get('GMAIL_PASS'))
                EmailSystem.sendmail('emergencylebel@gmail.com', patienEmail, Email)
            else:
                EmailSystem.login('emergencylebel@gmail.com', config('GMAIL_PASS'))
                EmailSystem.sendmail('emergencylebel@gmail.com', patienEmail, Email)   
            EmailSystem.quit()
            flash(u'Please check your Email, you need to confirm', 'success')
            return redirect(url_for("ticket", id=id))
        else:
            EmailMessage = patienFirstName +" "+patienLastName+" We have information that you have registered at the emergency level, if you have been your favor, visit the following url to continue with the registration process. "+'https://emergencylevel.herokuapp.com/singup/'+id
            subject= 'Emergency, Continue your singup'
            Email = 'Subject: {}\n\n{}'.format(subject, EmailMessage)
            EmailSystem = smtplib.SMTP('smtp.googlemail.com', 587)
            EmailSystem.starttls()
            if 'ENVIROMENT' in os.environ:
                EmailSystem.login('emergencylebel@gmail.com', os.environ.get('GMAIL_PASS'))
                EmailSystem.sendmail('emergencylebel@gmail.com', patienEmail, Email)
            else:
                EmailSystem.login('emergencylebel@gmail.com', config('GMAIL_PASS'))
                EmailSystem.sendmail('emergencylebel@gmail.com', patienEmail, Email) 
            EmailSystem.quit()
            return redirect(url_for("redirecting"))
    flash(u'Please check your Email, you need to confirm', 'success')
    return redirect(url_for("index"))

@app.route('/redirecting', methods=['GET','POST'])
def redirecting():
    userLog = mainClass.UserLog(request.form)
    if 'Username' in session:
        UserName = session['Username']
        userLog = dbColl.find_one({'userAccount.UserName': UserName})
        id = userLog['_id']
        if userLog:
            session['Username'] = UserName #=========================================================================================================
            id = userLog['_id']
            flash(u'you added success', 'success')
            return redirect(url_for("board", id =id, userlog=userLog ) )
        else:
            flash(u'User not exist', 'error')
            return redirect(url_for("index"))
    else:
        flash(u'User not found', 'error')
    return redirect(url_for("index"))



#======================================================================================= GENERATOR TICKET
@app.route('/ticket/<string:id>')
def ticket(id):
    ticketFullName = dbColl.find({"_id": ObjectId(id)})
    FullTicket = ticketFullName
    now = datetime.now()
    ticketNumData = now.strftime('%d%m%YE%H%M%S')
    dateTicket = now.strftime('%d/%m/%Y %H:%M')
    flash(u'Please print your ticket', 'success')
    try:
        Ticketquery = {"_id": ObjectId(id)}
        newvalues = {"$set": {
            "Emergincy."+ticketNumData: {'Date': dateTicket}
        }
        }
        dbColl.update_one(Ticketquery, newvalues)
    except:
        flash(u'We can not print your ticket', 'error')
        return redirect(url_for("index"))
    ticketNumDatas = now.strftime('%d%m%YE%H%M%S')
    return render_template("ticket.html", FullTickets=FullTicket, ticket = ticketNumDatas )
#======================================================================================= EMPLOYEE AREA
#========================================================= DOCTOR AREA

@app.route('/about')
def room():
    return render_template("doctorList.html")

@app.route('/staff')
def staff():
    if 'Username' in session:
        StaffTeam = mainClass.UserLog(request.form)
        return render_template("staff.html", form=StaffTeam)
    else:
        StaffTeam = mainClass.UserLog(request.form)
        return render_template("staff.html", form=StaffTeam)

@app.route('/board/<string:id>')
def board(id):
    if 'Username' in session:
        datadb = dbColl.find_one({"_id":ObjectId(id)})
        if datadb:
            return render_template("board.html", id = id, data = datadb, userlog =datadb)
    else:
        flash(u'You are not user register', 'error')
        return redirect(url_for("index"))
    flash(u'You are not logged or user register', 'error')
    return redirect(url_for("index"))

#========================================================= EMERGENCY AREA
@app.route('/EmergencyStaff/<string:id>')
def EmergencyStaff(id):
    if 'Username' in session:
        staff = dbColl.find_one({'_id':ObjectId(id)})
        page_size = 1
        page_num = 1
        skips = page_size * (page_num - 1)
        pages = dbColl.find({'Emergincy': {'$exists': 'true'}}).skip(skips).limit(page_size)
        for page in pages:
            print(page)
            pass
        if staff:
            patientListBD = dbColl.find({'Emergincy': {'$exists': 'true'}}).limit(5)
            if staff['Category'] == 'Nurse':
                Category = staff['Category']
                flash(" ", Category)
                return render_template("emergencyTeam.html", data=staff, ListBD = patientListBD, num=page, id=id )
            elif staff['Category'] == 'Doctor':
                Category = staff['Category']
                flash(" ", Category)
                return render_template("emergencyTeam.html", data=staff, ListBD = patientListBD, num=page, id=id)
            elif staff['Category'] == 'DirectorDoctor':
                Category = staff['Category']
                flash(" ", Category)
                return render_template("emergencyTeam.html", data=staff, ListBD = patientListBD, num=page, id=id)
            else:
                flash(u'You are not autorizated', 'warning')
                return redirect(url_for("index"))
    return redirect(url_for("index"))


#========================================================= Login AREA
@app.route('/singup/<string:id>')
def singup(id):
    Register = mainClass.UserLog(request.form)
    return render_template("singup.html", form = Register, id= id)

@app.route('/addsingup/<string:id>', methods = ['POST'])
def addsingup(id):
    Register = mainClass.UserLog(request.form)
    if request.method == 'POST' and Register.validate:
        newUser = request.form['Username']
        password = request.form['Password']
        CheckUser = dbColl.find_one({'_id': ObjectId(id)})
        if CheckUser:
            if 'userAccount.UserName' == newUser:
                return redirect(url_for("singup", id = id))  
            else:
                dbColl.update({'_id': ObjectId(id)}, {
                        '$set': {'userAccount':{"UserName":newUser, "Password":password}}})
                session['Username']= request.form['Username'] 
                return redirect(url_for("board", id = id))
    return redirect(url_for("board", id = id))    


@app.route('/mainLog', methods=['GET','POST'])
def mainLog():
    UserLog_class = mainClass.UserLog(request.form)
    if request.method == 'POST' and UserLog_class.validate:
        UserName = request.form['Username']
        PassUser = request.form['Password']
        userLog = dbColl.find_one({'userAccount.UserName': UserName})
        if userLog:
            PassDb = userLog['userAccount']['Password']
            if PassDb == PassUser:
                session['Username'] = request.form['Username']
                Category = userLog['Category']
                id = userLog['_id']
                flash(u'You are logged success', 'success')
                return redirect(url_for("board", id =id, userlog = userLog ) )
            else:
                flash(u'The password not match', 'error')
                return render_template("staff.html", form=UserLog_class)
        else:
            flash(u'The username not match', 'error')
            return render_template("staff.html", form=UserLog_class)
    return render_template("staff.html", form=UserLog_class)


#========================================================= Nurse STAFF AREA

@app.route('/Nourse/<string:id>', methods=['GET', 'POST'])
def Nourse(id):
    userLogs = mainClass.UserLog(request.form)
    Nourse = mainClass.Nourse(request.form)
    if 'Username' in session:
        UserName = session['Username']
        userLog = dbColl.find_one({'userAccount.UserName': UserName})
        if userLogs:
            NurId = userLog['_id']
            if request.method == 'POST'and Nourse.validate:
                AllergiesV = request.form['Mets']
                MetsV = request.form['BldPressure']
                DiagnosisV = request.form['Allergies']
                BldPressureV = request.form['Diagnosis']
                BreathingV = request.form['Breathing']
                PulseV = request.form['Pulse']
                BdTemperatureV = request.form['BdTemperature']
                NrsObservationV = request.form['NrsObservation']
                MdlIssuesV = request.form['MdlIssues']
                InttServiceV = request.form['InttService']
                now = datetime.now()
                MedicalDate = now.strftime('Date: %d-%m-%Y Hours: %H:%M:%S')
                try:
                    NewFieldIssuesV = request.form['NewFieldIssues']
                    newFieldtServiceV = request.form['newFieldtService']
                    MedicalData = {
                            "Date" : MedicalDate, 
                            "Nurse": userLog,
                            "Diagnosis":DiagnosisV,
                            "BloodPressure":BldPressureV,
                            "Breathing":BreathingV,
                            "Allergies":AllergiesV,
                            "Mets":MetsV,
                            "Pulse":PulseV,
                            "BodyTemperature":BdTemperatureV,
                            "NurseObservation":NrsObservationV,
                            "MedicalIssues":MdlIssuesV,
                            "IntensityService":InttServiceV,
                            "OtherIssues":NewFieldIssuesV,
                            "OtherService":newFieldtServiceV,
                            "Date": MedicalDate,
                    }
                    checkedField = dbColl.find_one({"_id": ObjectId(id)})
                    if checkedField:
                        if "NurseNote":
                            dbColl.update_one({"_id": ObjectId(id)}, {'$push':  {'NurseNote':MedicalData}})
                            return redirect(url_for('EmergencyStaff', id = NurId))
                        else:
                            dbColl.update_one({"_id": ObjectId(id)}, {'$set': {'NurseNote':MedicalData}})
                            return redirect(url_for("EmergencyStaff", id=NurId))
                    pass
                except:
                    MedicalData = {
                            "Date" : MedicalDate, 
                            "Nurse": userLog,
                            "Breathing":BreathingV,
                            "Allergies":AllergiesV,
                            "Mets":MetsV,
                            "Pulse":PulseV,
                            "BodyTemperature":BdTemperatureV,
                            "NurseObservation":NrsObservationV,
                            "MedicalIssues":MdlIssuesV,
                            "IntensityService":InttServiceV,
                            "Date": MedicalDate,
                    }
                    checkedField = dbColl.find_one({"_id": ObjectId(id)})
                    if checkedField:
                        if "NurseNote":
                            dbColl.update_one({"_id": ObjectId(id)}, {'$push':  {'NurseNote':MedicalData}})
                            return redirect(url_for('EmergencyStaff', id = NurId))
                        else:
                            dbColl.update_one({"_id": ObjectId(id)}, {'$set': {'NurseNote':MedicalData}})
                            return redirect(url_for("EmergencyStaff", id=NurId))
                    pass
        return redirect(url_for("board", id=NurId))


@app.route('/addNourse/<string:P_id>')
def addNourse(P_id):
    NourseForm = mainClass.Nourse(request.form)
    if 'Username' in session:
        UserName = session['Username']
        userLog = dbColl.find_one({'userAccount.UserName': UserName})
        if userLog:
            patientData = dbColl.find_one({'_id': ObjectId(P_id)})
            return render_template("/Nourse.html", PatientId=patientData, NurID=userLog, form=NourseForm)
        return redirect(url_for("index") )

#========================================================= DOCTOR STAFF AREA

@app.route('/Doctor/<string:Cid>/<string:id>', methods=['POST'])
def Doctor(Cid, id):
    if 'Username' in session:
        DrInfo = dbColl.find_one({"_id": ObjectId(Cid)})
        validatorForms = mainClass.validatorForm(request.form)
        if request.method == 'POST' and validatorForms.validate:
            Prescription = request.form['Prescription']
            Referencia = request.form['Referencia']
            Note = request.form['Note']
            AssigMed = request.form['assigMed']
            Indications = request.form['Indications']
            TestName = request.form['TestName']
            DoBefore = request.form['DoBefore']
            now = datetime.now()
            MedicalDate = now.strftime('Date: %d-%m-%Y Hours: %H:%M:%S')
            try:
                newMed = request.form['newMed']
                newInd = request.form['newInd']
                readyTestName = request.form['readyTestName']
                readyDoBefore = request.form['readyDoBefore']
                MedicalData={
                    "Date" : MedicalDate, 
                    "Doctor": DrInfo,
                "Prescription": Prescription,
                "Referencia": Referencia,
                "Note": Note,
                "Medication": (AssigMed, Indications),
                "OtherMedication":(newMed, newInd),
                "Test": (TestName, DoBefore),
                "OtherTest":(readyTestName,readyDoBefore),
                "MedicalDate":MedicalDate
                    }
            except:
                MedicalData={ 
                     "Date" : MedicalDate, 
                    "Doctor": DrInfo,
                "Prescription": Prescription,
                "Referencia": Referencia,
                "Note": Note,
                "Medication": (AssigMed, Indications),
                "Test": (TestName, DoBefore),
                    }
            finally:
                checkedField = dbColl.find_one({"_id": ObjectId(id)})
                if checkedField:
                    if "DoctorNote":
                        dbColl.update_one({"_id": ObjectId(id)}, {'$push':{'DoctorNote':MedicalData}})
                        return redirect(url_for('EmergencyStaff', id = Cid))
                    else:
                        dbColl.update_one({"_id": ObjectId(id)}, {'$set': {'DoctorNote':MedicalData}})
                        return redirect(url_for("EmergencyStaff", id=Cid))
    return redirect(url_for("EmergencyStaff", id=Cid))

@app.route('/addDoctor/<string:idD>/<string:id>', methods = ['GET'])
def addDoctor(idD, id):
    if 'Username' in session:
        validatorForms = mainClass.validatorForm(request.form)
        DrPasientsID = dbColl.find_one({'_id': ObjectId(idD)})
        if DrPasientsID:
            if DrPasientsID['Category'] == 'Doctor':
                Category = DrPasientsID['Category']
                flash(" ", Category)
                patientData = dbColl.find_one({'_id': ObjectId(id)})
                return render_template("/Doctor.html", DrPasientID=DrPasientsID, patientsData=patientData, id=patientData, form=validatorForms)
            elif DrPasientsID['Category'] == 'Nurse':
                Category = DrPasientsID['Category']
                flash(" ", Category)
                patientData = dbColl.find_one({'_id': ObjectId(id)})
                return render_template("/Doctor.html", DrPasientID=DrPasientsID, patientsData=patientData, id=patientData, form=validatorForms)

            elif DrPasientsID['Category'] == 'DirectorDoctor':
                Category = DrPasientsID['Category']
                flash(" ", Category)
                patientData = dbColl.find_one({'_id': ObjectId(id)})
                return render_template("/Doctor.html", DrPasientID=DrPasientsID, patientsData=patientData, id=patientData, form=validatorForms)
            else:
                flash(u'You are not autorizated', 'warning')
                return redirect(url_for("index"))
        else:
            flash(u'we not found', 'error')
            return redirect(url_for("index"))
            
#============================================================================================== Seach  AREA

@app.route('/Seach', methods=['POST'])
def Seach():
    UserLog = mainClass.UserLog(request.form)
    Seach = mainClass.Seach(request.form)
    if request.method == 'POST' and Seach.validate:
        PatientSeachD = request.form['Seach']
        PatientData = dbColl.find_one(
            {'Email': PatientSeachD, 'Category': 'Patient'})
        if PatientData:
            if PatientData['Email'] == PatientSeachD:
                return render_template("PatientScreem.html", PatientDataOut=PatientData, form=UserLog, Seach=Seach)        
        return render_template("PatientScreem.html", PatientDataOut=PatientData, form=UserLog, Seach=Seach)
#==============================================================================================
# BOARD  AREA
#==============================================================================================


#========================================================= Nurse STAFF AREA

@app.route('/SeeAll/<string:id>', methods = ['GET', 'POST'])
def SeeAll(id):
    if 'Username' in session:
        seach = mainClass.AllSeach(request.form)
    return render_template("/SeeAll.html", seach=seach, id=id)

@app.route('/See/<string:id>', methods = ['GET', 'POST'])
def See(id):
    if 'Username' in session:
        seach = mainClass.AllSeach(request.form)
        if request.method=='POST' and seach.validate:
            showData = request.form['SeachSelect']
            userid = dbColl.find_one({'_id':ObjectId(id)})
            if userid:
                if userid['Category']=='Patient' and showData == 'Patient':
                    Category = userid['Category']
                    flash(" ", Category )
                    print("usted no tiene permiso para ver a todos los"+showData)
                    return render_template("/SeeAll.html", seach=seach, AlluserCat=[], id=id)
                elif userid['Category']=='Patient':
                    data= dbColl.find({'Category':showData})
                    Category = userid['Category']
                    flash(" ", Category )
                    return render_template("/SeeAll.html", seach=seach, AlluserCat=data, id=id)
                else:
                    data= dbColl.find({'Category':showData})
                    Category = userid['Category']
                    flash(" ", Category )
                    return render_template("/SeeAll.html", seach=seach, AlluserCat=data, id=id)
            else:
                print("Hubo un error comuniquese con soporte tecnico")
                return redirect(url_for('/index'))
        else:
            print("Seleccione una opcion")
        return render_template("/SeeAll.html", seach=seach, AlluserCat=[], id=id)

#======================================================================================= USER AREA

@app.route('/Discharge/<string:id>', methods = ['GET', 'POST'])
def Discharge(id):
    if 'Username' in session:
        UserName = session['Username']
        userLog = dbColl.find_one({'userAccount.UserName': UserName})
        if userLog:
            session['Username'] = UserName
            Category = userLog['Category']
            DrId = userLog['_id']
            flash(" ", Category)
            emerdelete= dbColl.update({"_id":ObjectId(id)}, {'$unset':{"Emergincy":{'$exists':'true'}}})
            return redirect(url_for("EmergencyStaff", id = DrId))

@app.route('/edit/<string:id>', methods = ['GET', 'POST'])
def edit(id):
    if 'Username' in session:
        AllSeach = mainClass.AllSeach(request.form)
        Register = mainClass.Register(request.form)
        UserName = session['Username']
        userLog = dbColl.find_one({'userAccount.UserName': UserName})
        if userLog:
            session['Username'] = UserName
            Category = userLog['Category']
            flash(" ", Category)
        return render_template("edit.html", seach = AllSeach, form=Register, id = id,)


@app.route('/sumit_edit/<string:id>', methods = ['GET', 'POST'])
def sumit_edit(id):
    Register = mainClass.Register(request.form)
    if 'Username' in session:
        if request.method == 'POST' and Register.validate:
            name = request.form['firstname']
            lastName = request.form['LastName']
            BOD = request.form['BOD']
            Address = request.form['address']
            Email = request.form['email']
            numPhone = request.form['telephone']
            Category = request.form['SeachSelect']
            specialty = request.form['specialty']
            dataPost = {
                "Category": Category,
                "FirstName": name,
                "LastName": lastName,
                "BOD": BOD,
                "Address": Address,
                "Email": Email,
                "Phone": numPhone,
                "Specialty"   : specialty
            }
            dbColl.update({"_id":ObjectId(id)}, {'$set': dataPost})
        UserName = session['Username']
        userLog = dbColl.find_one({'userAccount.UserName': UserName})
        if userLog:
            session['Username'] = UserName
            Category = userLog['Category']
            AdmId = userLog['_id']
            flash(" ", Category)
            return redirect(url_for("board", id =AdmId ) )
        else:
            flash(u'we not found', 'error')
            return redirect(url_for("index") )
    else:
        flash(u'we not found the user', 'error')
        return redirect(url_for("index") )

        
@app.route('/MyDoctor/<string:id>', methods = ['GET', 'POST'])
def MyDoctor(id):
    if 'Username' in session:
        myInfo = dbColl.find_one({"_id": ObjectId(id)})
        return render_template("myDoctors.html", AlluserCat = myInfo, id = id,)

@app.route('/setMyDoctor/<string:id>/<string:Drid>')
def setMyDoctor(id, Drid):
    if 'Username' in session:
        getDoctor = dbColl.find_one({"_id":ObjectId(id)})
        myInfo = dbColl.find_one({"_id":ObjectId(Drid)})
        if getDoctor and myInfo:
            dbColl.update({"_id":ObjectId(Drid)}, {'$set':{'myDoctors':getDoctor}})
            return redirect(url_for('board', id=Drid))
        else:
            DrMessage = "We not have any doctor"
            flash(DrMessage)
        return redirect(url_for('board', id=Drid))

@app.route('/delete/<string:myid>')
def delete(myid):
    if 'Username' in session:
        dbColl.update({"_id":ObjectId(myid)}, {'$unset':{'myDoctors':{'$exists':'true'}}})
        pass
    return redirect(url_for('board', id=myid)) 

@app.route('/deleteDoc/<string:myid>')
def deleteDoc(myid):
    if 'Username' in session:
        dbColl.delete_one({"_id":ObjectId(myid)})
        UserName = session['Username']
        userLog = dbColl.find_one({'userAccount.UserName': UserName})
        if userLog:
            session['Username'] = UserName
            Category = userLog['Category']
            AdmId = userLog['_id']
            flash(" ", Category)
            return redirect(url_for("board", id =AdmId ) )
        else:
            print('Error')
    else:
        return redirect(url_for("index") )
        
@app.route('/myProfile/<string:id>')
def myProfile(id):
    if 'Username' in session:
        Profile = dbColl.find_one({'_id': ObjectId(id)})
        if Profile:
            return render_template("/myProfile.html", Profile = Profile, id=id)
        return render_template("/myProfile.html", Profile = Profile, id=id)

@app.route('/deleteAccount/<string:myid>')
def deleteAccount(myid):
    if 'Username' in session:
        dbColl.delete_one({"_id":ObjectId(myid)})
        flash(u'you delete your account success', 'sucess')
        return redirect(url_for('index')) 


if __name__ == '__main__':
    app.run(port=5500, debug=True)

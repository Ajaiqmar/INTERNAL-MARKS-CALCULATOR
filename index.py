import pandas as pd
import numpy as np
from flask import Flask
from flask import request,redirect,render_template,url_for
import os
from werkzeug.utils import secure_filename
import shutil

def cleanData(arr):
	for i in range(len(arr)):
		val = str(arr[i])
		val = "1117"+val[len(val)-8:]
		arr[i] = int(val)
	return arr

def getMcqPercentage(arr):
	for i in range(len(arr)):
		if not pd.isna(arr[i]):
        		val = list(map(float,str(arr[i]).strip().split("/")))
        		arr[i] = (val[0]/val[1])*20
		else:
			arr[i] = 0
	return arr

def getDcPercentage(arr):
	m = max(arr)
	for i in range(len(arr)):
		if not pd.isna(arr[i]):
			arr[i] = (arr[i]/m)*35
		else:
			arr[i] = 0
	return arr

def getDaPercentage(arr):
	for i in range(len(arr)):
		if not pd.isna(arr[i]):
        		val = list(map(float,str(arr[i]).strip().split("/")))
        		arr[i] = (val[0]/val[1])*10
		else:
			arr[i] = 0
	return arr

def getAutomataPercentage(arr):
	tarr = []
	for i in range(len(arr)):
		if not pd.isna(arr[i]):
			if(arr[i] < 0):
				tarr.append(0)
			else:
				tarr.append((arr[i]/100)*20)
		else:
			tarr.append(0)
	return tarr

def getWritex(arr):
	m = max(arr)
	tarr = []
	for i in range(len(arr)):
		if not pd.isna(arr[i]):
			if(arr[i] <= 0):
				tarr.append(0)
			else:
				tarr.append((arr[i]/m)*10)
		else:
			tarr.append(0)
	return tarr

def getTechnical(arr1,arr2):
	arr = []
	for i in range(len(arr1)):
		if pd.isna(arr1[i]):
			arr1[i] = 0
		if pd.isna(arr2[i]):
			arr2[i] = 0

		if(arr1[i] < 0):
			arr1[i] = 0
		if(arr2[i] < 0):
			arr2[i] = 0

		arr.append(((((arr1[i]+arr2[i])/2)/100)*10))

	return arr

def getAptitude(arr1,arr2,arr3):
	arr = []
	for i in range(len(arr1)):
		if pd.isna(arr1[i]):
			arr1[i] = 0
		if pd.isna(arr2[i]):
			arr2[i] = 0
		if pd.isna(arr3[i]):
			arr3[i] = 0

		if(arr1[i] < 0):
			arr1[i] = 0
		if(arr2[i] < 0):
			arr2[i] = 0
		if(arr3[i] < 0):
			arr3[i] = 0

		arr.append(((arr1[i]/100)*20)+((arr2[i]/100)*20)+((arr3[i]/100)*20))

	return arr

def getInternalMarks():
	df_amcat = pd.read_excel("uploads/amcat.xls",sheet_name="CSE & IT")
	df_skillrack = pd.read_excel("uploads/skillrack.xlsx")

	rollNoAmcat = cleanData(df_amcat["universityRollNo"].to_numpy().copy())
	rollNoSkillrack = df_skillrack["Regn Number"].to_numpy().copy()

	mcq = getMcqPercentage(df_skillrack["MCQ - APTITUDE"].to_numpy().copy())
	dc = getDcPercentage(df_skillrack["DAILYCHALLENGE"].to_numpy().copy())
	da = getDaPercentage(df_skillrack["MCQ - APTITUDE"].to_numpy().copy())
	ns = df_skillrack["Name"].to_numpy().copy()

	automata = getAutomataPercentage(df_amcat["Automata Fix(Score_3308)"].to_numpy().copy())
	writex = getWritex(df_amcat["WriteX - Essay Writing_Total Score"].to_numpy().copy())
	tech = getTechnical(df_amcat["Core Java (Entry Level)(Percentile_1937)"].to_numpy().copy(),df_amcat["Computer Science (Level 2)(Percentile_4305)"].to_numpy().copy())
	apt = getAptitude(df_amcat["Quantitative Ability (Advanced)(Percentile_6027)"].to_numpy().copy(),df_amcat["English Comprehension(Percentile_5954)"].to_numpy().copy(),df_amcat["Logical Ability(Percentile_5957)"].to_numpy().copy())

	rollNo = {}
	ind = 0

	for i in range(len(rollNoSkillrack)):
		if rollNoSkillrack[i] in rollNo:
			rollNo[rollNoSkillrack[i]].append(ns[i])
			rollNo[rollNoSkillrack[i]].append(((mcq[i]+dc[i]+35+da[i])/100)*50)
			rollNo[rollNoSkillrack[i]].append(0.0)
		elif(type(rollNoSkillrack[i]) == int):
			rollNo[int(rollNoSkillrack[i])] = [ns[i],((mcq[i]+dc[i]+35+da[i])/100)*50,0.0]

	for i in rollNoAmcat:
		if i in rollNo:
			rollNo[i][2] = (((automata[ind]+writex[ind]+tech[ind]+apt[ind])/100)*50)
		ind += 1

	return rollNo

def createExcel():
	rollNo = getInternalMarks()
	regNo = np.sort(list(rollNo.keys()))
	r = {}
	n = {}
	s = {}
	a = {}
	t = {}
	ind = 0

	for i in regNo:
		r[ind] = str(i)
		n[ind] = rollNo[i][0]
		s[ind] = rollNo[i][1]
		a[ind] = rollNo[i][2]
		t[ind] = rollNo[i][1]+rollNo[i][2]
		ind += 1

	dat = {"REGISTER NUMBER" : r,"NAME" : n,"SKILLRACK PERCENTILE":s,"AMCAT PERCENTILE":a,"INTERNAL MARKS PERCENTILE":t}
	df = pd.DataFrame(dat)
	df.to_excel("static/results/internalmarks.xlsx")


app = Flask(__name__)

@app.route("/")
def ma():
	if "uploads" in os.listdir():
		shutil.rmtree("uploads")
	os.mkdir("uploads")
	if os.path.isfile("static/results/internalmarks.xlsx"):
		os.remove("static/results/internalmarks.xlsx")
	return render_template("index.html")

@app.route("/student")
@app.route("/student/<int:id>")
def project(id = None):
	rollNo = getInternalMarks()
	if(id != None and id not in rollNo):
		return render_template("project.html",rollNo = rollNo,id = None,regNo = np.sort(list(rollNo.keys())))
	else:
		return render_template("project.html",rollNo = rollNo,id = id,regNo = np.sort(list(rollNo.keys())))

@app.route("/search", methods=["POST","GET"])
def searchStudent():
	return redirect("/student/{}".format(int(request.form["rno"])))

@app.route("/system")
def displaySystem():
	return render_template("system.html")


@app.route("/submit", methods=["POST","GET"])
def collectFile():
	f1 = request.files["sk"]
	f2 = request.files["am"]
	f1.save(os.path.join("uploads", secure_filename(f1.filename)))
	f2.save(os.path.join("uploads", secure_filename(f2.filename)))
	createExcel()
	return redirect("/system")

app.run(debug=True)

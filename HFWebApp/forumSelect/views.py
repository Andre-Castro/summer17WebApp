from django.shortcuts import render
import psycopg2

def index(request):
	dict = {
		"name": "NAME"
	}
	'''
	DBname = "MichalisPrj"
	pword = "1"
	tableName = "tbl_wilders_post"
	con = psycopg2.connect(database=DBname, user = "postgres", password=pword) #connect to postgres
	curs = con.cursor()
	ExecuteStatement = "SELECT title FROM " + tableName + " WHERE pdate > '2016-06-01'"
	curs.execute(ExecuteStatement)
	pdatesList = curs.fetchall()
	
	i = 0
	for pid in pdatesList:
		pdatesList[i] = str(pdatesList[i])
		i+= 1
	
	dict["pdates"] = pdatesList
	'''
	
	return render(request, 'forumSelect/home.html', dict)
from django.shortcuts import render
import psycopg2
import os
import re

def index(request):
	dict = {
		"name": "NAME"
	}
	file = open (os.path.join(os.path.dirname(os.path.realpath(__file__))+ '/templates/forumSelect/includes/ipList.dat'), 'r')
	#dict["ipList"] = [] #INSERT LIST OF IPs HERE
	
	list = re.split(r'\n', file.read())
	for i in range(len(list)):
		list[i] = re.split(r' ', list[i])
	dict["ipList"] = list
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
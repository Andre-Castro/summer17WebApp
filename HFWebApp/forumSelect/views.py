from django.shortcuts import render
import psycopg2
import os
import re
import sys
import math

PAGE_SIZE = 20

def index(request, forum):
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

def basic(request, forum):
    return render(request, 'forumSelect/home.html', dict)

def create_pager(current, max):
    max = int(max)
    current = int(current)
    
    pager = [current]
            
    left = range(1, current)
    if len(left) >= 2:
        pager = left[-2:] + pager
    else:
        pager = left + pager
        
    print >> sys.stderr, (pager)
    
    x = (5-len(pager))
    
    right = range(current+1, max)
    if len(right) >= x:
        pager = pager + right[0:x]
    else:
        pager = pager + right
    
    print >> sys.stderr, (pager)
    
    return ((current != 1), pager, (current != max))
        
IPLIST_SELECT_SQL = \
"""
SELECT a.addr, 
       a.freq, 
       a.tid, 
       a.pid, 
       b.country, 
       a.is_malicious::int 
FROM ip.ip a INNER JOIN ip.geolocation b ON a.addr = b.addr 
WHERE a.forum = %s 
LIMIT 20 OFFSET %s;
"""
IPLIST_SELECT_COUNT_SQL = \
"""
SELECT count(*) FROM ip.ip WHERE forum = %s
"""

def ip_list(request, forum, page=1):
    print >> sys.stderr, (forum, page)
    page = int(page)
    try:
        with psycopg2.connect(dbname='hackerchatter', host='localhost', user='hackerchatter', password='michalisfaloutsos') as con:
            cur = con.cursor()
            cur.execute(IPLIST_SELECT_COUNT_SQL, (forum,))
            total = cur.fetchone()[0]
            totalPage = math.ceil(total/PAGE_SIZE)
            
            has_prev, pager, has_next = create_pager(page, totalPage)
            
            offset = (page-1) * PAGE_SIZE        
            cur.execute(IPLIST_SELECT_SQL, (forum, offset))
            ipList = cur.fetchall()
            print ipList
    except psycopg2.Error as e:
        print(e.pgerror)
        
    dict = {
        'forum': forum,
        'ip': ipList,
        'has_prev': has_prev,
        'pager': pager,
        'has_next': has_next,
    }
        
    return render(request, 'forumSelect/home.html', dict)

def user(request, forum):
    return render(request, 'forumSelect/home.html', dict)
    
def extra(request, forum):
    return render(request, 'forumSelect/home.html', dict)

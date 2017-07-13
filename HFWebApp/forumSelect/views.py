from django.shortcuts import render
import psycopg2
import os
import re
import json
from pprint import pprint
import sys
import math
import numpy as np
import collections
import random
import time


# Hard coded forums info.
FORUMS = {
    'ashiyane': 'Ashiyane',
    'hackthissite': 'HackThisSite',
    'wilders': 'Wilders Secuiry Forum',
    'offcomm': 'Offensive Commnity',
}

PAGE_SIZE = 20

INDEX_FORUM_LIFESPAN_SQL = \
"""
SELECT coalesce(MAX(pdate)-MIN(pdate), 0) FROM post.post WHERE forum = %s;
"""
INDEX_REGISTERED_USERS_SQL = \
"""
SELECT COUNT(DISTINCT uid) FROM post.post WHERE forum = %s;
"""
INDEX_TOTAL_POSTS_SQL = \
"""
SELECT COUNT(DISTINCT pid) FROM post.post WHERE forum = %s;
"""
INDEX_TOTAL_THREADS_SQL = \
"""
SELECT COUNT(DISTINCT tid) FROM post.post WHERE forum = %s;
"""
INDEX_TOTAL_IP_SQL = \
"""
SELECT COUNT(DISTINCT addr) FROM ip.ip WHERE forum = %s;
"""
INDEX_POST_ACTIVITY_SQL = \
"""
SELECT g.month, COUNT(m), COUNT(DISTINCT m.tid)
FROM generate_series(1, 12) AS g(month)
    LEFT OUTER JOIN post.post AS m ON
        DATE_PART('year', m.pdate) = %s AND
        DATE_PART('month', m.pdate) = g.month AND 
        m.forum = 'hackthissite' 
GROUP BY g.month
ORDER BY g.month;
"""
INDEX_USER_DIST_SQL = \
"""
SELECT uid, count(*) c FROM post.post WHERE forum = %s GROUP BY uid ORDER BY c DESC
"""
INDEX_THREAD_DIST_SQL = \
"""
SELECT tid, count(*) c FROM post.post WHERE forum = %s GROUP BY tid ORDER by c DESC
"""

def cdf(data, reverse = False):
    cnt = collections.Counter()
    for val in data:
        cnt[val] += 1

    return sorted(cnt.items(), key=lambda x: x[0], reverse = reverse)

def index(request, forum):
    dict = {
        "forumName": FORUMS[forum],
        "forum": forum,
    }

    try:
        with psycopg2.connect(dbname='hackerchatter', host='localhost', user='hackerchatter', password='michalisfaloutsos') as con:
            cur = con.cursor()
            cur.execute(INDEX_FORUM_LIFESPAN_SQL, (forum,))
            # Warning: Trick here, need to fix.
            dict['lifespan'] = min(int(cur.fetchone()[0]), 4873)
            cur.execute(INDEX_REGISTERED_USERS_SQL, (forum,))
            dict['numUsers'] = int(cur.fetchone()[0])
            cur.execute(INDEX_TOTAL_THREADS_SQL, (forum,))
            dict['numThreads'] = int(cur.fetchone()[0])
            cur.execute(INDEX_TOTAL_POSTS_SQL, (forum,))
            dict['numPosts'] = int(cur.fetchone()[0])
            cur.execute(INDEX_TOTAL_IP_SQL, (forum,))
            dict['numIp'] = int(cur.fetchone()[0])

            years = [2015,2016]
            d = {}
            for y in years:
                t = {}
                cur.execute(INDEX_POST_ACTIVITY_SQL, (y,))
                data = cur.fetchall()
                t['post'] = json.dumps([x[1] for x in data])
                t['thread'] = json.dumps([x[2] for x in data])
                d[y] = t

            dict['activity'] = d

            cur.execute(INDEX_USER_DIST_SQL, ('hackthissite',))
            raw_data = np.array(cur.fetchall())

            data = cdf(raw_data[:,1].astype(float))
            data = np.array(data).astype(float)

            xs   = data[:,0]
            ys   = data[:,1]
            csum = np.cumsum(ys)
            ys   = csum / np.sum(ys)
            ys   = (1-ys) * 100

            dict['userDist'] = json.dumps([{'x': x[0],'y': x[1]} for x in zip(xs, ys)])
            dict['userTop5'] = raw_data[0:5].tolist()

            cur.execute(INDEX_THREAD_DIST_SQL, ('hackthissite',))
            raw_data = np.array(cur.fetchall())

            data = cdf(raw_data[:,1].astype(float))
            data = np.array(data).astype(float)

            xs   = data[:,0]
            ys   = data[:,1]
            csum = np.cumsum(ys)
            ys   = csum / np.sum(ys)
            ys   = (1-ys) * 100

            dict['threadDist'] = json.dumps([{'x': x[0],'y': x[1]} for x in zip(xs, ys)])
            dict['threadTop5'] = raw_data[0:5].tolist()

    except psycopg2.Error as e:
        print >> sys.stderr, str(e)

    dict["page"] = ["basicStats"]

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

IPLIST_LIST_SQL = \
"""
SELECT a.addr, 
       a.freq, 
       a.tid, 
       a.pid, 
       b.country, 
       a.is_malicious::int 
FROM ip.ip a 
    INNER JOIN ip.geolocation b ON 
        a.addr = b.addr 
WHERE a.forum = %s 
ORDER BY tid 
LIMIT 20 OFFSET %s;
"""
IPLIST_SELECT_COUNT_SQL = \
"""
SELECT count(*)
FROM ip.ip a 
    INNER JOIN ip.geolocation b ON 
        a.addr = b.addr
WHERE a.forum = %s;
"""
IPLIST_COUNTRY_DONUGHT_SQL = \
"""
SELECT b.country, 
       b.countrycode, 
       count(*) c 
FROM ip.ip a 
    INNER JOIN ip.geolocation b ON 
        a.addr = b.addr 
WHERE a.forum = %s 
GROUP BY b.country, b.countrycode 
ORDER BY c DESC 
LIMIT 5;
"""

def strTimeProp(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))

def randomDate(start, end, prop):
    return strTimeProp(start, end, '%m/%d/%Y', prop)

def ip_list(request, forum, page=1, malOnly=False):
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
            cur.execute(IPLIST_LIST_SQL, (forum, offset))
            data = cur.fetchall()
            # Warning: Trick here, need fix.
            ipList = [list(x) + [randomDate("1/1/2012", "8/1/2016", random.random())] for x in data]
            
            cur.execute(IPLIST_COUNTRY_DONUGHT_SQL, (forum,))
            data = cur.fetchall()
            
            donughData = [x[2] for x in data]
            donughData = donughData + [total-sum(donughData)]
            # print >> sys.stderr, donughData
            donughLabels = [x[0] for x in data] + ['Others']
            # print >> sys.stderr, donughLabels
            
            
    except psycopg2.Error as e:
       print >> sys.stderr, e.pgerror

    dict = {
        'forumName': FORUMS[forum],
        'forum': forum,
        'ip': ipList,
        'has_prev': has_prev,
        'pager': pager,
        'has_next': has_next,
        'page': ["malIP"],
        'donughData': json.dumps(donughData),
        'donughLabels': json.dumps(donughLabels),
    }
    
    print >> sys.stderr, dict

    return render(request, 'forumSelect/home.html', dict)

def user(request, forum):
    return render(request, 'forumSelect/home.html', dict)

def extra(request, forum):
    return render(request, 'forumSelect/home.html', dict)

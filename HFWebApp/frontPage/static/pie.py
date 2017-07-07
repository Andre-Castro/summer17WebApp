# -*- coding: utf-8 -*-
import os
import sys, traceback
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
# import MySQLdb as mdb
import psycopg2

def main(argv = None):

    width, height, dpi = 12, 6, 80

    # set parameters
    mpl.rcParams['figure.figsize'] = (width, height)
    mpl.rcParams['figure.dpi'] = dpi
    mpl.rcParams['font.size'] = 20
    # mpl.rcParams['figure.subplot.right'] = 0.96
    # mpl.rcParams['figure.subplot.left'] = 0.12
    # mpl.rcParams['figure.subplot.bottom'] = 0.14
    # mpl.rcParams['figure.subplot.top'] = 0.86

    # fetch data from database
    try:
        forums = ['offcomm','hackthissite','wilders','ethicalhackers','ashiyane']

        with psycopg2.connect(dbname='hackerchatter', host='localhost', user='hackerchatter', password='michalisfaloutsos') as con:
            cur = con.cursor()
            
            for forum in forums:
                sql = "SELECT SUM(freq) FROM ip.ip WHERE forum = %s"
                cur.execute(sql, (forum,))
                sum = cur.fetchone()[0]
            
                sql = "SELECT b.country, SUM(a.freq) AS c FROM ip.ip a INNER JOIN ip.geolocation b on a.addr = b.addr WHERE a.forum = 'ashiyane' GROUP BY b.country ORDER BY c DESC LIMIT 11"
                cur.execute(sql, (forum,))
                data = np.array(cur.fetchall())
                
                labels = data[:,0].tolist() + ['Others']
                xs = data[:,1].astype(float) / sum
                others = 1 - np.sum(xs)
                xs = xs.tolist() + [others]
                
                f, ax = plt.subplots()
                ax.pie(xs, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
                ax.axis('equal')
        
                # f.tight_layout()
                f.savefig('pie_%s.png' % forum)
                # fig.savefig('engagement_user_duration.pdf')
    
    except psycopg2.Error, e:
        print str(e)
        sys.exit(2)
    except Exception as e:
        # print type(e)
        print str(e)
        traceback.print_exc(file = sys.stdout)
        sys.exit(2)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
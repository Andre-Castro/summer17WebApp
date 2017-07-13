# -*- coding: utf-8 -*-
import os
import sys, traceback
# import random
import collections
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
# import MySQLdb as mdb
import psycopg2
import matplotlib.dates as mdates
# import matplotlib.cbook as cbook
import json

# years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
monthFmt = mdates.DateFormatter('%b')

def cdfBuild(data, reverse = False):
    cnt = collections.Counter()
    for val in data:
        cnt[val] += 1

    return sorted(cnt.items(), key=lambda x: x[0], reverse = reverse)

SPINE_COLOR = '#AEAEAE'
MAJOR_TICK_LINE_COLOR = '#878787'
MAJOR_TICK_LABEL_COLOR = '#878787'
MINOR_TICK_LINE_COLOR = '#AEAEAE'
MINOR_TICK_LABEL_COLOR = '#878787'
XAXIS_LABEL_COLOR = '#878787'
YAXIS_LABEL_COLOR = '#878787'
GRID_LINE_COLOR = '#D3D3D3'


def stylish(ax):
    ax.grid(True)
    gridlines = ax.get_xgridlines() + ax.get_ygridlines()

    for line in gridlines:
        line.set_linestyle('-.')
        line.set_color(GRID_LINE_COLOR)

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_color(SPINE_COLOR)
    ax.spines['bottom'].set_color(SPINE_COLOR)

    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    ax.tick_params(axis='both', labelcolor=MAJOR_TICK_LABEL_COLOR)
    # ax.tick_params(axis='y', colors='#878787')

    ax.tick_params(which='major', length=7, width=1.2, color=MAJOR_TICK_LINE_COLOR)
    ax.tick_params(which='minor', length=4, color=MINOR_TICK_LINE_COLOR)

    ax.yaxis.label.set_color(YAXIS_LABEL_COLOR)
    ax.xaxis.label.set_color(XAXIS_LABEL_COLOR)

def main(argv = None):

    width, height, dpi = 5.6, 3.6, 80

    # set parameters
    mpl.rcParams['figure.figsize'] = (width, height)
    mpl.rcParams['figure.dpi'] = dpi
    mpl.rcParams['font.size'] = 14
    # mpl.rcParams['figure.subplot.right'] = 0.96
    # mpl.rcParams['figure.subplot.left'] = 0.12
    # mpl.rcParams['figure.subplot.bottom'] = 0.14
    # mpl.rcParams['figure.subplot.top'] = 0.86

    # fetch data from database
    try:
        forums = ['offcomm','hackthissite']

        with psycopg2.connect(dbname='hackerchatter', host='localhost', user='hackerchatter', password='michalisfaloutsos') as con:
            cur = con.cursor()

            for forum in forums:
                sql = "SELECT uid, count(*) FROM post.post WHERE forum = %s GROUP BY uid"
                cur.execute(sql, (forum,))
                raw_data = np.array(cur.fetchall())

                data = cdfBuild(raw_data[:,1].astype(float))
                data = np.array(data).astype(float)

                xs   = data[:,0]
                ys   = data[:,1]
                csum = np.cumsum(ys)
                ys   = csum / np.sum(ys)
                ys   = (1-ys) * 100
                
                qq = zip(xs, ys)
                oo = [{'x': x[0], 'y': x[1]} for x in qq]
                print(json.dumps(oo))

                f, ax = plt.subplots()
                ax.plot(xs, ys, '-', lw=2, color='#4E8A96')
                ax.set_xscale('log')
                bottom, top = ax.get_ylim()
                ax.set_ylim(bottom=-(top-bottom)*0.05)
                ax.set_ylabel('Percentage')

                stylish(ax)

                f.tight_layout()
                f.savefig('user_dist_%s.png' % forum)

                sql = "SELECT tid, count(*) FROM post.post WHERE forum = %s GROUP BY tid"
                cur.execute(sql, (forum,))
                raw_data = np.array(cur.fetchall())

                data = cdfBuild(raw_data[:,1].astype(float))
                data = np.array(data).astype(float)

                xs   = data[:,0]
                ys   = data[:,1]
                csum = np.cumsum(ys)
                ys   = csum / np.sum(ys)
                ys   = (1-ys) * 100

                f, ax = plt.subplots()
                ax.plot(xs, ys, '-', lw=2, color='#4E8A96')
                ax.set_xscale('log')
                bottom, top = ax.get_ylim()
                ax.set_ylim(bottom=-(top-bottom)*0.05)
                ax.set_ylabel('Percentage')

                stylish(ax)

                f.tight_layout()
                f.savefig('thread_dist_%s.png' % forum)

                years = [2015, 2016]
                for y in years:
                    sql = "SELECT pdate, count(*) FROM post.post WHERE DATE_PART('year', pdate) = %s AND forum = %s GROUP BY pdate ORDER BY pdate;"
                    cur.execute(sql, (y, forum))
                    raw_data = np.array(cur.fetchall())

                    xs   = raw_data[:,0]
                    ys   = raw_data[:,1]

                    f, ax = plt.subplots()
                    ax.plot(xs, ys, '-', lw=2, color='#4E8A96')
                    # ax.set_ylabel('Percentage')
                    
                    ax.xaxis.set_major_locator(months)
                    ax.xaxis.set_major_formatter(monthFmt)

                    stylish(ax)

                    f.tight_layout()
                    f.savefig('post_date_%s_%s.png' % (y, forum))
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
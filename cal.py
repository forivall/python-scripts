#!/usr/bin/env python3.1
#
# Copyright (C) 2010 Richard Mortier <mort@cantab.net>.  All Rights Reserved.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA 02111-1307, USA.

import sys, calendar, getopt, datetime

Months = [ '',
           'january', 'february', 'march', 'april', 'may', 'june',
           'july', 'august', 'september', 'october', 'november', 'december' ]
Days = [ 'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
         'saturday', 'sunday' ]

def lookup(l, i):
    if i.isdigit(): return int(i)

    for j in range(max(map(len,l)),0,-1):
        ls = list(map(lambda s:s[:j], l))
        if i in ls: return ls.index(i)

    raise Exception("unknown month: %s" % (i,))

def die_with_usage(err="Usage: ", code=0):
    print("""%s: <options> <dates>
where available <options> are:
  -h/--help          : print this message
  -y/--year          : interpret arguments as years
  -c/--columns <n>   : format calendar across <n> columns
  -s/--separator <s> : format calendar using <s> as month separator
  -f/--firstday <d>  : format calendar with <d> as first-day-of-week
and <dates> are formatted as:
  <n>                 : month <n> if 1 <= n <= 12, else year <n>
  <m>/<y>             : month <m> in year <y>
  <m1>-<m2>           : months from <m1> to <m2>, inclusive
  <y1>-<y2>           : years from <y1> to <y2>, inclusive
  <m1>-<m2>/<y>       : months from <m1> to <m2> in year <y>, inclusive
  <m1>/<y1>-<m2>/<y2> : months from <m1> in year <y1> to <m2> in <y2>
for month <m> either 1-12, January-December, or abbreviation thereof
and year <y> is fully qualified, ie., 10 is year 10, not 2010.
    """ % (sys.argv[0], ))
    print(err)
    sys.exit(code)

def incr_month(y,m):
    m += 1
    if m > 12: y += 1; m = 1
    return y,m

def range_months(sy,sm, ey,em):
    y,m = sy,sm
    while True:
        yield calendar.month(y,m)
        y,m = incr_month(y,m)
        if (y,m) > (ey,em): break
        
def format_months(ms, ncols=3, sep='   '):
    empty_month = [((" "*20)+"\n")*8]

    ms = list(ms)
    ms += empty_month*ncols

    while len(ms) > ncols:
        mss = [ m.split("\n") for m in ms[:ncols] ]
        ms  = ms[ncols:]

        for i in range(ncols):
            mss[i] += ['']*(len(mss[i]) % 8)
            mss[i][0] = mss[i][0].strip().center(20)
            for j in range(8):
                mss[i][j] = mss[i][j].ljust(20)
                
        for i in range(8):
            for m in mss: yield "%s%s" % (m[i], sep)
            yield "\n"
    
if __name__ == '__main__':

    ## option parsing    
    pairs = [ "h/help", "y/year",
              "c:/columns=", "s:/separator=", "f:/firstday=", ]
    shortopts = "".join([ pair.split("/")[0] for pair in pairs ])
    longopts = [ pair.split("/")[1] for pair in pairs ]
    try: opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err: die_with_usage(err, 2)

    ncols = 3
    sep = ' '*4
    fullyear = False
    try:
        for o, a in opts:
            if o in ("-h", "--help"): die_with_usage()
            elif o in ("-y", "--year"): fullyear = True
            elif o in ("-c", "--columns"): ncols = int(a)
            elif o in ("-s", "--separator"): sep = a
            elif o in ("-f", "--firstday"):
                calendar.setfirstweekday(int(lookup(Days, a.lower())))
            else: assert False, "unhandled option"
    except Exception as err: die_with_usage(err, 3)

    ## compute the months to print
    year, month = datetime.date.isoformat(datetime.date.today()).split("-")[0:2]
    months = []
    if len(args) == 0: args = [ month ]
    for a in args:

        if fullyear: sy,sm, ey,em = int(a),1, int(a),12
        else:
            s,e = a,a
            if "-" in a: s,e = a.split("-")

            em,ey = e,int(year)
            if "/" in e: em,ey = e.split("/")
            try: em = lookup(Months, em)
            except Exception as err: die_with_usage(err, 4)

            sm,sy = s,ey
            if "/" in s: sm,sy = s.split("/")
            try: sm = lookup(Months, sm)
            except Exception as err: die_with_usage(err, 5)

            ## fix up if no month is given, only year or year range
            if sm > 12 or em > 12: sy,ey = sm,em ; sm,em = 1,12

        months.extend(list(range_months(int(sy),int(sm), int(ey),int(em))))

    ## format and print computed months
    for line in format_months(months, ncols, sep): print(line, end="")

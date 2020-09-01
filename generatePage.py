# 2020 08 20 -- ex cinera
# this will do something someday

import sys
import os
import time
# This is used to sleep.
from pathlib import Path
# For filesystem interactions.
import requests
# For scraping webpages.
from html.parser import HTMLParser
# Required to use BeautifulSoup.
from bs4 import BeautifulSoup
# The real meat and potatoes of the HTML parsing. + "/" + __file__
# Documentation for this is recommended reading to get how the program works.
from datetime import datetime


import psycopg2
# I am thinking of just putting the SQL stuff in its own file, I dunno.

dataname = "data"
timbername = "timber"
indicesname = "indices"
configname = "cfg"
configfilename = "sites.txt"
templatehead = "template-head.html"
templatefoot = "template-footer.html"
verbose = True
actuallyScrapeIndex = False
actuallyParseIndexTreeToDb = True
actuallyScrapeSubforums = False
actuallyParseThreadsToDb = False
# These ought to be set in config files, or by flags.


# I was using sys.path[0] to get the current directory
# but when I run it as sudo -u postgres it doesn't work
# However, os.getcwd() seems to work.
# -x 2020 08 22

datapath = Path(os.getcwd() + "/" + dataname)
# This is the directory where all program-generated data should live.
# Patrick Robotham told me to do this with Path on 2020 08 20.
timber = Path(os.getcwd() + "/" + dataname + "/" + timbername)
# Intermediate
#  (i.e. forum indices that list individual threads)
# Brighty is sad that I didn't call this some shit like /data/html/pages/ingest/toProcess/
indices = Path(os.getcwd() + "/" + dataname + "/" + indicesname)
# Top-level forum indexes (i.e. the main page of the website).
config = Path(os.getcwd() + "/" + configname)
configFilePath = Path(os.getcwd() + "/" + configname + "/" + configfilename)
headPath = Path(os.getcwd() + "/" + configname + "/" + templatehead)
headTemplatePath = Path(os.getcwd() + "/" + configname + "/" + "template-head-sample.html")
footPath = Path(os.getcwd() + "/" + configname + "/" + templatefoot)
footTemplatePath = Path(os.getcwd() + "/" + configname + "/" + "template-footer-sample.html")

if verbose:
	print("File name: " + __file__)
	print("Current path: " + os.getcwd() + "/" + __file__)
	print("Data path: " + str(datapath))
	print("Config file path: " + str(configFilePath))
	print("Running as user: " + os.getlogin())

try:
	headerFile = open(headPath, 'rb')
	header = headerFile.read().decode()
except:
	headerFile = open()
	pass


footerFile = open(footPath, 'rb')
footer = footerFile.read().decode()
# Open header and footer templates.

# conn = psycopg2.connect("dbname=threads user=postgres password=muensterenergy")
conn = psycopg2.connect(dbname="threads", user="postgres", password="muensterenergy")
cur = conn.cursor()
name_Database   = "threads";

mid = ""

base = "https://forums.somethingawful.com"

forumsArray = {}

fetchForums = cur.execute("SELECT * FROM forums ORDER BY forumid ASC")
i = 0
for f in cur:
	#print(f)
	forumsArray[f[0]] = f

# The structure of this is like so:
# cur.execute("CREATE TABLE IF NOT EXISTS forums (
#	0	forumid integer PRIMARY KEY,
#	1	title varchar,
#	2	description varchar,
#	3	parent integer,
#	4	website varchar,
#	5	websitename varchar,
#	6	icon varchar);")

#print(forumsArray)

#fetchString = cur.execute("SELECT * FROM threads ORDER BY lastpost DESC")
#fetchString = cur.execute("SELECT * FROM threads ORDER BY replycount DESC LIMIT 1000")
#fetchString = cur.execute("SELECT * FROM threads ORDER BY replycount DESC LIMIT 10000")
#fetchString = cur.execute("SELECT * FROM threads ORDER BY viewcount DESC LIMIT 1000")
#fetchString = cur.execute("SELECT * FROM threads WHERE replycount > 20000 ORDER BY lastpost DESC LIMIT 1000")
#fetchString = cur.execute("SELECT * FROM threads WHERE replycount > 20 ORDER BY viewcount/replycount DESC LIMIT 1000")
#fetchString = cur.execute("SELECT * FROM threads ORDER BY threadid ASC LIMIT 1000")
#fetchString = cur.execute("SELECT * FROM threads WHERE authorid = ")

#fetchString = cur.execute("SELECT forumid, COUNT(*) FROM threads GROUP BY forumid ORDER BY COUNT(*) DESC")

fetchString = cur.execute("SELECT * FROM threads ORDER BY lastpost DESC LIMIT 1000")

progress = 0
for r in cur:
	progress = progress +1
	print("Progress: " + str(progress))
# The order of the rs looks like:
# (3937588, 'Stanley Cup Playoffs Round 2 GDT: No Milbury Club', datetime.datetime(2020, 8, 30, 23, 37), -1, 124795, 'Escape Goat', 'marioinblack', False, False, False, 'https://fi.somethingawful.com/forums/posticons/sports-nhl.gif#147', 'Hockey', -1, 11772, 'null', True, False, 122, None, None)
# The schema is:
# cur.execute("CREATE TABLE IF NOT EXISTS recentthreads (
#	0	threadid integer PRIMARY KEY,
#	1	title varchar,
#	2	lastpost timestamp,
#	3	lastposterid integer,
#	4	authorid integer,
#	5	lastpostername varchar,
#	6	authorname varchar,
#	7	sticky boolean,
#	8	announcement boolean,
#	9	read boolean,
#	10	posticon varchar,
#	11	posticonalt varchar,
#	12	replycount integer,
#	13	viewcount integer,
#	14	rating varchar,
#	15	open boolean,
#	16	archived boolean,
#	17	forumid integer,
#	18	firstpost date,
#	19	firstpostid integer);")

	threadclass = "thread"
	if r[8] == True:
		threadclass = threadclass + " announcethread announce"
	if r[15] == False:
		threadclass = threadclass + " closed"
	if r[16] == True:
		threadclass = threadclass + " arch"
	mid = mid + "<tr class=\"" + threadclass +  "\" id=\"thread" + str(r[0]) + "\">\n"
	# Add the thread class and threadid TD.
	if r[8] == True:
		mid = mid + "<td class=\"star\"></td>\n"
		# Announcements threads have this even though it doesn't do anything.
	try:
		mid = mid + "<td class=\"fromsubforum\"><a href=\"" + base + "/forumdisplay.php?forumid=" + str(int(r[17])) + "\"><img src=\"" + forumsArray[int(r[17])][6] + "\" title=\"" + forumsArray[int(r[17])][1] + "\"></a></td>\n"
	except:
		mid = mid + "<td class=\"fromsubforum\"><a href=\"" + base + "/forumdisplay.php?forumid=" + str(r[17]) + "\">" + str(r[17]) + "</a></td>\n"
	# Add subforum TD
	posticonlocation = int(str(r[10]).find("#")) + 1
	# Find where the octothorpe is in the posticon url -- this is the icon's number for that subforum.
	posticon = str(r[10])[posticonlocation:]
	# Slice the string at that location to get the number of the posticon.
	mid = mid + "<td class=\"icon\"><a href=\"" + base + "/forumdisplay.php?forumid=" + str(r[17]) + "&amp;posticon=" + posticon + "\"><img src=\"" + str(r[10]) + "\" alt=\"" + str(r[11]) + "\"></a></td>\n"
	# Add icon TD.
	mid = mid + "<td class=\"title\">\n<div class=\"title_inner\">\n<div class=\"info\">\n<a href=\"" + base + "/showthread.php?threadid=" + str(r[0]) + "&goto=lastpost\" class=\"thread_title\">" + str(r[1]) + "</a>"
	# Add thread title and, possibly, page links.
	if r[12] > 40:
		# Not quite sure if I want to write out the whole list of pages here. It would be a nice touch but it'd take a while.
		# I also don't think anyone cares.
		...
	mid = mid + "\n</div>\n</div>\n</td>\n"
	# Finish thread title TD.
	mid = mid + "<td class=\"author\"><a href=\"" + base + "/member.php?action=getinfo&amp;userid=" + str(r[4]) + "\">" + str(r[6]) + "</a></td>\n"
	# Add author TD.
	mid = mid + "<td class=\"replies\"><a href=\"" + base + "/misc.php?action=whoposted&threadid=3937844\">" + str(r[12]) + "</a></td>\n"
	# Add reply count TD.
	mid = mid + "<td class=\"views\">" + str(r[13]) + "</td>\n"
	# Add view count TD.
	mid = mid + "<td class=\"rating\">&nbsp;</td>\n"
	mid = mid + "<td class=\"lastpost\"><div class=\"date\">" + str(r[2]) + "</div><a class=\"author\" href=\"" + base + "/member.php?action=getinfo&username=" + str(r[5]) + "\">" + str(r[5]) + "</a></td>\n"
	# Add last poster name TD.
	mid = mid + "</tr>"
	print(r)

htmlFull = str(header) + str(mid) + str(footer)


outputFile = open('index.html', 'w')
outputFile.write(htmlFull)
outputFile.close()


conn.commit()
cur.close()
conn.close()
# Close database cursor and database connection.
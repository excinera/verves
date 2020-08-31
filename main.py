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
verbose = True
actuallyScrapeIndex = True
actuallyParseIndexTreeToDb = False
actuallyScrapeSubforums = True
actuallyParseThreadsToDb = True
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

if verbose:
	print("File name: " + __file__)
	print("Current path: " + os.getcwd() + "/" + __file__)
	print("Data path: " + str(datapath))
	print("Attempting to execute in:")
	print(timber)
	print("Config file path: " + str(configFilePath))
	print("Running as user: " + os.getlogin())


# conn = psycopg2.connect("dbname=threads user=postgres password=muensterenergy")
conn = psycopg2.connect(dbname="threads", user="postgres", password="muensterenergy")
cur = conn.cursor()
name_Database   = "threads";
# Create table statement
# Create a table in PostgreSQL database

#cur.execute("DROP TABLE forums")
cur.execute("CREATE TABLE IF NOT EXISTS forums (forumid integer PRIMARY KEY, title varchar, description varchar, parent integer, website varchar, websitename varchar, icon varchar);")
# uncomment this to die instantly
cur.execute("CREATE TABLE IF NOT EXISTS recentthreads (threadid integer PRIMARY KEY, title varchar, lastpost timestamp, lastposterid integer, authorid integer, lastpostername varchar, authorname varchar, sticky boolean, announcement boolean, read boolean, posticon varchar, posticonalt varchar, replycount integer, viewcount integer, rating varchar, open boolean, archived boolean, forumid integer, firstpost date, firstpostid integer);")
cur.execute("DROP TABLE recentthreads")
cur.execute("CREATE TABLE IF NOT EXISTS recentthreads (threadid integer PRIMARY KEY, title varchar, lastpost timestamp, lastposterid integer, authorid integer, lastpostername varchar, authorname varchar, sticky boolean, announcement boolean, read boolean, posticon varchar, posticonalt varchar, replycount integer, viewcount integer, rating varchar, open boolean, archived boolean, forumid integer, firstpost date, firstpostid integer);")
# This one is for the HUGE table. Not for amateurs.
# cur.execute("DROP TABLE threads")
cur.execute("CREATE TABLE IF NOT EXISTS threads (threadid integer PRIMARY KEY, title varchar, lastpost timestamp, lastposterid integer, authorid integer, lastpostername varchar, authorname varchar, sticky boolean, announcement boolean, read boolean, posticon varchar, posticonalt varchar, replycount integer, viewcount integer, rating varchar, open boolean, archived boolean, forumid integer, firstpost date, firstpostid integer);")
conn.commit() 
# Make database change persistent.


cur.execute("SELECT * FROM threads")
print(cur.fetchone())


def insertIntoForums(argument):
	print(argument)
	cur.execute("""INSERT INTO forums (forumid, title, description, parent, website, websitename, icon) VALUES (%s, %s, %s, %s, %s, %s, %s)""",(argument['forumid'],
		argument['title'],
		argument['description'],
		int(argument['parent']),
		argument['website'],
		argument['websitename'],
		argument['icon']))

def insertIntoThreads(argument):
	# print(argument['forumid'])
	cur.execute("""INSERT INTO recentthreads (threadid, title, lastpost, lastposterid, authorid, lastpostername, authorname, sticky, announcement, read, posticon, posticonalt, replycount, viewcount, rating, forumid, open, archived) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",(argument['threadid'],
		argument['title'],
		argument['lastpost'],
		argument['lastposterid'],
		argument['authorid'],
		argument['lastpostername'],
		argument['authorname'],
		argument['sticky'],
		argument['announcement'],
		argument['read'],
		argument['posticon'],
		argument['posticonalt'],
		argument['replycount'],
		argument['viewcount'],
		argument['rating'],
		argument['forumid'],
		argument['open'],
		argument['archived']))

if verbose:
	print("At least the database stuff worked")
# os.mkdir(datapath) 
# This is the pleb way. Only villains go for this.

datapath.mkdir(mode=0o777, exist_ok = True)
timber.mkdir(mode=0o777, exist_ok = True)
config.mkdir(mode=0o777, exist_ok = True)
# Make sure that all the directories exist.
# the mode=0o777 comes from internet poster "farsicalrelease"
os.chdir(indices)

# there should be a thing here to parse in the list of URLs from a text file incl. auth details etc

try:
	cfgFile = open(configFilePath, 'r')
except:
	cfgFile = open(configFilePath, 'w')
	cfgFile.write("# Default configuration file for Verve Center\n# Fill this out and try to not fuck it up!\nURL: \nSite name: \nURL: \nSite name: ")
	pass

baseForumUrls = []
siteNames = []

for line in cfgFile:
	# print(line[5:])
	print(line.find("http"))
	if (line[5:].find("http") != -1):
		baseForumUrls.append(line[5:-1] + "/")
	if (line.find("Site name: ") != -1):
		siteNames.append(line[11:-1])

cfgFile.close()
print("Forum URLs: ", baseForumUrls)

siteIncrement = -1
for eachUrl in baseForumUrls:
	siteIncrement = siteIncrement + 1
	if actuallyScrapeIndex == True:
		print("Scraping " + str(eachUrl))
		r = requests.get(eachUrl, allow_redirects=False)
		indexu = open('indexu.html', 'wb')
		indexu.write(r.content)
		indexu.close()
		# If you're running it for real, this will scrape the top-level forums listing.
	indexu2 = open('indexu.html', 'rb')
	# this should just be a function that scrapes to a filename, instead of the same code written 4 times
	soupyIndex = BeautifulSoup(indexu2, 'html.parser')
	#print(soup.get_text())
	#print(soup.find_all(''))
	allForums = []
	# Initialize the array for the list of all forums.
	allForumNames = []
	# Initializes array for forum names.
	forumInfo = {}
	
	for eachTD in soupyIndex.find_all('td'):
		# This is the outer loop for the top-level index parser.
		# It runs over every TD element in the page (and all the forum listings are TDs).
		# Then, if the TD has <a class="forum"> or <div class="subforum">s in it, it parses those out.
		# It pushes all of the URLs of these forums/subforums into allForums.
	
		# Basically, the stuff below could be run on soupyIndex, but it would be fail because
		# the "eachA" and "eachDIV" loops would both be run over the entire document.
		# i.e. allForums would contain a list of every forum consecutively, and then a list of all subforums
		# This sucks because you lose the hierarchy of which subforums are children of which forums.
		# So instead, we iterate over each TD, so allForums will be a list of every forum,
		# with its subforums immediately after it
		#
		# Note: in later revisions, this will be storing to a database, and the subforums will just
		# have a field for "parent forum", which will be whatever the ID was of the last forum scraped.

		# Nested dictionary to contain all forums' info.
		#print("-----------------------------------------------")
		#print(eachTD)

		for eachA in eachTD.find_all('a'):
			try:
				#print(eachA)
				try:
					forumIcon = str(eachA.contents[0]['src'])
				except:
					...
					pass
				if 'forum' in eachA.attrs['class']:
		#			print("WOWIE WOWIE WOWIE WOWIE!!!!")
		#			print(eachA)
					thisForumId = str(eachA.attrs['href']).strip("forumdisplay.php?forumid=")
					print("Name: " + str(eachA.contents[0]) + " / URL: " + str(eachA.attrs['href']) + " ID: " + thisForumId)
					forumInfo[thisForumId] = {
					"forumid": thisForumId,
					"title": "",
					"description":"",
					"parent": -1,
					"website": eachUrl,
					"websitename": siteNames[siteIncrement],
					"icon": "https:" + forumIcon
					}
					forumInfo[thisForumId]['title'] = str(eachA.contents[0])
					allForumNames.append(eachA.contents[0].replace("/", "-"))
					print("|    " + str(eachA.attrs['title']))
					forumInfo[thisForumId]['description'] = eachA.attrs['title']
					forumInfo[thisForumId]['forumid'] = int(str(eachA.attrs['href']).strip("forumdisplay.php?forumid="))
					allForums.append(eachUrl + eachA.attrs['href'])
					#print("|    " + str(forumInfo[thisForumId]))
				if (eachA.attrs['class'][0] == 'subforums'):
					print("   ", eachA)
					# For some reason this never seems to trigger.
			except (IndexError, KeyError):
				#print(":/")
				pass	
		for eachDIV in eachTD.find_all('div'):
			try:
				if 'subforums' in eachDIV.attrs['class']:
					for eachAA in eachDIV.find_all('a'):
						thisSubForumId = int(str(eachAA.attrs['href']).strip("forumdisplay.php?forumid="))
						forumInfo[thisSubForumId] = {
						"forumid": thisSubForumId,
						"title": "",
						"description":"",
						"parent": forumInfo[thisForumId]['forumid'],
						"website": eachUrl,
						"websitename": siteNames[siteIncrement],
						"icon": forumInfo[thisForumId]['icon']
						}
						forumInfo[thisSubForumId]['title'] = str(eachAA.contents[0])
						forumInfo[thisSubForumId]['description'] = str(eachAA.contents[0])
						print("|--- Name: " + forumInfo[thisSubForumId]['title'] + " / URL: " + str(eachAA.attrs['href']) + " ID: " + str(thisSubForumId))
						allForumNames.append(eachAA.contents[0].replace("/", "-"))
						allForums.append(eachUrl + eachAA.attrs['href'])
						#print("|--- " + str(forumInfo[thisSubForumId]))
			except (IndexError, KeyError):
				pass
	
	indexu2.close()
	if actuallyParseIndexTreeToDb == True:
		print("------")
		print("------")
		print("------")
		for i in forumInfo:
			insertIntoForums(forumInfo[i])
		if verbose:
			print("Forums index scraped to DB.")


	time.sleep(5)
	if verbose:
		print(allForums)


	# okay now we're going to take this huge list of urls and scrape all the subforums WOOHOO
	
	os.chdir(timber)
	
	filenameIncrement = 0
	# The pages should, ideally, be saved with the actual titles of the HTML files, but whatever.
	bigList = []
	
	for eachSub in allForums:
		print(eachSub)
		if actuallyScrapeSubforums == True:
			r = requests.get(eachSub, allow_redirects=False)
			print(allForumNames[filenameIncrement])
			filenameForHtml = str(filenameIncrement) + " - " + allForumNames[filenameIncrement] + ".php"
			indexu = open(filenameForHtml, 'wb')
			indexu.write(r.content)
			indexu.close()
		filenameIncrement = filenameIncrement + 1
	
	listOfHtmls = sorted(timber.glob('*.php'))
	# This is "php" if working off scraped URLs, and also "php" if the block above is saving them to end with "php". Makes no difference, but "html" is easier to open in FF and debug.
	if verbose:
		print("Found {} htmls."
			.format(len(listOfHtmls)))
	progress = 0

	# This is the thing that will execute across every file! Meow!
	for incrementor in listOfHtmls:
		progress = progress + 1
		htmlFile = open(incrementor, 'rb')
	#	print("Opened html file")
		fileString = htmlFile.read().decode('cp1252')
	#	print("Decoded html file")
		soup = BeautifulSoup(fileString, 'html.parser')
	#	print(soup.get_text())
	#	print(soup.find_all(''))
		parentId = "0"
		# The ID of the forum's parent. We will set this, eventually, to the right thing.
		# Unless it's a top-level forum, in which case we want it to be set to zero.
		for eachDIV in soup.find_all('div'):
			try:
				# We're going to try to parse out the parent forum of each subforum, if it has any.
				# This means going in the div class "breadcrumbs" at the top of the page.
				# It will list the main forum, then the main category, etc down to the smallest parent.
				# i.e. Forums > Discussion > Ask/Tell > Business, Finance and Careers
				# We don't want to list every parent forum, just the last one (i.e. BFC only has parent Ask/Tell).
				# After parsing out the parent, there will still be more divs, but we'll break the loop because we're done.
				if eachDIV.attrs['class'][0] == 'breadcrumbs':
					#print(eachDIV)
					for eachA in eachDIV.find_all('a'):
						# print(eachA)
						#print(str(eachA).find("forumdisplay.php"))
						if (str(eachA).find("forumdisplay.php") != -1):
							#print("Gottem")
							lastParentId = parentId
							parentId = str(eachA.attrs['href']).strip("<a href=\"forumdisplay.php?forumid=")
							# print(parentId)
						if parentId == str(soup.body.attrs['data-forum']):
							break
			except:
				pass
		if actuallyParseIndexTreeToDb == True:
			# cur.execute(INSERT INTO forums)
			...
		print(str(incrementor) + " : " + str(progress) + "/" + str(len(listOfHtmls)) + " id:" + str(soup.body.attrs['data-forum']) + " par:" + lastParentId + " / " + str(soup.title.string))
		##print('////////////////////////////////////////////////////////////////////////////////')
		for eachTR in soup.find_all('tr'):
	#		print('---------')
			try:
				threadInfo = {
				"forumid":str(soup.body.attrs['data-forum']),
				"threadid":-1,
				"title":"null",
				"lastpost":datetime.strptime("00:00 Jan 01, 1970", "%H:%M %b %d, %Y"),
				"lastposterid":-1,
				"authorid":-1,
				"lastpostername":"null",
				"authorname":"null",
				"sticky":False,
				"announcement":False,
				"read":False,
				"posticon":"null",
				"posticonalt":"null",
				"replycount":-1,
				"viewcount":-1,
				"rating":"null",
				"firstpost":datetime.strptime("00:00 Jan 01, 1970", "%H:%M %b %d, %Y"),
				"firstpostid":-1,
				"open":True,
				"archived":False,
				"unreadcount":-1
				}


				if 'thread' in eachTR.attrs['class']:
					bigList.append(eachTR.attrs['class'])
					if ('closed' in eachTR.attrs['class']):
						threadInfo["open"] = False
					if ('announcethread' in eachTR.attrs['class']) or ('announce' in eachTR.attrs['class']):
						threadInfo["announcement"] = True
					if ('seen' in eachTR.attrs['class']):
						threadInfo["read"] = True
						#print("Seen thread:")
					else:
						...
						#print("Unseen thread:")
					if ('arch' in eachTR.attrs['class']):
						threadInfo["archived"] = True
	#				print('eachTR', " /// ", eachTR.attrs)
	#				print("WOWIE WOWIE WOWIE WOWIE!!!!")
					uselessVariable = 1;
	#				insertIntoThreads(threadid, title, lastpost, lastposterid, authorid, lastpostername, authorname, sticky, announcement, read, posticon, replycount, viewcount, rating)
	#				threadid integer PRIMARY KEY, title varchar, lastpost date, lastposterid integer, authorid integer, lastpostername varchar, authorname varchar, sticky boolean, announcement boolean, read boolean, posticon varchar, replycount integer, viewcount integer, rating varchar, firstpost date, firstpostid integer);")
					
					#print("///////")
					for eachTD in eachTR.find_all('td'):
	#					print(eachTD)
	#					print("///")
						try:
							if "icon" in eachTD.attrs['class']:
								threadInfo["posticon"] = str(eachTD.contents[0].contents[0]['src'])
								threadInfo["posticonalt"] = str(eachTD.contents[0].contents[0]['alt'])
								if verbose:
									print("------Icon: " + threadInfo["posticon"])
									print("-------Alt: " + threadInfo["posticonalt"])
							if "title_sticky" in eachTD.attrs['class']:
								threadInfo["sticky"] = True
							if "title" in eachTD.attrs['class']:
	#							eachTD.contents[1].div.a has the URL
	#							vvv This only works for unread threads, shouldn't be a problem if logged out
	#							print("Thread: " + str(eachTD.contents[1].div.a.contents[0]))
	#							vvv dogshit
	#							print("-*-Thread: " + str(eachTD.contents[1]))
								for eachA in eachTD.find_all('a'):
									if "count" in eachA.attrs['class']:
										threadInfo["unreadcount"] = int(str(eachA.contents[0])[3:-4])
										if verbose:
											print("----Unread: " + threadInfo["unreadcount"])
	#								vvv debug
	#								print(str(eachA.attrs['class']) + "/////" + str(eachA.contents))
									if "thread_title" in eachA.attrs['class']:
										uselessVariable = 1
										threadInfo["title"] = str(eachA.contents[0])
										#print(eachA.attrs['href'])
										# The link URL that the thread title goes to.
										# Will be something like "showthread.php?threadid=3930000"
										cutoff = (int(str(eachA.attrs['href']).find("threadid=")) + 9)
										# Point in the string where the thread ID is. It should be 24? I think.
										# But this allows it to be anything.c
										#print(int(str(eachA.attrs['href'])[cutoff:]))
										threadInfo["threadid"] = int(str(eachA.attrs['href'])[cutoff:])
										if verbose:
											print(str(threadInfo["threadid"]) + "   > " + threadInfo["title"])
							if "author" in eachTD.attrs['class']:
								uselessVariable = 1
								op = eachTD.contents[0]
								threadInfo["authorname"] = str(op.contents[0])
								# This is the OP's username (might be different from their current username)
								cutoff = (int(str(op.attrs['href']).find("userid=")) + 7)
								# Point in the string where the userID is. It should be 33, but it might not be sometimes.
								threadInfo["authorid"] = int(str(op.attrs['href'])[cutoff:])
								if verbose:
									print("--------OP: " + str(threadInfo["authorid"]) + " / " + threadInfo["authorname"])
							if "replies" in eachTD.attrs['class']:
								uselessVariable = 1
								if(str(eachTD.contents[0]) == "-"):
									threadInfo["replycount"] = -2
								else:
									# print(int(eachTD.contents[0]))
									if str(eachTD.contents[0]).find("href") != -1:
										if verbose:
											print("Href detected")
										threadInfo["replycount"] = int(str(eachTD.contents[0].contents[0]))
									else:
										threadInfo["replycount"] = int(str(eachTD.contents[0]))
									# This will probably break for logged-in pages.
	#							For some reason the same trick with the last-post-by doesn't work on this
	#							vvv link to everyone who posted in the thread
								if verbose:
									print("---Replies: " + str(threadInfo["replycount"]))
								#print("---Replies: " + str(eachTD.contents[0]))
	# doesnt work				print("---Replies: " + str(eachTD.contents[0].a))
							if "views" in eachTD.attrs['class']:
								uselessVariable = 1
								if(str(eachTD.contents[0]) == "-"):
									threadInfo["viewcount"] = -2
								else:
									threadInfo["viewcount"] = int(str(eachTD.contents[0]))
								if verbose:
									print("-----Views: " + str(threadInfo['viewcount']))
							if  'lastpost' in eachTD.attrs['class']:
								stamp = str(eachTD.contents[0].contents[0])
	#							Dates are formatted like:
	#							22:28 Aug 18, 2020
	#							22:28 Aug 8, 2020
	#							Sometimes a date be like:
	#							10:00 PM Aug 7, 2020
	#							If it's got a PM or an AM in it, we need to fix that.
								if(stamp.find("PM") != -1):
									stamp = str((int(stamp[:2]) + 12)) + stamp[2:5] + stamp[8:]
									# Add twelve to the timestamp and remove "PM".
								if(stamp.find("AM") != -1):
									stamp = stamp[:2] + stamp[2:5] + stamp[8:]
									# Take the timestamp and remove "AM".
									# I don't know what happens if it's like "9 AM", might need to check for that
									# but I'll have to wait until I find a post like that.
									# I think only announcements are formatted with the AM/PM thing.
								#print(stamp)
	#							This should work to zero-pad single-number days "Aug 8":
								if (stamp[11:][0] == ","):
									stamp = stamp[:10] + "0" + stamp[10:]
								if verbose:
									print("---Last at: " + stamp)
								datestamp = datetime.strptime(stamp, "%H:%M %b %d, %Y")
								threadInfo["lastpost"] = datestamp
								#print(datestamp)
								#print(datestamp.strftime("%a, %d %b %Y %T %z"))
	#							The full HTML link to the lastpost is at str(eachTD.contents[1])

								threadInfo["lastpostername"] = str(eachTD.contents[1].contents[0])
								if verbose:
									print("---Last by: " + str(threadInfo["lastpostername"]))
								if actuallyParseThreadsToDb == True:
									insertIntoThreads(threadInfo)
						except (IndexError, KeyError,AttributeError):
							print("OH NOES!!!!!!!")
							pass
			except KeyError:
				# print(eachTR)
				print(KeyError)
				pass
	#		print(type(eachA))	
	# <tr class="thread announcethread announce">
	# </tr>  ///  {'class': ['thread', 'announcethread', 'announce']}
	# this is the global sticky from jeffrey
	
	# normal stickies don't have a special tr class. 
	
	htmlFile.close()
# End of the loop that iterates over all top-level forums.
print("All done")
# print(bigList)
conn.commit()
cur.close()
conn.close()
# Close database cursor and database connection.
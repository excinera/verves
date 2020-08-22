# 2020 08 20 -- ex cinera
# this will do something someday

import sys
import os
from pathlib import Path
# For filesystem interactions.
import requests
# For scraping webpages.
from html.parser import HTMLParser
# Required to use BeautifulSoup.
from bs4 import BeautifulSoup
# The real meat and potatoes of the HTML parsing.
# Documentation for this is recommended reading to get how the program works.
from datetime import datetime

dataname = "data"
timbername = "timber"
indicesname = "indices"
configname = "cfg"
configfilename = "sites.txt"
verbose = True
actuallyScrapeIndex = False
actuallyScrapeSubforums = False
# These ought to be set in config files, or by flags.

datapath = Path(sys.path[0] + "/" + dataname)
# This is the directory where all program-generated data should live.
# Patrick Robotham told me to do this with Path on 2020 08 20.
timber = Path(sys.path[0] + "/" + dataname + "/" + timbername)
# Intermediate
#  (i.e. forum indices that list individual threads)
# Brighty is sad that I didn't call this some shit like /data/html/pages/ingest/toProcess/
indices = Path(sys.path[0] + "/" + dataname + "/" + indicesname)
# Top-level forum indexes (i.e. the main page of the website).
config = Path(sys.path[0] + "/" + configname)
configFilePath = Path(sys.path[0] + "/" + configname + "/" + configfilename)

# os.mkdir(datapath) 
# This is the pleb way. Only villains go for this.


if verbose:
	print(datapath)
	print("Attempting to execute in:")
	print(timber)
	print("Config file path: " + str(configFilePath))

datapath.mkdir(exist_ok = True)
timber.mkdir(exist_ok = True)
config.mkdir(exist_ok = True)
# Make sure that all the directories exist.
os.chdir(indices)




# there should be a thing here to parse in the list of URLs from a text file incl. auth details etc

try:
	cfgFile = open(configFilePath, 'r')
except:
	cfgFile = open(configFilePath, 'w')
	cfgFile.write("# Default configuration file for Verve Center\n# Fill this out and try to not fuck it up!\nURL: \nSite name: \nURL: \nSite name: ")
	pass

baseForumUrls = []

for line in cfgFile:
	# print(line[5:])
	print(line.find("http"))
	if (line[5:].find("http") != -1):
		baseForumUrls.append(line[5:])

cfgFile.close()
print("Forum URLs: ", baseForumUrls)


for eachUrl in baseForumUrls:
	if actuallyScrapeIndex == True:
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
	
		for eachA in eachTD.find_all('a'):
			try:
				if (eachA.attrs['class'][0] == 'forum'):
		#			print("WOWIE WOWIE WOWIE WOWIE!!!!")
		#			print(eachA)
					print("Name: " + str(eachA.contents[0]) + " / URL: " + str(eachA.attrs['href']))
					print("|    " + str(eachA.attrs['title']))
					allForums.append(eachUrl + eachA.attrs['href'])
				if (eachA.attrs['class'][0] == 'subforums'):
					print("   ", eachA)
			except (IndexError, KeyError):
		#		print(":/")
				pass	
		for eachDIV in eachTD.find_all('div'):
			try:
				if (eachDIV.attrs['class'][0] == 'subforums'):
					for eachAA in eachDIV.find_all('a'):
						print("|--- Name: " + str(eachAA.contents[0]) + " / URL: " + str(eachAA.attrs['href']))
						allForums.append(eachUrl + eachAA.attrs['href'])
			except (IndexError, KeyError):
				pass
	
	indexu2.close()
	
	print(allForums)
	
	
	# okay now we're going to take this huge list of urls and scrape all the subforums WOOHOO
	
	os.chdir(timber)
	
	filenameIncrement = 0
	# The pages should, ideally, be saved with the actual titles of the HTML files, but whatever.
	
	for eachSub in allForums:
		filenameIncrement = filenameIncrement + 1
		print(eachSub)
		if actuallyScrapeSubforums == True:
			r = requests.get(eachSub, allow_redirects=False)
			filenameForHtml = str(filenameIncrement) + ".html"
			indexu = open(filenameForHtml, 'wb')
			indexu.write(r.content)
			indexu.close()
	
	
	
	
	
	listOfHtmls = sorted(timber.glob('*.html'))
	if verbose:
		print("Found {} htmls."
			.format(len(listOfHtmls)))
	
	# This is the thing that will execute across every file! Meow!
	for incrementor in listOfHtmls:
		print(incrementor)
		htmlFile = open(incrementor, 'rb')
	#	print("Opened html file")
		fileString = htmlFile.read().decode('cp1252')
	#	print("Decoded html file")
		soup = BeautifulSoup(fileString, 'html.parser')
	#	print(soup.get_text())
	#	print(soup.find_all(''))
		print('//////////////////////////////////////////////////////////////////////////////////////////////////	//////////////////////////////////////////////////////////////////////////////////////////////////////')
		print(soup.title.string)
		print('//////////////////////////////////////////////////////////////////////////////////////////////////	//////////////////////////////////////////////////////////////////////////////////////////////////////')
		for eachTR in soup.find_all('tr'):
	#		print('---------')
			try:
				if eachTR.attrs['class'][0] == 'thread':
	#				print('eachTR', " /// ", eachTR.attrs)
	#				print("WOWIE WOWIE WOWIE WOWIE!!!!")
					uselessVariable = 1;
					#print("///////")
					for eachTD in eachTR.find_all('td'):
	#					print(eachTD)
	#					print("///")
						try:
							if eachTD.attrs['class'][0] == 'title':
	#							eachTD.contents[1].div.a has the URL
	#							vvv This only works for unread threads, shouldn't be a problem if logged out
	#							print("Thread: " + str(eachTD.contents[1].div.a.contents[0]))
	#							vvv dogshit
	#							print("-*-Thread: " + str(eachTD.contents[1]))
								for eachA in eachTD.find_all('a'):
	#								vvv debug
	#								print(str(eachA.attrs['class']) + "/////" + str(eachA.contents))
									if eachA.attrs['class'][0] == 'thread_title':
										uselessVariable = 1
										#print("---Thread : " + str(eachA.contents[0]))
							if eachTD.attrs['class'][0] == 'author':
								uselessVariable = 1
								#print("---OP     : " + str(eachTD.contents[0]))
							if eachTD.attrs['class'][0] == 'views':
								uselessVariable = 1
								#print("---Views  : " + str(eachTD.contents[0]))
							if eachTD.attrs['class'][0] == 'replies':
								uselessVariable = 1
	#							For some reason the same trick with the last-post-by doesn't work on this
	#							vvv link to everyone who posted in the thread
	#							print("---Replies: " + str(eachTD.contents[0]))
								#print("---Replies: " + str(eachTD.contents[0]))
	# doesnt work				print("---Replies: " + str(eachTD.contents[0].a))
							if eachTD.attrs['class'][0] == 'lastpost':
								stamp = str(eachTD.contents[0].contents[0])
	#							The full HTML link to the lastpost is at str(eachTD.contents[1])
								#print("---Last by: " + str(eachTD.contents[1].contents[0]))
	#							Dates are formatted like:
	#							22:28 Aug 18, 2020
	#							22:28 Aug 8, 2020
	#							so this should work to zero-pad dates (is very stupid):
								if (stamp[11:][0] == ","):
									stamp = stamp[:10] + "0" + stamp[10:]
								print("---Last at: " + stamp)
								datestamp = datetime.strptime(stamp, "%H:%M %b %d, %Y")
								print(datestamp)
								print(datestamp.strftime("%a, %d %b %Y %T %z"))
						except (IndexError, KeyError,AttributeError):
							pass
			except KeyError:
	#			print(":/")
				pass
	#		print(type(eachA))	
	# <tr class="thread announcethread announce">
	# </tr>  ///  {'class': ['thread', 'announcethread', 'announce']}
	# this is the global sticky from jeffrey
	
	# normal stickies don't have a special tr class. 
	
	
	
	
	
	htmlFile.close()
# End of the loop that iterates over all top-level forums.
print("All done")




# mega fail below this line LOL
# - x. 2020 08 20

# class MyHTMLParser(HTMLParser):
# 	def handle_starttag(self, tag, attrs):
# 		if tag == "a":
# 			#print("Encountered a start tag:", tag, " / ", attrs)
# 			if (len(attrs) > 1) and (attrs[1][0] == 'class'):
# 				isaClass = True
# 			else:
# 				isaClass = False
# 
# 	def handle_endtag(self, tag):
# 		if tag == "a":
# 			print("Encountered an end tag :", tag)
# 
# 	def handle_data(self, data):
# 		if isaClass == True:
# 			print("Encountered some data  :", data)
# 
# parser = MyHTMLParser()
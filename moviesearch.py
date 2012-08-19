from bs4 import BeautifulSoup
import urllib2
import re


movie_search_engine = "http://moviesearchengine.org/search/"

valid_movie_extensions = ["wmv", "avi", "mpeg"]
common_words = ["the", "a", "of", "and"]

extensions = {}


# give it a badly formed movie name, and it will return 
# a movie object
def movie_search2(movie_name):


	possibilities = {}



	words = movie_name.replace("_"," ").replace("-"," ").replace("["," ").replace(","," ").split()
	print words


	for word in words:
		if not word.lower() in common_words:
			result = re.match("\W", word)
			# valid word
			if result == None:
				response = urllib2.urlopen(movie_search_engine + word)
				html = response.read()
				soup = BeautifulSoup(html)
				results = soup.find_all('div', {"class":"search_frame"})
				for each in results:
					title = each.strong.text
					url = each.find("a").get("href")
					try:
						possibilities[title][1] += 1
					except KeyError:
						possibilities[title] = [url, 0]

	return possibilities





# give it a badly formed movie name, and it will return 
# a movie object
def movie_search(movie_name):


	possibilities = {}



	words = movie_name.replace("_"," ").replace("-"," ").replace("["," ").replace(","," ").split()
	#print words, len(words)

	for i in range(0,len(words)):
		try:
			#print words[i], words[i+1]
			response = urllib2.urlopen(movie_search_engine + words[i] + "+" + words[i+1])
		except IndexError:
			#print "single word", words
			response = urllib2.urlopen(movie_search_engine + words[i])
		html = response.read()
		soup = BeautifulSoup(html)
		results = soup.find_all('div', {"class":"search_frame"})
		for each in results:
			title = each.strong.text
			url = each.find("a").get("href")
			try:
				possibilities[title][1] += 1
			except KeyError:
				possibilities[title] = [url, 0]



	for word in words:
		if not word.lower() in common_words:
			result = re.match("\W", word)
			# valid word
			if result == None:
				response = urllib2.urlopen(movie_search_engine + word)
				html = response.read()
				soup = BeautifulSoup(html)
				results = soup.find_all('div', {"class":"search_frame"})
				for each in results:
					title = each.strong.text
					url = each.find("a").get("href")
					try:
						possibilities[title][1] += 1
					except KeyError:
						possibilities[title] = [url, 0]

	return possibilities







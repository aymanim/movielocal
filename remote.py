import ftputil
import moviesearch
import ftp_settings
import pickle
import os
import datetime
import time
import re
import threading

NUM_THREADS = 12

FILE_SIZE_THRESHOLD = 500 * 1024 * 1024

valid_movie_extensions = ["wmv", "avi", "mpeg", "mpg4", "mkv", "mp4"]
common_words = ["the", "a", "of", "and"]

movie_database_url = "http://moviesearchengine.org"

extensions = {}

cache_file = "moviecache"
ftp = None

def ftp_listing_callback(listing):
	# parse the listing
	# 0 - permissions
	# 4 - size
	# 8 to end - name



	tokenized = listing.split()
	name = " ".join(tokenized[8:len(tokenized)])
	if(tokenized[0][0] == 'd'):
		print "---"
	else:
		
		blast = name.split(".")
		extension = blast[-1]
		extensions[extension] = "1"
		movie_name = " ".join(blast[0:-1])
		print "FILE ",movie_name 
		names = movie_search(movie_name)

		for val, key in names.iteritems():
			flag = 0
			print "checking ", val
			for words in val.replace(":"," ").replace(","," ").split():
				if not words.lower() in movie_name.lower():
					flag = 1
					break
			if flag == 0:
				print "found it ", val, key[0], key[1] 



		print "====="

global_movie_list = []
global_resolved_list = []

def cleanname(name):
	
	remove_year = re.sub(r'[0-9][0-9][0-9][0-9]', ' ', name)
	remove_year = re.sub(r'\[[\w]*\]', ' ', remove_year)

	split_name = remove_year.lower().replace(":"," ").replace(","," ").replace("-"," ").replace("_", " ").split()
	
	for word in common_words:
		try:
			split_name.remove(word)
		except:
			pass

	return split_name

def name_resolution(movie_name):
	names = moviesearch.movie_search(movie_name)
	valid_candidate = None
	max_index = 0

	max_overlap = 0

	cleaned_movie_name = cleanname(movie_name)
	# get possible movie names
	for val, key in names.iteritems():
		flag = 0
		cleaned_val = cleanname(val)

		overlap = len(set(cleaned_movie_name).intersection(set(cleaned_val)))
		#print "checking ", val,  " -- ", overlap
		if overlap > max_overlap:
			#print "   seems to work [", overlap, "]"
			valid_candidate = [val, key[0]]
			max_overlap = overlap

	if not valid_candidate is None:
		#print "Found it - ", valid_candidate
		#print valid_candidate
		return valid_candidate
	else:
		#print "No valid candidate"
		#print "non"
		return ["",""]




def ftp_traverse(directory):
	print "ftp_traverse", directory
	for element in ftp.listdir(directory):
		path_to_element = directory + "\/" + element
		if ftp.path.isfile(path_to_element):

			# only add valid videos
			if(element.split(".")[-1] in valid_movie_extensions) and ftp.path.getsize(path_to_element) > FILE_SIZE_THRESHOLD:
				print "adding to list", element
				global_movie_list.append(element)
		else:
			print "cd ", element
			ftp_traverse(directory + "\/" + element)		


def create_movie_list():
	global ftp
	ftp_server = ftp_settings.FTP_SERVER
	ftp_username = ftp_settings.FTP_USERNAME
	ftp_password = ftp_settings.FTP_PASSWORD

	ftp_movie_directory = "Video\/Movies"


	print "Connecting to ", ftp_server

	# Connect to the server 
	ftp = ftputil.FTPHost(ftp_server, ftp_username, ftp_password)

	#ftp.listdir(ftp_movie_directory)

	ftp_traverse(ftp_movie_directory)

	file = open(cache_file, "w")
	pickle.dump(global_movie_list, file)


def multi_thread_name_resolve(start, end):
	for i in range(start, end):
		name = " ".join(global_movie_list[i].split(".")[0:-1])
		result = name_resolution(name)
		global_resolved_list.append([global_movie_list[i], result[0], result[1]])

def progress_bar():
	prev = -2
	while len(global_movie_list)  > len(global_resolved_list):
		if prev < len(global_resolved_list):
			print "\r", len(global_resolved_list) , " of ", len(global_movie_list)
			prev = len(global_resolved_list) 
		

# check to see if the cache file exists.
# if it does and is recent enough
try:
	file = open(cache_file, "r")
	#days since last modified
	a = datetime.timedelta(seconds=time.mktime(time.localtime()) - os.path.getmtime(cache_file))
	if a.days < 2:
		print "Cache is recent enough"
		global_movie_list = pickle.load(file)
	else:
		print "Recreating cache ..."
		create_movie_list()
except IOError:
	print "Creating cache ..."
	create_movie_list()


block_size = len(global_movie_list) / NUM_THREADS


threadarray = []

for i in range(0, NUM_THREADS):
	start = i * block_size
	end = start + block_size
	print "Setting up thread ", i, "start  ", start, "end ", end
	t = threading.Thread(target=multi_thread_name_resolve, args=(start, end))
	t.start()
	threadarray.append(t)

progressthread = threading.Thread(target=progress_bar)
progressthread.setDaemon(True)
progressthread.start()


for t in threadarray:
	t.join()

print "Done with the threads "


for stuff in global_resolved_list:
	print stuff[0], " | ", stuff[1], " | ", stuff[2]


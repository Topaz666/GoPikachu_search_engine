#This file is used to extract data from crawler and organize these data
#that can use to display in the webpage later. 
from crawler import crawler
from math import ceil
import codecs
from pprint import pprint 
import operator
import sqlite3
return_url = set()
res_file = './res.txt'

def Run_crawler():
	bot = crawler(None, "urls.txt")
	bot.crawl(depth=1)
	run_crawler_res = bot.get_resolved_inverted_index()
	return final_data

def URL_match_string(matchstring, res):
	for key,value in res.items():
		if matchstring == key: 
			return value

class urlList:
	def __init__(self, urllist, per_page):
		self.per_page = per_page
		self.total_count = len(urllist)
		self.url_list = urllist
		self.cur_page = 1
		self.total_page_num = (int)(ceil(float(len(urllist)) / per_page))

	def next_page(self):
		if (int)(self.cur_page) >= (int)(self.total_page_num):
			return self.cur_page
		else:
			return (int)(self.cur_page) + 1
	
	def prev_page(self):
		if (int)(self.cur_page) <= 1:
			return self.cur_page
		else:
			return (int)(self.cur_page) - 1
	
def flatten(getkeywords):
	for each in getkeywords:
		if not isinstance(each, list):
			yield str(each)
		else:
			for each1 in each:				
				yield str(each1)

if __name__ == "__main__":
	#url_after_filter = URL_match_string('hello') #this will uncomment if we start to crawler, because it is slow so, I copy result.
	aab = sqlite3.connect('dbFile.db')
	#b = aab.cursor()
	#print b
	#url = urlList(url_after_filter,5)
	#print (url_after_filter)
	#print (url.url_list[26])
	#print (url.total_page_num)
	#calculate_score(url_after_filter);
	print Run_crawler()
	#print (type(len(url.url_list[(i-1)*5:i*5])))
	#inv = bot.get_inverted_index()
	#for key,value in inv.items():
		#print ('{key}:{value}'.format(key = key, value = value))
	#calculate_score(url_after_filter)
	

from bottle import get, post, request, run, route, static_file, template, redirect,error,abort
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2WebServerFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from beaker.middleware import SessionMiddleware

import spellcorrect
import operator
import bottle
import codecs
import httplib2
import pagination
import sqlite3

con = sqlite3.connect("dbFile.db")
cur = con.cursor()
Input = []
misspelled = ""
urlList = []
login_mode = False;
return_url = []
CLIENT_ID = '125716807946-un0gi2j27hpje318p643lbeh2b8h3nje.apps.googleusercontent.com'
CLIENT_SECRET = 'WRxCdyY0Jg3H4Z_0_czh34tU'
SCOPE = 'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email'
REDIRECT_URI = 'http://localhost:8080/redirect'
multiword = []
trickKey = 0
user_id = ''
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': False,
    'session.data_dir': './TopRank',
	'session.auto': True
}

app = SessionMiddleware(bottle.app(), session_opts)


## Below is part of authentication of OAUTH2 google

## this is used to login google account, if you had already login then ignore prompt

history = {}
#this is a history dictionary which includes all the keywords and then ordered by frequency
def process_history(SearchingTerm):
	global history,user_id
	words = SearchingTerm.split()
	for term in words:
		if term in history:
			history[term]+= 1
		else:
			history[term] = 1
	if user_id != '':
		#very tricky bug, we must implement bottle.reques... than it will allow us to store.
		s = bottle.request.environ.get('beaker.session')
		temp = s.get(user_id,None)
		temp['History'] = history
		s.save()

	sorted_count = sorted(history.items(),key=operator.itemgetter(1))
	return sorted_count

#this is a input dictionary which includes all the keywords and then ordered by frequency
def process_input(SearchingTerm):
	local_count = dict()
	global multiword
	words = SearchingTerm.split()
	print(words)
	multiword = words
	for term in words:
		if term in local_count:
			local_count[term]+=1
		else:
			local_count[term] = 1
	sorted_count = sorted(local_count.items(),key=operator.itemgetter(1))
	return sorted_count


@route('/')
def frontpage():
	return template('FrontPage')


@route('/signinMode')
def loginpage():
	global user_id,history
	s = bottle.request.environ.get('beaker.session')
	temp = s.get(user_id,None)
	if user_id != '':
		if 'History' in temp:
			history =  temp['History']
			copyhistory = sorted(history.items(),key=operator.itemgetter(1))
		else:
			copyhistory = []
	else:
		return template('errorpage')
	return template('SigninfrontPage', user_ID = user_id ,user_name = temp['name'], user_picture = temp['picture'],History=copyhistory[-10:])


#this is loading image
@route('/static/<filename>')
def pikachu_image(filename):
	return static_file(filename, root='./img/')

@route('/get')
def get():
	#This is only for Lab1, extracting keyword and outputing history.
	global Input, urlList,return_url,misspelled
	getkeywords = request.query.keywords
	#getkeywords = list(pagination.flatten(getkeywords))
	if(getkeywords == ""):
		if(login_mode):
			redirect("/signinMode")
		else:
			redirect("/")
	Input = process_input(getkeywords)
	misspelled = ""
	for each in multiword:
		copymisspelled = each.encode("utf-8")
		print ("********",copymisspelled)
		misspelled += spellcorrect.correction(str(copymisspelled))+ " "
	print ("!!!!!!!!!!!!!!",misspelled)

	sql_extraction = cur.execute('SELECT * FROM word_url WHERE word in ({0})'.format(', '.join('?' for i in multiword)), multiword)
	return_url = []
	for item in sql_extraction:
		return_url.append((item[2].encode("utf-8"),item[3].encode("utf-8")))
	urlList = pagination.urlList(return_url,5)

	#print ("%%%%%%%%%%%%", misspelled)

	redirect("/&keywords="+getkeywords+"&page=1")

@route('/&keywords=<keywords>&page=<page_no>')
def web_pageintation(keywords,page_no):
	#print ("HHHHHHHHHHHHHHHHHHHHHHH", return_url)
	url_list_block = urlList.url_list[((int)(page_no)-1)*5:(int)(page_no)*5]
	urlList.cur_page = page_no
	next_page = urlList.next_page()
	prev_page = urlList.prev_page()
	firstchar = None
	i = 0
	found_like_phase = multiword
	if return_url != []: #if your entry is nothing
		print ("####################################")
		print ("total_page_num: ", urlList.total_page_num)
		print ("total_count: ", urlList.total_count)
		print ("per page: ", urlList.per_page)
		print ("next_page: ", next_page)
		print ("prev_page: ", prev_page)
		print ("length: ",len(url_list_block))
	else:
		print ("length: ",len(multiword))
		print ("type: ", type(multiword), multiword)
		while firstchar == None and i < len(multiword):
			print ("i +++++++:", i)
			firstchar = multiword[i][0:2] + "%"
			cur.execute('SELECT * FROM word_url WHERE word like ?', (firstchar,))
			firstchar = cur.fetchone()
			i += 1
	if firstchar == None:
		found_like_phase = None
	else:
		found_like_phase[i-1] = firstchar[4]
	print(found_like_phase)


	if(login_mode):
		copyhistory = process_history(keywords)
		s = bottle.request.environ.get('beaker.session')
		temp = s.get(user_id,None)
		return template('SigninMode_QueryPage',SearchingTerm=keywords, History=copyhistory[-10:], Input=Input, user_ID = user_id ,user_name = temp['name'], user_picture = temp['picture'], page_num = urlList.cur_page, next_page=next_page, prev_page=prev_page, url_list = url_list_block, pagelength= len(url_list_block),found_like_phase = found_like_phase, misspelled = misspelled)
	else:	#here is anonymous Mode
		return template('QueryPage', SearchingTerm=keywords, Input=Input, page_num = urlList.cur_page, next_page=next_page, prev_page=prev_page, url_list = url_list_block, pagelength= len(url_list_block),found_like_phase = found_like_phase, misspelled = misspelled)


@route('/login')
##we close google login in this lab
def login():
	flow = flow_from_clientsecrets("client_secret_125716807946-un0gi2j27hpje318p643lbeh2b8h3nje.apps.googleusercontent.com.json",scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email', redirect_uri='http://localhost:8080/redirect')
	url = flow.step1_get_authorize_url()
	bottle.redirect(str(url))

@route('/redirect')
def redirect_page():
	code = request.query.get('code', '')
	if code == '':
		redirect('/connecting')
	flow = OAuth2WebServerFlow(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,scope=SCOPE, redirect_uri=REDIRECT_URI)
	credentials = flow.step2_exchange(code)
	token = credentials.id_token['sub']
	http = httplib2.Http()
	http = credentials.authorize(http)
	# Get user email
	users_service = build('oauth2', 'v2', http=http)
	user_document = users_service.userinfo().get().execute()
	user_email = user_document['email']

	# save name and picture into cookie and key is email address
	temp_name = {'name':user_document.get('name', None)}
	user_data_list = {'picture':user_document.get('picture', None)}
	user_data_list = dict(temp_name, **user_data_list)
	global s,login_mode
	s = bottle.request.environ.get('beaker.session')
	if user_email not in s:
		print ("we are in the cookie")
		s[user_email] = user_data_list
		s.save()
	global user_id
	user_id = user_email
	login_mode = True
	bottle.redirect('/signinMode')


@route('/logout')
def logout():
	global user_id, history, login_mode
	print ("LOGOUT")
	user_id = ''
	history = {}
	login_mode = False
	bottle.redirect('/')

#error page
@error(404)
def error404(error):
    return template('errorpage')

@route('/error')
def errorpage():
	abort(404)

if __name__ == '__main__':
	run(app = app, host='localhost', port=8080, debug=True)

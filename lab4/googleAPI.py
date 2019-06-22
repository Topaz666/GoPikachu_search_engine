from bottle import get, post, request, run, route, static_file, template, redirect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2WebServerFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from beaker.middleware import SessionMiddleware
import operator
import bottle
import codecs
import httplib2
import Lab1

CLIENT_ID = '125716807946-un0gi2j27hpje318p643lbeh2b8h3nje.apps.googleusercontent.com'
CLIENT_SECRET = 'WRxCdyY0Jg3H4Z_0_czh34tU'
SCOPE = 'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email'
REDIRECT_URI = 'http://localhost:8080/redirect'


session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './TopRank',
    'session.auto': True
}

app = SessionMiddleware(bottle.app(), session_opts)


## Below is part of authentication of OAUTH2 google

## this is used to login google account, if you had already login then ignore prompt
@route('/login')
def login():
	flow = flow_from_clientsecrets("client_secret_125716807946-un0gi2j27hpje318p643lbeh2b8h3nje.apps.googleusercontent.com.json",scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email', redirect_uri="http://localhost:8080/redirect")
	uri = flow.step1_get_authorize_url()
	bottle.redirect(str(uri))

@route('/redirect')
def redirect_page():
	code = request.query.get('code', '')
	if code == '':
		redirect('/')
	flow = OAuth2WebServerFlow(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,scope=SCOPE, redirect_uri=REDIRECT_URI)
	credentials = flow.step2_exchange(code)
	token = credentials.id_token['sub']
	http = httplib2.Http()
	http = credentials.authorize(http)
	# Get user email
	users_service = build('oauth2', 'v2', http=http)
	user_document = users_service.userinfo().get().execute()
	user_email = user_document['email']
	
	temp_name = {'name':user_document.get('name', None)}
	user_data_list = {'picture':user_document.get('picture', None)}
	user_data_list = dict(temp_name, **user_data_list)

	s = bottle.request.environ.get('beaker.session')
	if user_email not in s:
		print 'we are in the s'
		s[user_email] = user_data_list
	print s
	print '\n'
	bottle.redirect('/loginpage')

#route('/logout')
#def logout():

if __name__ == '__main__':
	run(app = app, host='localhost', port=8080, debug=True)

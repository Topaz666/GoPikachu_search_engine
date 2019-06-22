from crawler import crawler
import unittest
import pprint
import operator
class crawlerTest(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		print ('Let us start the unit test')
	
	@classmethod
	def tearDownClass(self):
		print('Finish Unit test')
		
	#In our test, Pikachu, search are existing in these two websides, charmander is only existing in pokedex.org
	def test_run(self):
		bot = crawler(None, "test.txt")
		bot.crawl(depth=0)
		res = bot.get_resolved_inverted_index()
		inv = bot.get_inverted_index()
		# We check both two websites 
		self.assertEqual(res.get('pikachu'), set(['http://localhost:8080/', 'https://pokedex.org/']))
		self.assertEqual(res.get('charmander'), set(['https://pokedex.org/']))
		self.assertEqual(res.get('search'), set(['http://localhost:8080/', 'https://pokedex.org/']))
		print 'Pass all tests '

def Lab3Test():
	bot = crawler(None, "urls.txt")
	bot.crawl(depth=1)
	score = bot.get_score()
	sort = sorted(score.items(), key=operator.itemgetter(1), reverse = True)
	for item in sort:
			pprint.pprint(item)

if __name__=='__main__':
	'''print '---------------Lab1 Crawler Test---------------'	
	unittest.main()

	for key,value in res.items():
		print ('{key}:{value}'.format(key = key, value = value))'''

	print '\n\n\n---------------Lab3 Crawler Test---------------'
	Lab3Test()
































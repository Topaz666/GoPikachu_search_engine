from crawler import crawler
import unittest
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
		print 'Pass all tests'
if __name__=='__main__':
	unittest.main()

	for key,value in res.items():
		print ('{key}:{value}'.format(key = key, value = value))

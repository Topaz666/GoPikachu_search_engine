
# Copyright (C) 2011 by Peter Goodman
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib.request
import urllib.parse
import collections
from bs4 import BeautifulSoup
from collections import defaultdict
import re
import pagerank
import sqlite3
import codecs
import operator
res_file = './res.txt'

def attr(elem, attr):
    """An html attribute from an html element. E.g. <a href="">, then
    attr(elem, "href") will get the href or an empty string."""
    try:
        return elem[attr]
    except:
        return ""

WORD_SEPARATORS = re.compile(r'\s|\n|\r|\t|[^a-zA-Z0-9\-_]')

class crawler(object):
    """Represents 'Googlebot'. Populates a database by crawling and indexing
    a subset of the Internet.

    This crawler keeps track of font sizes and makes it simpler to manage word
    ids and document ids."""

    def __init__(self, db_conn, url_file):
        """Initialize the crawler with a connection to the database to populate
        and with the file containing the list of seed URLs to begin indexing."""
        self._url_queue = [ ]
        self._doc_id_cache = { }
        self._word_id_cache = { }
        self._inverted_index = {}
        self._resolved_inverted_index = {}

        self._url = {}
        self._word = {}
        self._score = {}
        self._ret_doc_text = {}
        self._links = set()
        self._url_docid = dict()


        # functions to call when entering and exiting specific tags
        self._enter = defaultdict(lambda *a, **ka: self._visit_ignore)
        self._exit = defaultdict(lambda *a, **ka: self._visit_ignore)

        # add a link to our graph, and indexing info to the related page
        self._enter['a'] = self._visit_a

        # record the currently indexed document's title an increase
        # the font size
        def visit_title(*args, **kargs):
            self._visit_title(*args, **kargs)
            self._increase_font_factor(7)(*args, **kargs)

        # increase the font size when we enter these tags
        self._enter['b'] = self._increase_font_factor(2)
        self._enter['strong'] = self._increase_font_factor(2)
        self._enter['i'] = self._increase_font_factor(1)
        self._enter['em'] = self._increase_font_factor(1)
        self._enter['h1'] = self._increase_font_factor(7)
        self._enter['h2'] = self._increase_font_factor(6)
        self._enter['h3'] = self._increase_font_factor(5)
        self._enter['h4'] = self._increase_font_factor(4)
        self._enter['h5'] = self._increase_font_factor(3)
        self._enter['title'] = visit_title

        # decrease the font size when we exit these tags
        self._exit['b'] = self._increase_font_factor(-2)
        self._exit['strong'] = self._increase_font_factor(-2)
        self._exit['i'] = self._increase_font_factor(-1)
        self._exit['em'] = self._increase_font_factor(-1)
        self._exit['h1'] = self._increase_font_factor(-7)
        self._exit['h2'] = self._increase_font_factor(-6)
        self._exit['h3'] = self._increase_font_factor(-5)
        self._exit['h4'] = self._increase_font_factor(-4)
        self._exit['h5'] = self._increase_font_factor(-3)
        self._exit['title'] = self._increase_font_factor(-7)

        # never go in and parse these tags
        self._ignored_tags = set([
            'meta', 'script', 'link', 'meta', 'embed', 'iframe', 'frame',
            'noscript', 'object', 'svg', 'canvas', 'applet', 'frameset',
            'textarea', 'style', 'area', 'map', 'base', 'basefont', 'param',
        ])

        # set of words to ignore
        self._ignored_words = set([
            '', 'the', 'of', 'at', 'on', 'in', 'is', 'it',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z', 'and', 'or',
        ])

        # TODO remove me in real version
        self._mock_next_doc_id = 1
        self._mock_next_word_id = 1

        # keep track of some info about the page we are currently parsing
        self._curr_depth = 0
        self._curr_url = ""
        self._curr_doc_id = 0
        self._font_size = 0
        self._curr_words = None

		#here is where we start to read in the file urls.txt
        # get all urls into the queue
        try:
            with open(url_file, 'r') as f:
                for line in f:
                    self._url_queue.append((self._fix_url(line.strip(), ""), 0))
        except IOError:
            pass

    # TODO remove me in real version
    def _mock_insert_document(self, url):
        """A function that pretends to insert a url into a document db table
        and then returns that newly inserted document's id."""
        ret_id = self._mock_next_doc_id
        self._mock_next_doc_id += 1
        elem = [ret_id, str(url), ""]


        return ret_id

    # TODO remove me in real version
    def _mock_insert_word(self, word):
        """A function that pretends to inster a word into the lexicon db table
        and then returns that newly inserted word's id."""
        ret_id = self._mock_next_word_id
        self._mock_next_word_id += 1
        return ret_id

    def word_id(self, word):
        """Get the word id of some specific word."""
        if word in self._word_id_cache:
            return self._word_id_cache[word]

        # TODO: 1) add the word to the lexicon, if that fails, then the
        #          word is in the lexicon
        #       2) query the lexicon for the id assigned to this word,
        #          store it in the word id cache, and return the id.

        word_id = self._mock_insert_word(word)
        self._word_id_cache[word] = word_id
        return word_id



    def document_id(self, url):
        """Get the document id for some url."""
        if url in self._doc_id_cache:
            return self._doc_id_cache[url]

        # TODO: just like word id cache, but for documents. if the document
        #       doesn't exist in the db then only insert the url and leave
        #       the rest to their defaults.

        doc_id = self._mock_insert_document(url)
        self._doc_id_cache[url] = doc_id
        return doc_id

    def _fix_url(self, curr_url, rel):
        """Given a url and either something relative to that url or another url,
        get a properly parsed url."""
		# curr_url contaons information of url and rel is empty

        rel_l = rel.lower()
        if rel_l.startswith("http://") or rel_l.startswith("https://"):
            curr_url, rel = rel, ""
            #curr_url = rel, rel = " "?
        # compute the new url based on import
        curr_url = urlparse.urldefrag(curr_url)[0]
        parsed_url = urlparse.urlparse(curr_url)
        return urlparse.urljoin(parsed_url.geturl(), rel)

    def add_link(self, from_doc_id, to_doc_id):
        """Add a link into the database, or increase the number of links between
        two pages in the database."""
        # TODO
        temp = (from_doc_id, to_doc_id)
        self._links.add(temp)

    def _visit_title(self, elem):
        """Called when visiting the <title> tag."""
        title_text = self._text_of(elem).strip()
        print ("document title= " + repr(title_text))


        # TODO update document title for document id self._curr_doc_id
        self._ret_doc_text[self._curr_doc_id] = title_text



    def _visit_a(self, elem):
        """Called when visiting <a> tags."""

        dest_url = self._fix_url(self._curr_url, attr(elem,"href"))

        #print "href="+repr(dest_url), \
        #      "title="+repr(attr(elem,"title")), \
        #      "alt="+repr(attr(elem,"alt")), \
        #      "text="+repr(self._text_of(elem))

        # add the just found URL to the url queue
        self._url_queue.append((dest_url, self._curr_depth))

        # add a link entry into the database from the current document to the
        # other document
        self.add_link(self._curr_doc_id, self.document_id(dest_url))

        # TODO add title/alt/text to index for destination url

    def _add_words_to_document(self):
        # TODO: knowing self._curr_doc_id and the list of all words and their
        #       font sizes (in self._curr_words), add all the words into the
        #       database for this document
        print ("    num words="+ str(len(self._curr_words)))

    def _increase_font_factor(self, factor):
        """Increade/decrease the current font size."""
        def increase_it(elem):
            self._font_size += factor
        return increase_it

    def _visit_ignore(self, elem):
        """Ignore visiting this type of tag"""
        pass

    def _add_text(self, elem):
        """Add some text to the document. This records word ids and word font sizes
        into the self._curr_words list for later processing."""
        words = WORD_SEPARATORS.split(elem.string.lower())
        for word in words:
            word = word.strip()
            if word in self._ignored_words:
                continue
            self._curr_words.append((self.word_id(word), self._font_size))
            self._word[self.word_id(word)] =word

            WordID = self.word_id(word)

            if word not in self._resolved_inverted_index:
                self._resolved_inverted_index[word] = {self._curr_url}
            else:
                self._resolved_inverted_index[word].add(self._curr_url)

            if WordID not in self._inverted_index:
                self._inverted_index[WordID] = {self._curr_doc_id}
            else:
                self._inverted_index[WordID].add(self._curr_doc_id)


    def _text_of(self, elem):
        """Get the text inside some element without any tags."""
        if isinstance(elem, Tag):
            text = [ ]
            for sub_elem in elem:
                text.append(self._text_of(sub_elem))

            return " ".join(text)
        else:
            return elem.string

    def _index_document(self, soup):
        """Traverse the document in depth-first order and call functions when entering
        and leaving tags. When we come accross some text, add it into the index. This
        handles ignoring tags that we have no business looking at."""
        class DummyTag(object):
            next = False
            name = ''

        class NextTag(object):
            def __init__(self, obj):
                self.next = obj

        tag = soup.html
        stack = [DummyTag(), soup.html]

        while tag and tag.next:
            tag = tag.next

            # html tag
            if isinstance(tag, Tag):

                if tag.parent != stack[-1]:
                    self._exit[stack[-1].name.lower()](stack[-1])
                    stack.pop()

                tag_name = tag.name.lower()

                # ignore this tag and everything in it
                if tag_name in self._ignored_tags:
                    if tag.nextSibling:
                        tag = NextTag(tag.nextSibling)
                    else:
                        self._exit[stack[-1].name.lower()](stack[-1])
                        stack.pop()
                        tag = NextTag(tag.parent.nextSibling)

                    continue

                # enter the tag
                self._enter[tag_name](tag)
                stack.append(tag)

            # text (text, cdata, comments, etc.)
            else:
                self._add_text(tag)

    def crawl(self, depth=2, timeout=3):
        """Crawl the web!"""
        seen = set()

        while len(self._url_queue):

            url, depth_ = self._url_queue.pop()

            # skip this url; it's too deep
            if depth_ > depth:
                continue

            doc_id = self.document_id(url)

            # we've already seen this document
            if doc_id in seen:
                continue

            seen.add(doc_id) # mark this document as haven't been visited

            socket = None
            try:
                socket = urllib2.urlopen(url, timeout=timeout)
                soup = BeautifulSoup(socket.read())

                self._curr_depth = depth_ + 1
                self._curr_url = url
                self._curr_doc_id = doc_id
                self._font_size = 0
                self._curr_words = [ ]
                self._index_document(soup)
                self._add_words_to_document()
                self._url[self.document_id(url)] =url
                print ("    url="+repr(self._curr_url))
                self._url_docid[doc_id] = url
            except Exception as e:
                print (e)
                pass
            finally:
                if socket:
                    socket.close()


    def get_inverted_index(self):
        temp = collections.OrderedDict()
        temp = self._inverted_index
        return temp

    def get_resolved_inverted_index(self):
        temp = collections.OrderedDict()
        temp = self._resolved_inverted_index
        return temp


    def get_score(self):
        page_rank_score = pagerank.page_rank(self._links)
        for docid in page_rank_score:
            self._score[docid] = page_rank_score[docid]

        return self._score


    def get_url(self,item):
        #print item
        return self._url_docid[item]


    def store_to_database(self):
        con = sqlite3.connect("dbFile.db")
        cur = con.cursor()

        for word_id in self._word:
            cur.execute("INSERT INTO lexicon(word_id, word) VALUES (?,?)", (word_id, self._word[word_id]))

        for doc_id in self._url:
            print(self._url,self._ret_doc_text)
            if doc_id not in self._ret_doc_text.keys():
                self._ret_doc_text[doc_id] = 'Title not defined'
            cur.execute("INSERT INTO document_index(doc_id, document, doc_name) VALUES (?,?,?)", (doc_id, self._url[doc_id], self._ret_doc_text[doc_id]))

        for word_id in self._inverted_index:
            for doc_id in self._inverted_index[word_id]:
                cur.execute("INSERT INTO inverted_index(word_id, doc_id) VALUES (?,?)", (word_id, doc_id))

        for doc_id in self._score:
            print (doc_id)
            cur.execute("INSERT INTO pagerank_scores(doc_id, score) VALUES (?,?)", (doc_id, self._score[doc_id]))

        cur.execute("insert into word_url select word_id, T2.doc_id as doc_id, document, doc_name,word, score from(select T.word_id as word_id, T.doc_id as doc_id, T.document as document, T.doc_name as doc_name,word from lexicon inner join (select word_id, document_index.doc_id as doc_id, document,doc_name from document_index inner join inverted_index on document_index.doc_id = inverted_index.doc_id) as T on lexicon.word_id = T.word_id) as T2 inner join pagerank_scores on pagerank_scores.doc_id = T2.doc_id order by score desc")
        con.commit()
        con.close()

    def calculate_score(self):
        score = self.get_score()
        sort = sorted(score.items(), key=operator.itemgetter(1), reverse = True)
        print (sort)
        return_url = set()
        for item in sort:
            return_url.add(bot.get_url(item[0]))
        return (return_url)



if __name__ == "__main__":
    bot = crawler(None, "urls.txt")
    bot.crawl(depth=1)
    fout =codecs.open(res_file, 'w')
    for item in bot._url_docid:
        fout.write(bot._url_docid[item] +'\n')
    fout.close()
    bot = crawler(None, "res.txt")
    bot.crawl(depth=0)
   ############################################
    #inv = bot.get_inverted_index()
    #for key,value in inv.items():
     #   print ('{key}:{value}'.format(key = key, value = value))

    #res = bot.get_resolved_inverted_index()
    #for key,value in res.items():
     #   print ('{key}:{value}'.format(key = key, value = value))
    #bot.get_score()
    #print ("word_id_cache: ",bot._word_id_cache)
   ##############################################
    return_url = bot.calculate_score()
    con = sqlite3.connect("dbFile.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS lexicon(word_id INTEGER, word TEXT UNIQUE, PRIMARY KEY (word_id));")
    cur.execute("CREATE TABLE IF NOT EXISTS document_index(doc_id INTEGER, document TEXT UNIQUE, doc_name TEXT,PRIMARY KEY (doc_id));")
    cur.execute("CREATE TABLE IF NOT EXISTS inverted_index(word_id INTEGER KEY, doc_id INTEGER);")
    cur.execute("CREATE TABLE IF NOT EXISTS pagerank_scores(doc_id INTEGER, score TEXT, PRIMARY KEY (doc_id));")
    cur.execute("CREATE TABLE IF NOT EXISTS word_url(word_id INTEGER, doc_id TEXT, url TEXT, url_name TEXT,word TEXT, score FLOAT, PRIMARY KEY (doc_id, word_id));")
    con.commit()
    con.close()
    bot.store_to_database()

import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pymongo import MongoClient
from collections import deque

# Create a database connection object using pymongo
DB_NAME = "assignment_3"
DB_HOST = "localhost"
DB_PORT = 27017
db = None
pages = None
try:
    client = MongoClient(host=DB_HOST, port=DB_PORT)
    db = client[DB_NAME]
    pages = db['Pages']
except:
    print("Database not connected successfully")

SEED_URL = "https://www.cpp.edu/sci/computer-science/"
CPP_BASE_URL = "https://www.cpp.edu/"
IS_RELATIVE_URL_RE = r'^(?!https?:\/\/www.)' # Does not contain url beginning
IS_CPP_FULL_ADDRESS_RE = r'^https?:\/\/www.cpp.edu'
IS_HTML_OR_SHTML_RE = r'^.*\.s?html\/?$'

# Use deque for O(1) time to pop the head url
# A list would take O(n) time to pop the head url because it needs to shift the rest of the elements by 1
frontier = deque([SEED_URL])
# Use a set to determine if a url has been visited already so we don't visit it twice
visited_urls = set()

# While there are still url's in frontier, crawl
while frontier:
    try:
        url = frontier.popleft()
        if(url == TARGET_URL):
            print('found target url')
        html = urlopen(url)

        html_response_body = html.read()
        bs = BeautifulSoup(html_response_body, 'html.parser')

        # Check if page is our target ( contains <h1 class="cpp-h1">Permanent Faculty</h1> )
        target = bs.find('h1', { 'class': 'cpp-h1' }, string='Permanent Faculty')
        if (target):
            # Store page in MongoDB pages collection with target flag
            pages.insert_one({ '_id': url, 'html': html_response_body.decode('utf-8'), 'isTarget': True })
            # Stop crawling
            break
        else:
            # Store page in MongoDB pages collection
            pages.insert_one({ '_id': url, 'html': html_response_body.decode('utf-8') })
            linked_urls = []
            # Find all <a> tags that has an href
            a_tags_with_href = bs.find_all('a', href=True)

            # Store all unique forward links in linkedUrls
            for a in a_tags_with_href:
                # Remove any leading or trailing whitespaces
                url = a['href'].strip()

                # Remove any trailing / character
                if re.match(r'^.*\/$', url):
                    url = url[:-1]

                # Convert relative addresses to full addresses
                if re.match(IS_RELATIVE_URL_RE, url):
                    # Remove leading / if relative url starts with it
                    if re.match(r'^\/', url):
                        url = url[1:]

                    # Remove leading ~ if relative url starts with it
                    if re.match(r'^~', url):
                        url = url[1:]

                    url = CPP_BASE_URL + url
                
                # Filter for .html or shtml files and CPP only urls
                if re.match(IS_HTML_OR_SHTML_RE, url) and re.match(IS_CPP_FULL_ADDRESS_RE, url):
                    # Store each url in our linkedUrls array if not already in it
                    if url not in linked_urls:
                        linked_urls.append(url)
            
            # Add any non visited url's to frontier and to visited_urls
            for url in linked_urls:
                if url not in visited_urls:
                    visited_urls.add(url)
                    frontier.append(url)
    except Exception as e:
        print(e)
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Create a database connection object using pymongo
DB_NAME = "assignment_3"
DB_HOST = "localhost"
DB_PORT = 27017
db = None
pages = None
professors = None
try:
    client = MongoClient(host=DB_HOST, port=DB_PORT)
    db = client[DB_NAME]
    pages = db['Pages']
    professors = db['Professors']
except:
    print("Database not connected successfully")

# Retrieve the target html from the Pages Collection in MongoDB
target_page = pages.find_one({ 'isTarget': True })
target_html = target_page['html']
bs = BeautifulSoup(target_html, 'html.parser')

for div in bs.find_all('div', { 'class': 'clearfix' }):
    professor_info = {}

    # NAME
    try:
        professor_info['name'] = div.find('h2').get_text().strip()
    except:
        # If no name, then it is an empty div. Continue to the next div
        continue

    # TITLE
    try:
        professor_info['title'] = div.find('strong', string=re.compile(r'Title')).next_sibling.strip()
    except:
        print(professor_info['name'] + " does not have a title listed")

    # OFFICE
    try:
        professor_info['office'] = div.find('strong', string=re.compile(r'Office')).next_sibling.strip()
    except:
        print(professor_info['name'] + " does not have an office listed")

    # PHONE
    try:
        professor_info['phone'] = div.find('strong', string=re.compile(r'Phone')).next_sibling.strip()
    except:
        print(professor_info['name'] + " does not have a phone listed")

    # EMAIL
    try:
        professor_info['email'] = div.find('strong', string=re.compile(r'Email')).next_sibling.next_sibling.get_text().strip()
    except:
        print(professor_info['name'] + " does not have an email listed")

    # WEBSITE
    try:
        professor_info['website'] = div.find('strong', string=re.compile(r'Web')).next_sibling.next_sibling.get_text().strip()
    except:
        print(professor_info['name'] + " does not have a website listed")

    # Clean up text
    for key, value in professor_info.items():
        # Replace various whitespace characters with just a space
        professor_info[key] = ' '.join(value.split())

        # Clean up some text that start with ': '
        # (Why is the structure so inconsistent?? We spent so much money on this website)
        if (re.match(r'^: ', value)):
            professor_info[key] = value[2:]

    # Add professor info to the database
    professors.insert_one(professor_info)
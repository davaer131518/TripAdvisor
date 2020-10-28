#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
import requests
import time
from selenium import webdriver
import pandas as pd
from tqdm.notebook import tqdm
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent


# In[2]:


flatten = lambda l: [item for sublist in l for item in sublist]


# In[3]:


url_part1 = 'https://www.tripadvisor.com/Restaurants-g293932-'
url_part2 = 'oa'
url_part3 = '-Yerevan.html'
base_url = 'https://www.tripadvisor.com'
ua = UserAgent()
options = Options()
user_agent = ua.random
options.add_argument(f'user-agent={user_agent}')
options.add_argument("--incognito")


# In[4]:


pages = []
pages.append('https://www.tripadvisor.com/Restaurants-g293932-Yerevan.html')
for i in range(27):
    pages.append(url_part1 + url_part2 + str((i + 1)*30) + url_part3)


# In[5]:


all_links = []
for page in tqdm(pages):
    headers = {'User-Agent': ua.random}
    content = requests.get(page, headers = headers, timeout = 3)
    soup = BeautifulSoup(content.text, 'html.parser')
    rest_container = soup.find('div', class_ = '_1kXteagE')
    btf_restcontainer = BeautifulSoup(str(rest_container), 'html.parser')
    
    narrowContainer = btf_restcontainer.find_all('div', class_ = 'wQjYiB7z')
    rawlink = [i.find('a', {'href': True}) for i in narrowContainer]
    link = [i['href'] for i in rawlink]
    full_link = [base_url + i for i in link]
    all_links.append(full_link)
all_links = flatten(all_links)
all_links = set(all_links)


# In[6]:


all_names = []
all_ratings = []
rating_count = []
all_longLat = []
all_address = []
for link in tqdm(all_links):
    browser = webdriver.Chrome(options=options)
    browser.get(link)
    time.sleep(3)
    source = browser.page_source
    soup = BeautifulSoup(source, 'html.parser')
    
    test_name = soup.find('h1', {'data-test-target':'top-info-header'})
    if test_name:    
        name = soup.find('h1', {'data-test-target':'top-info-header'}).text.strip()
        all_names.append(name)
    else:
        name = 'Not available'
        all_names.append(name)
    
    test = soup.find('span', {'class':'r2Cf69qf'})
    if test:
        rating = soup.find('span', {'class':'r2Cf69qf'}).text.strip()
        rating_amount = soup.find('a', {'class':'_10Iv7dOs'}).text.strip()
        all_ratings.append(rating)
        rating_count.append(rating_amount)
    else:
        rating = 'No rating'
        rating_amount = '0 reviews'
        all_ratings.append(rating)
        rating_count.append(rating_amount)
        
    tester_longlat = soup.find('img', {'class':'rAA8XwlX'})
    if tester_longlat:
        longlat_container = soup.find('img', {'class':'rAA8XwlX'})
        longlat_container = str(longlat_container)
        a = longlat_container.replace('<img alt="" class="rAA8XwlX" src="https://maps.google.com/maps/api/staticmap?&amp;channel=ta.desktop.restaurant_review&amp;zoom=15&amp;size=347x137&amp;scale=1&amp;client=gme-tripadvisorinc&amp;format=jpg&amp;sensor=false&amp;language=en_US&amp;center=', '').replace('&amp;maptype=roadmap&amp;&amp;markers=icon:http%3A%2F%2Fc1.tacdn.com%2F%2Fimg2%2Fmaps%2Ficons%2Fcomponent_map_pins_v1%2FR_Pin_Small.png|',' ').replace('&amp;signature=',' ').replace('="/>','')
        long_lat = a.split()[0]
        all_longLat.append(long_lat)
        all_address.append('')
    else:
        address = soup.find('span', {'class':'_2saB_OSe'}).text.strip()
        long_lat = 'Not available'
        all_address.append(address)
        all_longLat.append(long_lat)
      


# In[7]:


df = pd.DataFrame({"Restaurant Names" : all_names, "Rating" : all_ratings, "Rating Count" : rating_count, "Coordinates" : all_longLat, "Addresses" : all_address})
df.to_csv(r'C:\Users\PREDATOR\Desktop\Projects\Data Visualization\TripAdvisorRestaurant.csv', index = False)


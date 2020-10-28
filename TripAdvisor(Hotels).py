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


url_part1 = 'https://www.tripadvisor.com/Hotels-g293932-'#Yerevan-Hotels.html
url_part2 = 'oa'
url_part3 = '-Yerevan-Hotels.html'
base_url = 'https://www.tripadvisor.com'
ua = UserAgent()
options = Options()
user_agent = ua.random
options.add_argument(f'user-agent={user_agent}')
options.add_argument("--incognito")


# In[4]:


pages = []
pages.append('https://www.tripadvisor.com/Hotels-g293932-Yerevan-Hotels.html')
for i in range(25):
    pages.append(url_part1 + url_part2 + str((i + 1)*30) + url_part3)
    


# In[6]:


all_links = []
for page in tqdm(pages):
    headers = {'User-Agent': ua.random}
    content = requests.get(page, headers = headers, timeout = 3)
    soup = BeautifulSoup(content.text, 'html.parser')
    hotels_container = soup.find('div', class_ = 'ppr_rup ppr_priv_hsx_hotel_list_lite')
    btf_hotelscontainer = BeautifulSoup(str(hotels_container), 'html.parser')
    
    narrowContainer = btf_hotelscontainer.find_all('div', class_ = 'listing_title')
    rawlink = [i.find('a', {'href': True}) for i in narrowContainer]
    link = [i['href'] for i in rawlink]
    full_link = [base_url + i for i in link]
    all_links.append(full_link)
all_links = flatten(all_links)


# In[22]:


all_names = []
all_prices = []
all_ratings = []
rating_count = []
restaurants = []
attractions = []
for link in tqdm(all_links):
    browser = webdriver.Chrome(options=options)
    browser.get(link)
    time.sleep(3)
    source = browser.page_source
    soup = BeautifulSoup(source, 'html.parser')
#     headers = {'User-Agent': ua.random}
#     content = requests.get(link, headers = headers, timeout = 3)
#     soup = BeautifulSoup(content.text, 'html.parser')

    name = soup.find('div', class_ = '_1vnZ1tmP').text.strip()
    all_names.append(name)

    test_price = soup.find('div', class_ = 'CEf5oHnZ')
    test_price2 = soup.find('div', class_ = '_36QMXqQj autoResize')
    test_price3 = soup.find('div', class_ = '_36QMXqQj')

    if test_price3:
        price = soup.find('div', class_ = '_36QMXqQj').text.replace('AMD\xa0', '').strip()
        all_prices.append(price)
        
    elif test_price2:
        price = soup.find('div', class_ = '_36QMXqQj autoResize').text.replace('AMD\xa0', '').strip()
        all_prices.append(price)

    elif test_price:
        price = soup.find('div', class_ = 'CEf5oHnZ').text.replace('AMD\xa0', '').strip()
        all_prices.append(price)
        
    else:
        price = 'Not available'
        all_prices.append(price)
        
    test_rating = soup.find('span', {'class':'_3cjYfwwQ'})
    if test_rating:
        rating = soup.find('span', {'class':'_3cjYfwwQ'}).text.strip()
        rating_amount = soup.find('span', {'class':'_3jEYFo-z'}).text.strip()
        rating_count.append(rating_amount)
        all_ratings.append(rating)
        
    else:
        rating = 'No rating'
        rating_amount = '0 reviews'
        rating_count.append(rating_amount)
        all_ratings.append(rating)
    
    test_restaurant = soup.find('span', {'class':'oPMurIUj TrfXbt7b'})
    if test_restaurant:
        amountof_rests = soup.find('span', {'class':'oPMurIUj TrfXbt7b'}).text.strip() + ' restaurants within walking distance.'
        restaurants.append(amountof_rests)
    else:
        amountof_rests = 'None within walking distance'
        restaurants.append(amountof_rests)        
    
    test_attrac = soup.find('span', {'class':'oPMurIUj _1WE0iyL_'})
    if test_restaurant:
        amountof_attrac = soup.find('span', {'class':'oPMurIUj _1WE0iyL_'}).text.strip() + ' attraction areas within walking distance.'
        attractions.append(amountof_attrac)
        
    else:
        amountof_attrac = 'None within walking distance'
        attractions.append(amountof_attrac)


# In[35]:


df = pd.DataFrame({"Hotel Names" : all_names, "Price" : all_prices, "Rating" : all_ratings, "Rating Count" : rating_count, "Nearby Resaurants" : restaurants, "Nearby Attractions" : attractions})
df.to_csv(r'C:\Users\PREDATOR\Desktop\Projects\Data Visualization\TripAdvisor.csv', index = False)


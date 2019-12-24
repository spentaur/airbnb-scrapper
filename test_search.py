import requests
from random import uniform
from time import sleep
import csv
import pprint as pp
import json
from urllib import parse

if __name__ == '__main__':

    params = {'_format':         'for_explore_search_web',
              'currency':        'USD',
              'items_per_grid':  '18',
              'key':             'd306zoyjsyarp7ifhu67rjxn52tv0t20',
              'price_min':       '601',
              'query':           'Chicago, IL, United States',
              'search_type':     'pagination',
              'selected_tab_id': 'home_tab'}

    r = requests.get(
        'https://www.airbnb.com/api/v2/explore_tabs', params=params)
    status = r.status_code
    if status == 200:
        num_of_listings = 0
        results = r.json()['explore_tabs'][0]
        with open('data.txt', 'w') as outfile:
            json.dump(r.json(), outfile)

        sections = results['sections']
        print("number of sections", len(sections))
        for section in sections:
            if 'listings' in section:
                tmp_listings = section['listings']
                print("number of listings in section",
                      len(tmp_listings))
                for listing in tmp_listings:
                    num_of_listings += 1
                    print(listing['listing']['name'])

        print("num of listings on page", num_of_listings)
        print("total listings", results['home_tab_metadata']['listings_count'])

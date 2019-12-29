import csv
import datetime
import os
from random import uniform
from time import sleep

import requests
from boto3 import session
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':

    today = datetime.date.today()

    # credentials for digital ocean
    ACCESS_ID = os.getenv("ACCESS_ID")
    SECRET_KEY = os.getenv("SECRET_KEY")

    # setting up for digital ocean upload
    session = session.Session()
    client = session.client('s3',
                            region_name='nyc3',
                            endpoint_url='https://nyc3.digitaloceanspaces.com',
                            aws_access_key_id=ACCESS_ID,
                            aws_secret_access_key=SECRET_KEY)
    # url
    url = 'https://www.airbnb.com/api/v2/explore_tabs'

    # listing id's that are going to get saved to a csv, maybe not the most
    # efficient but it's only like 10k records and only just id's so oh well
    listing_ids = set()

    # total estimated listings
    total_estimated_listings = 0
    # total actual listings
    total_actual_listings = 0

    # max attempts
    attempts = 0
    max_attempts = 10

    estimated_number_of_pages = None

    estimated_listings_in_range = None

    for price in range(10, 406):
        # print price range
        print(f"price range: {price}")
        # url query string
        params = {'_format':         'for_explore_search_web',
                  'currency':        'USD',
                  'items_per_grid':  '18',
                  'key':             'd306zoyjsyarp7ifhu67rjxn52tv0t20',
                  'query':           'Chicago, IL, United States',
                  'search_type':     'pagination',
                  'selected_tab_id': 'home_tab',
                  'price_min':       price}
        # add price range to params
        if price < 404:
            params['price_max'] = price

        # set up the pagination stuff, it works with an offset, so it's page
        # * 18, first page is 0 so offset is 0
        page = 0
        # this is just to make sure that i'm not getting the same results if
        # i set the offset to something, because i've noticed that
        # "has_next_page" can't always be trusted
        prev_page_ids = set()
        has_next_page = True

        items_offset = 0

        # how many listings per range actually gotten
        listings_per_range = 0
        ids_per_range = set()

        while has_next_page:
            # loop through the pages for each given price range

            # make the actual request
            r = requests.get(url, params=params)

            # reset attempts
            attempts = 0

            # check the status code
            status = r.status_code
            if status == 200:
                page_listing_ids = set()
                if page:
                    items_offset += len(prev_page_ids)
                    print("offset: ", items_offset)
                    params['items_offset'] = items_offset

                # increment page
                page += 1

                # reset attempts
                attempts = 0

                # get the json results only care about explore tabs i think
                # which is 1 element array of dictionaries so just get the
                # first element
                results = r.json()['explore_tabs'][0]

                # print the theoretical number of listings
                if page == 1:
                    estimated_listings_in_range = results['home_tab_metadata'][
                        'listings_count']
                    print("estimated number of listings in range:",
                          estimated_listings_in_range)

                    # add estimated listings in range to estimated total
                    # listings
                    total_estimated_listings += estimated_listings_in_range

                    estimated_number_of_pages = -(
                            estimated_listings_in_range // -18)
                    print("estimated number of pages:",
                          estimated_number_of_pages)
                    print("\n")
                if estimated_number_of_pages:
                    print(f"page: {page} / {estimated_number_of_pages}")

                # update has next page, this will break the while loop. i'm
                # pretty sure this is always returned, i should verify that tho
                has_next_page = results['pagination_metadata']['has_next_page']

                # sections is where the "results" are stored
                sections = results['sections']
                for section in sections:
                    if 'listings' in section:
                        # loop through the sections and only get the listing
                        # results, cuz they return like experiences and
                        # stuff too
                        tmp_listings = section['listings']
                        for listing in tmp_listings:
                            # loop through the listing and save the id's
                            page_listing_ids.add(listing['listing']['id'])
                            listing_ids.add(listing['listing']['id'])
                            listings_per_range += 1
                            ids_per_range.add(listing['listing']['id'])

                # if the page is the same as the last one then it has no
                # next page
                if page_listing_ids != prev_page_ids:
                    prev_page_ids = page_listing_ids
                else:
                    has_next_page = False

                # save all listing id's to csv, this is not the best way do
                # it because i'm constantly saving the full array but it's
                # whatever it's only 10k records and one number so oh well
                with open(f'../airbnb-data/ids/chicago/'
                          f'{str(today)}/chicago_listing_ids.csv',
                          'w', newline='') as f:
                    writer = csv.writer(f, delimiter='\n')
                    writer.writerow(listing_ids)

                client.upload_file(
                    f'../airbnb-data/ids/chicago/'
                    f'{str(today)}/chicago_listing_ids.csv',
                    'spentaur',
                    f'airbnb/ids/chicago/{str(today)}/chicago_listing_ids.csv')

                # another insurance that has next page is right, if i get
                # less than 18 there's no way there's a next page right?
                if len(page_listing_ids) != 18:
                    has_next_page = False

                # print out some valuable stuff
                print("number of listings on page:", len(page_listing_ids))
                print("number of ids per range:", len(ids_per_range))
                print("number of listings per range:", listings_per_range)
                print("\n")
                # sleep between requests just to try to mitigate changes of
                # getting banned, probably too long sleep times but oh well
                # better safe than sorry
                # sleep_for = uniform(1, 5)
                # print('sleeping for:', sleep_for)
                # sleep(sleep_for)

                if page == estimated_number_of_pages:
                    total_actual_listings += listings_per_range
                    print("\n")
                    print("actual total for range:", listings_per_range)
                    print("total_actual_listings:", total_actual_listings)
                    print("len listing_ids:", len(listing_ids))
                    if estimated_listings_in_range:
                        print("amount missing:", estimated_listings_in_range -
                              listings_per_range)
                    print("----------------------------------------------")
            else:
                # if the status code is not 200, something went wrong and
                # let's just sleep and the request will be repeated. this
                # repeats the while loop so nothing get's changed it's just
                # the same request over again right? should verify that

                # increment attempts
                attempts += 1
                if attempts >= max_attempts:
                    break
                print("status code", status)
                sleep_for = uniform(3, 9)
                print('sleeping for:', sleep_for)
                sleep(sleep_for)
        print("\n")

        if attempts >= max_attempts:
            break

    print("total estimated listings:", total_estimated_listings)
    print("total actual listings:", total_actual_listings)
    print("len of listing ids", len(listing_ids))

import csv
import datetime
import os
import sys
from time import sleep
from time import time

import numpy as np
import requests
from boto3 import session
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

load_dotenv()


def requests_retry_session(retries=5, backoff_factor=2,
                           status_forcelist=(500, 502, 504, 429, 403),
                           session=None):
    """https://dev.to/ssbozy/python-requests-with-retries-4p03

    just going to go with this"""
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        status=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_and_format_location():
    city = input("City, State: ")
    city_formatted = city.lower().replace(',', '').replace(' ', '_')
    return city, city_formatted


def get_directory(city_formatted):
    today = datetime.date.today()
    return f"../airbnb-data/ids/{city_formatted}/{str(today)}"


def get_full_file_path(directory, city_formatted):
    return f"{directory}/{city_formatted}.csv"


def check_and_created_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def set_up_digital_ocean(ACCESS_ID, SECRET_KEY):
    url = 'https://nyc3.digitaloceanspaces.com'
    client = session.Session().client('s3',
                                      region_name='nyc3',
                                      endpoint_url=url,
                                      aws_access_key_id=ACCESS_ID,
                                      aws_secret_access_key=SECRET_KEY)
    return client


def get_page(city_formatted, price_min, price_max, page):
    items_offset = 18 * page
    url = 'https://www.airbnb.com/api/v2/explore_tabs'
    params = {'_format':         'for_explore_search_web',
              'currency':        'USD',
              'items_per_grid':  '18',
              'key':             'd306zoyjsyarp7ifhu67rjxn52tv0t20',
              'query':           f'{city_formatted}, United States',
              'search_type':     'pagination',
              'selected_tab_id': 'home_tab',
              'price_min':       price_min,
              'items_offset':    items_offset}
    if price_max:
        params['price_max'] = price_max
    t0 = time()
    try:
        response = requests_retry_session().get(url=url, params=params)
    except Exception as x:
        print('It failed :(')
        print(x)
    else:
        print('It eventually worked', response.status_code)
        return response
    finally:
        t1 = time()
        print('Took', t1 - t0, 'seconds')


def go_through_pages_in_range(city_formatted, price_min, price_max):
    page = 0
    prev_page_ids = set()
    has_next_page = True
    listing_ids = []
    estimated_listings_in_range = 0

    while has_next_page:
        response = get_page(city_formatted, price_min, price_max, page)
        print(type(response))
        if response is not None:
            page += 1
            results = response.json()['explore_tabs'][0]
            estimated_listings_in_range = results['home_tab_metadata'][
                'listings_count']
            estimated_number_of_pages = min(17, -(
                    estimated_listings_in_range // -18))
            print(f"{page} / {estimated_number_of_pages}")
            has_next_page = results['pagination_metadata']['has_next_page']
            sections = results['sections']
            page_listing_ids = get_listing_ids_from_sections(sections)
            if prev_page_ids == page_listing_ids:
                break
            prev_page_ids = page_listing_ids
            listing_ids += list(page_listing_ids)
            if len(page_listing_ids) != 18:
                has_next_page = False

            take_break(estimated_number_of_pages, page)

    return listing_ids, estimated_listings_in_range


def save_listing_ids_to_csv(listing_ids, full_file_path):
    with open(full_file_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\n')
        writer.writerow(listing_ids)


def upload_to_digital_ocean(full_file_path):
    ACCESS_ID = os.getenv("ACCESS_ID")
    SECRET_KEY = os.getenv("SECRET_KEY")

    client = set_up_digital_ocean(ACCESS_ID, SECRET_KEY)
    client.upload_file(full_file_path, 'spentaur', full_file_path[3:])


def get_listing_ids_from_sections(sections):
    listing_ids = set()
    for section in sections:
        if 'listings' in section:
            # loop through the sections and only get the listing
            # results, cuz they return like experiences and
            # stuff too
            tmp_listings = section['listings']
            for listing in tmp_listings:
                listing_ids.add(listing['listing']['id'])
    return listing_ids


def take_break(estimated_number_of_pages, page):
    if (estimated_number_of_pages > 1) and (
            page != estimated_number_of_pages):
        for remaining in range(20, 0, -1):
            sys.stdout.write("\r")
            sys.stdout.write(
                "{:2d} seconds remaining".format(remaining))
            sys.stdout.flush()
            sleep(1)
        sys.stdout.write("\rComplete!            \n")


def split_and_save_ids(listing_ids, directory, number_of_sections=6):
    splits = np.array_split(np.array(listing_ids), number_of_sections)
    city_formatted = directory.split("/")[3]
    for num, ids in enumerate(splits):
        full_file_path = f"{directory}/{city_formatted}_{num + 1}.csv"
        save_listing_ids_to_csv(ids, full_file_path)
        upload_to_digital_ocean(full_file_path)


def main():
    city, city_formatted = get_and_format_location()
    directory = get_directory(city_formatted)
    full_file_path = get_full_file_path(directory, city_formatted)
    check_and_created_directory(directory)

    total_estimated_listings = 0
    total_listing_ids = []

    for price_min in range(10, 406):
        print("Price:", price_min)
        if price_min < 404:
            price_max = price_min
        else:
            price_max = None

        listing_ids, estimated_listings_in_range = go_through_pages_in_range(
            city_formatted, price_min, price_max)

        total_listing_ids += listing_ids
        total_estimated_listings += estimated_listings_in_range

        save_listing_ids_to_csv(total_listing_ids, full_file_path)
        upload_to_digital_ocean(full_file_path)

        print("Estimated Listings in Price Range:",
              estimated_listings_in_range)
        print("Listings Saved in Price Range:", len(listing_ids))
        print("Total Estimated Listings:", total_estimated_listings)
        print("Total Listings Saved:", len(total_listing_ids))
        print("-------------------------------------------")
        print("\n")

    split_and_save_ids(total_listing_ids, directory)


if __name__ == '__main__':
    main()

import datetime
import os
import sys
from time import sleep

import pandas as pd
from dotenv import load_dotenv

from get_listing_info import get_all_listing_info
from helpers import get_and_format_location, \
    get_directory, get_full_file_path, check_and_created_directory, \
    get_page, upload_to_digital_ocean

load_dotenv()


def go_through_pages_in_range(query, price_min, price_max):
    listing_ids = []

    has_next_page = True

    attempts = 0
    page = 0
    items_per_grid = 50
    max_attempts = 500
    estimated_range = 0
    place_id = None
    federated_search_session_id = None
    s_tag = None
    search_session_id = None
    offset_factor = items_per_grid // 2

    url = 'https://www.airbnb.com/api/v2/explore_tabs'

    while has_next_page:
        params = {'_format':                       'for_explore_search_web',
                  'auto_ib':                       'false', 'currency': 'USD',
                  'current_tab_id':                'home_tab',
                  'experiences_per_grid':          '20',
                  'fetch_filters':                 'true',
                  'guidebooks_per_grid':           '20',
                  'has_zero_guest_treatment':      'true',
                  'hide_dates_and_guests_filters': 'false',
                  'is_guided_search':              'true',
                  'is_new_cards_experiment':       'true',
                  'is_standard_search':            'true', 'locale': 'en',
                  'metadata_only':                 'false',
                  'query_understanding_enabled':   'true',
                  'satori_version':                '1.2.5',
                  'section_offset':                '4',
                  'show_groupings':                'true',
                  'supports_for_you_v3':           'true',
                  'timezone_offset':               '-360', 'version': '1.7.0',
                  'items_per_grid':                items_per_grid,
                  'key':                           os.getenv("AIRBNB_KEY"),
                  'query':                         f'{query}',
                  'search_type':                   'pagination',
                  'selected_tab_id':               'home_tab',
                  'price_min':                     price_min,
                  'items_offset':                  offset_factor * page}

        if price_max:
            params['price_max'] = price_max

        if place_id and federated_search_session_id and s_tag and \
                search_session_id:
            params['place_id'] = place_id
            params['s_tag'] = s_tag
            params['federated_search_session_id'] = federated_search_session_id
            params['last_search_session_id'] = search_session_id

        response = get_page(url, params)
        results = response.json()['explore_tabs'][0]
        metadata = response.json()['metadata']
        home_tab_meta_data = results['home_tab_metadata']

        place_id = metadata['geography']['place_id']
        federated_search_session_id = metadata['federated_search_session_id']
        s_tag = home_tab_meta_data['search']['mobile_session_id']

        estimated_range = home_tab_meta_data['listings_count']
        has_next_page = results['pagination_metadata']['has_next_page']

        if has_next_page:
            search_session_id = results['pagination_metadata'][
                'search_session_id']

        sections = results['sections']
        page_listing_ids = [
            listing['listing']['id']
            for section in sections
            if 'listings' in section
            for listing in section['listings']
        ]
        estimated_pages = (-(estimated_range // -offset_factor)) - 1

        break_conditions = {
            attempts >= max_attempts,
            estimated_range > 306
        }
        attempts_conditions = {
            response is None,
            len(set(listing_ids + page_listing_ids)) < estimated_range
        }

        if True in break_conditions:
            print(break_conditions)
            break
        if True in attempts_conditions:
            print("\n")
            print("Attempting Again...")
            print(f"Attempt number {attempts + 1}")
            print(f"Length of listing ids and page ids"
                  f" {len(set(listing_ids + page_listing_ids))}")
            attempts += 1
            place_id = None
            federated_search_session_id = None
            s_tag = None
            search_session_id = None
            page = 0
            listing_ids = []
            has_next_page = True
            continue

        page += 1
        listing_ids += page_listing_ids
        if page == 1:
            print("Estimated Listings in Range: ", estimated_range)
            print("\n")

        sys.stdout.write("\r")
        sys.stdout.write(f"Page: {page} / {max(estimated_pages, 1)}")
        sys.stdout.flush()

    sys.stdout.write(
        f"\rDone Getting {len(set(listing_ids))} Listing Ids!            \n")

    return list(set(listing_ids)), estimated_range


def main():
    # TODO changed price range, update readme and split and save?
    # TODO combine function
    # TODO verify location and query, basically all user inputs

    today = datetime.date.today()
    city, city_formatted, query = get_and_format_location()
    directory = get_directory(city_formatted, str(today))
    check_and_created_directory(directory)
    starting_price = int(input("Starting Price: "))
    ending_price = input("Ending Price: ")
    print("\n")
    total_listings_saved = pd.DataFrame()

    if ending_price == '':
        ending_price = 1000
    else:
        ending_price = int(ending_price)

    if starting_price == '':
        starting_price = 10
    else:
        starting_price = int(starting_price)

    total_estimated_listings = 0
    over_300 = []

    for price_min in range(starting_price, ending_price + 1):
        full_file_path = get_full_file_path(directory, price_min)
        listings = pd.DataFrame()
        print("Price:", price_min)
        if price_min < 1000:
            price_max = price_min
        else:
            price_max = None

        data = go_through_pages_in_range(query, price_min, price_max)
        listings_ids, estimated_number = data

        if estimated_number >= 300:
            over_300.append((price_min, price_max))
            print("There are over 300 estimated listings in this range")
            continue

        for num, listing_id in enumerate(listings_ids):
            sys.stdout.write("\r")
            sys.stdout.write(f"Listing: {num + 1} / {len(listings_ids)}")
            sys.stdout.flush()
            listing = get_all_listing_info(listing_id)
            listings = pd.concat([listings, listing])
            # sleep(10)

        sys.stdout.write(f"\rDone!            \n")

        if len(listings) > 0:
            listings.to_csv(full_file_path, index=None)
            upload_to_digital_ocean(full_file_path)
            total_listings_saved = pd.concat([listings,
                                              total_listings_saved])
        else:
            sleep(10)

        total_estimated_listings += estimated_number
        num_saved = 0
        if len(total_listings_saved) > 0:
            num_saved = total_listings_saved['id'].nunique()

        assert (num_saved >= total_estimated_listings)

        print("Estimated Listings in Price Range:",
              estimated_number)
        print("Listings Saved in Price Range:", len(listings))
        print("Total Estimated Listings:", total_estimated_listings)
        print("Total Listings Saved:", num_saved)

        print("-------------------------------------------")
        print("\n")

    # after all price ranges have been gone through
    if not over_300:
        print("Listings in these price ranges had more than 300 estimated "
              "results meaning you will need to find another way to make "
              "sure you get all of them. None of these listings were saved "
              "in order to ensure you don't get them twice.")
        print(over_300)


if __name__ == '__main__':
    main()

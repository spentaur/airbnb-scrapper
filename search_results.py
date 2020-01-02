import datetime
import os

import pandas as pd
from dotenv import load_dotenv

from get_listing_info import get_all_listing_info
from helpers import get_and_format_location, \
    get_directory, get_full_file_path, check_and_created_directory, \
    get_page, upload_to_digital_ocean, take_break

load_dotenv()


def go_through_pages_in_range(query, price_min, price_max):
    prev_page_ids = set()
    listing_ids = set()
    listings = pd.DataFrame()

    has_next_page = True

    attempts = 0
    page = 0
    items_per_grid = 50
    max_attempts = 3
    estimated_range = 0

    url = 'https://www.airbnb.com/api/v2/explore_tabs'
    params = {'_format':         'for_explore_search_web',
              'items_per_grid':  str(items_per_grid),
              'key':             os.getenv("AIRBNB_KEY"),
              'query':           f'{query}',
              'search_type':     'pagination',
              'selected_tab_id': 'home_tab',
              'price_min':       price_min}
    if price_max:
        params['price_max'] = price_max

    while has_next_page:
        params['items_offset'] = items_per_grid * page
        response = get_page(url, params)
        results = response.json()['explore_tabs'][0]
        home_tab_meta_data = results['home_tab_metadata']
        estimated_range = home_tab_meta_data['listings_count']
        has_next_page = results['pagination_metadata']['has_next_page']
        sections = results['sections']
        page_listing_ids = {
            listing['listing']['id']
            for section in sections
            if 'listings' in section
            for listing in section['listings']
        }
        estimated_pages = min(7, -(estimated_range // -50))
        num_on_page = len(page_listing_ids)
        num_previously = len(listing_ids)
        estimated_combined_len = num_on_page + num_previously
        listing_ids = listing_ids.union(page_listing_ids)

        break_conditions = {
            attempts > max_attempts,
            estimated_range > 306,
            prev_page_ids == page_listing_ids
        }
        attempts_conditions = {
            response is None,
            estimated_combined_len != len(listing_ids)
        }

        if True in break_conditions:
            break
        if True in attempts_conditions:
            attempts += 1
            continue

        attempts = 0
        page += 1
        print(f"Page: {page} / {max(estimated_pages, 1)}")
        if page == 1:
            print("Estimated Listings in Range: ", estimated_range)
        print("\n")
        prev_page_ids = page_listing_ids

        if len(page_listing_ids) == 0:
            take_break(10)

        for listing_id in page_listing_ids:
            listing = get_all_listing_info(listing_id)
            listings = pd.concat([listings, listing])
            take_break(10)

    return listings, estimated_range


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
        print("Price:", price_min)
        if price_min < 1000:
            price_max = price_min
        else:
            price_max = None

        data = go_through_pages_in_range(query, price_min, price_max)
        listings, estimated_number = data

        if estimated_number >= 300:
            over_300.append((price_min, price_max))
            print("There are over 300 estimated listings in this range")
            continue

        if len(listings) > 0:
            listings.to_csv(full_file_path, index=None)
            upload_to_digital_ocean(full_file_path)
            total_listings_saved = pd.concat([listings, total_listings_saved])

        total_estimated_listings += estimated_number

        print("Estimated Listings in Price Range:",
              estimated_number)
        print("Listings Saved in Price Range:", len(listings))
        print("Total Estimated Listings:", total_estimated_listings)
        print("Total Listings Saved:", total_listings_saved['id'].nunique())

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

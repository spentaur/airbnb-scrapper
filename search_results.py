import csv
import datetime
import os
import sys
from time import sleep

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from helpers import get_and_format_location, \
    get_directory, get_full_file_path, check_and_created_directory, \
    get_page, upload_to_digital_ocean

load_dotenv()


def go_through_pages_in_range(query, price_min, price_max):
    page = 0
    prev_page_ids = set()
    has_next_page = True
    listing_ids = []
    estimated_listings_in_range = 0
    url = 'https://www.airbnb.com/api/v2/explore_tabs'
    params = {'_format':         'for_explore_search_web',
              'currency':        'USD',
              'items_per_grid':  '18',
              'key':             os.getenv("AIRBNB_KEY"),
              'query':           f'{query}, United States',
              'search_type':     'pagination',
              'selected_tab_id': 'home_tab',
              'price_min':       price_min}
    if price_max:
        params['price_max'] = price_max

    while has_next_page:
        # TODO this will go on forever
        params['items_offset'] = 18 * page
        response = get_page(url, params)
        if response is not None:
            page += 1
            results = response.json()['explore_tabs'][0]
            estimated_listings_in_range = results['home_tab_metadata'][
                'listings_count']
            if estimated_listings_in_range < 300:
                estimated_number_of_pages = min(17, -(
                        estimated_listings_in_range // -18))
                print(f"Page: {page} / {max(estimated_number_of_pages, 1)}")
                has_next_page = results['pagination_metadata']['has_next_page']
                sections = results['sections']
                page_listing_ids = get_listing_ids_from_sections(sections)
                if prev_page_ids == page_listing_ids:
                    break
                prev_page_ids = page_listing_ids
                listing_ids += list(page_listing_ids)
                if len(page_listing_ids) != 18:
                    has_next_page = False

                take_break(60)

            else:
                has_next_page = False

    return listing_ids, estimated_listings_in_range


def save_listing_ids_to_csv(listing_ids, full_file_path):
    with open(full_file_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\n')
        writer.writerow(listing_ids)


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


def take_break(sleep_for=20):
    for remaining in range(sleep_for, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write(
            "{:2d} seconds remaining".format(remaining))
        sys.stdout.flush()
        sleep(1)
    sys.stdout.write("\rComplete!            \n")


def split_and_save_ids(listing_ids, directory, number_of_sections=6):
    splits = np.array_split(np.array(listing_ids), number_of_sections)
    city_formatted = directory.split("/")[3]
    # TODO fix this
    for num, ids in enumerate(splits):
        full_file_path = f"{directory}/{city_formatted}_{num + 1}.csv"
        save_listing_ids_to_csv(ids, full_file_path)
        upload_to_digital_ocean(full_file_path)


def main():
    # TODO changed price range, update readme and split and save?
    # TODO combine function
    # TODO verify that if search_results runs overnight it doesn't change today
    # TODO readme mkdir update
    # TODO verify location and query, basically all user inputs
    # TODO verify that total estimated and total listings are diff
    # TODO change mkdir, should just be in python honestly
    # TODO starting price none
    today = datetime.date.today()
    city, city_formatted, query = get_and_format_location()
    directory = get_directory(city_formatted, "ids", str(today))
    check_and_created_directory(directory)
    starting_price = int(input("Starting Price: "))
    ending_price = input("Ending Price: ")
    if ending_price == '':
        ending_price = 1000
    else:
        ending_price = int(ending_price)
    total_estimated_listings = 0
    total_listing_ids = []
    over_300 = []

    for price_min in range(starting_price, ending_price + 1):
        full_file_path = get_full_file_path(directory, price_min)
        print("Price:", price_min)
        if price_min < 1000:
            price_max = price_min
        else:
            price_max = None

        listing_ids, estimated_listings_in_range = go_through_pages_in_range(
            query, price_min, price_max)

        if estimated_listings_in_range >= 300:
            over_300.append((price_min, price_max))
            print("There are over 300 estimated listings in this range, "
                  "so none of them have been saved as you'll need to find "
                  "another way to ensure you get all of them. (use map, "
                  "change types, etc.")
        else:
            total_estimated_listings += estimated_listings_in_range
            if len(listing_ids) > 0:
                total_listing_ids += listing_ids
                prices = [price_min] * len(listing_ids)
                df = pd.DataFrame(zip(listing_ids, prices))
                df.to_csv(full_file_path, index=None)
                upload_to_digital_ocean(full_file_path)

            print("Estimated Listings in Price Range:",
                  estimated_listings_in_range)
            print("Listings Saved in Price Range:", len(listing_ids))
            print("Total Estimated Listings:", total_estimated_listings)
            print("Total Listings Saved:", len(total_listing_ids))

        print("-------------------------------------------")
        print("\n")

    # TODO split and save
    # split_and_save_ids(total_listing_ids, directory)

    if not over_300:
        print("Listings in these price ranges had more than 300 estimated "
              "results meaning you will need to find another way to make "
              "sure you get all of them. None of these listings were saved "
              "in order to ensure you don't get them twice.")
        print(over_300)


if __name__ == '__main__':
    main()

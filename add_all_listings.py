import datetime
from os import path
from os import scandir
from random import shuffle
from time import time

import pandas as pd
from dateutil.parser import parse

from get_listing_info import get_all_listing_info
from helpers import get_and_format_location, get_full_file_path, \
    get_directory, upload_to_digital_ocean


def main():
    today = datetime.date.today()
    city, city_formatted, _ = get_and_format_location()

    id_date = input("Date Id's Collected: ")
    if id_date.lower() == "newest":
        s = "/"
        folder = get_directory(city_formatted, 'ids', str(today)).split('/')[
                 :-1]
        folder = s.join(folder)
        dates = [parse(f.name) for f in scandir(folder) if f.is_dir()]
        newest = sorted(dates)[-1]
        id_date = newest.strftime("%Y-%m-%d")

    # TODO all
    ids_id = input("Which set of ids to get: ")

    ids_directory = get_directory(city_formatted, 'ids', id_date)
    ids_full_path = get_full_file_path(ids_directory, ids_id)

    listings_directory = get_directory(city_formatted, 'listings', str(today))
    listings_full_path = get_full_file_path(listings_directory, ids_id)

    ids = set(pd.read_csv(ids_full_path)['ids'].tolist())

    if path.exists(listings_full_path):
        listings = pd.read_csv(listings_full_path)
        listing_ids = set(listings['id'].tolist())
    else:
        listings = pd.DataFrame()
        listing_ids = set()

    ids = list(ids - listing_ids)

    shuffle(ids)

    for listing_id in ids:
        start = time()
        print("listing id:", listing_id)
        listing = get_all_listing_info(listing_id)
        if listing is not None:
            listings = pd.concat([listings, listing])
            listings.to_csv(listings_full_path, index=False)
            print("-------------------------------------------")
            print("\n")

            upload_to_digital_ocean(listings_full_path)


# TODO get calendar info as well
if __name__ == '__main__':
    main()

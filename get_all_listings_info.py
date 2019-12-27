from os import path
from random import uniform, shuffle
from time import sleep
from time import time

import pandas as pd

from listing_info import get_all_listing_info

# TODO get calendar info as well
# TODO add checkin and checkout dates to df?

if __name__ == '__main__':
    ids = set(pd.read_csv('data/ids/chicago_listing_ids.csv')['ids'].tolist())

    if path.exists("data/listings/chicago_listings.csv"):
        listings = pd.read_csv('data/listings/chicago_listings.csv')
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
            listings.to_csv("data/listings/chicago_listings.csv", index=False)
            sleep_for = uniform(1, 5)
            sleep(sleep_for)
            print(f"this listing took: {time() - start} seconds")
            print("\n")

from os import path
from random import uniform
from time import sleep
from time import time

import pandas as pd

from get_listing_info import get_all_listing_info

if __name__ == '__main__':

    if path.exists("data/listings/chicago_listings.csv"):
        listings = pd.read_csv('data/listings/chicago_listings.csv')
        listing_ids = set(listings['id'].tolist())
    else:
        listings = pd.DataFrame()
        listing_ids = set()

    listing_id = input("Listing ID: ")
    start = time()
    listing = get_all_listing_info(listing_id)
    if listing is not None:
        listings = pd.concat([listings, listing])
        listings.to_csv("data/listings/chicago_listings.csv", index=False)
        sleep_for = uniform(1, 5)
        sleep(sleep_for)
        print(f"this listing took: {time() - start} seconds")
        print("\n")

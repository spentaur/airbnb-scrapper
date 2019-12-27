from random import uniform, shuffle
from time import sleep
from time import time

import pandas as pd

from listing_info import get_all_listing_info

# TODO get calendar info as well
# TODO add checkin and checkout dates to df?

if __name__ == '__main__':
    ids = pd.read_csv('chicago_listing_ids.csv')['ids'].tolist()
    shuffle(ids)

    df = pd.DataFrame()

    for listing_id in ids:
        start = time()
        print("listing id:", listing_id)
        listing = get_all_listing_info(listing_id)
        if listing is not None:
            df = pd.concat([df, listing])
            df.to_csv("chicago_listings.csv")
            sleep_for = uniform(1, 5)
            sleep(sleep_for)
            print(f"this listing took: {time() - start} seconds")
            print("\n")

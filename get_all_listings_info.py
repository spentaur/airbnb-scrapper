from os import path
from random import shuffle
from time import time

import pandas as pd
from boto3 import session
from dotenv import load_dotenv

from listing_info import get_all_listing_info

load_dotenv()

# TODO get calendar info as well
# TODO add checkin and checkout dates to df?

if __name__ == '__main__':
    # credentials for digital ocean
    ACCESS_ID = input("Access ID: ")
    SECRET_KEY = input("Secret Key: ")
    # setting up for digital ocean upload
    session = session.Session()
    client = session.client('s3',
                            region_name='nyc3',
                            endpoint_url='https://nyc3.digitaloceanspaces.com',
                            aws_access_key_id=ACCESS_ID,
                            aws_secret_access_key=SECRET_KEY)

    ids_id = input("Which set of ids to get: ")
    ids = set(pd.read_csv(f'data/ids/chicago_listing_ids_{ids_id}.csv')[
                  'ids'].tolist())

    if path.exists(f"chicago_listings_{ids_id}.csv"):
        listings = pd.read_csv(f"chicago_listings_{ids_id}.csv")
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
            listings.to_csv(f"chicago_listings_{ids_id}.csv", index=False)
            print(f"this listing took: {time() - start} seconds")
            print("\n")

            client.upload_file(f"chicago_listings_{ids_id}.csv", 'spentaur',
                               f'airbnb/listings/chicago_listings_'
                               f'{ids_id}.csv')

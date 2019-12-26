import pandas as pd

# TODO function to loop through all listing id's
# TODO retries on getting listing info if not 200
# TODO think about where i want the timeouts to be
# TODO saving listing info in csv, how big can it be?
# TODO get calendar info as well

if __name__ == '__main__':
    ids = pd.read_csv('chicago_listing_ids.csv')

import os

import pandas as pd
from dotenv import load_dotenv

from helpers import set_up_digital_ocean, upload_to_digital_ocean

load_dotenv()


def download_dir(client, dist, local='../', bucket='spentaur'):
    # https://stackoverflow.com/a/33350380
    paginator = client.get_paginator('list_objects')
    for result in paginator.paginate(Bucket=bucket, Delimiter='/',
                                     Prefix=dist):
        if result.get('CommonPrefixes') is not None:
            for subdir in result.get('CommonPrefixes'):
                download_dir(client, subdir.get('Prefix'), local, bucket)
        for file in result.get('Contents', []):
            dest_pathname = os.path.join(local, file.get('Key'))
            print(os.path.dirname(dest_pathname))
            if not os.path.exists(os.path.dirname(dest_pathname)):
                os.makedirs(os.path.dirname(dest_pathname))
            client.download_file(bucket, file.get('Key'), dest_pathname)
            client.delete_object(bucket, file.get('Key'))


def combine_all_listing_ids(city_formatted, date):
    client = set_up_digital_ocean(os.getenv("ACCESS_ID"),
                                  os.getenv("SECRET_KEY"))
    folder_path = f'airbnb-data/ids/{city_formatted}/{date}'
    file_path = f"{folder_path}/{city_formatted}.csv"
    download_dir(client, folder_path)

    df = pd.DataFrame()
    with os.scandir(f'../{folder_path}') as i:
        for entry in i:
            if entry.is_file():
                print(entry.path)
                df = pd.concat([df, pd.read_csv(entry.path, header=None)])
                os.remove(entry.path)

    df.to_csv(file_path, index=None)
    upload_to_digital_ocean(file_path)
    print("Done!")

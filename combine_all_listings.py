import datetime
import os

import numpy as np
import pandas as pd
from dateutil.parser import parse
from dotenv import load_dotenv

from helpers import set_up_digital_ocean, upload_to_digital_ocean, \
    get_and_format_location, get_directory

load_dotenv()


# TODO change this to update it for now just saving listings not listing ids
# TODO make sure that it's 1000 or 990 csv


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
            if not os.path.exists(os.path.dirname(dest_pathname)):
                os.makedirs(os.path.dirname(dest_pathname))
            client.download_file(bucket, file.get('Key'), dest_pathname)
            client.delete_object(Bucket=bucket, Key=file.get('Key'))


def combine_all_listings(city_formatted, date):
    client = set_up_digital_ocean(os.getenv("ACCESS_ID"),
                                  os.getenv("SECRET_KEY"))
    folder_path = f'airbnb-data/{city_formatted}/{date}/'
    download_dir(client, folder_path)

    df = pd.DataFrame()
    with os.scandir(f'../{folder_path}') as i:
        for entry in i:
            if entry.is_file():
                df = pd.concat([df, pd.read_csv(entry.path)])
                # os.remove(entry.path)

    dfs = np.array_split(df, 10)
    for idx, df_split in enumerate(dfs):
        file_path = f"{folder_path}{city_formatted}_{idx + 1}.csv"
        df_split.to_csv(f"../{file_path}", index=None)
        upload_to_digital_ocean(f"../{file_path}")
    print("Done!")


if __name__ == '__main__':
    today = datetime.date.today()
    city, city_formatted, _ = get_and_format_location()
    date_collected = input("Date Collected: ")
    if date_collected.lower() == "":
        s = "/"
        folder = get_directory(city_formatted, str(today)).split('/')[
                 :-1]
        folder = s.join(folder)
        dates = [parse(f.name) for f in os.scandir(folder) if f.is_dir()]
        newest = sorted(dates)[-1]
        id_date = newest.strftime("%Y-%m-%d")
    combine_all_listings(city_formatted, date_collected)

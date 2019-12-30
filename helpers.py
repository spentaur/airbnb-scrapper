import os
from time import time

import requests
from boto3 import session
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

load_dotenv()


def requests_retry_session(retries=10, backoff_factor=3,
                           status_forcelist=(500, 502, 504, 429),
                           session=None):
    """https://dev.to/ssbozy/python-requests-with-retries-4p03

    just going to go with this"""
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        status=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_and_format_location():
    city = input("City, State: ")
    city_formatted = city.lower().replace(',', '').replace(' ', '_')
    return city, city_formatted


def get_directory(city_formatted, ids_or_listings, date):
    return f"../airbnb-data/{ids_or_listings}/{city_formatted}/{date}"


def get_full_file_path(directory, city_formatted, number=None):
    # TODO i dont need city again, just get from dir?
    return f"{directory}/{city_formatted}{f'_{number}' if number else ''}.csv"


def check_and_created_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def set_up_digital_ocean(ACCESS_ID, SECRET_KEY):
    url = 'https://nyc3.digitaloceanspaces.com'
    client = session.Session().client('s3',
                                      region_name='nyc3',
                                      endpoint_url=url,
                                      aws_access_key_id=ACCESS_ID,
                                      aws_secret_access_key=SECRET_KEY)
    return client


def get_page(url, params):
    t0 = time()
    try:
        response = requests_retry_session().get(url=url, params=params)
    except Exception as x:
        print('It failed :(')
        print(x)
    else:
        print('It eventually worked', response.status_code)
        return response
    finally:
        t1 = time()
        print('Took', t1 - t0, 'seconds')


def upload_to_digital_ocean(full_file_path):
    ACCESS_ID = os.getenv("ACCESS_ID")
    SECRET_KEY = os.getenv("SECRET_KEY")

    client = set_up_digital_ocean(ACCESS_ID, SECRET_KEY)
    client.upload_file(full_file_path, 'spentaur', full_file_path[3:])
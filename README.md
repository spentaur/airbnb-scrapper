# This is a program set up to run on Digital Ocean and scrape the airbnb api and save listing information to a csv.
----
## Set up server
1) Create and ssh into droplet.
2) `git clone https://github.com/spentaur/airbnb-scrapper.git`
3) `cd airbnb-scrapper`
4) `sudo chmod a+x ./setup.sh`
5) `sudo ./setup.sh`
6) Enter digital ocean Access ID and Secret Key when prompted.
6) Enter AirBnB key when prompted.
7) `pipenv install`
8) `mkdir ../airbnb-data/listings/CITY/$(date +%Y-%m-%d)` Make sure to
 update city to the proper format (champaign_il)
9) `mkdir ../airbnb-data/ids/CITY/$(date +%Y-%m-%d)`

```
git clone https://github.com/spentaur/airbnb-scrapper.git
git clone https://github.com/spentaur/airbnb-data.git
cd airbnb-scrapper
sudo chmod a+x ./setup.sh
sudo ./setup.sh
pipenv install
mkdir ../airbnb-data/listings/CITY/$(date +%Y-%m-%d)
mkdir ../airbnb-data/ids/CITY/$(date +%Y-%m-%d)'
```

----

#### Get all listing ids for city

1) `python search_results.py`
2) Enter City (Example: Champaign, Il)
3) Enter Query (Example: Champaign, Il, United States)

----

#### Get all listings info

1) `python add_all_listings.py`
2) Enter City (Example: Champaign, Il)
3) Enter which subset of listing id's you'd like to get information on.

----
#### TODO
1) ~~search_results should be generalized~~
2) better documentation
    - how to get airbnb key, query
3) ~~handle retries better~~
4) ~~get calendar information~~
5) ~~move data to separate repo~~
6) tests
7) could this be containerized?
8) ~~403 errors are listings that no longer exists, handle better~~
9) data dictionary
10) ~~make it so you can change cities~~
11) figure out how to get all listings from big cities where even if price
 is $89 min and max, results are still over 300
12) add single listing upload to digital ocean
13) ~~save listing ids in multiple files~~
14) save pages that failed
    - search, listings
    - if a price range fails or a has over 300 or if a page in a range fails
    - if listing is 403 or couldn't get all the info 
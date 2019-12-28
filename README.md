## This is a program set up to run on Digital Ocean and scrape the airbnb api and save listing information to a csv.
----
#### Get all listings info
1) Create and ssh into droplet.
2) git clone https://github.com/spentaur/airbnb-scrapper.git
3) cd airbnb-scrapper
4) sudo chmod a+x ./setup.sh
5) sudo ./setup.sh
6) Enter digital ocean Access ID and Secret Key when prompted.
7) pipenv install
8) python add_all_listings.py
9) Enter which subset of listing id's you'd like to get information on.

```
git clone https://github.com/spentaur/airbnb-scrapper.git
cd airbnb-scrapper
sudo chmod a+x ./setup.sh
sudo ./setup.sh
pipenv install
python add_all_listings.py
```

----
#### TODO
1) search_results should be generalized
2) better documentation
3) handle retries better
4) get calendar information
5) ~~move data to separate repo~~
6) tests
7) could this be containerized?
8) 403 errors are listings that no longer exists, handle better
9) data dictionary
10) make it so you can change cities
    - figure out how to get all listings from big cities where even if price
     is $89 min and max, results are still over 300
11) add single listing upload to digital ocean
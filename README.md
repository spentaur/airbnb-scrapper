# This is a program set up to run on Digital Ocean and scrape the airbnb api and save listing information to a csv.

**_Be warned: This Will Take a Long Time To Run!_**  
Because of airbnb rate limiting, you have to take a decent break when you
get a 429 error. So search_results can take a long time. Also I've found
that taking a break between pages for a given range is necessary to ensure
that listings don't repeat on the next page for whatever reason. If
someone can think of a better way, let me know.  
    
Also, to get all the information on a given listing, you must hit
multiple urls, some of them multiple times, so that can also take a
long time.  
  
This is why I've chosen to run this on digital ocean servers. I can spin up
multiple servers and chunk the ids and run them simultaneously. I already
use them so I have spaces already set up so I can just save all the data
there, but you could modify this to save it to a database. Just remember
that any data stored locally on the server wont be available once you
destroy it. You don't need anything fancy, just go with the $5 a month
droplet.
   

----

## Getting AirBnB key and query

1) Open inspector panel and go to network tab.
2) Go to https://airbnb.com.
3) Pick a city. You don't need to worry about check-in, checkout, or number
 or guests for this purpose.
4) In the `Filter URLs` search box, type 'explore_tabs'
    - There might be multiple, and not all of them have the query param so
     you might have to check more than one. You can start with the largest
      one, that's most likely it. 
5) In the bottom section, select the Params tab.
6) In the  `Filter Request Parameters` box type 'key'. This is the `Airbnb
 Key` requested during set up
7) Next type 'query'. This will be the 'query' field requested during
  `search_results.py`. It should look similar to the city you are searching
   for (Example: Champaign, IL, United States)

If you just need to get the query, for instance you are searching for
 another city, just ignore the key part, you don't need to get it every time. 
 You can save it somewhere and just reference it later.


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


#### Get all listings info

1) `python add_all_listings.py`
2) Enter City (Example: Champaign, Il)
3) Enter which subset of listing id's you'd like to get information on.


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
15) setup without digital ocean
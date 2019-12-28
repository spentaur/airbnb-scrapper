## This is a program set up to run on Digital Ocean and scrape the airbnb api and save listing information to a csv.

1) Create and ssh into droplet.
2) git clone https://github.com/spentaur/airbnb-scrapper.git
3) cd airbnb-scrapper
4) sudo chmod a+x ./setup.sh
5) sudo ./setup.sh
6) Enter digital ocean Access ID and Secret Key when prompted.
7) pipenv install
8) python add_all_listings.py
9) Enter which subset of listing id's you'd like to get information on.


----
TODO
1) search_results should be generalized
2) better documentation
3) handle retries better
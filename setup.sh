#!/bin/bash
apt-get update
apt install python3-pip
pip3 install pipenv
read -p 'Access Id: ' access_id
read -p 'Secret Key: ' secret_key
touch .env
echo "ACCESS_ID='${access_id}'" >> .env
echo "SECRET_KEY='${secret_key}'" >> .env
pipenv --python /usr/bin/python3
pipenv shell
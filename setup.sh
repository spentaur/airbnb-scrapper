#!/bin/bash
apt-get update
apt install python3-pip
pip3 install pipenv
read -r -p 'Access Id: ' access_id
read -r -p 'Secret Key: ' secret_key
read -r -p 'AirBnB Key: ' airbnb_key
touch .env
{
  echo "ACCESS_ID='${access_id}'"
  echo "SECRET_KEY='${secret_key}'"
  echo "AIRBNB_KEY='${airbnb_key}'"
} >>.env
pipenv --python /usr/bin/python3
pipenv shell

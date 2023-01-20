'''
Description: Test the functions
Author: Nan Li
Contact: linan.lqq0@gmail.com
'''

# import packages
import os
import re
import time
from headers import headers
from random import randrange
from functions import readPostcode, createUrl, get_cookie, update_cookie
from classes import ExtractListPage, ExtractHouseURL, ExtractHouseInfo

# change working directory to current folder
os.chdir(os.path.dirname(__file__))

url = 'https://www.realestate.com.au/sold/in-glen+waverley,+vic+3150%3b/list-1?includeSurrounding=false'

def update_header():
    for i in range(7):
        print("update cookie {}".format(i))
        update_cookie(headers[i]["cookie"], get_cookie(url, headers[i]["user-agent"]))

def test_func():
    while True:
        try:
            list_page = ExtractListPage(url, randrange(7))
            break
        except:
            continue
    houselinks = list_page.getHouseLink()
    houselink = houselinks[0]
    house_url = 'https://www.realestate.com.au' + houselink
    while True:
        try:
            house = ExtractHouseURL(house_url, randrange(7))
            break
        except:
            time.sleep(1)
            continue
    history_url = house.getHistoryURL()
    if history_url is not None:
        while True:
            try:
                house_history = ExtractHouseInfo(history_url, randrange(7))
                break
            except:
                time.sleep(1)
                continue
        address, suburb, post_code = house_history.getAddress()
        solddate = house.getSoldDate()
        house_id = house.getHouseID()
        soldprice = house.getSoldPrice()
        agency = house.getAgency()
        bedroom, bathroom, parking = house.getFeatures()
        housetype = house_history.getHouseType()
        latitude, longitude = house_history.getLocation()
        REA_id = house_history.getREAID()
        land_size, floor_area, year_built = house_history.getLandInfo()
        print(address, suburb, post_code, solddate, house_id, soldprice, agency, bedroom, bathroom, parking,
            housetype, latitude, longitude, REA_id, land_size, floor_area, year_built)
            
    address, suburb, post_code = house.getAddress()
    solddate = house.getSoldDate()
    house_id = house.getHouseID()
    soldprice = house.getSoldPrice()
    agency = house.getAgency()
    bedroom, bathroom, parking = house.getFeatures()
    housetype = house.getHouseType()
    latitude, longitude = house.getLocation()
    REA_id = None
    land_size = house.getLandSize()
    floor_area = 0
    year_built = 0
    print(address, suburb, post_code, solddate, house_id, soldprice, agency, bedroom, bathroom, parking,
        housetype, latitude, longitude, REA_id, land_size, floor_area, year_built)

def test_connection():
    i = -1
    while i < 6:
        i = i + 1
        print("test cookie {}".format(i))
        try:
            list_page = ExtractListPage(url, i)
            continue
        except:
            continue

if __name__ == '__main__':
    test_connection()
    test_func()
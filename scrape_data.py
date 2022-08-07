'''
Description: Scrape sold house data from realestate.com.au
Author: Nan Li
Contact: linan.lqq0@gmail.com
'''

# import packages
import os
import re
import time
import mysql.connector
from random import randrange
from datetime import datetime
from functools import partial
from multiprocessing import Pool
from mysql.connector import pooling
from mysql.connector import errorcode
from functions import readPostcode, createUrl
from classes import ExtractListPage, ExtractHouseURL, ExtractHouseInfo

# change working directory to current folder
os.chdir(os.path.dirname(__file__))

# connect mySQL database
try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mysql_pool",
                                                                pool_size=5,
                                                                pool_reset_session=True,
                                                                host='localhost',
                                                                database='aus_sold_houses',
                                                                user='root',
                                                                password='1LoveBMW',
                                                                autocommit=True)
    #print("Connection Pool Size - ", connection_pool.pool_size)
    #print("Database connected sucessfully!")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
    exit()

# main function of scrawler
def main(state, start_date):
    # scrape data according to postcode
    print('Start ' + state)
    file_name = './Postcode/{}.xlsx'.format(state)
    postcodes = readPostcode(file_name)
    house_url = ''
    for postcode in postcodes:
        print(postcode)
        page = 1
        while True:
            url = createUrl(postcode, page)
            while True:
                try:
                    list_page = ExtractListPage(url, randrange(7))
                    break
                except:
                    time.sleep(1)
                    continue
            firstdate = list_page.getFirstSoldDate()
            if firstdate is not None and firstdate < start_date:
                print('Postcode {:d} done! Total: {:d} pages!'.format(postcode, page-1), datetime.now())
                break
            nextpage = list_page.getNextPage()
            houselinks = list_page.getHouseLink()
            noLinks = len(houselinks)
            if noLinks == 0:
                print('Postcode {:d} has no sold houses!'.format(postcode), datetime.now())
                break
            noThread = min([3, noLinks])
            with Pool(noThread) as p:
                p.map(partial(getHouseInfo,postcode=postcode,state=state,start_date=start_date), houselinks)

            '''for houselink in houselinks:
                getHouseInfo(houselink, postcode, state, start_date)'''

            if nextpage is not None:
                page = page + 1
            else:
                print('Postcode {:d} done! Total: {:d} pages!'.format(postcode, page), datetime.now())
                break
    print(state + ' completed!!!', datetime.now())

# get house info
def getHouseInfo(houselink, postcode, state, start_date):
    error = 0
    house_url = 'https://www.realestate.com.au' + houselink
    try:
        connection_object = connection_pool.get_connection()
        if connection_object.is_connected():
            cursor = connection_object.cursor()
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
            if post_code != postcode:
                return
            solddate = house.getSoldDate()
            if solddate is not None and solddate < start_date:
                return
            house_id = house.getHouseID()
            soldprice = house.getSoldPrice()
            agency = house.getAgency()
            bedroom, bathroom, parking = house.getFeatures()
            housetype = house_history.getHouseType()
            latitude, longitude = house_history.getLocation()
            REA_id = house_history.getREAID()
            land_size, floor_area, year_built = house_history.getLandInfo()
        else:
            address, suburb, post_code = house.getAddress()
            if post_code != postcode:
                return
            solddate = house.getSoldDate()
            if solddate is not None and solddate < start_date:
                return
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

        # set an error tracking flag
        error = 1

        # save to mySQL database
        sql = """INSERT INTO {} (
            house_id, REA_id, address, suburb, postcode, house_type, bedroom, bathroom, parking, land_size, 
            floor_area, year_built, sold_price, sold_date, agency, latitude, longitude, link, time) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""".format(state)
        val = (house_id, REA_id, address, suburb, post_code, housetype, bedroom, bathroom, parking, land_size, 
                floor_area, year_built, soldprice, solddate, agency, latitude, longitude, house_url)
        cursor.execute(sql, val)

    except:
        if error == 0: # error happens during URL extraction
            print('error happens', datetime.now())
            if not os.path.exists('./error log'):
                os.makedirs('./error log')
            file = open('./error log/'+state+'_error.log', 'a')
            file.write(house_url + '\n')
        return

    finally:
        print(postcode, datetime.now())
        #closing database connection.
        if(connection_object.is_connected()):
            cursor.close()
            connection_object.close()
    
# deal with error logs
def handle_error(state):
    print('Start ' + state)
    file_name = './error log/{}_error.log'.format(state)
    try:
        f = open(file_name, 'r')
    except:
        print('{} has no errors. All done!'.format(state))
        return
    houselinks = [url for url in f]
    '''noLinks = len(houselinks)
    noThread = min([5, noLinks])
    with Pool(noThread) as p:
        p.map(partial(getHouseInfo1,state=state), houselinks)'''

    for houselink in houselinks:
        getHouseInfo1(houselink, state)

    print(state + ' completed!!!', datetime.now())

# get house info
def getHouseInfo1(houselink, state):
    error = 0
    house_url = houselink.replace('\n', '')
    try:
        connection_object = connection_pool.get_connection()
        if connection_object.is_connected():
            cursor = connection_object.cursor()

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
        else:
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

        # set an error tracking flag
        error = 1

        # save to mySQL database
        sql = """INSERT INTO {} (
            house_id, REA_id, address, suburb, postcode, house_type, bedroom, bathroom, parking, land_size, 
            floor_area, year_built, sold_price, sold_date, agency, latitude, longitude, link, time) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""".format(state)
        val = (house_id, REA_id, address, suburb, post_code, housetype, bedroom, bathroom, parking, land_size, 
                floor_area, year_built, soldprice, solddate, agency, latitude, longitude, house_url)
        cursor.execute(sql, val)

    except:
        if error == 0: # error happens during URL extraction
            print('error happens', datetime.now())
            file = open('./error log/'+state+'_error_1.log', 'a')
            file.write(house_url + '\n')
        return

    finally:
        print(datetime.now())
        #closing database connection.
        if(connection_object.is_connected()):
            cursor.close()
            connection_object.close()

# scrape latest sold data
def update(date):
    main('australian_capital_territory', date)
    main('new_south_wales', date)
    main('northern_territory', date)
    main('queensland', date)
    main('south_australia', date)
    main('tasmania', date)
    main('victoria', date)
    main('western_australia', date)

def retry_error():
    handle_error('australian_capital_territory')
    handle_error('new_south_wales')
    handle_error('northern_territory')
    handle_error('queensland')
    handle_error('south_australia')
    handle_error('tasmania')
    handle_error('victoria')
    handle_error('western_australia')

if __name__ == '__main__': 
    update(datetime(2022, 7, 1))
    #retry_error()

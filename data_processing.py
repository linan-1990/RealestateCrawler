'''
Description: Realestate data processing
Author: Nan Li
Contact: linan.lqq0@gmail.com
'''

# import packages
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector
from mysql.connector import errorcode

# change working directory to current folder
os.chdir(os.path.dirname(__file__))

# set the font size of plot
plt.rc('font', size=16)
plt.rc('xtick', labelsize=16)
plt.rc('ytick', labelsize=16)
plt.rc('figure', titlesize=20)
plt.rc('legend', fontsize=12)

# connect mySQL database
try:
    con=mysql.connector.connect(user='root',password='1LoveBMW',database='aus_sold_houses')
    print("Database connected sucessfully!")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
    exit()

# get data from database
def get_avg_price(state, house_type):
    # select data from database
    if house_type == 'house':
        sql = """ SELECT COUNT(*) AS total_sold, AVG(sold_price) as avg_price, 
            YEAR(sold_date) as year FROM {}
            WHERE sold_date is not null and sold_price is not null AND YEAR(sold_date) > 2007
            AND sold_price < 100000000 and sold_price > 10000 AND
            (LOWER(house_type) LIKE 'house' OR LOWER(house_type) LIKE 'townhouse' OR LOWER(house_type) LIKE 'unit')
            GROUP BY YEAR(sold_date) ORDER BY YEAR(sold_date)""".format(state)
    elif house_type == 'apartment':
        sql = """ SELECT COUNT(*) AS total_sold, AVG(sold_price) as avg_price, 
            YEAR(sold_date) as year FROM {}
            WHERE sold_date is not null and sold_price is not null AND YEAR(sold_date) > 2007
            AND sold_price < 100000000 and sold_price > 10000 AND
            (LOWER(house_type) LIKE 'apartment' OR LOWER(house_type) LIKE 'studio' OR LOWER(house_type) LIKE 'flat')
            GROUP BY YEAR(sold_date) ORDER BY YEAR(sold_date)""".format(state)
    cursor = con.cursor(dictionary=True, buffered=True)
    cursor.execute(sql)    
    avg_price = []
    year = []
    while True:
        row = cursor.fetchone()
        if row == None:
            break
        avg_price.append(row['avg_price'])
        year.append(row['year'])
    cursor.close()
    return np.asarray(year), np.asarray(avg_price)

# get data from database
def get_landsize(state):
    # select data from database
    sql = """ SELECT land_size, sold_price FROM {}
        WHERE land_size > 0 AND land_size < 500 AND sold_price is not null 
        AND sold_price < 1000000 and sold_price > 100000 AND 
        postcode = 3149 AND
        (LOWER(house_type) LIKE 'house' OR LOWER(house_type) LIKE 'townhouse' OR LOWER(house_type) LIKE 'unit')
        """.format(state)  
    cursor = con.cursor(dictionary=True, buffered=True)
    cursor.execute(sql)    
    land_size = []
    sold_price = []
    while True:
        row = cursor.fetchone()
        if row == None:
            break
        land_size.append(row['land_size'])
        sold_price.append(row['sold_price'])
    cursor.close()
    return np.asarray(land_size), np.asarray(sold_price)

# get aveage sold price for different states
year_act, avg_price_house_act = get_avg_price('australian_capital_territory', 'house')
year_act, avg_price_apart_act = get_avg_price('australian_capital_territory', 'apartment')
year_nsw, avg_price_house_nsw = get_avg_price('new_south_wales', 'house')
year_nsw, avg_price_apart_nsw = get_avg_price('new_south_wales', 'apartment')
year_nt, avg_price_house_nt = get_avg_price('northern_territory', 'house')
year_nt, avg_price_apart_nt = get_avg_price('northern_territory', 'apartment')
year_qld, avg_price_house_qld = get_avg_price('queensland', 'house')
year_qld, avg_price_apart_qld = get_avg_price('queensland', 'apartment')
year_sa, avg_price_house_sa = get_avg_price('south_australia', 'house')
year_sa, avg_price_apart_sa = get_avg_price('south_australia', 'apartment')
year_tas, avg_price_house_tas = get_avg_price('tasmania', 'house')
year_tas, avg_price_apart_tas = get_avg_price('tasmania', 'apartment')
year_vic, avg_price_house_vic = get_avg_price('victoria', 'house')
year_vic, avg_price_apart_vic = get_avg_price('victoria', 'apartment')
year_wa, avg_price_house_wa = get_avg_price('western_australia', 'house')
year_wa, avg_price_apart_wa = get_avg_price('western_australia', 'apartment')

# plot data and save as image
fig = plt.figure(figsize=(18, 10))
fig.suptitle('Comprisons of house price in Australia [AU k$]')
# victoria
ax_vic = fig.add_subplot(2, 2, 1)
ax_vic.set_xlabel('Year')
ax_vic.set_title('Victoria',fontsize=14)
ax_vic.plot(year_vic, avg_price_house_vic/1000, 'r-o', lw = 3, label='House')
ax_vic.plot(year_vic, avg_price_apart_vic/1000, 'c-o', lw = 3, label='Apartment')
ax_vic.legend(bbox_to_anchor=(0.005, 0.8, 1., .102), loc=3, framealpha = 0.5,
            ncol=1, borderaxespad=0., shadow=False, fancybox=True)
ax_vic.grid()
# new south wales
ax_nsw = fig.add_subplot(2, 2, 2)
ax_nsw.set_xlabel('Year')
ax_nsw.set_title('New South Wales',fontsize=14)
ax_nsw.plot(year_nsw, avg_price_house_nsw/1000, 'r-o', lw = 3, label='House')
ax_nsw.plot(year_nsw, avg_price_apart_nsw/1000, 'c-o', lw = 3, label='Apartment')
ax_nsw.legend(bbox_to_anchor=(0.005, 0.8, 1., .102), loc=3, framealpha = 0.5,
            ncol=1, borderaxespad=0., shadow=False, fancybox=True)
ax_nsw.grid()
# south australia
ax_sa = fig.add_subplot(2, 2, 3)
ax_sa.set_xlabel('Year')
ax_sa.set_title('South Australia',fontsize=14)
ax_sa.plot(year_sa, avg_price_house_sa/1000, 'r-o', lw = 3, label='House')
ax_sa.plot(year_sa, avg_price_apart_sa/1000, 'c-o', lw = 3, label='Apartment')
ax_sa.legend(bbox_to_anchor=(0.005, 0.8, 1., .102), loc=3, framealpha = 0.5,
            ncol=1, borderaxespad=0., shadow=False, fancybox=True)
ax_sa.grid()
# western australia
ax_wa = fig.add_subplot(2, 2, 4)
ax_wa.set_xlabel('Year')
ax_wa.set_title('Western Australia',fontsize=14)
ax_wa.plot(year_wa, avg_price_house_wa/1000, 'r-o', lw = 3, label='House')
ax_wa.plot(year_wa, avg_price_apart_wa/1000, 'c-o', lw = 3, label='Apartment')
ax_wa.legend(bbox_to_anchor=(0.005, 0.8, 1., .102), loc=3, framealpha = 0.5,
            ncol=1, borderaxespad=0., shadow=False, fancybox=True)
ax_wa.grid()
plt.subplots_adjust(hspace = 0.5)
plt.subplots_adjust(wspace = 0.3)
#plt.show()
img_name = './Results/price1.png'
fig.savefig(img_name, bbox_inches="tight", pad_inches=0)
plt.close(fig)

# plot data and save as image
fig = plt.figure(figsize=(18, 10))
fig.suptitle('Comprisons of house price in Australia [AU k$]')
# australian capital territory
ax_act = fig.add_subplot(2, 2, 1)
ax_act.set_xlabel('Year')
ax_act.set_title('Australian Capital Territory',fontsize=14)
ax_act.plot(year_act, avg_price_house_act/1000, 'r-o', lw = 3, label='House')
ax_act.plot(year_act, avg_price_apart_act/1000, 'c-o', lw = 3, label='Apartment')
ax_act.legend(bbox_to_anchor=(0.005, 0.8, 1., .102), loc=3, framealpha = 0.5,
            ncol=1, borderaxespad=0., shadow=False, fancybox=True)
ax_act.grid()
# queensland
ax_qld = fig.add_subplot(2, 2, 2)
ax_qld.set_xlabel('Year')
ax_qld.set_title('Queensland',fontsize=14)
ax_qld.plot(year_qld, avg_price_house_qld/1000, 'r-o', lw = 3, label='House')
ax_qld.plot(year_qld, avg_price_apart_qld/1000, 'c-o', lw = 3, label='Apartment')
ax_qld.legend(bbox_to_anchor=(0.005, 0.8, 1., .102), loc=3, framealpha = 0.5,
            ncol=1, borderaxespad=0., shadow=False, fancybox=True)
ax_qld.grid()
# tasmania
ax_tas = fig.add_subplot(2, 2, 3)
ax_tas.set_xlabel('Year')
ax_tas.set_title('Tasmania',fontsize=14)
ax_tas.plot(year_tas, avg_price_house_tas/1000, 'r-o', lw = 3, label='House')
ax_tas.plot(year_tas, avg_price_apart_tas/1000, 'c-o', lw = 3, label='Apartment')
ax_tas.legend(bbox_to_anchor=(0.005, 0.8, 1., .102), loc=3, framealpha = 0.5,
            ncol=1, borderaxespad=0., shadow=False, fancybox=True)
ax_tas.grid()
# northern territory
ax_nt = fig.add_subplot(2, 2, 4)
ax_nt.set_xlabel('Year')
ax_nt.set_title('Northern Territory',fontsize=14)
ax_nt.plot(year_nt, avg_price_house_nt/1000, 'r-o', lw = 3, label='House')
ax_nt.plot(year_nt, avg_price_apart_nt/1000, 'c-o', lw = 3, label='Apartment')
ax_nt.legend(bbox_to_anchor=(0.005, 0.8, 1., .102), loc=3, framealpha = 0.5,
            ncol=1, borderaxespad=0., shadow=False, fancybox=True)
ax_nt.grid()
plt.subplots_adjust(hspace = 0.5)
plt.subplots_adjust(wspace = 0.3)
#plt.show()
img_name = './Results/price2.png'
fig.savefig(img_name, bbox_inches="tight", pad_inches=0)
plt.close(fig)

# plot data and save as image
fig = plt.figure(figsize=(22, 8))
fig.suptitle('Comprisons of house price in Australia [AU k$]')
color = ['m','r','k','g','orange','y','b','c']
# house
ax_house = fig.add_subplot(1, 2, 1)
ax_house.set_xlabel('Year')
ax_house.set_title('House',fontsize=14)
ax_house.plot(year_act, avg_price_house_act/1000, '-o', color=color[0], lw = 3, label='ACT')
ax_house.plot(year_nsw, avg_price_house_nsw/1000, '-o', color=color[1], lw = 3, label='NSW')
ax_house.plot(year_nt, avg_price_house_nt/1000, '-o', color=color[2], lw = 3, label='NT')
ax_house.plot(year_qld, avg_price_house_qld/1000, '-o', color=color[3], lw = 3, label='QLD')
ax_house.plot(year_sa, avg_price_house_sa/1000, '-o', color=color[4], lw = 3, label='SA')
ax_house.plot(year_tas, avg_price_house_tas/1000, '-o', color=color[5], lw = 3, label='TAS')
ax_house.plot(year_vic, avg_price_house_vic/1000, '-o', color=color[6], lw = 3, label='VIC')
ax_house.plot(year_wa, avg_price_house_wa/1000, '-o', color=color[7], lw = 3, label='WA')
ax_house.legend(bbox_to_anchor=(0.005, 0.82, 1., .102), loc=3, framealpha = 0.5,
            ncol=2, borderaxespad=0., shadow=False, fancybox=True)
ax_house.grid()
# apartment
ax_apart = fig.add_subplot(1, 2, 2)
ax_apart.set_xlabel('Year')
ax_apart.set_title('Apartment',fontsize=14)
ax_apart.plot(year_act, avg_price_apart_act/1000, '-o', color=color[0], lw = 3, label='ACT')
ax_apart.plot(year_nsw, avg_price_apart_nsw/1000, '-o', color=color[1], lw = 3, label='NSW')
ax_apart.plot(year_nt, avg_price_apart_nt/1000, '-o', color=color[2], lw = 3, label='NT')
ax_apart.plot(year_qld, avg_price_apart_qld/1000, '-o', color=color[3], lw = 3, label='QLD')
ax_apart.plot(year_sa, avg_price_apart_sa/1000, '-o', color=color[4], lw = 3, label='SA')
ax_apart.plot(year_tas, avg_price_apart_tas/1000, '-o', color=color[5], lw = 3, label='TAS')
ax_apart.plot(year_vic, avg_price_apart_vic/1000, '-o', color=color[6], lw = 3, label='VIC')
ax_apart.plot(year_wa, avg_price_apart_wa/1000, '-o', color=color[7], lw = 3, label='WA')
ax_apart.legend(bbox_to_anchor=(0.005, 0.82, 1., .102), loc=3, framealpha = 0.5,
            ncol=2, borderaxespad=0., shadow=False, fancybox=True)
ax_apart.grid()
plt.subplots_adjust(hspace = 0.5)
plt.subplots_adjust(wspace = 0.3)
#plt.show()
img_name = './Results/price3.png'
fig.savefig(img_name, bbox_inches="tight", pad_inches=0)
plt.close(fig)

# price vs landsize in VIC
land_size, sold_price = get_landsize('victoria')
fig = plt.figure(figsize=(18, 10))
plt.plot(land_size, sold_price/1000, 'b.')
plt.title('Price vs Land_Size (Victoria)')
plt.xlabel('Land size [m^2]')
plt.ylabel('Sold price [AU k$]')
plt.grid()
img_name = './Results/price4.png'
fig.savefig(img_name, bbox_inches="tight", pad_inches=0)
plt.close(fig)

con.close()
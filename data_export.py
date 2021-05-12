'''
Description: Realestate data export
Author: Nan Li
Contact: linan.lqq0@gmail.com
'''

# import packages
import os
import pandas as pd
import pandas.io.sql as sql
import mysql.connector
from mysql.connector import errorcode

# change working directory to current folder
os.chdir(os.path.dirname(__file__))

# connect mySQL database
try:
    con = mysql.connector.connect(user='root',password='1LoveBMW',database='aus_sold_houses')
    print("Database connected sucessfully!")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
    exit()

def export_excel(state): 
    sql_cmd = """ SELECT address, suburb, postcode, house_type, bedroom, bathroom, parking, sold_price, sold_date FROM {}
        WHERE sold_date is not null and sold_price is not null AND YEAR(sold_date) > 2017
        AND sold_price < 100000000 and sold_price > 10000
        ORDER BY YEAR(sold_date)""".format(state)
    df = sql.read_sql(sql_cmd, con)
    df.to_excel(writer, index=False, sheet_name = state)
    print("Successfully created excel file")

file_name = os.getcwd()
file_name = file_name + "/Results/data.xlsx";    
writer = pd.ExcelWriter(file_name, engine = 'openpyxl')
export_excel('australian_capital_territory')
export_excel('new_south_wales')
export_excel('northern_territory')
export_excel('queensland')
export_excel('south_australia')
export_excel('tasmania')
export_excel('victoria')
export_excel('western_australia')
writer.save()
writer.close()
con.close()
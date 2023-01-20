'''
Description: Definitions of classes
Author: Nan Li
Contact: linan.lqq0@gmail.com
'''

# import packages
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup

from request import Request
#from request_selenium import Request

# class to extract infos from list page
class ExtractListPage(Request):
    def getNextPage(self):
        nextpage = self.soup.find('a', attrs={'title':'Go to Next Page'})
        return nextpage
    
    def getHouseLink(self):
        houselinks = []
        for link in self.soup.findAll('a', attrs={'href': re.compile(r'/sold/property-\S+-[a-z|-|+]+-[0-9]')}):
            houselinks.append(link.get('href'))
        houselinks = list(dict.fromkeys(houselinks))
        return houselinks

    def getFirstSoldDate(self):
        firstdate = self.soup.find('div', attrs={'class':'residential-card__content'})
        if firstdate is not None:
            firstdate = re.search(r'Sold on [0-9|a-z|A-Z|\s]+[0-9]', firstdate.text)
            if firstdate is not None:
                firstdate = firstdate.group()[8:]
            try:
                firstdate = datetime.strptime(firstdate, '%d %b %Y')
            except:
                firstdate = None
        return firstdate

# class to get house history link from house sold page
class ExtractHouseURL(Request):
    def getHouseID(self):
        house_id = self.soup.find('span', attrs={'class':'listing-metrics__property-id'})
        if house_id is not None:
            house_id = int(re.search(r'[0-9]+', house_id.text).group())
        return house_id

    def getHistoryURL(self):
        history = self.soup.find('div', attrs={'class':'property-info__footer-content'})
        if history is not None:
            try:
                history = history.a['href']
            except:
                history = None
        return history

    def getSoldPrice(self):
        soldprice = None
        soldprice_str = self.soup.find('span', attrs={'class':'property-price property-info__price'}).text
        price = re.search(r'[0-9|,]+', soldprice_str)
        if price is not None:
            soldprice = int(price.group().replace(',', ''))
        return soldprice

    def getSoldDate(self):
        solddate = self.soup.find('div', attrs={'class':'property-info__middle-content'})
        if solddate is not None:
            solddate = re.search(r'Sold on [0-9|a-z|A-Z|\s]+[0-9]', solddate.text)
            if solddate is not None:
                solddate = solddate.group()[8:]
            try:
                solddate = datetime.strptime(solddate, '%d %b %Y')
            except:
                solddate = None
        return solddate
    
    def getAgency(self):
        agency = self.soup.findAll('a', attrs={'class':'LinkBase-sc-12oy0hl-0 cZuyFH sidebar-traffic-driver__name'})
        num = len(agency)
        if num > 0 and agency[num-1] is not None:
            agency = agency[num-1].text
        else:
            agency = None
        return agency

    def getAddress(self):
        address_full = self.soup.find('h1', attrs={'class':'property-info-address'}).text
        suburb = re.search(r',\s[a-z|A-Z|\-|\s]+,\s[a-z|A-Z]+\s[0-9]+', address_full).group()
        suburb = re.search(r',[a-z|A-Z|\-|\s]+,', suburb).group()
        suburb = suburb[2:-1]
        post_code = re.findall(r',[a-z|A-Z|\s]+[0-9]+', address_full)[-1]
        post_code = re.search(r'[0-9]+', post_code).group()
        address = address_full.rfind(suburb)
        address = address_full[:address-2]
        return address, suburb, int(post_code)

    def getHouseType(self):
        housetype = self.soup.find('span', attrs={'class':'property-info__property-type'}).text
        return housetype

    def getFeatures(self):
        bedroom = 0
        bathroom = 0
        parking = 0
        feature_str = ''
        
        for feature in self.soup.findAll('div', attrs={'class':'View__PropertyDetail-sc-11ysrk6-0 gIMwxl'}):
            feature_str = feature_str + feature.get('aria-label')
        bed = re.search(r'[0-9]+\sbedroom', feature_str)
        if bed is not None:
            bedroom = int(re.search(r'[0-9]+', bed.group()).group())
        bath = re.search(r'[0-9]+\sbathroom', feature_str)
        if bath is not None:
            bathroom = int(re.search(r'[0-9]+', bath.group()).group())
        park = re.search(r'[0-9]+\sparking space', feature_str)
        if park is not None:
            parking = int(re.search(r'[0-9]+', park.group()).group())
        return bedroom, bathroom, parking

    def getLocation(self):
        latitude = re.search(r'"latitude\\\\\\":-[0-9|.]+', self.text)
        if latitude is not None:
            latitude = -float(re.search(r'[0-9|.]+', latitude.group()).group())
        longitude = re.search(r'"longitude\\\\\\":[0-9|.]+', self.text)
        if longitude is not None:
            longitude = float(re.search(r'[0-9|.]+', longitude.group()).group())
        return latitude, longitude

    def getLandSize(self):
        land_size  = self.soup.find('div', attrs={'class':'View__PropertySizeGroup-sc-1psmy31-1 gGCxa-D property-size-group'})
        if land_size is not None:
            land_size = re.search(r'[0-9|.|,]+', land_size.text).group().replace(',','')
            land_size = int(float(land_size))
        else:
            land_size = 0
        return land_size

# class to get house info from house history page
class ExtractHouseInfo(Request):
    def getAddress(self):
        address = re.search(r'REA.longStreetAddress = "[0-9|a-z|A-Z|\/|-|\s|\-]+";', self.text)
        if address is not None:
            address = re.search(r'".*"', address.group()).group()
            address = address[1: -1]
        suburb = re.search(r'REA.suburb = "[0-9|a-z|A-Z|\s]+";', self.text)
        if suburb is not None:
            suburb = re.search(r'"[0-9|a-z|A-Z|\s]+"', suburb.group()).group()
            suburb = suburb[1: -1]
        post_code = re.search(r'REA.postcode = "[0-9|a-z|A-Z|\s]+";', self.text)
        if post_code is not None:
            post_code = re.search(r'"[0-9|a-z|A-Z|\s]+"', post_code.group()).group()
            post_code = post_code[1: -1]
        return address, suburb, int(post_code)

    def getHouseType(self):
        housetype = re.search(r'REA.buildingType = "[0-9|a-z|A-Z|\s]+";', self.text)
        if housetype is not None:
            housetype = re.search(r'"[0-9|a-z|A-Z|\s]+"', housetype.group()).group()
            housetype = housetype[1: -1]
        return housetype

    def getLocation(self):
        latitude = re.search(r'REA.lat = "-[0-9|.]+";', self.text)
        if latitude is not None:
            latitude = re.search(r'".*"', latitude.group()).group()
            latitude = latitude[1: -1]
            latitude = float(latitude)
        longitude = re.search(r'REA.lon = "[0-9|.]+";', self.text)
        if longitude is not None:
            longitude = re.search(r'".*"', longitude.group()).group()
            longitude = longitude[1: -1]
            longitude = float(longitude)
        return latitude, longitude
    
    def getREAID(self):
        REA_id = re.search(r'REA.propertyId = "[0-9]+";', self.text)
        if REA_id is not None:
            REA_id = re.search(r'".*"', REA_id.group()).group()
            REA_id = REA_id[1: -1]
            REA_id = int(REA_id)
        return REA_id
        
    def getLandInfo(self):
        land_info = self.soup.find('table', attrs={'class':'info-table'})
        land_size = 0
        floor_area = 0
        year_built = 0
        if land_info is not None:
            land_info = land_info.text
            land_size = re.search(r'Land size\s+[0-9|,]+\s', land_info)
            if land_size is not None:
                try:
                    land_size = int(re.search(r'[0-9|,]+', land_size.group()).group().replace(',', ''))
                except:
                    land_size = 0
            else:
                land_size = 0
            floor_area = re.search(r'Floor area\s+[0-9|,]+\s', land_info)
            if floor_area is not None:
                try:
                    floor_area = int(re.search(r'[0-9|,]+', floor_area.group()).group().replace(',', ''))
                except:
                    floor_area = 0
            else:
                floor_area = 0
            year_built = re.search(r'Year built\s+[0-9]+', land_info)
            if year_built is not None:
                try:
                    year_built = int(re.search(r'[0-9]+', year_built.group()).group().replace(',', ''))
                except:
                    year_built = 0
            else:
                year_built = 0
        return land_size, floor_area, year_built

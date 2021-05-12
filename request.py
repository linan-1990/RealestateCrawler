'''
Description: Definitions of Request class
Author: Nan Li
Contact: linan.lqq0@gmail.com
'''

# import packages
import time
import requests
from headers import headers
from bs4 import BeautifulSoup
from functions import get_cookie, update_cookie

header = headers

# class to send request to web server
class Request:
    def __init__(self, url, randnum):
        self.url = url
        self.redir_url = None
        self.header = header[randnum]
        resp = requests.get(url=self.url, headers=self.header)
        for r in resp.history:
            self.redir_url = r.headers['Location']
        self.status_code = resp.status_code
        if self.status_code != 200:
            print("{}, {}".format(randnum, self.status_code))
            # update cookie in memory and on disk
            cookie = get_cookie(url, headers[randnum]["user-agent"])
            header[randnum]["cookie"] = cookie
            update_cookie(headers[randnum]["cookie"], cookie)
            raise Exception('cookie does not work.')
        self.text = resp.text
        self.soup = BeautifulSoup(self.text, 'html.parser')
        #time.sleep(1)
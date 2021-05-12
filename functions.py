'''
Description: Definitions of functions
Author: Nan Li
Contact: linan.lqq0@gmail.com
'''
# import packages
import re
import time
import pandas as pd
from headers import headers
from datetime import datetime
from seleniumwire import webdriver

# short names dictionary
address_dict = ({'road':'rd', 'street':'st', 'place':'pl', 'avenue':'ave',
                'parade':'pde', 'highway':'hwy', 'drive':'dr', 'grove':'gr',
                'crescent':'cres', 'court':'ct', 'close':'cl', 'circuit':'cct',
                'avenue':'ave', 
                })

# function to read postcode from excel file
def readPostcode(file_name):
    postcode = pd.read_excel(file_name).sort_values(by=['Postcode'])
    postcode = postcode.values
    postcode = postcode[:,0].astype(int)
    return postcode

# function to create valid url according to postcode
def createUrl(postcode, page_no):
    url_pre = 'https://www.realestate.com.au/sold/in-'
    if postcode < 1000:
        url = '{}0{}/list-{}?includeSurrounding=false'.format(url_pre, postcode, page_no)
    elif postcode < 10000:
        url = '{}{}/list-{}?includeSurrounding=false'.format(url_pre, postcode, page_no)
    else:
        print('Wrong postcode!!')
        exit()
    return url

# function to create valid url according to address
def createHouseUrl1(address, suburb, postcode, use_short):
    url_pre = 'https://www.realestate.com.au/property/'
    str_address = address.lower()
    if re.search(r'[0-9|a-z]+/[0-9]', str_address) is not None:
        str_address = 'unit-' + str_address
    if use_short:
        for key in address_dict.keys():
            street_name = re.search(key, str_address)
            if street_name is not None:
                str_address = re.sub(street_name.group(), address_dict[key], str_address)
    str_suburb = suburb.lower()
    if postcode < 1000:
        str_postcode = 'nt-0{:d}'.format(postcode)
    elif postcode < 2600:
        str_postcode = 'nsw-{:d}'.format(postcode)
    elif postcode < 2700:
        str_postcode = 'act-{:d}'.format(postcode)
    elif postcode < 2800:
        str_postcode = 'nsw-{:d}'.format(postcode)
    elif postcode < 3000:
        str_postcode = 'act-{:d}'.format(postcode)
    elif postcode < 4000:
        str_postcode = 'vic-{:d}'.format(postcode)
    elif postcode < 5000:
        str_postcode = 'qld-{:d}'.format(postcode)
    elif postcode < 6000:
        str_postcode = 'sa-{:d}'.format(postcode)
    elif postcode < 7000:
        str_postcode = 'wa-{:d}'.format(postcode)
    elif postcode < 8000:
        str_postcode = 'tas-{:d}'.format(postcode)
    str_address = '{}-{}-{}'.format(str_address, str_suburb, str_postcode)
    str_address = re.sub('[,|\s|/]', '-', str_address)
    for _ in range(4):
        str_address = re.sub('--', '-', str_address)
    url = url_pre + str_address
    return url

# function to create url according to REA_id
def createHouseUrl2(REA_id):
    url = 'https://www.realestate.com.au/property/lookup?id={:d}'.format(REA_id)
    return url

def get_cookie(url, user_agent):
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=100x100")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    driver = webdriver.Chrome(options=options)
    driver._orig_get = driver.get
    def _get_wrapped(*args, **kwargs):
        if driver.execute_script("return navigator.webdriver"):
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": """
                                Object.defineProperty(window, 'navigator', {
                                    value: new Proxy(navigator, {
                                    has: (target, key) => (key === 'webdriver' ? false : key in target),
                                    get: (target, key) =>
                                        key === 'webdriver'
                                        ? undefined
                                        : typeof target[key] === 'function'
                                        ? target[key].bind(target)
                                        : target[key]
                                    })
                                });
                            """
                },
            )
        return driver._orig_get(*args, **kwargs)
    driver.get = _get_wrapped
    driver.get = _get_wrapped
    driver.get = _get_wrapped
    original_user_agent_string = driver.execute_script(
        "return navigator.userAgent"
    )
    driver.execute_cdp_cmd(
        "Network.setUserAgentOverride",
        {
            "userAgent": original_user_agent_string.replace("Headless", ""),
        },
    )
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                            Object.defineProperty(navigator, 'maxTouchPoints', {
                                get: () => 1
                        })"""
        },
    )

    def interceptor(request):
        del request.headers['user-agent']
        request.headers['user-agent'] = user_agent
        # Block PNG, JPEG and GIF images
        if request.path.endswith(('.png', '.jpg', '.gif')):
            request.abort()

    driver.request_interceptor = interceptor
    driver.get(url)
    time.sleep(1) # wait for cookies loaded
    for request in driver.requests:
        if request.response.status_code == 200:
            cookie = re.search(r"(bm_aksd=[\S]+);", str(request.response.headers))
            if cookie is not None:
                cookie = cookie.group(1)
                break
    driver.quit()
    return cookie

def update_cookie(old, new):
    with open("headers.py", "r") as f:
        data = f.read()
        data = re.sub(old, new, data)
        
    with open("headers.py", "w") as f:
        f.write(data)
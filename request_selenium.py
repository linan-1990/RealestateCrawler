'''
Description: Definitions of Request using Selenium class
Author: Nan Li
Contact: linan.lqq0@gmail.com
'''

# import packages
import io
import re
import time
import string
import random
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver


# class to send request to web server
class Request:
    def __init__(self, url, randnum):
        self.url = url
        #self.executable_path = r"C:/Program Files/Python38/chromedriver.exe"
        #self.patch_binary()
        options = webdriver.ChromeOptions()
        #options.add_argument("--headless")
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
        driver.get(url)
        time.sleep(2) # wait for cookies loaded
        self.text = driver.page_source
        self.soup = BeautifulSoup(self.text, 'html.parser')
        driver.quit()

    @staticmethod
    def random_cdc():
        cdc = random.choices(string.ascii_lowercase, k=26)
        cdc[-6:-4] = map(str.upper, cdc[-6:-4])
        cdc[2] = cdc[0]
        cdc[3] = "_"
        return "".join(cdc).encode()

    def patch_binary(self):
        """
        Patches the ChromeDriver binary
        :return: False on failure, binary name on success
        """
        linect = 0
        replacement = self.random_cdc()
        with io.open(self.executable_path, "r+b") as fh:
            for line in iter(lambda: fh.readline(), b""):
                if b"cdc_" in line:
                    fh.seek(-len(line), 1)
                    newline = re.sub(b"cdc_.{22}", replacement, line)
                    fh.write(newline)
                    linect += 1
            return linect
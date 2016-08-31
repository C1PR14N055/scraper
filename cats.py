#!/bin/python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
''' WAIT FOR EXPECTED CONDITIONS IMPORTS '''
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
''' END WAIT FOR EXPECTED CONDITIONS IMPORTS '''

from pprint import pprint #pretty print json
import os, time, json

admin_url = 'http://www.premium-store.ro/admin/'
admin_usr = 'admin'
admin_pass = '2VxHnFZfCeF6'
auth_token = None

#URLS
insert_cat_url = 'http://www.premium-store.ro/admin/index.php?route=catalog/category/insert'
#URLS

browser = None
once = False

list_of_cats = []
cat_input = "#language2 > table > tbody > tr:nth-child(1) > td:nth-child(2) > input[type='text']"

def make_cats():
    rootDir = './prod/'
    for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
        #print('Found directory: %s' % dirName)
        for fname in fileList:
            #print('\t%s' % fname) 
            if fname == "prod.json":
                #print dirName + " >> " + fname
                with open(dirName + "/" + fname) as data_file:    
                    prod = json.load(data_file)
                if ("Accesorii " + prod["title"] + " " + prod["subtitle"]) not in list_of_cats:
                    list_of_cats.append(("Accesorii " + prod["title"] + " " + prod["subtitle"]))

    for cat in list_of_cats:
        #print cat.encode("utf-8")
        browser.get(insert_cat_url + auth_token)
        wait_for_presence(cat_input)
        q(cat_input)[0].send_keys(cat)
        exec_s("$('#form').submit();")


def exec_s(script):
    global browser
    browser.execute_script(script)   

def wait_for_presence(selector):
    global browser
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))      

def q(css_sel):
    global browser
    return browser.find_elements_by_css_selector(css_sel)      

def q_name(name_sel):
    global browser
    return browser.find_elements_by_name(name_sel)[0]          

def login():
    global browser
    browser.get(admin_url)
    username = browser.find_elements_by_name("username")[0]
    password = browser.find_elements_by_name("password")[0]
    username.send_keys(admin_usr)
    password.send_keys(admin_pass)
    q("form a.button")[0].click()
    return browser.current_url[browser.current_url.index("&token="):]

def init():
    global browser, auth_token
    browser = webdriver.Firefox()
    auth_token = login()
    make_cats()

init()
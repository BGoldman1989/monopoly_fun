"""
Scrapes history of codes entered by user for the
online Monopoly Sweepstakes and outputs to csv
"""

import ConfigParser
from csv import DictWriter, QUOTE_MINIMAL
from os import path, makedirs
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

config = ConfigParser.ConfigParser()
config.read("config.ini")

#Initialize Webdriver
options = ChromeOptions()
options.add_argument("--incognito")
driver = Chrome(executable_path="chromedriver.exe",
                chrome_options=options)

#Login to monopoly sweepstakes page
driver.get("https://www.playmonopoly.us/login")
email = driver.find_element_by_id("email")
password = driver.find_element_by_id("password")
submit = driver.find_element_by_class_name("btn-submit")
email.send_keys(config.get("Monopoly Login Credentials","email"))
password.send_keys(config.get("Monopoly Login Credentials","password"))
submit.click()

try:
    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CLASS_NAME, "logged-in"))
    )
    driver.get("https://www.playmonopolycodes.us/code-history")

    #get table of entered codes
    code_history = driver.find_element_by_class_name("table")
    header = code_history.find_elements_by_css_selector("thead th")
    body = code_history.find_elements_by_css_selector(".codes tr")

    #Write to csv file
    if not path.exists("output"):
        makedirs("output")
    with open("output/codes.csv", "w+") as csvfile:
        fieldnames = [col.text for col in header[1:]]
        code_history_csv = DictWriter(csvfile, lineterminator='\n',
                                        quoting=QUOTE_MINIMAL,
                                        fieldnames=fieldnames)
        code_history_csv.writeheader()

        for row in body:
            row_arr = {}
            cols = row.find_elements_by_tag_name("td")
            for i in xrange(1, len(cols)):
                row_arr[fieldnames[i-1]] = cols[i].text
            code_history_csv.writerow(row_arr)
finally:
    driver.quit()

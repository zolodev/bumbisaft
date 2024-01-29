#****************************************************************************
# Filename      : fetchSkandiaData.py
# Created       : Fri Jan 19 2024
# Author        : Zolo
# Github        : https://github.com/zolodev
# Description   : This is a test to get fund information from Skandia
#****************************************************************************

import os
import time
import json, operator
from seleniumwire import webdriver
from haralyzer import HarParser, HarPage
from datetime import datetime

TITLE = "Skandia"


def obj_dict(obj):
    return obj.__dict__

class FundData(object):
    Name = ""
    isin = ""
    URL = ""
    LastUpdated = ""
    Day = 0.0
    Week = 0.0
    

    def __init__(self, name, isin, url, lastUpdated, day, week):
        self.Name = name
        self.isin = isin
        self.URL = url
        self.LastUpdated = lastUpdated
        self.Day = day
        self.Week = week

    def to_json(self): 
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__) 

def write_HAR_file(filename=None, har_to_write=""):
    # Write the information to a new JSON file
    if filename is not None:
        with open('HAR_'+filename+'.har', 'w') as f:
            f.write(json.dumps(har_to_write, indent=4, sort_keys=True))
    else:
        with open('HAR_Data.har', 'w') as f:
            f.write(json.dumps(har_to_write, indent=4, sort_keys=True))



def write_HAR_from_URL(filename, URL, WAIT_SECONDS=29, WRITE_TO_FILE=True):
    # Chrome options configurations
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument('--no-sandbox')
    
    # Selenium-Wire configuration
    sw_options = {
        'enable_har': True
    }

    # Prepare the driver
    driver = webdriver.Chrome(
        options=chrome_options,
        seleniumwire_options=sw_options
    )

    # Get the URL contents
    driver.get(URL)
    time.sleep(WAIT_SECONDS)
    driver.implicitly_wait(WAIT_SECONDS)

    # Store the HAR data in a new variable
    har_to_return = json.loads(driver.har)

    # Close and Quit the driver
    driver.close()
    driver.quit()

    if WRITE_TO_FILE:
        write_HAR_file(filename, har_to_return)

    return har_to_return


def find_HAR_content_by_req(filename, part_to_find=""):
    #PART_TO_FIND = "/api/fundlist/desktop"

    # Read the HAR data
    with open('HAR_'+filename+'.har', 'r') as f:
        har_parser = HarParser(json.loads(f.read()))

    # Traverse the HAR data
    for page in har_parser.pages:
        for entry in page.entries:

            # Find the correct request by url
            req_url = entry['request']['url']
            #print("Requests URL: " + req_url )
            if part_to_find in req_url:
                print("Requests URL: " + req_url )

                # Get the response content where the request match
                res_content = str(entry['response']['content']['text'])
                #print(json.dumps(json.loads(res_content), indent=4, sort_keys=True))

                # Save the json information to a file for further processing
                with open(filename+'_data.json', 'w') as f:
                    f.write(json.dumps(json.loads(res_content), indent=4, sort_keys=True))


def filter_skandia_json_data(filename="Skandia"):
    skandia_data = ""
    with open(filename+'_data.json') as f:
        skandia_data = json.load(f)

    filtered_funds = []
    for i in range(0, len(skandia_data)):
        
        # Check if the fund is in correct collection
        if "Fondf\u00f6rs\u00e4kring" not in skandia_data[i]["collections"]:
            continue

        returnOneDay = float(skandia_data[i]["returnOneDay"]) if skandia_data[i]["returnOneDay"] is not None else 0
        returnOneWeek = float(skandia_data[i]["returnOneWeek"]) if skandia_data[i]["returnOneWeek"] is not None else 0
        returnOneMonth = float(skandia_data[i]["returnOneMonth"]) if skandia_data[i]["returnOneMonth"] is not None else 0
        returnThreeMonths = float(skandia_data[i]["returnThreeMonths"]) if skandia_data[i]["returnThreeMonths"] is not None else 0
        returnSixMonths = float(skandia_data[i]["returnSixMonths"]) if skandia_data[i]["returnSixMonths"] is not None else 0
        returnThisYear = float(skandia_data[i]["returnThisYear"]) if skandia_data[i]["returnThisYear"] is not None else 0
        returnOneYear = float(skandia_data[i]["returnOneYear"]) if skandia_data[i]["returnOneYear"] is not None else 0
        returnThreeYears = float(skandia_data[i]["returnThreeYears"]) if skandia_data[i]["returnThreeYears"] is not None else 0
        returnFiveYears = float(skandia_data[i]["returnFiveYears"]) if skandia_data[i]["returnFiveYears"] is not None else 0
        returnTenYears = float(skandia_data[i]["returnTenYears"]) if skandia_data[i]["returnTenYears"] is not None else 0


        # Check all values to be positive before adding the fund to the list
        if( returnOneDay > 0 and
            returnOneWeek > 0 and
            returnOneMonth> 0 and
            returnThreeMonths > 0 and
            returnSixMonths > 0 and
            returnThisYear > 0 and
            returnOneYear > 0 and
            returnThreeYears > 0 and
            returnFiveYears > 0 and
            returnTenYears > 0):
                fund_name = skandia_data[i]["name"]
                fund_isin = skandia_data[i]["isin"]
                fund_currency = skandia_data[i]["currency"]
            
                fund_url_base = "https://www.skandia.se/spara-pension/satt-att-spara/spara-fonder/fondlista#/fund/details/[isin]/[currency]"
                
                fund_url = fund_url_base.replace("[isin]", str(fund_isin))
                fund_url = fund_url.replace("[currency]", str(fund_currency))
            
                # Get current date and time
                now = datetime.now()
                dt_string = now.strftime("%Y-%m-%d %H:%M:%S") # YYYY-MM-DD HH:MM:SS
                
                fundDataObj = {}
                fundDataObj = FundData( name = fund_name,
                                        isin = fund_isin,
                                        url = fund_url,
                                        lastUpdated = str(dt_string) + " (UTC)",
                                        day = returnOneDay,
                                        week = returnOneWeek)

                filtered_funds.append(fundDataObj)

    # Sort the list based on the day
    sorted_filtered_funds = sorted(filtered_funds, key=lambda fundDataObj: fundDataObj.Day, reverse=True)

    with open(filename+'_data_filtered.json', 'w') as f:
        f.write(json.dumps(sorted_filtered_funds, indent=4, default=lambda o: o.__dict__))

    return sorted_filtered_funds


def run():
    #write_HAR_from_URL("Google", "https://www.google.com")
    sel_har = write_HAR_from_URL("Skandia", "https://www.skandia.se/spara-pension/satt-att-spara/spara-fonder/fondlista?collections=Fondf%C3%B6rs%C3%A4kring")

    find_HAR_content_by_req(TITLE, "/api/fundlist/desktop")

    filter_skandia_json_data()
    
    # Delete the HAR file because it could be large and unnecessary to have it in the repo
    os.remove("HAR_Skandia.har")
    #os.remove("Skandia_data.json")
    

if __name__ == "__main__":
    run()

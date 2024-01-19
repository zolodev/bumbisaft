#****************************************************************************
# Filename      : fetchSkandiaData.py
# Created       : Fri Jan 19 2024
# Author        : Zolo
# Github        : https://github.com/zolodev
# Description   : This is a test to get fund information from Skandia
#****************************************************************************


import json
from seleniumwire import webdriver
from haralyzer import HarParser, HarPage


TITLE = "Skandia"


def write_HAR_file(filename=None, har_to_write=""):
    # Write the information to a new JSON file
    if filename is not None:
        with open('HAR_'+filename+'.har', 'w') as f:
            f.write(json.dumps(har_to_write, indent=4, sort_keys=True))
    else:
        with open('HAR_Data.har', 'w') as f:
            f.write(json.dumps(har_to_write, indent=4, sort_keys=True))



def write_HAR_from_URL(filename, URL, WAIT_SECONDS=15, WRITE_TO_FILE=True):
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

    


def run():
    #write_HAR_from_URL("Google", "https://www.google.com")
    sel_har = write_HAR_from_URL("Skandia", "https://www.skandia.se/spara-pension/satt-att-spara/spara-fonder/fondlista?collections=Fondf%C3%B6rs%C3%A4kring")

    find_HAR_content_by_req(TITLE, "/api/fundlist/desktop")


if __name__ == "__main__":
    run()
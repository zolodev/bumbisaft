#****************************************************************************
# Filename      : fetchData.py
# Created       : Fri Jan 19 2024
# Author        : Zolo
# Github        : https://github.com/zolodev
# Description   : Test get aggregated data to a local json file.
#****************************************************************************

import requests
import json

# Helper Function to print object to json
# For example: json.dumps(listToPrint, default=obj_dict, indent=4) 
def obj_dict(obj):
    return obj.__dict__

class FundDataList:
    Label = ""
    FundData = []

    def __init__(self, label, fundData):
            self.Label = label
            self.FundData = fundData

class FundData(object):
    Name = ""
    PPMCode = 0
    URL = ""
    Current = 0.0
    Yesterday = 0.0
    LastWeek = 0.0
    TrendDay = ""
    TrendWeek = ""
    TrendAwesome = ""
    Label = ""

    def __init__(self, name, ppmcode, url, current, yesterday, lastWeek, trendDay, trendWeek, trendAwesome, label):
        self.Name = name
        self.PPMCode = ppmcode
        self.URL = url
        self.Current = current
        self.Yesterday = yesterday
        self.LastWeek = lastWeek
        self.TrendDay = trendDay
        self.TrendWeek = trendWeek
        self.TrendAwesome = trendAwesome
        self.Label = label

    def to_json(self): 
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__) 

def get_fund_trend_by_id(single_fund_id :int):
    dict_to_return = {}
    
    single_fund_url = "https://www.avanza.se/_api/fund-guide/chart/<ID>/three_months"
    single_fund_url = single_fund_url.replace("<ID>", str(single_fund_id))
    
    single_fund_payload = ""
    headers = {
        "Content-Type": "application/json",
        "charset": "UTF-8"
    }

    single_fund_response = requests.request("GET", single_fund_url, data=single_fund_payload, headers=headers)
    single_fund_data = json.loads(single_fund_response.text)

    points_len = int(len(single_fund_data["dataSerie"]))

    # Store some extra data in the return object
    dict_to_return["day_current_value"] = float(single_fund_data["dataSerie"][points_len-1]["y"])
    dict_to_return["day_prev_value"] = float(single_fund_data["dataSerie"][points_len-2]["y"])
    dict_to_return["week_prev_value"] = float(single_fund_data["dataSerie"][points_len-8]["y"])

    # Day trend
    if(float(single_fund_data["dataSerie"][points_len-1]["y"]) > float(single_fund_data["dataSerie"][points_len-2]["y"])):
        #return "▲"
        dict_to_return["day"] = "▲"
    if(float(single_fund_data["dataSerie"][points_len-1]["y"]) < float(single_fund_data["dataSerie"][points_len-2]["y"])):
        #return "▼"
        dict_to_return["day"] = "▼"
    if(float(single_fund_data["dataSerie"][points_len-1]["y"]) == float(single_fund_data["dataSerie"][points_len-2]["y"])):
        #return "-"
        dict_to_return["day"] = "-"

    # Week trend
    if(float(single_fund_data["dataSerie"][points_len-1]["y"]) > float(single_fund_data["dataSerie"][points_len-8]["y"])):
        dict_to_return["week"] = "▲"
    if(float(single_fund_data["dataSerie"][points_len-1]["y"]) < float(single_fund_data["dataSerie"][points_len-8]["y"])):
        dict_to_return["week"] = "▼"
    if(float(single_fund_data["dataSerie"][points_len-1]["y"]) == float(single_fund_data["dataSerie"][points_len-8]["y"])):
        dict_to_return["week"] = "-"

    return dict_to_return


def get_funds_from_ListView(label :str, funds_list :list):
    fundDataList_to_return = []

    single_fund_payload = ""
    single_headers = {
        "Content-Type": "application/json",
        "charset": "UTF-8"
    }

    funds_list_len = len(funds_list["fundListViews"])
    
    for i in range(0, funds_list_len):
        
        current_fund_id = funds_list["fundListViews"][i]["orderbookId"]
        api_url = "https://www.avanza.se/_api/fund-reference/reference/"+current_fund_id
        fund_url ="https://www.avanza.se/fonder/om-fonden.html/"+current_fund_id
        fund_name = funds_list["fundListViews"][i]["name"]

        single_response = requests.request("GET", api_url, data=single_fund_payload, headers=single_headers)
        single_response_data = json.loads(single_response.text)

        if single_response_data["ppmCode"] is not None:
            dict_trend = get_fund_trend_by_id(current_fund_id)

            # Set flex, when trend for day and week both point upwards
            bAwesome = ""
            if (dict_trend["day"] == "\u25b2" and dict_trend["week"] == "\u25b2"):
                bAwesome = "💪"

            fundDataObj = {}
            fundDataObj = FundData(name = fund_name, 
                                    ppmcode = single_response_data["ppmCode"],
                                    url = fund_url,
                                    current = dict_trend["day_current_value"],
                                    yesterday = dict_trend["day_prev_value"],
                                    lastWeek = dict_trend["week_prev_value"],
                                    trendDay = dict_trend["day"],
                                    trendWeek = dict_trend["week"],
                                    trendAwesome = bAwesome,
                                    label = label)
            
            fundDataList_to_return.append(fundDataObj)

    return fundDataList_to_return


def run():
    fund_list_url = "https://www.avanza.se/_api/fund-guide/list"

    fund_list_payload_day = {
        "sortField": "developmentOneDay",
        "sortDirection": "DESCENDING"
    }

    fund_list_payload_week = {
        "sortField": "developmentOneWeek",
        "sortDirection": "DESCENDING"
    }

    headers = {
        "Content-Type": "application/json",
        "charset": "UTF-8"
    }

    fund_list_daily_response = requests.request("POST", fund_list_url, json=fund_list_payload_day, headers=headers)

    fund_list_weekly_response = requests.request("POST", fund_list_url, json=fund_list_payload_week, headers=headers)

    fundListViewsWeeklyData = json.loads(fund_list_weekly_response.text)
    fundListViewsDailyData = json.loads(fund_list_daily_response.text)

    listDailyFunds = get_funds_from_ListView("DAILYS", fundListViewsDailyData)
    listWeeklyFunds = get_funds_from_ListView("WEEKLYS", fundListViewsWeeklyData)

    fundDataListDaily = FundDataList("DAILYS", listDailyFunds)
    fundDataListWeekly = FundDataList("WEEKLYS", listWeeklyFunds)

    # Aggregate the lists
    fundDataList = [fundDataListDaily, fundDataListWeekly]

    avanza_dailys_and_weeklys_funds_data = json.dumps(fundDataList, default=obj_dict, indent=4)
    print(avanza_dailys_and_weeklys_funds_data)

    if avanza_dailys_and_weeklys_funds_data is not None:
        with open('data.json', 'w') as f:
                f.write(avanza_dailys_and_weeklys_funds_data)


if __name__ = "__main__":
    run()
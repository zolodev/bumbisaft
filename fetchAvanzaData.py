#****************************************************************************
# Filename      : fetchData.py
# Created       : Fri Jan 19 2024
# Author        : Zolo
# Github        : https://github.com/zolodev
# Description   : Test get aggregated data to a local json file.
#****************************************************************************

import json
from datetime import datetime, timedelta

import requests


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
    LastUpdated = ""
    history = False

    def __init__(self, name, ppmcode, url, current, yesterday, lastWeek, trendDay, trendWeek, trendAwesome, label, lastUpdated, history):
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
        self.LastUpdated = lastUpdated
        self.history = history

    def to_json(self): 
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__) 

def check_name(name_to_check, list_to_check):
    return any(obj['Name'] == name_to_check for obj in list_to_check)

def get_history_data(github_user:str = "zolodev", 
                    repo:str = "bumbisaft", 
                    file:str = "avanza_data.json"):


    # Calculate the timestamp for one week ago
    now = datetime.now()
    one_week_ago = now - timedelta(days=7)
    timestamp_since = int(one_week_ago.timestamp())
    timestamp_until = int(datetime.now().timestamp())

    url = f"https://api.github.com/repos/{github_user}/{repo}/commits?path={file}&since={timestamp_since}&until={timestamp_until}"
    response = requests.get(url)
    data = json.loads(response.text)
    
    list_sha = []
    for single_sha in data:
        list_sha.append(single_sha["sha"])

    merged_data = []
    for sha in list_sha:
        template_url = f"https://raw.githubusercontent.com/{github_user}/{repo}/{sha}/{file}"
        response_tmp = requests.get(template_url)
        data_single = json.loads(response_tmp.text)
        merged_data += data_single[0]["FundData"] # Get all DAILYS
        merged_data += data_single[1]["FundData"] # Get all WEEKLYS


    # Separate each type into separate lists
    merged_DAILYS = []
    merged_WEEKLYS = []

    for obj in merged_data:
        if any("HISTORY" in obj for key in obj):
            del obj["HISTORY"]

        # Mark as a history fund
        obj["history"] = True

        # Remove older than 7days of history
        delta = datetime.now() - datetime.strptime(obj["LastUpdated"], "%Y-%m-%d %H:%M:%S")
        if delta.days < 7:
            if "Label" in obj and obj["Label"] == "DAILYS":
                if not check_name(obj["Name"], merged_DAILYS):
                    merged_DAILYS.append(obj)
            else:
                if not check_name(obj["Name"], merged_WEEKLYS):
                    merged_WEEKLYS.append(obj)

    # Return a dict for each type
    return {"DAILYS": merged_DAILYS, "WEEKLYS":merged_WEEKLYS}

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


            # Get current date and time
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S") # YYYY-MM-DD HH:MM:SS
            
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
                                    label = label,
                                    lastUpdated = str(dt_string) + " (UTC)",
                                    history = False)
            
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

    # Fetch previously 7 days of history data
    dict_history = get_history_data()
    
    listDailyFunds = get_funds_from_ListView("DAILYS", fundListViewsDailyData)
    listDailyFunds += dict_history["DAILYS"]
    
    listWeeklyFunds = get_funds_from_ListView("WEEKLYS", fundListViewsWeeklyData)
    listWeeklyFunds += dict_history["WEEKLYS"]

    fundDataListDaily = FundDataList("DAILYS", listDailyFunds)
    fundDataListWeekly = FundDataList("WEEKLYS", listWeeklyFunds)

    # Aggregate the lists
    fundDataList = [fundDataListDaily, fundDataListWeekly]

    avanza_dailys_and_weeklys_funds_data = json.dumps(fundDataList, default=obj_dict, indent=4)
    print(avanza_dailys_and_weeklys_funds_data)

    if avanza_dailys_and_weeklys_funds_data is not None:
        with open('avanza_data.json', 'w') as f:
                f.write(avanza_dailys_and_weeklys_funds_data)

if __name__ == "__main__":
    run()
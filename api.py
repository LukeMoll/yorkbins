import requests
import datetime

def get_properties_for_postcode(postcode):
    url = "https://doitonline.york.gov.uk/BinsApi/EXOR/getPropertiesForPostCode"
    r = requests.get(url, params={'postcode': postcode})
    return r.json()

def get_waste_collection_data_by_uprn(uprn):
    url = "https://doitonline.york.gov.uk/BinsApi/EXOR/getWasteCollectionDatabyUprn"
    r = requests.get(url, params={'uprn': uprn})
    return r.json()

def parse_date(date_str):
    assert date_str.startswith("/Date(") and date_str.endswith(")/"), "date_str doesn't match expected format!"
    return datetime.date.fromtimestamp(int(date_str[6:-2])/1000)


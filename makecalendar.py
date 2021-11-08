import dates
import api
import ics
import datetime

def make_calendar(uprn : int, cuttoff:datetime.date=datetime.date.today() + datetime.timedelta(days=365)):
    data = api.get_waste_collection_data_by_uprn(uprn)
    today = datetime.date.today()

    cal = ics.Calendar()
    for collection in data:
        for collection_date in dates.calculate_collections_frequency(collection):
            if collection_date > cuttoff: break
            # else
            e = ics.Event()
            e.name = "Bin collection: {}".format(collection["MaterialsCollected"])
            e.begin = datetime.datetime.combine(
                collection_date - datetime.timedelta(days=1), 
                datetime.time(18,0))
            e.end = datetime.datetime.combine(
                collection_date,
                datetime.time(6,0)
            )
            e.url = "https://doitonline.york.gov.uk/BinsApi/Calendars/Index?uprn={}".format(uprn)
            e.description = "See {} for more up-to-date information\nRetrieved on {}".format(e.url, today)
            
            cal.events.add(e)
    
    return cal

if __name__ == "__main__":
    print("Enter UPRN:")
    uprn = int(input())
    with open("bins.ics", "w") as fd:
        fd.writelines(make_calendar(uprn))
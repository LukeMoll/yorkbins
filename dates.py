import datetime
import typing
import api


iso_weekdays = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday"
}

months = {
    1:  "January",
    2:  "February",
    3:  "March",
    4:  "April",
    5:  "May",
    6:  "June",
    7:  "July",
    8:  "August",
    9:  "September",
    10: "October",
    11: "November",
    12: "December"
}

def calculate_collections_incremental(collection_data):
    """Returns a list of calculated collection dates from the supplied collection data, for a single type of waste collection.
    
    Args:
        collection_data: A single object from get_waste_collection_data_by_uprn
    Returns:
        list<datetime.date>
    """

    assert "Frequency" in collection_data
    assert "FrequencyInDays" in collection_data["Frequency"]
    assert "LastCollection" in collection_data
    assert "NextCollection" in collection_data
    assert "MaterialsCollected" in collection_data

    frequency_td = datetime.timedelta(days=int(collection_data["Frequency"]["FrequencyInDays"]))

    last_collection = api.parse_date(collection_data["LastCollection"])
    next_collection = api.parse_date(collection_data["NextCollection"])
    next_collection_calculated =(
        last_collection + 
        frequency_td
    )
    
    yield next_collection

    assert next_collection_calculated == next_collection, "Calculated next collection date did not match provided one"

    while True:
        # not sure when the formula stops being accurate, we might add some logic for crossing year boundaries. 
        next_collection_calculated += frequency_td
        yield next_collection_calculated

        """
            Calculating without induction
            Requires Frequency, CollectionDayFull and CollectionDayOfWeek
            BUT does the week start on 0th or 1st day of week (sun or mon, res)

        day 1 2 3 4 5 6 7 8 9 
            S S M T W T F S S
             | Sunday week 2
 Sunday week 1 |           
        """


def get_week_from_number(year, number, week_starts_on=1) -> typing.Tuple[datetime.date, datetime.date]:
    if week_starts_on == 0: week_starts_on = 7
    assert 1 <= week_starts_on <=7

    firstday = datetime.date(year, 1, 1)
    firstweek = None

    if firstday.isoweekday() == week_starts_on:
        # print("Year starts on a week boundary! ({})".format(iso_weekdays[firstday.isoweekday()]))
        firstweek = (firstday, firstday + datetime.timedelta(days=7))
    else:
        # year starts halfway through a week
        lastday = None
        for i in range(7):
            if datetime.date(year, 1, i+1).isoweekday() == week_starts_on:
                lastday = datetime.date(year, 1, i+1)
                break
        assert lastday is not None
        firstweek = (lastday - datetime.timedelta(days=7), lastday)

    assert firstweek is not None

    return tuple(map(lambda d: d + datetime.timedelta(days=7*(number-1)), firstweek))

# probably use this one tbh
def calculate_collections_frequency(collection_data, year:int=datetime.date.today().year, week_starts_on:int=1) -> typing.Generator[datetime.date, None, None]: 
    while True:
        starting_week = get_week_from_number(year, collection_data["Frequency"]["StartingWeekNumber"], week_starts_on=week_starts_on)

        next_day = starting_week[0] + datetime.timedelta(days=collection_data["CollectionDayOfWeek"]-week_starts_on)

        starting_week_next = get_week_from_number(year + 1, collection_data["Frequency"]["StartingWeekNumber"], week_starts_on=week_starts_on)
        while next_day < starting_week_next[0]:
            yield next_day
            next_day += datetime.timedelta(days=collection_data["Frequency"]["FrequencyInDays"])
        year += 1
        
if __name__ == "__main__":
    import api
    with open('uprn.txt') as fd:
        uprn = int(fd.read())
    data = api.get_waste_collection_data_by_uprn(uprn)
    idx = 1
    print(data[idx]["MaterialsCollected"])
    print(data[idx]["Frequency"], data[idx]["CollectionDayFull"])

    for d in calculate_collections_frequency(data[idx]):
        print(d, months[d.month], iso_weekdays[d.isoweekday()], d.day, end="")
        input()
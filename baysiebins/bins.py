from flask import Flask
import flask
import requests
import icalendar
import pytz
import datetime

app = Flask(__name__)


def get_bin_json(address):
    url = "https://citymapsdev.bayswater.wa.gov.au/arcgis/rest/services/BayswaterExternal/PropertyAddressAGOL_WasteNew_WEB/MapServer/0/query"
    response = requests.get(
        url,
        {
            "f": "json",
            "where": "PropertyAddress='{}'".format(address),
            "returnGeometry": "true",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "PropertyAddress,PropertyName,DomesticWasteCollection,NextGreenWasteCollection,NextRecyclingCollection,WasteArea,cobsuburb,OBJECTID",
            "orderByFields": "PropertyAddress ASC",
            "outSR": "102100",
        },
    )
    obj = response.json()
    if "features" not in obj:
        return
    features = obj["features"]
    if len(features) == 0:
        return
    return features[0]["attributes"]


# https://stackoverflow.com/questions/6558535/find-the-date-for-the-first-monday-after-a-given-date
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


def json_to_ical(obj):
    cal = icalendar.Calendar()
    cal.add("prodid", "-//Bayswater Bins//mxm.dk//")
    cal.add("version", "2.0")

    # figure out our binday
    lookup = {
        "MONDAY": 0,
        "TUESDAY": 1,
        "WEDNESDAY": 2,
        "THURSDAY": 3,
        "FRIDAY": 4,
        "SATURDAY": 5,
        "SUNDAY": 6,
    }

    def get_refuse_date(typ):
        attr = obj[typ].rsplit(" - ", 1)[-1]
        return datetime.datetime.strptime(attr, "%d/%m/%Y").date()

    # in reality for now this is general waste; baysie devs might change this though
    redbin_dt = get_refuse_date("NextGreenWasteCollection")
    yellowbin_dt = get_refuse_date("NextRecyclingCollection")

    binday = obj["DomesticWasteCollection"]
    start_dt = next_weekday(datetime.date.today(), lookup[binday])
    perth = pytz.timezone("Australia/Perth")
    for week in range(-12, 13):
        bin_dt = start_dt + datetime.timedelta(days=7 * week)

        if (bin_dt - redbin_dt).days % 14 == 0:
            thisbin = "Red"
        else:
            thisbin = "Yellow"
        event_dt = bin_dt + datetime.timedelta(days=-1)
        start = datetime.datetime(
            event_dt.year, event_dt.month, event_dt.day, 20, 0, 0, tzinfo=perth
        )
        end = datetime.datetime(
            event_dt.year, event_dt.month, event_dt.day, 21, 0, 0, tzinfo=perth
        )
        event = icalendar.Event()
        event.add("summary", "Put the bins out: Green and {}".format(thisbin))
        event.add("dtstart", start)
        event.add("dtend", end)
        cal.add_component(event)

    return flask.Response(cal.to_ical(), "text/calendar")


@app.route("/<address>.ics")
def hello_world(address):
    obj = get_bin_json(address)
    if not obj:
        flask.abort(404)
    return json_to_ical(obj)

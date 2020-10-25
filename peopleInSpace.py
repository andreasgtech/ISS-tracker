from geopy.distance import geodesic
import requests, json, geocoder, time

def pushbullet_message(title, body):
    msg = {"type": "note", "title": title, "body": body}
    TOKEN = 'INSERT_TOKEN_HERE'
    resp = requests.post('https://api.pushbullet.com/v2/pushes', 
                         data=json.dumps(msg),
                         headers={'Authorization': 'Bearer ' + TOKEN,
                                  'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Error',resp.status_code)
    else:
        print ('Message sent')

def callStation(signal):
    lat = (requests.get("http://api.open-notify.org/iss-now.json")).json()['iss_position']['latitude']
    long = (requests.get("http://api.open-notify.org/iss-now.json")).json()['iss_position']['longitude']
    req = requests.get("http://api.open-notify.org/iss-pass.json?lat=37.983810&lon=23.727539")
    curr_time = int(time.time())
    next_pass = req.json()['response'][1]['risetime']
    g = geocoder.osm([lat, long], method='reverse')
    if (signal == 1) and (g.country == "Greece") and (lat >= 37.868349) and (lat <= 38.134557) and (long >= 23.564478) and (long <= 23.914901):
        signal = 2
        pushbullet_message("ISS visible from Athens now!", "http://www.google.com/maps/place/{},{}".format(lat, long))
    if (signal == 0) and (next_pass - curr_time <= 10800):
        signal = 1
        hours = (next_pass-curr_time)//3600
        minutes = ((next_pass-curr_time)%3600)//60
        seconds = ((next_pass-curr_time)%3600)%60
        pushbullet_message("ISS will be visible from Athens soon!", "{} hour(s), {} minute(s), {} second(s)".format(hours, minutes, seconds))
    if (signal == 2) and (next_pass - curr_time > 10800):
        signal = 0
    print("Landmarks the station is visible from: ", g.country)
    print("See location: ","http://www.google.com/maps/place/{},{}".format(lat, long))
    lastknown = (lat,long)
    return (lastknown,signal)
def callDistance(lastknown, currentknown):
    print("ISS has traveled approximately ", geodesic(lastknown, currentknown).kilometers, "kilometers in 10 seconds.")
    return currentknown
def calcDistance(firstknown,currentknown):
    print("The ISS is traveling at approximately  ", geodesic(firstknown, currentknown).miles, "miles per minuite.")
    mile_hour = (int(geodesic(firstknown, currentknown).miles) * 60)
    print("The ISS is traveling at approximately ", mile_hour, " miles per hour.\n>>>discontinuing tracking>>>")

data = (requests.get("http://api.open-notify.org/astros.json")).json();print("Data Request: ",(data['message'])),print("Total humans in orbit: ",data['number'],"\nPrinting manifest:")
for i in range(len(data['people'])):
    print(("%s is currently in space aboard the %s." % ((data['people'][i]['name']), (data['people'][i]['craft']))))
signal = 0
(lastknown,signal) = callStation(signal)
firstknown = lastknown
time.sleep(60)
while (1):
        (currentknown,signal) = callStation(signal)
        lastknown = callDistance(lastknown, currentknown)
        time.sleep(60)

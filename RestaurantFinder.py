import requests
import time
import csv

#see https://developers.google.com/maps/documentation/places/web-service/search-nearby
#see https://console.cloud.google.com/

radius = 100000 #km
type = 'food'
newark = '40.73161387439148,-74.14866312026871'
harrison = "40.73927771267584,-74.157386600653"
springfield = "40.69201684539105,-74.34814061026131"
elizabeth = "40.66405437353767,-74.20852363222934"
timesquare = "40.75798787636964,-73.98555333131311"

location = elizabeth
key='AIzaSyBweRvfYm2BU9MLYVXvNToMxUkpxYgJqQQ'
params = {'keyword': 'restaurant', 'location': location , 'radius': radius, 'type': type, 'key': key}
page_number = 0

header = ["business_name", "addres_1", "addres_1", "city", "state", "postal_code", "phone_number", "website", "status"]

def write_to_file(data):
    with open('restaurant_data.csv', 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f, delimiter = ";")

        # write the header
        writer.writerow(data)


write_to_file(header)

while True:
    r = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', params=params)
    if r.status_code == 200: 
        json = r.json()
        if 'error_message' in json:
            print(f"==> error_message: {json['error_message']}")
            break
        print(f"==> page_number: {page_number}")
        if "results" not in json or len(json['results']) == 0:
            print(f"==> without more results")
            break
        print(f"==> len: {len(json['results'])}")
        restaurant_info = dict.fromkeys(header, "")
        for restaurant in json['results']:
            time.sleep(1)
            params2={'place_id': restaurant['place_id'], 'key': key}
            r2 = requests.get('https://maps.googleapis.com/maps/api/place/details/json', params=params2)
            restaurant_details = r2.json()
            details_result = restaurant_details['result']
            restaurant_info['business_name'] = details_result['name']
            restaurant_info['website'] = details_result['website'] if 'website' in details_result else ''
            restaurant_info['status'] = details_result['business_status'] if 'business_status' in details_result else ''
            restaurant_info['phone_number'] = details_result['formatted_phone_number'] if 'formatted_phone_number' in details_result else ''
            street_number = ""
            for adr_components in details_result['address_components']:
                if 'street_number' in adr_components['types']:
                    street_number = adr_components['short_name']
                elif 'route' in adr_components['types']:
                     restaurant_info['addres_1'] = street_number + " " + adr_components['short_name']
                elif 'locality' in adr_components['types']:
                    restaurant_info['city'] = adr_components['short_name']
                elif 'administrative_area_level_1' in adr_components['types']:
                    restaurant_info['state'] = adr_components['short_name']
                elif 'postal_code' in adr_components['types']:
                    restaurant_info['postal_code'] = adr_components['short_name']
            print(f"==> restaurant name: {restaurant_info}")
            data = list(restaurant_info.values())
            write_to_file(data)
        if 'next_page_token' not in json or json['next_page_token'] == None or json['next_page_token'] == '': 
            print(f"==> without more pages")
            break
        params['pagetoken'] = json['next_page_token']
        page_number += 1
        time.sleep(3)
    else:
        print(f"==> Request error: {r.status_code}")
        break
print(f"==> DONE!")

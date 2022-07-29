import requests
import pprint
from flask import Flask, render_template, url_for, redirect
import urllib.parse
from forms import SearchBar, HomePage
import googlemaps

pp = pprint.PrettyPrinter(indent=4)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR_OWN_API_KEY'

API_KEY= 'YOUR_OWN_API_KEY'

gmaps = googlemaps.Client(key=API_KEY)

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    form=SearchBar()
    if form.validate_on_submit():
        user_input = form.user_search.data
        url = 'https://maps.googleapis.com/maps/api/geocode/json?'
        params = {
            'key': API_KEY,
            'address': user_input
        }

        response = requests.get(url, params=params).json()

        coordinates = response['results'][0]['geometry']['location']
        place_id = response['results'][0]['place_id']

        x = coordinates['lat']
        y = coordinates['lng']
        #print("Coordinates of marker: ", x, y)

        reverse_geocoding_params = {
            'key': API_KEY,
            'fields': ['geometry', 'location'],
            'latlng': "{}, {}".format(x, y)
        }

        reverse_response = requests.get(url, params=reverse_geocoding_params).json()
        latlng_to_address = reverse_response['results'][0]['formatted_address'] 

        map_url = 'https://maps.googleapis.com/maps/api/staticmap?'

        center = "{}, {}".format(x, y)
        zoom_level = 15
        size = '400x400'
        map_key = API_KEY

        marker_params = {
            'color': 'purple',
            'label': 'X',
            'lng': x,
            'lat': y
        }
        marker_string = 'color:{}|label:{}|{},{}'.format(marker_params['color'], marker_params['label'], marker_params['lng'], marker_params['lat'])

        map_params = {
            'center': center,
            'zoom': zoom_level,
            'size': size,
            'key': map_key,
            'markers': marker_string
        }

        map_params_str = urllib.parse.urlencode(map_params, safe=':+')
        #print(map_params_str)

        map_request = requests.get(map_url, params=map_params_str)
        #print('----------------------------------------')
        #print('Map request w/ marker: ', map_request.url)

        nearby_locations_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'

        nearby_locations_parameters = {
            'key': API_KEY,
            'fields': ['geometry', 'location'],
            'location': '{},{}'.format(x, y),
            'keyword': 'restroom',
            'radius': 25000
        }

        nearby_location_info = requests.get(nearby_locations_url, params=nearby_locations_parameters).json()
        nearby_location_info_list = nearby_location_info['results']

        smallest_distance = 99999999.0
        shortest_x = None
        shortest_y = None

        coordinate_list = []
        restaurant_names_list = []
        place_ids_list = []
        for restaurant_dict in nearby_location_info_list:
            restaurant_names = restaurant_dict['name']
            restaurant_geo = restaurant_dict['geometry']
            restaurant_x = restaurant_geo['location']['lat']
            restaurant_y = restaurant_geo['location']['lng']
            temp_distance = (((float(x) - float(restaurant_x)) ** 2) + ((float(y) - float(restaurant_y)) ** 2)) ** 0.5
            if temp_distance < smallest_distance:
                smallest_distance = temp_distance
                shortest_x = restaurant_x
                shortest_y = restaurant_y
            coordinate_list.append((restaurant_x, restaurant_y))
            restaurant_names_list.append(restaurant_names)
            place_ids_list.append(restaurant_dict['place_id'])

        smallest_distance_idx = coordinate_list.index((shortest_x, shortest_y))
        smallest_distance_restaurant = restaurant_names_list[smallest_distance_idx]
        smallest_distance_place_id = place_ids_list[smallest_distance_idx]

        coordinate_list.pop(smallest_distance_idx)

        restaurant_marker_str = map_request.url

        for restaurant_tuples in coordinate_list:
            temp_str = '&markers=color:red%7Clabel:W%7C{}%2C{}'.format(restaurant_tuples[0], restaurant_tuples[1])
            restaurant_marker_str = restaurant_marker_str + temp_str
        restaurant_marker_str = restaurant_marker_str + '&markers=color:yellow%7Clabel:Z%7C{}%2C{}'.format(shortest_x, shortest_y)

        #print('----------------------------------------')
        print(restaurant_marker_str)

        iframe_url = "https://https://www.google.com/maps/embed/v1/directions?origin=place_id:{}&destination=place_id:{}&key={}".format(place_id, smallest_distance_place_id, API_KEY)
        #print(iframe_url)
        return render_template('map_page.html', all_locations=restaurant_marker_str, place_id=place_id, next_id=smallest_distance_place_id, key=API_KEY)
    return render_template('search_page.html', form=form)

@app.route('/map')
def map_page():
    return render_template('map_page.html')

@app.route('/', methods=['GET', 'POST'])
def home_page():
    form=HomePage()
    if form.validate_on_submit():
        return redirect(url_for('search_page'))
    return render_template('home_page.html', form=form)

from flask import Flask, request, jsonify, render_template
import numpy as np
from geopy.geocoders import Nominatim
import requests
from python_tsp.heuristics import solve_tsp_local_search

app = Flask(__name__)
@app.route('/') # render Home page index.html
def index():
    return render_template('index2.html'),200


@app.route('/get_coordinates', methods=['POST'])
def get_coordinates():
    locations = request.json.get('locations', [])
    geolocator = Nominatim(user_agent="my_agent")
    coordinates = []
    for location in locations:
        try:
            loc = geolocator.geocode(f"{location}, Mumbai, India")
            if loc:
                coordinates.append((loc.latitude, loc.longitude))
            else:
                print(f"Couldn't find coordinates for {location}")
        except Exception as e:
            print(f"Error finding coordinates for {location}: {e}")
    return jsonify({'coordinates': coordinates})

@app.route('/get_distance_matrix', methods=['POST'])
def get_distance_matrix():
    coordinates = request.json.get('coordinates', [])
    n = len(coordinates)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            distance = get_osrm_distance(coordinates[i], coordinates[j])
            matrix[i][j] = matrix[j][i] = distance
    return jsonify({'distance_matrix': matrix.tolist()})

@app.route('/optimize_route', methods=['POST'])
def optimize_route():
    distance_matrix = np.array(request.json.get('distance_matrix', []))
    permutation, distance = solve_tsp_local_search(distance_matrix)
    return jsonify({'permutation': permutation, 'total_distance': distance})

def get_osrm_distance(coord1, coord2):
    url = f"http://router.project-osrm.org/route/v1/driving/{coord1[1]},{coord1[0]};{coord2[1]},{coord2[0]}?overview=false"
    response = requests.get(url)
    data = response.json()
    if data['code'] == 'Ok':
        distance = data['routes'][0]['distance'] / 1000  # Convert meters to kilometers
        return distance
    else:
        print(f"Error with OSRM request: {data['message']}")
        return float('inf')

if __name__ == '__main__':
    app.run(debug=True)

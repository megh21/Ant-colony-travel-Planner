import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from python_tsp.heuristics import solve_tsp_local_search
import folium

def get_locations():
    locations = []
    print("Enter locations in Mumbai (press Enter without input to finish):")
    while True:
        location = input("Enter location: ")
        if not location:
            break
        locations.append(location)
    return locations

def get_coordinates(locations):
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
    return coordinates

def create_distance_matrix(coordinates):
    n = len(coordinates)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            distance = geodesic(coordinates[i], coordinates[j]).kilometers
            matrix[i][j] = matrix[j][i] = distance
    return matrix

def optimize_route(distance_matrix):
    permutation, distance = solve_tsp_local_search(distance_matrix)
    return permutation, distance

def visualize_route(coordinates, permutation, locations):
    center_lat = sum(coord[0] for coord in coordinates) / len(coordinates)
    center_lon = sum(coord[1] for coord in coordinates) / len(coordinates)
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # Add markers and route line
    route_coords = [coordinates[i] for i in permutation] + [coordinates[permutation[0]]]
    for i, coord in enumerate(route_coords[:-1]):
        folium.Marker(
            coord,
            popup=f"{i+1}. {locations[permutation[i]]}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)

    folium.PolyLine(route_coords, color="blue", weight=2, opacity=0.8).add_to(m)

    m.save("mumbai_optimized_route.html")
    print("Map saved as 'mumbai_optimized_route.html'")

def main():
    locations = get_locations()
    if len(locations) < 2:
        print("Please enter at least two locations.")
        return

    print("Fetching coordinates...")
    coordinates = get_coordinates(locations)
    if len(coordinates) < 2:
        print("Couldn't find enough valid coordinates.")
        return

    print("Calculating distances...")
    distance_matrix = create_distance_matrix(coordinates)

    print("Optimizing route...")
    permutation, total_distance = optimize_route(distance_matrix)

    print("\nOptimized Route:")
    for i in permutation:
        print(f"{locations[i]}")
    print(f"\nTotal distance: {total_distance:.2f} km")

    print("Generating map...")
    visualize_route(coordinates, permutation, locations)

if __name__ == "__main__":
    main()
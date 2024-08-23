const map = L.map('map').setView([19.076, 72.8777], 12); // Center on Mumbai

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

async function calculateRoute() {
    const locationsText = document.getElementById('locations').value;
    const locations = locationsText.split('\n').filter(loc => loc.trim() !== '');

    const response = await fetch('/get_coordinates', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ locations })
    });
    const { coordinates } = await response.json();

    const distanceMatrixResponse = await fetch('/get_distance_matrix', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ coordinates })
    });
    const { distance_matrix } = await distanceMatrixResponse.json();

    const optimizeRouteResponse = await fetch('/optimize_route', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ distance_matrix })
    });
    const { permutation, total_distance } = await optimizeRouteResponse.json();

    showRoute(coordinates, permutation);
    document.getElementById('result').innerHTML = `Total distance: ${total_distance.toFixed(2)} km`;
}

function showRoute(coordinates, permutation) {
    const routeCoordinates = [];

    for (let i = 0; i < permutation.length; i++) {
        const start = coordinates[permutation[i]];
        const end = coordinates[permutation[(i + 1) % permutation.length]];
        fetch(`http://router.project-osrm.org/route/v1/driving/${start[1]},${start[0]};${end[1]},${end[0]}?overview=full&geometries=geojson`)
            .then(response => response.json())
            .then(data => {
                if (data.code === 'Ok') {
                    const route = data.routes[0].geometry.coordinates;
                    route.forEach(coord => routeCoordinates.push([coord[1], coord[0]]));
                    if (i === permutation.length - 1) {
                        L.polyline(routeCoordinates, { color: 'blue' }).addTo(map);
                        map.fitBounds(L.polyline(routeCoordinates).getBounds());
                    }
                }
            });
    }
}

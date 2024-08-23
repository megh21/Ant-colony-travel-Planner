let map;
let routeLayer;

function initMap() {
    map = L.map('map').setView([19.076, 72.8777], 12); // Center on Mumbai

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
}

async function calculateRoute() {
    const locationsText = document.getElementById('locations').value;
    const locations = locationsText.split('\n').filter(loc => loc.trim() !== '');

    if (locations.length < 2) {
        showAlert('Please enter at least two locations.', 'danger');
        return;
    }

    showAlert('Calculating route...', 'info');

    try {
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
        document.getElementById('result').innerHTML = `
            <h5>Route Summary</h5>
            <p>Total distance: ${total_distance.toFixed(2)} km</p>
            <ol>
                ${permutation.map(i => `<li>${locations[i]}</li>`).join('')}
            </ol>
        `;
        showAlert('Route calculated successfully!', 'success');
    } catch (error) {
        console.error('Error:', error);
        showAlert('An error occurred while calculating the route.', 'danger');
    }
}

function showRoute(coordinates, permutation) {
    if (routeLayer) {
        map.removeLayer(routeLayer);
    }

    const routeCoordinates = [];
    const markers = [];

    for (let i = 0; i < permutation.length; i++) {
        const start = coordinates[permutation[i]];
        const end = coordinates[permutation[(i + 1) % permutation.length]];
        
        markers.push(L.marker([start[0], start[1]]).addTo(map)
            .bindPopup(`Stop ${i + 1}`));

        fetch(`http://router.project-osrm.org/route/v1/driving/${start[1]},${start[0]};${end[1]},${end[0]}?overview=full&geometries=geojson`)
            .then(response => response.json())
            .then(data => {
                if (data.code === 'Ok') {
                    const route = data.routes[0].geometry.coordinates;
                    route.forEach(coord => routeCoordinates.push([coord[1], coord[0]]));
                    if (i === permutation.length - 1) {
                        routeLayer = L.polyline(routeCoordinates, { color: 'blue', weight: 4 }).addTo(map);
                        map.fitBounds(routeLayer.getBounds());
                    }
                }
            });
    }
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.querySelector('.card-body').prepend(alertDiv);
}

// Initialize map when the page loads
document.addEventListener('DOMContentLoaded', initMap);
document.addEventListener('DOMContentLoaded', function() {
    const mapContainer = document.getElementById('mapContainer');
    const url = mapContainer ? mapContainer.getAttribute('data-url') : null;

    if (!mapContainer || !url) {
        console.error("Required elements are missing from the DOM.");
        return;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {

            let defaultLat = 0;
            let defaultLng = 0;

            if (data.city) {
                defaultLat = parseFloat(data.city.latitude);
                defaultLng = parseFloat(data.city.longitude);
            }

            const map = L.map('map').setView([defaultLat, defaultLng], 15);

            L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}{r}.jpg?api_key=804a57a3-dbf8-4d82-a63f-b6cac9e41dc2', {
                maxZoom: 17,
            }).addTo(map);

            const markers = {};
            const storedNodeData = loadNodeDataFromLocalStorage();

            if (data.parcelles && data.parcelles.length > 0) {
                const bounds = [];
                data.parcelles.forEach(parcelle => {
                    const polygon = L.polygon(parcelle.coordinates, {
                        color: 'blue',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.5
                    });
                    polygon.addTo(map);
                    bounds.push(...parcelle.coordinates);

                    parcelle.nodes.forEach(node => {
                        const marker = L.marker([node.latitude, node.longitude]);
                        const nodeData = storedNodeData[node.ref] || {};
                        const popupContent = `
                            <b>Name:</b>${node.name}<br>
                            <b>Ref:</b>${node.ref}<br>
                            <b>Temperature:</b>${nodeData.temperature || 'N/A'} °C<br>
                            <b>Humidity:</b>${nodeData.humidity || 'N/A'} %<br>
                            <b>Gaz:</b>${nodeData.gaz || 'N/A'} ppm<br>
                            <b>Pressure:</b>${nodeData.pressure || 'N/A'} hPa<br>
                            <b>Detection:</b>${nodeData.detection || 'N/A'}<br>
                            <b>RSSI:</b>${nodeData.rssi || 'N/A'}
                        `;
                        marker.bindPopup(popupContent);
                        marker.addTo(map);

                        if (!markers[node.ref]) {
                            markers[node.ref] = [];
                        }
                        markers[node.ref].push(marker);
                    });
                });
                map.fitBounds(bounds);
            } else {
                console.log("No parcels found for this project.");
            }

            const socket = new WebSocket("ws://127.0.0.1:8000/ws/mqtt/");

            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.message === 'MQTT data received') {
                    const nodeData = data.data;
                    const nodeMarkers = markers[nodeData.device_id];
                    if (nodeMarkers) {
                        nodeMarkers.forEach(marker => {
                            const updatedContent = `
                                <b>Ref:</b>${nodeData.device_id}<br>
                                <b>Temperature:</b>${nodeData.temperature} °C<br>
                                <b>Humidity:</b>${nodeData.humidity} %<br>
                                <b>Gaz:</b>${nodeData.gaz} ppm<br>
                                <b>Pressure:</b>${nodeData.pressure} hPa<br>
                                <b>Detection:</b>${nodeData.detection}<br>
                                <b>RSSI:</b>${nodeData.rssi}
                            `;
                            marker.setPopupContent(updatedContent);
                        });
                        saveNodeDataToLocalStorage(nodeData.device_id, nodeData);
                    }
                }
            };

            socket.onopen = function(event) {
                console.log("WebSocket connection established");
            };

            socket.onclose = function(event) {
                console.log("WebSocket connection closed");
            };

            socket.onerror = function(error) {
                console.error("WebSocket error: ", error);
            };

        })
        .catch(error => console.error('Error fetching parcels:', error));

    function saveNodeDataToLocalStorage(ref, data) {
        const nodeDataCache = loadNodeDataFromLocalStorage();
        nodeDataCache[ref] = data;
        localStorage.setItem('nodeDataCache', JSON.stringify(nodeDataCache));
    }

    function loadNodeDataFromLocalStorage() {
        const nodeDataCache = localStorage.getItem('nodeDataCache');
        return nodeDataCache ? JSON.parse(nodeDataCache) : {};
    }
});

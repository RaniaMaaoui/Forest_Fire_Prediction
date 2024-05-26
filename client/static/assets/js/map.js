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
                        const nodeData = storedNodeData[node.ref] || node.last_data || {};
                        const popupContent = `
                            <div class="node-popup">
                                <div class="node-label">Node</div><br>
                                <b>Name:</b> ${node.name}<br>
                                <b>Ref:</b> ${node.ref}<br>
                                <b>RSSI:</b> ${nodeData.rssi || 'N/A'}<br>
                                <b>FWI:</b> ${nodeData.fwi || 'N/A'}<br>
                                <b>Prediction result:</b> ${nodeData.prediction_result || 'N/A'}<br><br>
                                <b>Temperature:</b> ${nodeData.temperature || 'N/A'} °C<br>
                                <b>Humidity:</b> ${nodeData.humidity || 'N/A'} %<br>
                                <b>Pressure:</b> ${nodeData.pressure || 'N/A'} hPa<br>
                                <b>Gaz:</b> ${nodeData.gaz || 'N/A'} ppm<br>
                                <b>Wind speed:</b> ${nodeData.wind_speed || 'N/A'} km/h<br>
                                <b>Rain volume:</b> ${nodeData.rain_volume || 'N/A'} mm
                            </div>
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
                                <div class="node-popup">
                                    <div class="node-label">Node</div><br>
                                    <b>Ref:</b> ${nodeData.device_id}<br>
                                    <b>RSSI:</b> ${nodeData.rssi || 'N/A'}<br>
                                    <b>FWI:</b> ${nodeData.fwi || 'N/A'}<br>
                                    <b>Prediction result:</b> ${nodeData.prediction_result || 'N/A'}<br><br>
                                    <b>Temperature:</b> ${nodeData.temperature || 'N/A'} °C<br>
                                    <b>Humidity:</b> ${nodeData.humidity || 'N/A'} %<br>
                                    <b>Pressure:</b> ${nodeData.pressure || 'N/A'} hPa<br>
                                    <b>Gaz:</b> ${nodeData.gaz || 'N/A'} ppm<br>
                                    <b>Wind speed:</b> ${nodeData.wind_speed || 'N/A'} km/h<br>
                                    <b>Rain volume:</b> ${nodeData.rain_volume || 'N/A'} mm
                                </div>
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

            document.querySelectorAll('.locate-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const lat = parseFloat(this.getAttribute('data-lat'));
                    const lng = parseFloat(this.getAttribute('data-lng'));
                    const name = this.getAttribute('data-name');
                    const ref = this.getAttribute('data-ref');
                    const nodeData = storedNodeData[ref] || {};
                    const popupContent = `
                        <div class="node-popup">
                            <div class="node-label">Node</div><br>
                            <b>Name:</b> ${name}<br>
                            <b>Ref:</b> ${ref}<br>
                            <b>RSSI:</b> ${nodeData.rssi || 'N/A'}<br>
                            <b>FWI:</b> ${nodeData.fwi || 'N/A'}<br>
                            <b>Prediction result:</b> ${nodeData.prediction_result || 'N/A'}<br><br>
                            <b>Temperature:</b> ${nodeData.temperature || 'N/A'} °C<br>
                            <b>Humidity:</b> ${nodeData.humidity || 'N/A'} %<br>
                            <b>Pressure:</b> ${nodeData.pressure || 'N/A'} hPa<br>
                            <b>Gaz:</b> ${nodeData.gaz || 'N/A'} ppm<br>
                            <b>Wind speed:</b> ${nodeData.wind_speed || 'N/A'} km/h<br>
                            <b>Rain volume:</b> ${nodeData.rain_volume || 'N/A'} mm
                        </div>
                    `;
                    const tempMarker = L.marker([lat, lng]).addTo(map).bindPopup(popupContent).openPopup();
                    map.setView([lat, lng], 18);  // Ajuster le niveau de zoom
                    setTimeout(() => {
                        const popup = tempMarker.getPopup().getElement();
                        popup.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 200);  // Délai pour s'assurer que le popup est bien ouvert
                });
            });

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
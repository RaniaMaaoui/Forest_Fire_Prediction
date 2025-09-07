document.addEventListener('DOMContentLoaded', function() {
    const mapContainer = document.getElementById('mapContainer');
    const url = mapContainer ? mapContainer.getAttribute('data-url') : null;

    // --- Fonctions FWI prédits avec échelle EFFIS ---
    function getColorFromPrediction(fwi_predit) {
        if (fwi_predit < 11.2) return 'green';        // Faible
        else if (fwi_predit < 21.3) return 'yellow'; // Modéré
        else if (fwi_predit < 38.0) return 'orange'; // Élevé
        else if (fwi_predit < 50.0) return 'red';    // Très élevé
        else return 'purple';                         // Extrême
    }

    function getPredictionMessageFromPrediction(fwi_predit) {
        if (fwi_predit < 11.2) return 'Low risk';
        else if (fwi_predit < 21.3) return 'Moderate risk';
        else if (fwi_predit < 38.0) return 'High risk';
        else if (fwi_predit < 50.0) return 'Very high risk';
        else return 'Extreme risk';
    }

    // --- Fonctions de notification ---
    function showNotification(data) {
        const notification = createNotificationElement(data);
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.remove('show');
            notification.addEventListener('transitionend', () => notification.remove());
        }, 15000); // disparaît après 15 secondes
    }

    function createNotificationElement(data) {
        const container = document.createElement('div');
        container.className = 'notification-container show';

        const header = document.createElement('div');
        header.className = 'notification-header';

        const title = document.createElement('div');
        title.className = 'notification-title';
        title.innerHTML = `<img src="/static/assets/images/icons/danger.png" style="width:24px; height:24px; margin-right:10px;"> Fire Alert Notification!`;

        const closeBtn = document.createElement('span');
        closeBtn.className = 'close';
        closeBtn.innerHTML = '&times;';
        closeBtn.onclick = function() {
            container.classList.remove('show');
            container.addEventListener('transitionend', () => container.remove());
        };

        const body = document.createElement('div');
        body.className = 'notification-body';
        body.innerHTML = `
            <p>Node ID: <strong>${data.device_id}</strong> detected a potential fire!</p>
            <p><b>FWI prédit:</b> ${data.fwi_predit || 'N/A'}</p>
            <p><b>Prediction:</b> 
                <span style="color:${getColorFromPrediction(data.fwi_predit)}; font-weight:bold;">
                    ${getPredictionMessageFromPrediction(data.fwi_predit)}
                </span>
            </p>
            <p><b>Temperature:</b> ${data.temperature || 'N/A'} °C | <b>Humidity:</b> ${data.humidity || 'N/A'} %</p>
        `;

        header.appendChild(title);
        header.appendChild(closeBtn);
        container.appendChild(header);
        container.appendChild(body);

        return container;
    }

    if (!mapContainer || !url) {
        console.error("Required elements are missing from the DOM.");
        return;
    }

    // --- Initialisation map ---
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

            L.tileLayer('http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                maxZoom: 17,
            }).addTo(map);

            const markers = {};
            const polygons = {};
            const storedNodeData = loadNodeDataFromLocalStorage();

            // --- Création initiale des parcelles et marqueurs ---
            if (data.parcelles && data.parcelles.length > 0) {
                const bounds = [];

                data.parcelles.forEach(parcelle => {
                    let maxFwiPred = 0;
                    parcelle.nodes.forEach(node => {
                        const nodeData = storedNodeData[node.ref] || node.last_data || {};
                        const fwi_predit = nodeData.fwi_predit || 0;
                        if (fwi_predit > maxFwiPred) maxFwiPred = fwi_predit;
                    });

                    const polygon = L.polygon(parcelle.coordinates, {
                        color: getColorFromPrediction(maxFwiPred),
                        weight: 3.5,
                        opacity: 1,
                        fillOpacity: 0.1,
                        fillColor: getColorFromPrediction(maxFwiPred)
                    }).addTo(map);

                    polygons[parcelle.id] = polygon;
                    bounds.push(...parcelle.coordinates);

                    parcelle.nodes.forEach(node => {
                        const marker = L.marker([node.latitude, node.longitude]);
                        const nodeData = storedNodeData[node.ref] || node.last_data || {};
                        const popupContent = generatePopupContent(node, nodeData);
                        marker.bindPopup(popupContent).addTo(map);

                        if (!markers[node.ref]) markers[node.ref] = [];
                        markers[node.ref].push(marker);
                    });
                });

                map.fitBounds(bounds);
            }

            // --- WebSocket temps réel ---
            const socket = new WebSocket("ws://51.68.81.225:8000/ws/data/");

            socket.onmessage = function(event) {
                const wsData = JSON.parse(event.data);
                if (wsData.message === 'MQTT data received') {
                    const nodeData = wsData.data;

                    // Mise à jour cache
                    saveNodeDataToLocalStorage(nodeData.device_id, nodeData);

                    // Mise à jour marqueurs
                    const nodeMarkers = markers[nodeData.device_id];
                    if (nodeMarkers) {
                        nodeMarkers.forEach(marker => {
                            const updatedContent = generatePopupContent({ref: nodeData.device_id, name: nodeData.device_id}, nodeData);
                            marker.setPopupContent(updatedContent);
                        });
                    }

                    // Mise à jour parcelle
                    const parcelle = data.parcelles.find(p =>
                        p.nodes.some(node => node.ref === nodeData.device_id)
                    );

                    if (parcelle) {
                        let maxFwiPred = 0;
                        parcelle.nodes.forEach(node => {
                            const nData = loadNodeDataFromLocalStorage()[node.ref] || node.last_data || {};
                            if ((nData.fwi_predit || 0) > maxFwiPred) maxFwiPred = nData.fwi_predit;
                        });

                        const color = getColorFromPrediction(maxFwiPred);
                        polygons[parcelle.id].setStyle({ color, fillColor: color });
                    }

                    // Afficher notification si FWI élevé
                    if (nodeData.fwi_predit >= 38) {  
                        showNotification(nodeData);
                    }
                }
            };

            socket.onopen = () => console.log("WebSocket connection established");
            socket.onclose = () => console.log("WebSocket connection closed");
            socket.onerror = (error) => console.error("WebSocket error: ", error);
        })
        .catch(error => console.error('Error fetching parcels:', error));

    // --- LocalStorage ---
    function saveNodeDataToLocalStorage(ref, data) {
        const nodeDataCache = loadNodeDataFromLocalStorage();
        nodeDataCache[ref] = data;
        localStorage.setItem('nodeDataCache', JSON.stringify(nodeDataCache));
    }

    function loadNodeDataFromLocalStorage() {
        const nodeDataCache = localStorage.getItem('nodeDataCache');
        return nodeDataCache ? JSON.parse(nodeDataCache) : {};
    }

    // --- Génération du contenu popup ---
    function generatePopupContent(node, nodeData) {
        return `
            <div class="node-popup">
                <div class="node-label" style="background-color: ${getColorFromPrediction(nodeData.fwi_predit || 0)};">Node</div><br>
                <b>Name:</b> ${node.name}<br>
                <b>ID Parcelle:</b> ${node.ref}<br>
                <b>RSSI:</b> ${nodeData.rssi || 'N/A'}<br>
                <b>FWI:</b> ${nodeData.fwi || 'N/A'}<br>
                <b>FWI prédit:</b> ${nodeData.fwi_predit || 'N/A'}<br>
                <b>Prediction result:</b>
                <span style="color: ${getColorFromPrediction(nodeData.fwi_predit || 0)}; font-weight: bold;">
                    ${getPredictionMessageFromPrediction(nodeData.fwi_predit || 0)}
                </span><br><br>
                <b>Temperature:</b> ${nodeData.temperature || 'N/A'} °C<br>
                <b>Humidity:</b> ${nodeData.humidity || 'N/A'} %<br>
                <b>Pressure:</b> ${nodeData.pressure || 'N/A'} hPa<br>
                <b>Gaz:</b> ${nodeData.gaz || 'N/A'} ppm<br>
                <b>Wind speed:</b> ${nodeData.wind_speed ? nodeData.wind_speed.toFixed(2) : 'N/A'} km/h<br>
            </div>
        `;
    }
});

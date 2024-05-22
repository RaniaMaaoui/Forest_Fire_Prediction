document.addEventListener('DOMContentLoaded', function() {
    window.onload = function() {
        const selectedMap = document.getElementById('selected-map');
        const mapContainer = document.getElementById('mapContainer');
        const url = mapContainer ? mapContainer.getAttribute('data-url') : null;

        if (!selectedMap || !mapContainer || !url) {
            console.error("Required elements are missing from the DOM.");
            return;
        }

        const latitude = parseFloat(selectedMap.getAttribute('map-latitude'));
        const longitude = parseFloat(selectedMap.getAttribute('map-longitude'));

        let map;

        if (!isNaN(latitude) && !isNaN(longitude)) {
            localStorage.setItem('latitude', latitude);
            localStorage.setItem('longitude', longitude);
            map = L.map("map", {
                center: [latitude, longitude],
                zoom: 15,
            });
        } else {
            const storedLatitude = parseFloat(localStorage.getItem('latitude'));
            const storedLongitude = parseFloat(localStorage.getItem('longitude'));
            if (!isNaN(storedLatitude) && !isNaN(storedLongitude)) {
                map = L.map("map", {
                    center: [storedLatitude, storedLongitude],
                    zoom: 15,
                });
            } else {
                map = L.map("map", {
                    center: [0, 0],
                    zoom: 2,
                });
            }
        }

        L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}{r}.jpg?api_key=804a57a3-dbf8-4d82-a63f-b6cac9e41dc2', {}).addTo(map);

        map.on('moveend', function() {
            const mapState = {
                center: map.getCenter(),
                zoom: map.getZoom(),
            };
            localStorage.setItem('mapState', JSON.stringify(mapState));
        });

        const projectSelect = document.getElementById('id_project');
        if (projectSelect) {
            projectSelect.addEventListener('change', function() {
                const selectedOption = projectSelect.options[projectSelect.selectedIndex];
                const latitude = parseFloat(selectedOption.getAttribute('data-latitude'));
                const longitude = parseFloat(selectedOption.getAttribute('data-longitude'));

                if (!isNaN(latitude) && !isNaN(longitude)) {
                    map.setView([latitude, longitude], 15);
                }

                // Fetch and display parcels
                fetchParcellesForProject(selectedOption.value);
            });
        }

        let drawnItemsPolygon = new L.FeatureGroup();
        map.addLayer(drawnItemsPolygon);

        let drawControlPolygon = new L.Control.Draw({
            edit: {
                featureGroup: drawnItemsPolygon
            },
            draw: {
                polygon: true,
                polyline: false,
                rectangle: false,
                circle: false,
                marker: false,
                circlemarker: false
            }
        });
        map.addControl(drawControlPolygon);

        map.on(L.Draw.Event.CREATED, function(event) {
            const layer = event.layer;
            drawnItemsPolygon.addLayer(layer);
        });

        // Function to fetch and display parcels for the selected project
        function fetchParcellesForProject(projectId) {
            fetch(`/dashboard_super/get_parcelles_for_project/?project_id=${projectId}`)
                .then(response => response.json())
                .then(data => {
                    drawnItemsPolygon.clearLayers();
                    data.parcelles.forEach(parcelle => {
                        const polygon = L.polygon(parcelle.coordinates);
                        polygon.feature = { properties: { id: parcelle.id } };  // Attach the id to the feature properties
                        drawnItemsPolygon.addLayer(polygon);
                    });
                })
                .catch(error => console.error('Error:', error));
        }

        const nextButtonPolygon = document.getElementById('nextButtonPolygon');
        if (nextButtonPolygon) {
            nextButtonPolygon.addEventListener('click', function() {
                const nameInput = document.getElementById('id_name_polygon');
                if (!nameInput) {
                    console.error('Name input is missing.');
                    return;
                }

                const nameValue = nameInput.value;
                const projectId = projectSelect ? projectSelect.options[projectSelect.selectedIndex].value : null;

                const layers = drawnItemsPolygon.getLayers();
                if (layers.length === 0) {
                    alert('Please draw at least one polygon on the map.');
                    return;
                }

                const layer = layers[layers.length - 1]; // Save the last drawn polygon
                const coordinates = layer.getLatLngs()[0].map(latlng => [latlng.lat, latlng.lng]);
                if (coordinates.length > 0 && (coordinates[0][0] !== coordinates[coordinates.length - 1][0] || coordinates[0][1] !== coordinates[coordinates.length - 1][1])) {
                    coordinates.push(coordinates[0]); // Close the polygon
                }

                // Send the data via AJAX
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: `name=${encodeURIComponent(nameValue)}&coordinates=${JSON.stringify(coordinates)}&project=${projectId}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        // Hide the first modal
                        const projectMapModal = bootstrap.Modal.getInstance(document.getElementById('projectMapModal'));
                        projectMapModal.hide();

                        // Show the display parcels modal
                        const displayParcelsModal = new bootstrap.Modal(document.getElementById('displayParcelsModal'), {
                            backdrop: 'static',
                            keyboard: false
                        });
                        displayParcelsModal.show();

                        // Update the hidden field with the new parcel ID
                        const lastParcelle = data.parcels[data.parcels.length - 1];
                        if (lastParcelle) {
                            document.getElementById('id_parcelle').value = lastParcelle.id;
                        } else {
                            console.error('No parcels returned from the server.');
                        }

                        // Optionally, load parcels on the display map
                        loadParcelsOnDisplayMap(data.parcels);
                    } else if (data.error) {
                        // Show error messages
                        if (data.error.name) {
                            // Specific handling for name field error
                            alert(`Name: ${data.error.name[0].message}`);
                        } else {
                            let errorMessage = '';
                            for (const [field, errors] of Object.entries(data.error)) {
                                errors.forEach(error => {
                                    errorMessage += `${field}: ${error.message}\n`;
                                });
                            }
                            alert(errorMessage);
                        }
                    }
                })
                .catch(error => console.error('Error:', error));
            });
        }

        // Load parcels on the display map
        function loadParcelsOnDisplayMap(parcels) {
            const displayMap = L.map("displayMap", {
                center: map.getCenter(),
                zoom: map.getZoom(),
            });

            L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}{r}.jpg?api_key=804a57a3-dbf8-4d82-a63f-b6cac9e41dc2', {}).addTo(displayMap);

            parcels.forEach(parcelle => {
                const polygon = L.polygon(parcelle.coordinates);
                polygon.feature = { properties: { id: parcelle.id } };  // Attach the id to the feature properties
                polygon.addTo(displayMap);
            });

            let drawnItemsMarker = new L.FeatureGroup();
            displayMap.addLayer(drawnItemsMarker);

            let drawControlMarker = new L.Control.Draw({
                edit: {
                    featureGroup: drawnItemsMarker
                },
                draw: {
                    polygon: false,
                    polyline: false,
                    rectangle: false,
                    circle: false,
                    marker: true,
                    circlemarker: false
                }
            });
            displayMap.addControl(drawControlMarker);

            displayMap.on(L.Draw.Event.CREATED, function(event) {
                const layer = event.layer;
                const latlng = layer.getLatLng();
                if (isPointInsideAnyParcelle(latlng)) {
                    drawnItemsMarker.addLayer(layer);
                    updatePositionFields(latlng);
                } else {
                    alert('The marker must be placed inside a parcel.');
                }
            });

            function isPointInsideAnyParcelle(latlng) {
                let isInside = false;
                drawnItemsPolygon.getLayers().forEach(function(polygonLayer) {
                    if (polygonLayer.getBounds().contains(latlng)) {
                        isInside = true;
                    }
                });
                return isInside;
            }

            function updatePositionFields(latlng) {
                const positionField = document.getElementById('nodePosition');
                const latitudeField = document.getElementById('id_latitude');
                const longitudeField = document.getElementById('id_longitude');
                const parcelleField = document.getElementById('id_parcelle');
                
                if (positionField) {
                    positionField.value = `POINT(${latlng.lng.toFixed(6)} ${latlng.lat.toFixed(6)})`;
                } else {
                    console.error('Position field is missing.');
                }
                if (latitudeField) {
                    latitudeField.value = latlng.lat.toFixed(6);
                } else {
                    console.error('Latitude field is missing.');
                }
                if (longitudeField) {
                    longitudeField.value = latlng.lng.toFixed(6);
                } else {
                    console.error('Longitude field is missing.');
                }
                if (parcelleField) {
                    let parcelleValue = '';
                    drawnItemsPolygon.getLayers().forEach(function(polygonLayer) {
                        if (polygonLayer.getBounds().contains(latlng)) {
                            if (polygonLayer.feature && polygonLayer.feature.properties) {
                                parcelleValue = polygonLayer.feature.properties.id;
                            } else {
                                console.warn('Feature or properties missing for polygonLayer');
                            }
                        }
                    });
                    parcelleField.value = parcelleValue;
                    console.log('Assigned Parcelle Value:', parcelleValue); // Debug: Log the assigned parcelle value
                }
                console.log(`Updated Position: ${positionField.value}, Latitude: ${latitudeField.value}, Longitude: ${longitudeField.value}, Parcelle: ${parcelleField.value}`);  // Debug: Afficher les valeurs mises à jour
            }

            const nextButtonMarker = document.getElementById('nextButtonMarker');
            if (nextButtonMarker) {
                nextButtonMarker.addEventListener('click', function() {
                    const nameInput = document.getElementById('nodeName');
                    const nodeReference = document.getElementById('nodeReference');
                    const nodeSensors = document.getElementById('nodeSensors');
                    const nodeOrder = document.getElementById('nodeOrder');
                    const parcelleInput = document.getElementById('id_parcelle');

                    if (!nameInput || !nodeReference || !nodeSensors || !nodeOrder || !parcelleInput) {
                        console.error('Required input fields are missing.');
                        return;
                    }

                    const nameValue = nameInput.value;
                    const nodeReferenceValue = nodeReference.value;
                    const nodeSensorsValue = nodeSensors.value;
                    const nodeOrderValue = nodeOrder.value;

                    const layers = drawnItemsMarker.getLayers();
                    if (layers.length === 0) {
                        alert('Please draw at least one marker on the map.');
                        return;
                    }

                    const layer = layers[layers.length - 1];
                    const coordinates = layer.getLatLng();

                    let isInsideAnyParcelle = false;
                    drawnItemsPolygon.getLayers().forEach(function(polygonLayer) {
                        if (polygonLayer.getBounds().contains(coordinates)) {
                            isInsideAnyParcelle = true;
                            if (polygonLayer.feature && polygonLayer.feature.properties) {
                                parcelleInput.value = polygonLayer.feature.properties.id;
                            }
                        }
                    });

                    if (!isInsideAnyParcelle) {
                        alert('Marker must be placed inside a parcel.');
                        return;
                    }

                    // Vérifiez que le champ parcelle n'est pas vide
                    if (!parcelleInput.value) {
                        alert('Parcelle must not be empty.');
                        return;
                    }

                    // Update hidden fields with the correct values
                    document.getElementById('nodePosition').value = `POINT(${coordinates.lng.toFixed(6)} ${coordinates.lat.toFixed(6)})`;
                    document.getElementById('id_latitude').value = coordinates.lat.toFixed(6);
                    document.getElementById('id_longitude').value = coordinates.lng.toFixed(6);

                    console.log(`Submitting Node: Name=${nameValue}, Reference=${nodeReferenceValue}, Sensors=${nodeSensorsValue}, Order=${nodeOrderValue}, Position=${document.getElementById('nodePosition').value}, Latitude=${document.getElementById('id_latitude').value}, Longitude=${document.getElementById('id_longitude').value}, Parcelle=${parcelleInput.value}`);  // Debug: Afficher les valeurs soumises

                    fetch('/dashboard_super/add_node/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        },
                        body: `name=${encodeURIComponent(nameValue)}&reference=${encodeURIComponent(nodeReferenceValue)}&sensors=${encodeURIComponent(nodeSensorsValue)}&node_range=${encodeURIComponent(nodeOrderValue)}&position=POINT(${coordinates.lng.toFixed(6)} ${coordinates.lat.toFixed(6)})&latitude=${coordinates.lat.toFixed(6)}&longitude=${coordinates.lng.toFixed(6)}&parcelle=${encodeURIComponent(parcelleInput.value)}`
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.message) {
                            window.location.href = '/dashboard_super/project_list/';
                        } else if (data.error) {
                            let errorMessage = '';
                            for (const [field, errors] of Object.entries(data.error)) {
                                errors.forEach(error => {
                                    errorMessage += `${field}: ${error.message}\n`;
                                });
                            }
                            alert(errorMessage);
                        }
                    })
                    .catch(error => console.error('Error:', error));
                });
            }
        }

        const closeDisplayParcelsModalButton = document.getElementById('closeDisplayParcelsModal');
        if (closeDisplayParcelsModalButton) {
            closeDisplayParcelsModalButton.addEventListener('click', function() {
                const listUrl = document.body.getAttribute('data-list-url');
                window.location.href = listUrl;
            });
        }

        const backDisplayButton = document.getElementById('backDisplayButton');
        if (backDisplayButton) {
            backDisplayButton.addEventListener('click', function() {
                var displayParcelsModal = bootstrap.Modal.getInstance(document.getElementById('displayParcelsModal'));
                displayParcelsModal.hide();

                var projectMapModal = new bootstrap.Modal(document.getElementById('projectMapModal'), {
                    backdrop: 'static',
                    keyboard: false
                });
                projectMapModal.show();
            });
        }

        if (projectSelect) {
            const initialProjectId = projectSelect.options[projectSelect.selectedIndex].value;
            if (initialProjectId) {
                fetchParcellesForProject(initialProjectId);
            }
        }
    };
});

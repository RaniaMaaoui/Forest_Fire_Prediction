document.addEventListener('DOMContentLoaded', function() {
    window.onload = function() {
        var storedMapState = JSON.parse(localStorage.getItem('mapState'));
        var map;
        const selectedMap = document.getElementById('selected-map');
        const latitude = parseFloat(selectedMap.getAttribute('map-latitude'));
        const longitude = parseFloat(selectedMap.getAttribute('map-longitude'));

        // Prioritize the attributes from the selectedMap over localStorage
        if (latitude && longitude) {
            localStorage.setItem('latitude', latitude);
            localStorage.setItem('longitude', longitude);
        } else {
            latitude = parseFloat(localStorage.getItem('latitude'));
            longitude = parseFloat(localStorage.getItem('longitude'));
        }

        if (storedMapState) {
            map = L.map("map", {
                center: storedMapState.center,
                zoom: storedMapState.zoom,
            });
        } else if (latitude && longitude) {
            map = L.map("map", {
                center: [latitude, longitude],
                zoom: 15,
            });
        } else {
            // Default center if no coordinates available
            map = L.map("map", {
                center: [0, 0],
                zoom: 2,
            });
        }

        L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}{r}.jpg?api_key=804a57a3-dbf8-4d82-a63f-b6cac9e41dc2', {}).addTo(map);

        map.on('moveend', function() {
            var mapState = {
                center: map.getCenter(),
                zoom: map.getZoom(),
            };
            localStorage.setItem('mapState', JSON.stringify(mapState));
        });
    };
});

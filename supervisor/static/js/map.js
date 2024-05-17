document.addEventListener('DOMContentLoaded', function() {
    window.onload = function() {
        const selectedMap = document.getElementById('selected-map');
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
    };
});

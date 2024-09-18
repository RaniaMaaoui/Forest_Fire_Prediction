document.addEventListener('DOMContentLoaded', function() {
    const mapWrapper = document.getElementById('mapWrapper');
    if (!mapWrapper) {
        console.error('Map wrapper not found');
        return;
    }

    const latitude = 37.207400;
    const longitude = 10.116500;
    const zoomLevel = 12;  
    let map;

    window.onload = function() {
        const initializeMap = (lat, lng, zoom) => {
            if (map !== undefined) {
                map.remove();
            }

            map = L.map('map', {
                center: [lat, lng],
                zoom: zoom,
            });

            L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}{r}.jpg?api_key=a1289e53-2a2d-4848-a6ca-53538acae488', {}).addTo(map);

            map.on('moveend', function() {
                const mapState = {
                    center: map.getCenter(),
                    zoom: map.getZoom(),
                };
                localStorage.setItem('mapState', JSON.stringify(mapState));
            });
        };

        initializeMap(latitude, longitude, zoomLevel);
    };
});

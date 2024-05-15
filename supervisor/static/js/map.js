document.addEventListener('DOMContentLoaded', function() {
    // Attendre que la page soit complètement chargée avant d'initialiser la carte
    window.onload = function() {
        // Récupérer les coordonnées de la carte depuis le stockage local
        var storedMapState = JSON.parse(localStorage.getItem('mapState'));
        var map;

        // Si des coordonnées sont disponibles, restaurer la carte avec ces coordonnées
        if (storedMapState) {
            map = L.map("map", {
                center: storedMapState.center,
                zoom: storedMapState.zoom,
            });
        } else {
            // Si aucune coordonnée n'est disponible, créer une nouvelle carte avec des coordonnées par défaut
            map = L.map("map", {
                center: [51.505, -0.09],
                zoom: 20,
            });
        }

        // Ajouter des tuiles de carte à la carte
        L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}{r}.jpg?api_key=804a57a3-dbf8-4d82-a63f-b6cac9e41dc2', {}).addTo(map);

        // Écouter l'événement de déplacement de la carte et enregistrer les coordonnées dans le stockage local
        map.on('moveend', function() {
            var mapState = {
                center: map.getCenter(),
                zoom: map.getZoom(),
            };
            localStorage.setItem('mapState', JSON.stringify(mapState));
        });

        
    };
});

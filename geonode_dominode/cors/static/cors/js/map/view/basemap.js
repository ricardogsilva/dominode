define([
    'backbone', 'leaflet'], function (Backbone, L) {
    return Backbone.View.extend({
        basemaps: {
            "OSM": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            })
        },
        initialize: function (mapView) {
            this.basemaps[Object.keys(this.basemaps)[0]].addTo(mapView.map);
        },
    });
});
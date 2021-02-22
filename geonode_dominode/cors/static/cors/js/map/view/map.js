define([
    'backbone',
    'jquery',
    'view/basemap',
    'view/layer',
], function (
    Backbone, $, Basemap, Layer) {
    return Backbone.View.extend({
        initBounds: [[15.5257612, -61.833855], [15.3169172, -60.90965]],
        initialize: function () {
            // listeners
            this.listenTo(dispatcher, 'map:pan', this.panTo);

            // constructor
            this.map = L.map('map').fitBounds(this.initBounds);
            new Basemap(this);
            this.layer = new Layer();
        },
        /**
         * Pan map to lat lng
         * @param lat
         * @param lng
         * @param zoom
         */
        panTo: function (lat, lng, zoom) {
            if (zoom) {
                this.map.flyTo([lat, lng], zoom, {
                    duration: 0.5
                });
            } else {
                this.map.panTo(new L.LatLng(lat, lng));
            }
        }
    });
});
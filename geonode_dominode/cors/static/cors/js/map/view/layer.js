define([
    'backbone', 'leaflet'], function (Backbone, L) {
    return Backbone.View.extend({
        features: {},
        initialize: function () {
            this.data = null;
            this.layer = null;
            this.fetchData();
        },
        /** Fetch data through API
         *
         */
        fetchData: function () {
            const that = this;
            Request.get(
                '/cors/api/list', {}, null,
                /** SUCCESS **/
                function (data) {
                    that.data = data;
                    that.initLayer();
                }
            )
        },
        initLayer: function () {
            if (this.layer) {
                try {
                    map.removeLayer(this.layer)
                } catch (e) {

                }
            }
            // create layer
            this.layer = L.geoJSON(this.data, {
                onEachFeature: function (feature, layer) {
                    // bind popup
                    layer.on({
                        click: function (e) {
                            let feature = e.target.feature;
                            let ID = feature.properties.ID;
                            dispatcher.trigger('side-panel:render-open', ID, feature.properties)
                        }
                    });
                }
            });
            this.add()
        },
        /** Add layer to map **/
        add: function () {
            this.layer.addTo(map);
        },
        /** Remove layer to map **/
        remove: function () {
            this.layer.removeFrom(map);
        },
    });
});
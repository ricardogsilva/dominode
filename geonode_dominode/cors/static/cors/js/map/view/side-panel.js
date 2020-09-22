define([
    'backbone',
    'jquery',
    'jqueryUI'
], function (Backbone, $, $ui) {
    return Backbone.View.extend({
        initialize: function () {
            this.id = null;
            this.$el = $('#side-panel');
            this.$featureProperties = $('#feature-properties')
            this.listenTo(dispatcher, 'side-panel:render-open', this.renderAndOpen);

            this.$observationForm = $('#download-observation');

            // let's reposition side panel
            this.$el.css('right', `-${this.$el.outerWidth()}px`);
            this.initFormSubmit()
        },
        /** initiate form submit **/
        initFormSubmit: function () {
            let checkDetail = true
            this.$observationForm.submit(function (e) {
                if (checkDetail) {
                    e.preventDefault();
                    const $form = $(this);
                    $.ajax({
                        url: $(this).attr('action') + '/detail',
                        type: 'post',
                        dataType: 'json',
                        data: $(this).serialize(),
                        success: function (msg) {
                            checkDetail = false
                            $form.submit()
                        },
                        error: function (XMLHttpRequest, textStatus, errorThrown) {
                            alert(XMLHttpRequest.responseText);
                        }
                    })
                } else {
                    checkDetail = true
                }
            });
        },
        /** Render and open side panel  */
        renderAndOpen: function (id, properties) {
            this.id = id;
            this.$observationForm.attr('action', observationDownloadURL.replace('/0/', `/${id}/`));
            this.render(properties);
            this.open();
        },
        /** Render side panel  */
        render: function (properties) {
            let html = ''
            $.each(properties, function (key, value) {
                html += `<tr><td>${key.capitalize().replaceAll('_', ' ')}</td><td>${value}</td></tr>`
            });
            this.$featureProperties.html(html);
        },
        /** Open side panel
         */
        open: function () {
            if (!this.$el.is(":visible")) {
                this.$el.show();
                this.$el.animate({right: '0'}, 200);
            }
        },
        /** Close side panel
         */
        close: function () {
            const that = this;
            if (this.$el.is(":visible")) {
                this.$el.animate({right: `-${this.$el.outerWidth()}`}, 200, function () {
                    that.$el.hide();
                });
            }
        }
    });
});
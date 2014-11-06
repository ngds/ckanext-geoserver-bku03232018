'use strict';

ckan.module('geoserver_resource_form', function ($, _) {
  return {
    initialize: function () {
      var form
        , res
        , obj
        ;

      obj = this;

      $.proxyAll(this, /_on/);
      this.el.on('click', this._onClick);

      form = $('.primary .module-content').find('form');

      form.submit(function () {
        var data
          , injection
          ;

        res = form.find('input[name="md_resource"]').val();
        if (res) {
          res = JSON.parse(res);
        }

        data = obj.publishServices();

        res.geoserver = data;

        injection = $('<input>')
          .attr('type', 'hidden')
          .attr('name', 'md_resource')
          .val(JSON.stringify(res));
        form.append($(injection));
      })
    },
    _onClick: function () {
      var target = $(this.el);
      if (target.hasClass('active')) {
        target.removeClass('active');
        this._setPublish(false);
      }
      else {
        target.addClass('active');
        this._setPublish(true);
      }
    },
    _setPublish: function (val) {
      var publish;

      if (val) {
        publish = val;
      }
      else {
        return publish;
      }
    },
    publishServices: function () {
      var publish = this._setPublish();
      return {'publish_ogc': publish};
    }
  }
});
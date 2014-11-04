'use strict';

ckan.module('geoserver_resource_form', function ($, _) {
  return {
    initialize: function () {
      $.proxyAll(this, /_on/);
      this.el.on('click', this._onClick);

      $('#md-resource-edit').submit(function () {
        data = obj.buildSchema();
        form = $(this);
        injection = $('<input>')
          .attr('type', 'hidden')
          .attr('name', 'md_resource')
          .val(JSON.stringify(data));
        $('#md-resource-edit').append($(injection));
      })

    },
    _onClick: function () {
      var target = $(this.el);
      if (target.hasClass('active')) {
        target.removeClass('active');
      } else {
        target.addClass('active');
        this.publishServices(target);
      }
    },
    publishServices: function (e) {
      console.log(e);
      console.log($(e.form.id));
    }
  }
});
'use strict';

ckan.module('geoserver_resource_form', function ($, _) {
  return {
    initialize: function () {
      var form;

      $.proxyAll(this, /_on/);
      this.el.on('click', this._onClick);

      form = $('.primary .module-content').find('form');

      form.submit(function () {
        var data
          , injection
          ;

        data = obj.publishServices();
        injection = $('<input>')
          .attr('type', 'hidden')
          .attr('name', 'md_resource')
          .val(JSON.stringify(data));
        form.append($(injection));
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

    }
  }
});
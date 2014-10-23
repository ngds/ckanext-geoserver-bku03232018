'use strict';

ckan.module('geoserver_resource_form', function ($, _) {
  return {
    initialize: function () {
      $.proxyAll(this, /_on/);
      this.el.on('click', this._onClick);
    },
    _onClick: function () {
      var target = $(this.el);
      if (target.hasClass('active')) {
        target.removeClass('active');
      } else {
        target.addClass('active');
      }
    }
  }
});
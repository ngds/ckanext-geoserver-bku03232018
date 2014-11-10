'use strict';

ckan.module('geoserver_publish_ogc', function ($, _) {
  return {
    initialize: function () {
      var form
        , res
        , obj
        ;

      obj = this;
      obj.fieldnames = '';

      $.proxyAll(this, /_on/);
      this.el.on('click', this._onClick);
    },
    _onClick: function (e) {
      var id
        , obj
        , fields
        ;

      obj = this;
      id = e.currentTarget.id;

      obj.postSearch(id, function (res) {
        if (res.success) {
          obj.fieldnames = obj.parseResponse(res);
          obj.sandbox.client.getTemplate('geoserver_publish_ogc_form.html',
            obj.options, obj._onReceiveSnippet);
        }
        else {
          return null;
        }
      });

      return false;
    },
    _onReceiveSnippet: function (html) {
      var obj
        , latSelect
        , lngSelect
        , fields
        , option
        , i
        ;

      obj = this;
      fields = obj.fieldnames;

      $(html).modal('show');

      latSelect = $(html).find('#geoserver_lat_field');
      lngSelect = $(html).find('#geoserver_lng_field');

      for (i = 0; i < fields.length; i++) {
        option = $('<option></option>')
          .attr('value', fields[i])
          .text(fields[i])
        ;

        latSelect.append(option);
        lngSelect.append(option);
      }
    },
    postSearch: function (id, callback) {
      var path
        , type
        , dataType
        , data
        ;

      path = '/api/action/datastore_search';
      type = 'POST';
      dataType = 'JSON';
      data = JSON.stringify({'id': id});

      $.ajax({
        url: path,
        type: type,
        dataType: dataType,
        data: data,
        success: function (response) {
          callback(response);
        }
      })
    },
    parseResponse: function (res) {
      var fields
        , resFields
        , i
        ;

      fields = [];
      resFields = res.result.fields;

      for (i = 0; i < resFields.length; i++) {
        fields.push(resFields[i].id);
      }

      return fields;
    }
  }
});
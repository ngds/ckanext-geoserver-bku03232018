'use strict';

ckan.module('geoserver_publish_ogc', function ($, _) {
  return {
    initialize: function () {
      var form
        , res
        , obj
        ;

      obj = this;

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
          fields = obj.parseResponse(res);
          console.log(fields);
        }
        else {
          return null;
        }
      });

      return false;
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
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
	, selects
	, resourceInput
	, packageInput
	, ogcForm
        ;

      obj = this;
      fields = obj.fieldnames;

      //Make sure removing old modal if exists
      $('#publish_ogc_modal').remove();
      //append new modal into body
      $('body').append(html);

      selects =  $('body').find('#geoserver_lat_field, #geoserver_lng_field');
      resourceInput = $('body').find('#resource_id').val(obj.options.resource);
      packageInput = $('body').find('#package_id').val(obj.options.package);

      for (i = 0; i < fields.length; i++) {
	selects.each(function(){
	  $(this).append($('<option>', {value: fields[i]}).text(fields[i]));
	});
      }

      //show modal
      $('#publish_ogc_modal').modal('show');

      $("#publish_ogc_modal").on('shown', function() {
	ogcForm = $(this).find('form#publish-ogc-form');
	
	//bind submit event to publish OGC
	ogcForm.submit(function(e){
	    //publish ogc
	    obj.postPublishOGC($(this));

	    //prevent page from loading
	    e.preventDefault();
	    return false;
	});
      });
    },
    postPublishOGC: function(form) {
      var data
	, path
	;

	path = '/geoserver/publish-ogc';
	data = form.serializeArray();

	$.ajax({
          url: path,
          type: 'POST',
          dataType: 'JSON',
          data: data,
          success: function (result) {

		$('.modal-body .alert')
                        .html(result.message)
                        .css({'display': 'block'});

		if(result.success)
		{
		   //Success 
		    $('.modal-body .alert')
                        .addClass('alert-success');

		   //reload the page
		   location.reload();
		}
		else
		{
		    //error
		    $('.modal-body .alert')
			.addClass('alert-error');
		}
          }
      })

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

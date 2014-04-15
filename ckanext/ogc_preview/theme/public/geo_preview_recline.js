/* Copyright (c) 2014, Siemens Coporate Technology and Arizona Geological Survey */
// recline preview module
this.ckan.module('reclinepreview', function (jQuery, _) {
  return {
    options: {
      i18n: {
        errorLoadingPreview: "Could not load preview",
        errorDataProxy: "DataProxy returned an error",
        errorDataStore: "DataStore returned an error",
        previewNotAvailableForDataType: "Preview not available for data type: "
      },
      site_url: ""
    },

    initialize: function () {
      jQuery.proxyAll(this, /_on/);
      this.el.ready(this._onReady);
      // hack to make leaflet use a particular location to look for images
      L.Icon.Default.imagePath = this.options.site_url + 'vendor/leaflet/0.4.4/images';
    },

    _onReady: function() {
      this.loadPreviewDialog(preload_resource);
    },

    // **Public: Loads a data preview**
    //
    // Fetches the preview data object from the link provided and loads the
    // parsed data from the webstore displaying it in the most appropriate
    // manner.
    //
    // link - Preview button.
    //
    // Returns nothing.
    loadPreviewDialog: function (resourceData) {
      var self = this;

      function showError(msg){
        msg = msg || _('error loading preview');
        window.parent.ckan.pubsub.publish('data-viewer-error', msg);
      }

      recline.Backend.DataProxy.timeout = 10000;

      // 2 situations
      // a) something was posted to the datastore - need to check for this
      // b) csv or xls (but not datastore)
      resourceData.formatNormalized = this.normalizeFormat(resourceData.format);

      resourceData.url  = this.normalizeUrl(resourceData.url);

      if (resourceData.formatNormalized === '') {
        var tmp = resourceData.url.split('/');
        tmp = tmp[tmp.length - 1];
        tmp = tmp.split('?'); // query strings
        tmp = tmp[0];
        var ext = tmp.split('.');
        if (ext.length > 1) {
          resourceData.formatNormalized = ext[ext.length-1];
        }
      }

      var errorMsg, dataset;

      if (resourceData.protocol === "OGC:WFS") {
          resourceData.backend = 'memory';
          dataset = new recline.Model.Dataset({records:resourceData.reclineJSON});
          dataset.fetch().done(function(dataset){self.initializeDataExplorer(dataset)});
      } else if (resourceData.protocol === "OGC:WMS") {
        function initMap() {
            map = new L.Map('map');

            var baseUrl='http://{s}.maptile.maps.svc.ovi.com/maptiler/v2/maptile/newest/terrain.day/{z}/{x}/{y}/256/png8';
            var osmAttrib='Map data © OpenStreetMap contributors';
            var osm = new L.TileLayer(baseUrl, {minZoom: 1, maxZoom: 12, attribution: osmAttrib});
            var serviceUrl = resourceData.service_url.split('?')[0];
            
            var wms = new L.TileLayer.WMS(serviceUrl, {
                layers: resourceData.layer,
                format: "image/png",
                transparent: true
             });

            var bbox = resourceData.bbox;
            var bounds = L.latLngBounds([
                [bbox[1], bbox[0]],
                [bbox[3], bbox[2]]
            ]);

            map.fitBounds(bounds);
            map.addLayer(osm);
            map.addLayer(wms);
        }
        initMap();
      }
    },

    initializeDataExplorer: function (dataset) {
      var views = [
        {
          id: 'grid',
          label: 'Grid',
          view: new recline.View.SlickGrid({
            model: dataset
          })
        },
        {
          id: 'graph',
          label: 'Graph',
          view: new recline.View.Graph({
            model: dataset
          })
        },
        {
          id: 'map',
          label: 'Map',
          view: new recline.View.Map({
            model: dataset
          })
        },
        // @NGDS: added a tab for histograms
        {
            id: 'histogram',
            label: 'Histogram',
            view: new recline.View.FlotHisto({
              model: dataset
            })
          }
      ];

      var sidebarViews = [
        {
          id: 'valueFilter',
          label: 'Filters',
          view: new recline.View.ValueFilter({
            model: dataset
          })
        }
      ];

      var dataExplorer = new recline.View.MultiView({
        el: this.el,
        model: dataset,
        views: views,
        sidebarViews: sidebarViews,
        config: {
          readOnly: true
        }
      });

    },
    normalizeFormat: function (format) {
      var out = format.toLowerCase();
      out = out.split('/');
      out = out[out.length-1];
      return out;
    },
    normalizeUrl: function (url) {
      if (url.indexOf('https') === 0) {
        return 'http' + url.slice(5);
      } else {
        return url;
      }
    }
  };
});

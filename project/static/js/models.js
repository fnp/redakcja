/*globals Editor fileId SplitView PanelContainerView*/
var documentsUrl = '/api/documents/';


Editor.Model = Editor.Object.extend({
  synced: false,
  data: null
});


Editor.XMLModel = Editor.Model.extend({
  serverURL: null,
  
  init: function(serverURL) {
    this.serverURL = serverURL;
  },
  
  getData: function() {
    if (!this.data) {
      this.reload();
    }
    return this.data;
  },
  
  setData: function(data) {
    this.data = data;
    this.dataChanged();
  },
  
  load: function() {
    if (!this.get('synced')) {
      $.ajax({
        url: this.serverURL,
        dataType: 'text',
        success: this.reloadSucceeded.bind(this)
      });
    }
  },
  
  reloadSucceeded: function(data) {
    this.set('data', data);
    this.set('synced', true);
  }
});


Editor.HTMLModel = Editor.Model.extend({
  serverURL: null,
  
  init: function(serverURL) {
    this.serverURL = serverURL;
  },
  
  load: function() {
    if (!this.get('synced')) {
      $.ajax({
        url: this.serverURL,
        dataType: 'text',
        success: this.reloadSucceeded.bind(this)
      });
    }
  },
  
  reloadSucceeded: function(data) {
    this.set('data', data);
    this.set('synced', true);
  }
});


Editor.DocumentModel = Editor.Model.extend({
  data: null, // name, text_url, latest_rev, latest_shared_rev, parts_url, dc_url, size
  contentModels: {},
  
  init: function() {
    this.load();
  },
  
  load: function() {
    console.log('DocumentModel#load');
    $.ajax({
      cache: false,
      url: documentsUrl + fileId,
      dataType: 'json',
      success: this.successfulLoad.bind(this)
    });
  },
  
  successfulLoad: function(data) {
    console.log('DocumentModel#successfulLoad:', data);
    this.set('data', data);
    this.contentModels = {
      'xml': new Editor.XMLModel(data.text_url),
      'html': new Editor.HTMLModel(data.html_url)
    };
  }
});


var leftPanelView, rightPanelContainer, doc;

$(function() {
  doc = new Editor.DocumentModel();
  var splitView = new SplitView('#splitview', doc);
  leftPanelView = new PanelContainerView('#left-panel-container', doc);
  rightPanelContainer = new PanelContainerView('#right-panel-container', doc);
});

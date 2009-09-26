/*globals Editor fileId SplitView PanelContainerView*/
var documentsUrl = '/api/documents/';


Editor.Model = Editor.Object.extend({
  synced: false,
  data: null
});


Editor.XMLModel = Editor.Model.extend({
  _className: 'Editor.XMLModel',
  serverURL: null,
  
  init: function(serverURL) {
    this._super();
    this.serverURL = serverURL;
  },
  
  getData: function() {
    if (!this.data) {
      this.reload();
    }
    return this.data;
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
  _className: 'Editor.HTMLModel',
  serverURL: null,
  data: '',
  
  init: function(serverURL) {
    this._super();
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
  _className: 'Editor.DocumentModel',
  data: null, // name, text_url, latest_rev, latest_shared_rev, parts_url, dc_url, size
  contentModels: {},
  
  init: function() {
    this._super();
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
    for (var key in this.contentModels) {
      this.contentModels[key].addObserver(this, 'data', this.contentModelDataChanged.bind(this));
    }
  },
  
  contentModelDataChanged: function(property, value, contentModel) {
    console.log('data of', contentModel.description(), 'changed!');
    for (var key in this.contentModels) {
      if (this.contentModels[key].guid() != contentModel.guid()) {
        console.log(this.contentModels[key].description(), 'frozen');
        this.contentModels[key].set('synced', false);
      }
    }
  }
});


var leftPanelView, rightPanelContainer, doc;

$(function() {
  doc = new Editor.DocumentModel();
  var splitView = new SplitView('#splitview', doc);
  leftPanelView = new PanelContainerView('#left-panel-container', doc);
  rightPanelContainer = new PanelContainerView('#right-panel-container', doc);
});

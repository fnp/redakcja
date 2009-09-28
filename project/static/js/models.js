/*globals Editor fileId SplitView PanelContainerView EditorView*/
var documentsUrl = '/api/documents/';


Editor.Model = Editor.Object.extend({
  synced: false,
  data: null
});


Editor.ToolbarButtonsModel = Editor.Model.extend({
  _className: 'Editor.ToolbarButtonsModel',
  serverURL: '/api/toolbar/buttons',
  buttons: {},
  
  init: function() {
    this._super();
  },
  
  load: function() {
    if (!this.get('buttons').length) {
      $.ajax({
        url: this.serverURL,
        dataType: 'json',
        success: this.loadSucceeded.bind(this)
      });
    }
  },
  
  loadSucceeded: function(data) {
    this.set('buttons', data);
  }
});


// Stany modelu:
//
// empty -> loading -> synced -> unsynced -> loading
//                           \
//                            -> dirty -> updating -> updated -> synced
//
Editor.XMLModel = Editor.Model.extend({
  _className: 'Editor.XMLModel',
  serverURL: null,
  data: '',
  state: 'empty',
  
  init: function(serverURL) {
    this._super();
    this.set('state', 'empty');
    this.serverURL = serverURL;
    this.toolbarButtonsModel = new Editor.ToolbarButtonsModel();
    this.addObserver(this, 'data', this.dataChanged.bind(this));
  },
  
  load: function() {
    if (this.get('state') == 'empty') {
      this.set('state', 'loading');
      $.ajax({
        url: this.serverURL,
        dataType: 'text',
        success: this.loadingSucceeded.bind(this)
      });
      return true;
    }
    return false;
  },
  
  update: function(message) {
    if (this.get('state') == 'dirty') {
      this.set('state', 'updating');
      
      var payload = {
        contents: this.get('data')
      };
      if (message) {
        payload.message = message;
      }
      
      $.ajax({
        url: this.serverURL,
        type: 'put',
        dataType: 'json',
        data: payload,
        success: this.updatingSucceeded.bind(this),
        error: this.updatingFailed.bind(this)
      });
      return true;
    }
    return false;
  },
  
  updatingSucceeded: function() {
    if (this.get('state') != 'updating') {
      alert('erroneous state:', this.get('state'));
    }
    this.set('state', 'updated');
  },
  
  updatingFailed: function() {
    if (this.get('state') != 'updating') {
      alert('erroneous state:', this.get('state'));
    }
    this.set('state', 'dirty');
  },
  
  set: function(property, value) {
    if (property == 'state') {
      console.log(this.description(), ':', property, '=', value);
    }
    return this._super(property, value);
  },
  
  dataChanged: function(property, value) {
    if (this.get('state') == 'synced') {
      this.set('state', 'dirty');
    }
  },
  
  loadingSucceeded: function(data) {
    if (this.get('state') != 'loading') {
      alert('erroneous state:', this.get('state'));
    }
    this.set('data', data);
    this.set('state', 'synced');
  },
  
  dispose: function() {
    this.removeObserver(this);
    this._super();
  }
});


Editor.HTMLModel = Editor.Model.extend({
  _className: 'Editor.HTMLModel',
  serverURL: null,
  data: '',
  state: 'empty',
  
  init: function(serverURL) {
    this._super();
    this.set('state', 'empty');
    this.serverURL = serverURL;
  },
  
  load: function() {
    if (this.get('state') == 'empty') {
      this.set('state', 'loading');
      $.ajax({
        url: this.serverURL,
        dataType: 'text',
        success: this.loadingSucceeded.bind(this)
      });
    }
  },
  
  loadingSucceeded: function(data) {
    if (this.get('state') != 'loading') {
      alert('erroneous state:', this.get('state'));
    }
    this.set('data', data);
    this.set('state', 'synced');
  },
  
  set: function(property, value) {
    if (property == 'state') {
      console.log(this.description(), ':', property, '=', value);
    }
    return this._super(property, value);
  }
});


Editor.DocumentModel = Editor.Model.extend({
  _className: 'Editor.DocumentModel',
  data: null, // name, text_url, latest_rev, latest_shared_rev, parts_url, dc_url, size
  contentModels: {},
  state: 'empty',
  
  init: function() {
    this._super();
    this.set('state', 'empty');
    this.load();
  },
  
  load: function() {
    if (this.get('state') == 'empty') {
      this.set('state', 'loading');
      $.ajax({
        cache: false,
        url: documentsUrl + fileId,
        dataType: 'json',
        success: this.successfulLoad.bind(this)
      });
    }
  },
  
  successfulLoad: function(data) {
    this.set('data', data);
    this.set('state', 'synced');
    this.contentModels = {
      'xml': new Editor.XMLModel(data.text_url),
      'html': new Editor.HTMLModel(data.html_url)
    };
    for (var key in this.contentModels) {
      this.contentModels[key].addObserver(this, 'state', this.contentModelStateChanged.bind(this));
    }
  },
  
  contentModelStateChanged: function(property, value, contentModel) {
    if (value == 'dirty') {
      for (var key in this.contentModels) {
        if (this.contentModels[key].guid() != contentModel.guid()) {
          // console.log(this.contentModels[key].description(), 'frozen');
          this.contentModels[key].set('state', 'unsynced');
        }
      }
    }
  },
  
  quickSave: function(message) {
    for (var key in this.contentModels) {
      if (this.contentModels[key].get('state') == 'dirty') {
        this.contentModels[key].update(message);
        break;
      }
    }
  }
});


var leftPanelView, rightPanelContainer, doc;

$(function() {
  doc = new Editor.DocumentModel();
  var editor = new EditorView('#body-wrap', doc);
  editor.freeze();
  var splitView = new SplitView('#splitview', doc);
  leftPanelView = new PanelContainerView('#left-panel-container', doc);
  rightPanelContainer = new PanelContainerView('#right-panel-container', doc);
});

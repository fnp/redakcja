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
  
  init: function(serverURL, revision) {
    this._super();
    this.set('state', 'empty');
    this.set('revision', revision);
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
        data: {revision: this.get('revision')},
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
        contents: this.get('data'),
        revision: this.get('revision')
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
  
  // For debbuging
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
  
  init: function(serverURL, revision) {
    this._super();
    this.set('state', 'empty');
    this.set('revision', revision);
    this.serverURL = serverURL;
  },
  
  load: function() {
    if (this.get('state') == 'empty') {
      this.set('state', 'loading');
      $.ajax({
        url: this.serverURL,
        dataType: 'text',
        data: {revision: this.get('revision')},
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

  // For debbuging
  set: function(property, value) {
    if (property == 'state') {
      console.log(this.description(), ':', property, '=', value);
    }
    return this._super(property, value);
  }
});


Editor.ImageGalleryModel = Editor.Model.extend({
  _className: 'Editor.ImageGalleryModel',
  serverURL: null,
  data: [],
  state: 'empty',

  init: function(serverURL) {
    this._super();
    this.set('state', 'empty');
    this.serverURL = serverURL;
    // olewać data    
    this.pages = [];
  },

  load: function() {
    if (this.get('state') == 'empty') {
      this.set('state', 'loading');
      $.ajax({
        url: this.serverURL,
        dataType: 'json',
        success: this.loadingSucceeded.bind(this)
      });
    }
  },  

  loadingSucceeded: function(data) {
    if (this.get('state') != 'loading') {
      alert('erroneous state:', this.get('state'));
    }

    $.log('galleries:', data);

    if (data.length === 0) {
        this.set('data', []);
    } else {
        $.log('dupa');
        this.set('data', data[0].pages);
    }  

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
  data: null, // name, text_url, user_revision, latest_shared_rev, parts_url, dc_url, size, merge_url
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
      'xml': new Editor.XMLModel(data.text_url, data.user_revision),
      'html': new Editor.HTMLModel(data.html_url, data.user_revision),
      'gallery': new Editor.ImageGalleryModel(data.gallery_url)
    };
    for (var key in this.contentModels) {
      this.contentModels[key].addObserver(this, 'state', this.contentModelStateChanged.bind(this));
    }
  },
  
  contentModelStateChanged: function(property, value, contentModel) {
    if (value == 'dirty') {
      this.set('state', 'dirty');
      for (var key in this.contentModels) {
        if (this.contentModels[key].guid() != contentModel.guid()) {
          this.contentModels[key].set('state', 'unsynced');
        }
      }
    } else if (value == 'updated') {
      this.set('state', 'synced');
      for (key in this.contentModels) {
        if (this.contentModels[key].guid() == contentModel.guid()) {
          this.contentModels[key].set('state', 'synced');
        } else if (this.contentModels[key].get('state') == 'unsynced') {
          this.contentModels[key].set('state', 'empty');
        }
      }
    }
  },
  
  saveDirtyContentModel: function(message) {
    for (var key in this.contentModels) {
      if (this.contentModels[key].get('state') == 'dirty') {
        this.contentModels[key].update(message);
        break;
      }
    }
  },
  
  update: function() {
    this.set('state', 'loading');
    $.ajax({
      url: this.data.merge_url,
      dataType: 'json',
      type: 'post',
      data: {
        type: 'update',
        target_revision: this.data.user_revision
      },
      complete: this.updateCompleted.bind(this),
      success: function(data) { this.set('updateData', data); }.bind(this)
    });
  },
  
  updateCompleted: function(xhr, textStatus) {
    console.log(xhr.status, textStatus);
    if (xhr.status == 200) { // Sukces
      this.data.user_revision = this.get('updateData').revision;
      for (var key in this.contentModels) {
        this.contentModels[key].set('revision', this.data.user_revision);
        this.contentModels[key].set('state', 'empty');
      }
    } else if (xhr.status == 202) { // Wygenerowano PullRequest (tutaj?)
    } else if (xhr.status == 204) { // Nic nie zmieniono
    } else if (xhr.status == 409) { // Konflikt podczas operacji
    } 
    this.set('state', 'synced');
    this.set('updateData', null);
  },
  
  merge: function(message) {
    this.set('state', 'loading');
    $.ajax({
      url: this.data.merge_url,
      type: 'post',
      dataType: 'json',
      data: {
        type: 'share',
        target_revision: this.data.user_revision,
        message: message
      },
      complete: this.mergeCompleted.bind(this),
      success: function(data) { this.set('mergeData', data); }.bind(this)
    });
  },
  
  mergeCompleted: function(xhr, textStatus) {
    console.log(xhr.status, textStatus);
    if (xhr.status == 200) { // Sukces
      this.data.user_revision = this.get('mergeData').revision;
      for (var key in this.contentModels) {
        this.contentModels[key].set('revision', this.data.user_revision);
        this.contentModels[key].set('state', 'empty');
      }
    } else if (xhr.status == 202) { // Wygenerowano PullRequest
    } else if (xhr.status == 204) { // Nic nie zmieniono
    } else if (xhr.status == 409) { // Konflikt podczas operacji
    }
    this.set('state', 'synced');
    this.set('mergeData', null);
  },
  
  // For debbuging
  set: function(property, value) {
    if (property == 'state') {
      console.log(this.description(), ':', property, '=', value);
    }
    return this._super(property, value);
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

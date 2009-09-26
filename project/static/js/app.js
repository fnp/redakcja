/*global Class*/
var editor;
var panel_hooks;


(function(){
  // Classes
  var initializing = false, fnTest = /xyz/.test(function(){xyz;}) ? /\b_super\b/ : /.*/;
  this.Class = function(){};
  Class.extend = function(prop) {
    var _super = this.prototype;
    initializing = true;
    var prototype = new this();
    initializing = false;
    for (var name in prop) {
      prototype[name] = typeof prop[name] == "function" &&
        typeof _super[name] == "function" && fnTest.test(prop[name]) ?
        (function(name, fn){
          return function() {
            var tmp = this._super;
            this._super = _super[name];
            var ret = fn.apply(this, arguments);       
            this._super = tmp;           
            return ret;
          };
        })(name, prop[name]) :
        prop[name];
    }   
    function Class() {
      if ( !initializing && this.init )
        this.init.apply(this, arguments);
    }
    Class.prototype = prototype;
    Class.constructor = Class;
    Class.extend = arguments.callee;   
    return Class;
  };
  
  // Templates
  var cache = {};

  this.render_template = function render_template(str, data){
    // Figure out if we're getting a template, or if we need to
    // load the template - and be sure to cache the result.
    var fn = !/^[\d\s-_]/.test(str) ?
      cache[str] = cache[str] ||
        render_template(document.getElementById(str).innerHTML) :

      // Generate a reusable function that will serve as a template
      // generator (and which will be cached).
      new Function("obj",
        "var p=[],print=function(){p.push.apply(p,arguments);};" +

        // Introduce the data as local variables using with(){}
        "with(obj){p.push('" +

        // Convert the template into pure JavaScript
        str
          .replace(/[\r\t\n]/g, " ")
          .split("<%").join("\t")
          .replace(/((^|%>)[^\t]*)'/g, "$1\r")
          .replace(/\t=(.*?)%>/g, "',$1,'")
          .split("\t").join("');")
          .split("%>").join("p.push('")
          .split("\r").join("\\'")
      + "');}return p.join('');");

      // Provide some basic currying to the user
    return data ? fn( data ) : fn;
  };
})();

(function() {
  var slice = Array.prototype.slice;
  
  function update(array, args) {
    var arrayLength = array.length, length = args.length;
    while (length--) array[arrayLength + length] = args[length];
    return array;
  };
  
  function merge(array, args) {
    array = slice.call(array, 0);
    return update(array, args);
  };
  
  Function.prototype.bind = function(context) {
    if (arguments.length < 2 && typeof arguments[0] === 'undefined') {
      return this;
    } 
    var __method = this;
    var args = slice.call(arguments, 1);
    return function() {
      var a = merge(args, arguments);
      return __method.apply(context, a);
    }
  }
  
})();
 
var panels = [];

var documentsUrl = '/api/documents/';


var Model = Class.extend({
  observers: {},
  
  init: function() {},
  
  signal: function(event, data) {
    console.log('signal', this, event, data);
    if (this.observers[event]) {
      for (key in this.observers[event]) {
        this.observers[event][key](event, data);
      }
    };
    return this;
  },
  
  addObserver: function(observer, event, callback) {
    if (!this.observers[event]) {
      this.observers[event] = {};
    }
    this.observers[event][observer.id] = callback;
    return this;
  },
  
  removeObserver: function(observer, event) {
    if (!event) {
      for (e in this.observers) {
        this.removeObserver(observer, e);
      }
    } else {
      delete this.observers[event][observer.id];
    }
    return this;
  }
});


var XMLModel = Model.extend({
  parent: null,
  data: '',
  serverURL: null,
  needsReload: false,
  
  init: function(parent, serverURL) {
    this.parent = parent;
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
  
  reload: function() {
    $.ajax({
      url: this.serverURL,
      dataType: 'text',
      success: this.reloadSucceeded.bind(this)
    });
  },
  
  reloadSucceeded: function(data) {
    this.data = data;
    this.signal('reloaded');
  },
  
  dataChanged: function() {
    this.parent.modelChanged('xml');
    this.signal('dataChanged');
  },
  
  needsReload: function() {
    this.needsReload = true;
    this.signal('needsReload');
  }
})



var HTMLModel = Model.extend({
  parent: null,
  data: '',
  serverURL: null,
  needsReload: false,
  
  init: function(parent, serverURL) {
    this.parent = parent;
    this.serverURL = serverURL;
  },
  
  getData: function() {
    if (!this.data) {
      this.reload();
    }
    return this.data;
  },
  
  setData: function(data) {
    console.log('setData');
    if (this.data != data) {
      this.data = data;
      this.dataChanged();
    }
  },
  
  reload: function() {
    $.ajax({
      url: this.serverURL,
      dataType: 'text',
      success: this.reloadSucceeded.bind(this)
    });
  },
  
  reloadSucceeded: function(data) {
    this.data = data;
    this.signal('reloaded');
  },
  
  dataChanged: function() {
    this.parent.modelChanged('html');
  },
  
  needsReload: function() {
    this.needsReload = true;
    this.signal('needsReload');
  }
})


var DocumentModel = Model.extend({
  data: null, // name, text_url, latest_rev, latest_shared_rev, parts_url, dc_url, size
  xml: null,
  html: null,
  contentModels: {},
  
  init: function() {
    this.getData();
  },
  
  getData: function() {
    console.log('DocumentModel#getData');
    $.ajax({
      cache: false,
      url: documentsUrl + fileId,
      dataType: 'json',
      success: this.successfulGetData.bind(this)
    });
  },
  
  successfulGetData: function(data) {
    console.log('DocumentModel#successfulGetData:', data);
    this.data = data;
    this.contentModels = {
      'xml': new XMLModel(this, data.text_url)
    };
  },
  
  modelChanged: function(contentModelName) {
    for (modelName in this.contentModels) {
      if (!(modelName == contentModelName)) {
        this.contentModels[modelName].needsReload();
      }
    }
  }
});

var leftPanelView, rightPanelContainer, doc;

$(function() {
  doc = new DocumentModel();
  var splitView = new SplitView('#splitview', doc);
  leftPanelView = new PanelContainerView('#left-panel-container', doc);
  rightPanelContainer = new PanelContainerView('#right-panel-container', doc);
});

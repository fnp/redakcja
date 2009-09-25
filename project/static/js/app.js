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
      for (observer in this.observers[event]) {
        observer.handle(event, data);
      }
    };
    return this;
  },
  
  addObserver: function(observer, event) {
    if (!this.observers[event]) {
      this.observers[event] = [];
    }
    this.observers[event][observer] = observer;
    return this;
  },
  
  removeObserver: function(observer, event) {
    if (!event) {
      for (e in this.observers) {
        this.removeObserver(observer, e);
      }
    } else {
      delete this.observers[event][observer];
    }
    return this;
  }
});


var XMLModel = Model.extend({
  parent: null,
  data: null,
  serverURL: null,
  
  init: function(parent, serverURL) {
    this.parent = parent;
    this.serverURL = serverURL;
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
})

var DocumentModel = Model.extend({
  data: null, // name, text_url, latest_rev, latest_shared_rev, parts_url, dc_url, size
  xml: null,
  html: null,
  
  init: function() {},
  
  getData: function(callback) {
    console.log('get:', documentsUrl + fileId);
    $.ajax({
      cache: false,
      url: documentsUrl + fileId,
      dataType: 'json',
      success: this.successfulGetData.bind(this, callback)
    });
  },
  
  successfulGetData: function(callback, data) {
    this.data = data;
    this.signal('changed');
    if (callback) {
      (callback.bind(this))(data);
    }
  },
  
  load: function(key) {
    if (!this.data) {
      this.getData(function() { this.load(key); }.bind(this));
    } else {
      console.log('load', key, this.data[key + 'url']);
      $.ajax({
        url: this.data[key + '_url'],
        dataType: 'text',
        success: this.loadSucceeded.bind(this, key)
      });
    }
  },
  
  loadSucceeded: function(key, data) {
    console.log('loadSucceeded', key, data);
    this.set(key, data);
  },
  
  get: function(key) {
    console.log(this[key]);
    if (this[key]) {
      return this[key]
    } else {
      this.load(key);
      return '';
    }
  },
  
  set: function(key, value) {
    this[key] = value;
    this.signal(key + '-changed');
    return this;
  }
});

var leftPanelView, rightPanelContainer, doc;

$(function() {
  doc = new DocumentModel();
  var splitView = new SplitView('#splitview', doc);
  leftPanelView = new PanelContainerView('#left-panel-container', doc);
  rightPanelContainer = new PanelContainerView('#right-panel-container', doc);
});

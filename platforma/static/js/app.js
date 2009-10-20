/*global Class*/
var editor;
var panel_hooks;


// prevent a console.log from blowing things up if we are on a browser that
// does not support it
if (typeof console === 'undefined') {
  window.console = {} ;
  console.log = console.info = console.warn = console.error = function(){};
}


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


var Editor = Editor || {};

// Obiekt implementujący wzorzec KVC/KVO
Editor.Object = Class.extend({
  _className: 'Editor.Object',
  _observers: {},
  _guid: null,
  
  init: function() {
    this._observers = {};
  },
  
  description: function() {
    return this._className + '(guid = ' + this.guid() + ')';
  },
  
  addObserver: function(observer, property, callback) {
    // console.log('Add observer', observer.description(), 'to', this.description(), '[', property, ']');
    if (!this._observers[property]) {
      this._observers[property] = {}
    }
    this._observers[property][observer.guid()] = callback;
    return this;
  },
  
  removeObserver: function(observer, property) {
    if (!property) {
      for (var property in this._observers) {
        this.removeObserver(observer, property)
      }
    } else {
      // console.log('Remove observer', observer.description(), 'from', this.description(), '[', property, ']');
      delete this._observers[property][observer.guid()];
    }
    return this;
  },
  
  notifyObservers: function(property) {
    var currentValue = this[property];
    for (var guid in this._observers[property]) {
      // console.log(this._observers[property][guid]);
      // console.log('Notifying', guid, 'of', this.description(), '[', property, ']');
      this._observers[property][guid](property, currentValue, this);
    }
    return this;
  },
  
  guid: function() {
    if (!this._guid) {
      this._guid = ('editor-' + Editor.Object._lastGuid++);
    }
    return this._guid;
  },
  
  get: function(property) {
    return this[property];
  },
  
  set: function(property, value) {
    if (this[property] != value) {
      this[property] = value;
      this.notifyObservers(property);
    }
    return this;
  },
  
  dispose: function() {
    delete this._observers;
  }
});

// Handle JSON error responses in uniform way
function parseXHRError(response)
{
    var message = "";
    var level = "";
    
    try {
      var json = $.evalJSON(response.responseText);

      if(json.reason == 'xml-parse-error') {
          message = json.message.replace(/(line\s+)(\d+)(\s+)/i,
            "<a class='xml-editor-ref' href='#xml-$2-1'>$1$2$3</a>");

          message = message.replace(/(line\s+)(\d+)(\,\s*column\s+)(\d+)/i,
            "<a class='xml-editor-ref' href='#xml-$2-$4'>$1$2$3$4</a>");

          level = "warning";
      }
      else {
         message = json.message || json.reason || "Nieznany błąd :((";
         level = "error";
      }
    } catch(e) {
        // not a valid JSON response
        message = response.statusText || 'Brak połączenia z serwerem';
        level = "error";
    }
    
    return {error_message: message, error_level: level};
}

function parseXHRResponse(xhr) {
    var response = {}
    
    if(xhr.status >= 200 && xhr.status < 300) 
    {
        response.success = true;
        try {
            response.data = $.evalJSON(xhr.responseText);
        } catch(e) {
            response.data = {};
        }

        return response;
    }

    return parseXHRError(xhr);
}

Editor.Object._lastGuid = 0;

var panels = [];
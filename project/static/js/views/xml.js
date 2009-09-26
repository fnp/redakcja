/*global View CodeMirror render_template panels */
var XMLView = View.extend({
  element: null,
  model: null,
  template: 'xml-view-template',
  editor: null,
  buttonToolbar: null,
  
  init: function(element, model, template) {
    this._super(element, model, template);
    
    this.freeze('Ładowanie edytora...');
  	this.editor = new CodeMirror($('.xmlview', this.element).get(0), {
      parserfile: 'parsexml.js',
      path: "/static/js/lib/codemirror/",
      stylesheet: "/static/css/xmlcolors.css",
      parserConfig: {useHTMLKludges: false},
      textWrapping: false,
      tabMode: 'spaces',
      indentUnit: 0,
      onChange: this.editorDataChanged.bind(this),
      initCallback: this.editorDidLoad.bind(this)
    });
  },
  
  editorDidLoad: function(editor) {
    $(editor.frame).css({width: '100%', height: '100%'});
    
    this.model
      .addObserver(this, 'data', this.modelDataChanged.bind(this))
      .addObserver(this, 'synced', this.modelSyncChanged.bind(this));
    
    if (!this.model.get('synced')) {
      this.freeze('Niezsynchronizowany...');
      this.model.load();
    } else {
      this.editor.setCode(this.model.get('data'));
    }
    this.unfreeze();
  
    // editor.grabKeys(
    //   $.fbind(self, self.hotkeyPressed),
    //   $.fbind(self, self.isHotkey)
    // );
  },
  
  editorDataChanged: function() {
    this.model.set('data', this.editor.getCode());
  },
  
  modelDataChanged: function(property, value) {
    if (this.editor.getCode() != value) {
      this.editor.setCode(value);
    }
  },
  
  modelSyncChanged: function(property, value) {
    if (value) {
      this.unfreeze();
    } else {
      this.freeze('Niezsynchronizowany...');
    }
  },
    
  dispose: function() {
    this.model.removeObserver(this);
    $(this.editor.frame).remove();
    this._super();
  }
});

// Register view
panels['xml'] = XMLView;

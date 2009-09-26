/*global View CodeMirror render_template panels */
var XMLView = View.extend({
  element: null,
  model: null,
  template: 'xml-view-template',
  editor: null,
  
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
      onChange: this.changed.bind(this),
      initCallback: this.editorDidLoad.bind(this)
    });
  },
  
  changed: function() {
    this.model.setData(this.editor.getCode());
  },
  
  editorDidLoad: function(editor) {
    editor.setCode('Ładowanie edytora...');
    $(editor.frame).css({width: '100%', height: '100%'});
    this.editor.setCode(this.model.getData());
    this.unfreeze();
    this.model
      .addObserver(this, 'reloaded', function() {
        this.editor.setCode(this.model.getData()); this.unfreeze(); }.bind(this))
      .addObserver(this, 'needsReload', function() { 
        this.freeze('Niezsynchronizowany'); }.bind(this))
      .addObserver(this, 'dataChanged', this.textDidChange.bind(this));

    // editor.grabKeys(
    //   $.fbind(self, self.hotkeyPressed),
    //   $.fbind(self, self.isHotkey)
    // );
  },
  
  textDidChange: function(event) {
    console.log('textDidChange!');
    if (this.editor.getCode() != this.model.getData()) {
      this.editor.setCode(this.model.getData());
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

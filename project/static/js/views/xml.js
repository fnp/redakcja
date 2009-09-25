/*global View CodeMirror render_template panels */
var XMLView = View.extend({
  element: null,
  model: null,
  template: 'xml-view-template',
  editor: null,
  
  init: function(element, model, template) {
    this.element = $(element);
    this.model = $(model).get(0);
    this.template = template || this.template;
    this.element.html(render_template(this.template, {}));
    
    this.model
      .addObserver(this, 'xml-freeze')
      .addObserver(this, 'xml-unfreeze');
    
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
    this.model.set('text', this.editor.getCode());
  },
  
  editorDidLoad: function(editor) {
    editor.setCode('Ładowanie edytora...');
    $(editor.frame).css({width: '100%', height: '100%'});
    this.editor.setCode(this.model.get('text'));
    this.model.addObserver(this, 'text-changed');
    this.unfreeze();
    // editor.grabKeys(
    //   $.fbind(self, self.hotkeyPressed),
    //   $.fbind(self, self.isHotkey)
    // );
  },
  
  handle: function(event, data) {
    console.log('handle', this, event, data);
    if (event == 'text-changed') {
      this.freeze('Niezsynchronizowany');
      // this.unfreeze();      
    } else if (event == 'xml-freeze') {
      this.freeze('Ładowanie XMLa...');
    } else if (event == 'xml-unfreeze') {
      this.editor.setCode(this.model.get('text'));
      this.unfreeze();
    }
  },
  
  dispose: function() {
    this.model.removeObserver(this);
    $(this.editor.frame).remove();
    this._super();
  }
});

// Register view
panels.push({name: 'xml', klass: XMLView});

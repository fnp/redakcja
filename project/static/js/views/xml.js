/*global View CodeMirror render_template panels */
var XMLView = View.extend({
  element: null,
  model: null,
  template: 'xml-view-template',
  editor: null,
  
  init: function(element, model, template) {
    this.element = $(element);
    this.model = $(model).get(0);
    console.log('XMLView#init model:', model);
    this.template = template || this.template;
    this.element.html(render_template(this.template, {}));
    
    $(this.model)
      .bind('modelxmlfreeze.xmlview',
        function() { this.freeze('Ładowanie danych z serwera...'); }.bind(this))
      .bind('modelxmlunfreeze.xmlview',
        this.unfreeze.bind(this));
    
    this.freeze('Ładowanie edytora...');
  	this.editor = new CodeMirror($('.xmlview', this.element).get(0), {
      parserfile: 'parsexml.js',
      path: "/static/js/lib/codemirror/",
      stylesheet: "/static/css/xmlcolors.css",
      parserConfig: {useHTMLKludges: false},
      textWrapping: false,
      tabMode: 'spaces',
      indentUnit: 0,
      // onChange: function() {
      //        self.fireEvent('contentChanged');
      // },
      initCallback: this.editorDidLoad.bind(this)
    });
  },
  
  editorDidLoad: function(editor) {
    console.log('init', this.model);
    editor.setCode('Ładowanie...');
    $(editor.frame).css({width: '100%', height: '100%'});
    this.editor.setCode(this.model.xml);
    $(this.model).bind('modelxmlchanged.xmlview', this.codeChanged.bind(this));
    this.unfreeze();
    this.model.getXML();
    // editor.grabKeys(
    //   $.fbind(self, self.hotkeyPressed),
    //   $.fbind(self, self.isHotkey)
    // );
  },
  
  codeChanged: function() {
    console.log('setCode:', this.editor, this.model);
    this.editor.setCode(this.model.xml);
    this.unfreeze();
  },
  
  dispose: function() {
    $(this.model)
      .unbind('modelxmlchanged.xmlview')
      .unbind('modelxmlfreeze.xmlview')
      .unbind('modelxmlunfreeze.xmlview');
    $(this.editor.frame).remove();
    this._super();
  }
});

// Register view
panels.push({name: 'xml', klass: XMLView});

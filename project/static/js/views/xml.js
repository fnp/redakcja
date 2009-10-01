/*global View CodeMirror ButtonToolbarView render_template panels */
var XMLView = View.extend({
  _className: 'XMLView',
  element: null,
  model: null,
  template: 'xml-view-template',
  editor: null,
  buttonToolbar: null,
  
  init: function(element, model, parent, template) {
    this._super(element, model, template);
    this.parent = parent;
    this.buttonToolbar = new ButtonToolbarView(
      $('.xmlview-toolbar', this.element), 
      this.model.toolbarButtonsModel, parent);

    $('.xmlview-toolbar', this.element).bind('resize.xmlview', this.resized.bind(this));
    
    this.parent.freeze('Ładowanie edytora...');
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
  
  resized: function(event) {
    var height = this.element.height() - $('.xmlview-toolbar', this.element).outerHeight();
    $('.xmlview', this.element).height(height);
  },
  
  reload: function() {
    this.model.load(true);
  },
  
  editorDidLoad: function(editor) {
    $(editor.frame).css({width: '100%', height: '100%'});
    this.model
      .addObserver(this, 'data', this.modelDataChanged.bind(this))
      .addObserver(this, 'state', this.modelStateChanged.bind(this))
      .load();
    
    this.parent.unfreeze();
      
    this.editor.setCode(this.model.get('data'));
    this.modelStateChanged('state', this.model.get('state'));
        
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
  
  modelStateChanged: function(property, value) {
    if (value == 'synced' || value == 'dirty') {
      this.unfreeze();
    } else if (value == 'unsynced') {
      this.freeze('Niezsynchronizowany...');
    } else if (value == 'loading') {
      this.freeze('Ładowanie...');
    } else if (value == 'saving') {
      this.freeze('Zapisywanie...');
    } else if (value == 'error') {
      this.freeze(this.model.get('error'));
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

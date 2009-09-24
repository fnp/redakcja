/*global Class CodeMirror render_template panels */
var XMLView = Class.extend({
  element: null,
  template: 'xml-view-template',
  editor: null,
  
  init: function(element, template) {
    this.element = $(element);
    this.template = template || this.template;
    this.element.html(render_template(this.template, {}));
    
    var self = this;
  	this.editor = CodeMirror.fromTextArea($('textarea', this.element)[0], {
      parserfile: 'parsexml.js',
      path: "/static/js/lib/codemirror/",
      stylesheet: "/static/css/xmlcolors.css",
      parserConfig: {useHTMLKludges: false},
      // onChange: function() {
      //        self.fireEvent('contentChanged');
      // },
      initCallback: function(editor) {
        console.log('whatever');
        // editor.grabKeys(
        //   $.fbind(self, self.hotkeyPressed),
        //   $.fbind(self, self.isHotkey)
        // );
        editor.setCode('Ala ma kota a kot ma Alę!');
      }
    });
    console.log(this.editor);
    $(this.editor.frame).css({width: '100%', height: '100%'});
  },
  
  dispose: function() {
    
  }
});

// Register view
panels.push({name: 'xml', klass: XMLView});

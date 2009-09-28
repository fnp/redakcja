/*global View render_template panels */
var EditorView = View.extend({
  _className: 'EditorView',
  element: null,
  model: null,
  template: null,
  
  init: function(element, model, template) {
    this._super(element, model, template);
    this.model.load();
    
    $('#action-quick-save', this.element).bind('click.editorview', this.quickSave.bind(this));
    $('#action-commit', this.element).bind('click.editorview', this.commit.bind(this));
    $('#action-update', this.element).bind('click.editorview', this.update.bind(this));
    this.freeze('Ładowanie');
  },
  
  quickSave: function(event) {
    console.log('quickSave');
  },
  
  commit: function(event) {
    console.log('commit');
  },
  
  update: function(event) {
    console.log('update');
  },
  
  dispose: function() {
    $('#action-quick-save', this.element).unbind('click.editorview');
    $('#action-commit', this.element).unbind('click.editorview');
    $('#action-update', this.element).unbind('click.editorview');
    this._super();
  }
});

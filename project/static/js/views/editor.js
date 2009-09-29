/*global View render_template panels */
var EditorView = View.extend({
  _className: 'EditorView',
  element: null,
  model: null,
  template: null,
  
  init: function(element, model, template) {
    this._super(element, model, template);
    this.model.load();
    
    this.quickSaveButton = $('#action-quick-save', this.element).bind('click.editorview', this.quickSave.bind(this));
    this.commitButton = $('#action-commit', this.element).bind('click.editorview', this.commit.bind(this));
    this.updateButton = $('#action-update', this.element).bind('click.editorview', this.update.bind(this));
    this.mergeButton = $('#action-merge', this.element).bind('click.editorview', this.merge.bind(this));
    
    this.model.addObserver(this, 'state', this.modelStateChanged.bind(this));
    this.modelStateChanged('state', this.model.get('state'));
  },
  
  quickSave: function(event) {
    this.model.quickSave();
  },
  
  commit: function(event) {
  },
  
  update: function(event) {
  },
  
  merge: function(event) {
  },
  
  modelStateChanged: function(property, value) {
    // Uaktualnia stan przycisków
    if (value == 'dirty') {
      this.quickSaveButton.attr('disabled', null);
      this.commitButton.attr('disabled', null);
      this.updateButton.attr('disabled', 'disabled');
      this.mergeButton.attr('disabled', 'disabled');
    } else if (value == 'synced') {
      this.quickSaveButton.attr('disabled', 'disabled');
      this.commitButton.attr('disabled', 'disabled');
      this.updateButton.attr('disabled', null);
      this.mergeButton.attr('disabled', null);      
    } else if (value == 'empty') {
      this.quickSaveButton.attr('disabled', 'disabled');
      this.commitButton.attr('disabled', 'disabled');
      this.updateButton.attr('disabled', 'disabled');
      this.mergeButton.attr('disabled', 'disabled');
    }
  },
  
  dispose: function() {
    $('#action-quick-save', this.element).unbind('click.editorview');
    $('#action-commit', this.element).unbind('click.editorview');
    $('#action-update', this.element).unbind('click.editorview');
    $('#action-merge', this.element).unbind('click.editorview');

    this.model.removeObserver(this);
    this._super();
  }
});

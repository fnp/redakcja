/*global View render_template panels */
var HTMLView = View.extend({
  _className: 'HTMLView',
  element: null,
  model: null,
  template: 'html-view-template',
  
  init: function(element, model, parent, template) {
    this._super(element, model, template);
    this.parent = parent;
    
    this.model
      .addObserver(this, 'data', this.modelDataChanged.bind(this))
      .addObserver(this, 'synced', this.modelSyncChanged.bind(this));
      
    $('.htmlview', this.element).html(this.model.get('data'));
    if (!this.model.get('synced')) {
      this.parent.freeze('Niezsynchronizowany...');
      this.model.load();
    }
  },
  
  modelDataChanged: function(property, value) {
    $('.htmlview', this.element).html(value);
  },
  
  modelSyncChanged: function(property, value) {
    if (value) {
      this.parent.unfreeze();
    } else {
      this.parent.freeze('Niezsynchronizowany...');
    }
  },
  
  dispose: function() {
    this.model.removeObserver(this);
    this._super();
  }
});

// Register view
panels['html'] = HTMLView;
/*global View render_template panels */
var HTMLView = View.extend({
  element: null,
  model: null,
  template: 'html-view-template',
  
  init: function(element, model, template) {
    this._super(element, model, template);
    
    this.model
      .addObserver(this, 'data', this.modelDataChanged.bind(this))
      .addObserver(this, 'synced', this.modelSyncChanged.bind(this));
      
    if (!this.model.get('synced')) {
      this.freeze('Niezsynchronizowany...');
      this.model.load();
    } else {
      $('.htmlview', this.element).html(this.model.get('data'));
    }
  },
  
  modelDataChanged: function(property, value) {
    $('.htmlview', this.element).html(value);
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
    this._super();
  }
});

// Register view
panels['html'] = HTMLView;
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
      .addObserver(this, 'state', this.modelStateChanged.bind(this));
      
    $('.htmlview', this.element).html(this.model.get('data'));
    this.modelStateChanged('state', this.model.get('state'));
    this.model.load();
  },
  
  modelDataChanged: function(property, value) {
    $('.htmlview', this.element).html(value);
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
    }
  },
  
  dispose: function() {
    this.model.removeObserver(this);
    this._super();
  }
});

// Register view
panels['html'] = HTMLView;
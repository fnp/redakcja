/*global View render_template panels */
var HTMLView = View.extend({
  element: null,
  model: null,
  template: 'html-view-template',
  
  init: function(element, model, template) {
    this._super(element, model, template);
  },
  
  dispose: function() {
    this._super();
  }
});

// Register view
panels['html'] = HTMLView;
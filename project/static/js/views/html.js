/*global Class render_template panels */
var HTMLView = Class.extend({
  element: null,
  model: null,
  template: 'html-view-template',
  
  init: function(element, model, template) {
    this.element = $(element);
    this.model = model;
    this.template = template || this.template;
    this.element.html(render_template(this.template, {}));
  },
  
  dispose: function() {
    
  }
});

// Register view
panels.push({name: 'html', klass: HTMLView});
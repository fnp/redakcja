/*global Class render_template panels */
var XMLView = Class.extend({
  element: null,
  template: 'xml-view-template',
  
  init: function(element, template) {
    this.element = $(element);
    this.template = template || this.template;
    this.element.html(render_template(this.template, {}));
  },
  
  dispose: function() {
    
  }
});

// Register view
panels.push({name: 'xml', klass: XMLView});

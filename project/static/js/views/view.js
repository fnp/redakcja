/*globals Class render_template*/
var View = Class.extend({
  element: null,
  model: null,
  template: null,
  overlayClass: 'view-overlay',
  overlay: null,

  init: function(element, model, template) {
    this.element = $(element);
    this.model = model;
    this.template = template || this.template;
    
    if (this.template) {
      this.element.html(render_template(this.template, {}));
    }
  },

  frozen: function() {
    return !!this.overlay;
  },
  
  freeze: function(message) {
    this.overlay = this.overlay 
      || $('<div><div>' + message + '</div></div>')
            .addClass(this.overlayClass)
            .css({
              position: 'absolute',
              width: this.element.width(),
              height: this.element.height(),
              top: this.element.position().top,
              left: this.element.position().left
            })
            .appendTo(this.element.parent());
            
    this.overlay.children('div').css({
      position: 'relative',
      top: this.overlay.height() / 2 - 20
    });
  },
  
  unfreeze: function() {
    if (this.frozen()) {
      this.overlay.remove();
      this.overlay = null;      
    }
  },

  dispose: function() {
    this.unfreeze();
    this.element.contents().remove();
  }
});

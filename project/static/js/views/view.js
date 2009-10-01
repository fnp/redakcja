/*globals Editor render_template*/
var View = Editor.Object.extend({
  _className: 'View',
  element: null,
  model: null,
  template: null,
  overlayClass: 'view-overlay',
  overlay: null,
  
  init: function(element, model, template) 
  {
    console.log("init for view");
    this.element = $(element);
    this.model = model;
    this.template = template || this.template;
    
    if (this.template) this.render();
    
    this._resizeHandler = this.resized.bind(this);
    $(window).bind('resize', this._resizeHandler);
    $(this.element).bind('resize', this._resizeHandler);
  },

  render: function() {
      console.log('rendering:', this._className);
      this.element.html(render_template(this.template, this));
  },
  
  frozen: function() {
    return !!this.overlay;
  },
  
  freeze: function(message) {
    if (this.frozen()) {
      this.unfreeze();
    }
    this.overlay = this.overlay 
      || $('<div><div>' + message + '</div></div>')
            .addClass(this.overlayClass)
            .css({
              position: 'absolute',
              width: this.element.width(),
              height: this.element.height(),
              top: this.element.position().top,
              left: this.element.position().left,
              'user-select': 'none',
              '-webkit-user-select': 'none',
              '-khtml-user-select': 'none',
              '-moz-user-select': 'none',
              overflow: 'hidden'
            })
            .attr('unselectable', 'on')
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

  resized: function(event) {
    if (this.frozen()) {
      this.overlay.css({
        position: 'absolute',
        width: this.element.width(),
        height: this.element.height(),
        top: this.element.position().top,
        left: this.element.position().left
      }).children('div').css({
        position: 'relative',
        top: this.overlay.height() / 2 - 20
      });
    }
  },
  
  dispose: function() {
    $(window).unbind('resize', this._resizeHandler);
    $(this.element).unbind('resize', this._resizeHandler);
    this.unfreeze();
    this.element.contents().remove();
  }
});

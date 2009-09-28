/*global View render_template panels */
var EditorView = View.extend({
  _className: 'EditorView',
  element: null,
  model: null,
  template: null,
  
  init: function(element, model, template) {
    this._super(element, model, template);
    this.model.load();
  }
});

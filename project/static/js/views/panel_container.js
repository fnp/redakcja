/*globals Class render_template panels*/

var PanelContainerView = Class.extend({
  element: null,
  model: null,
  template: 'panel-container-view-template',
  contentView: null,
  
  init: function(element, model, template) {
    this.element = $(element);
    this.model = model;
    this.template = template || this.template;
    
    this.element.html(render_template(this.template, {panels: panels}));
    $('select', this.element.get(0)).bind('change.panel-container-view', this.selectChanged.bind(this));
  },
  
  selectChanged: function(event) {
    var view = panels[$('select', this.element.get(0)).val()];
    var klass = view.klass;
    console.log(view, klass);
    if (this.contentView) {
      this.contentView.dispose();
      this.contentView = null;
    }
    this.contentView = new klass($('.content-view', this.element.get(0)), this.model);
    console.log(this.contentView);
  },
  
  dispose: function() {
    $('select', this.element.get(0)).unbind('change.panel-container-view');
  }
});


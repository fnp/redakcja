/*globals View render_template panels*/

var PanelContainerView = View.extend({
  _className: 'PanelContainerView',
  element: null,
  model: null,
  template: 'panel-container-view-template',
  contentView: null,
  
  init: function(element, model, template) {
    this._super(element, model, template);

    $('select', this.element.get(0)).bind('change.panel-container-view', this.selectChanged.bind(this));
  },
  
  selectChanged: function(event) {
    var value = $('select', this.element.get(0)).val();
    var klass = panels[value];
    if (this.contentView) {
      this.contentView.dispose();
      this.contentView = null;
    }
    this.contentView = new klass($('.content-view', 
      this.element.get(0)), this.model.contentModels[value], this);
  },
  
  dispose: function() {
    $('select', this.element.get(0)).unbind('change.panel-container-view');
    this._super();
  }
});


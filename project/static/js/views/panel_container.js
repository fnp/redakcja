/*globals View render_template panels*/

var PanelContainerView = View.extend({
  _className: 'PanelContainerView',
  element: null,
  model: null,
  template: 'panel-container-view-template',
  contentView: null,
  
  init: function(element, model, template) {
    this._super(element, model, template);

    $('.panel-main-toolbar select', this.element.get(0)).bind('change.panel-container-view', this.selectChanged.bind(this));
    $('.panel-main-toolbar .refresh', this.element.get(0))
      .bind('click.panel-container-view', this.refreshButtonClicked.bind(this))
      .attr('disabled', 'disabled');
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
    $('.panel-main-toolbar .refresh', this.element.get(0)).attr('disabled', null);
  },
  
  refreshButtonClicked: function(event) {
    if (this.contentView) {
      console.log('refreshButtonClicked');
      this.contentView.reload();
    }
  },
  
  dispose: function() {
    $('.panel-main-toolbar .refresh', this.element.get(0)).unbind('click.panel-container-view');
    $('.panel-main-toolbar select', this.element.get(0)).unbind('change.panel-container-view');
    this._super();
  }
});


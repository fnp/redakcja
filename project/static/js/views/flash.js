/*globals View render_template*/
var FlashView = View.extend({
  template: 'flash-view-template',

  init: function(element, model, template) {
    this.shownMessage = null;
    this._super(element, model, template);
    this.setModel(model);
  },
  
  setModel: function(model) {
    if (this.model) {
      this.model.removeObserver(this);
    }
    this.model = model;
    this.shownMessage = null;
    if (this.model) {
      this.shownMessage = this.model.get('firstFlashMessage');
      this.model.addObserver(this, 'firstFlashMessage', this.modelFirstFlashMessageChanged.bind(this));
    }
    this.render();
  },
  
  render: function() {
    this.element.html(render_template(this.template, this));
  },
  
  modelFirstFlashMessageChanged: function(property, value) {
    this.element.fadeOut('slow', function() {
      this.shownMessage = value;
      this.render();
      this.element.fadeIn('slow');
    }.bind(this));
  }
});

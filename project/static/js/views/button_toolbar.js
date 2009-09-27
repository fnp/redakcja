/*globals View render_template scriptletCenter*/
var ButtonToolbarView = View.extend({
  _className: 'ButtonToolbarView',
  template: null,
  buttons: null,
  
  init: function(element, model, parent, template) {
    this._super(element, model, null);
    this.parent = parent;
    this.template = 'button-toolbar-view-template';
    
    this.model.addObserver(this, 'buttons', this.modelButtonsChanged.bind(this));
    this.buttons = this.model.get('buttons');
    this.model.load();
    this.render();
  },
  
  modelButtonsChanged: function(property, value) {
    this.set('buttons', value);
    this.render();
  },
  
  render: function() {
    $('.buttontoolbarview-tab', this.element).unbind('click.buttontoolbarview');
    $('.buttontoolbarview-button', this.element).unbind('click.buttontoolbarview');
    
    this.element.html(render_template(this.template, this));
    
    $('.buttontoolbarview-tab', this.element).bind('click.buttontoolbarview', function() {
      var groupIndex = $(this).attr('ui:groupindex');
      $('.buttontoolbarview-group', this.element).each(function() {
        if ($(this).attr('ui:groupindex') == groupIndex) {
          $(this).show();
        } else {
          $(this).hide();
        }
      });
    });
    
    var self = this;
    $('.buttontoolbarview-button', this.element).bind('click.buttontoolbarview', function() {
      var groupIndex = parseInt($(this).attr('ui:groupindex'), 10);
      var buttonIndex = parseInt($(this).attr('ui:buttonindex'), 10);
      var button = self.get('buttons')[groupIndex].buttons[buttonIndex];
      var scriptletId = button.scriptlet_id;
      var params = eval('(' + button.params + ')'); // To nie powinno być potrzebne
      console.log('Executing', scriptletId, 'with params', params);
      scriptletCenter[scriptletId](self.parent, params);
    });
  },
  
  dispose: function() {
    $('.buttontoolbarview-tab', this.element).unbind('click.buttontoolbarview');
    $('.buttontoolbarview-button', this.element).unbind('click.buttontoolbarview');
    this._super();
  }
});


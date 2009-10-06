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
        var self = this;
    
        this.element.html(render_template(this.template, this));
    
        $('.buttontoolbarview-tab', this.element).bind('click.buttontoolbarview', function() {
            var groupIndex = $(this).attr('ui:groupindex');
            $('.buttontoolbarview-group', self.element).each(function() {
                if ($(this).attr('ui:groupindex') == groupIndex) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });
            $(self.element).trigger('resize');
        });
    
        $('.buttontoolbarview-button', this.element).
        bind('click.buttontoolbarview', this.buttonPressed.bind(this) );
            
        $(this.element).trigger('resize');
    },

    buttonPressed: function(event)
    {
        var target = event.target;
        
        var groupIndex = parseInt($(target).attr('ui:groupindex'), 10);
        var buttonIndex = parseInt($(target).attr('ui:buttonindex'), 10);
        var button = this.get('buttons')[groupIndex].buttons[buttonIndex];
        var scriptletId = button.scriptlet_id;
        var params = eval('(' + button.params + ')'); // To nie powinno być potrzebne

        console.log('Executing', scriptletId, 'with params', params);
        try {
            scriptletCenter.scriptlets[scriptletId](this.parent, params);
        } catch(e) {
            console.log("Scriptlet", scriptletId, "failed.");
        }

    },
  
    dispose: function() {
        $('.buttontoolbarview-tab', this.element).unbind('click.buttontoolbarview');
        $('.buttontoolbarview-button', this.element).unbind('click.buttontoolbarview');
        this._super();
    }
});


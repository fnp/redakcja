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

    render: function(template) {
        console.log('rendering:', this._className);
        this.element.html(render_template(template || this.template, this));
    },
  
    frozen: function() {
        return !!this.overlay;
    },
  
    freeze: function(message) {
        if (this.frozen()) {
            this.unfreeze();
        }
        this.overlay = this.overlay || $('<div><div>' + message + '</div></div>');

        this.overlay.addClass(this.overlayClass)
        .css({
            
        }).attr('unselectable', 'on')

        this.overlay.appendTo(this.element);

        var ovc = this.overlay.children('div');        
        var padV = (this.overlay.height() - ovc.outerHeight())/2;
        var padH = (this.overlay.width() - ovc.outerWidth())/2;
                   
        this.overlay.children('div').css({
            top: padV, left: padH
        });    
    },
  
    unfreeze: function() {
        if (this.frozen()) {
            this.overlay.remove();
            this.overlay = null;
        }
    },

    resized: function(event) {
        if(this.overlay) {
            var ovc = this.overlay.children('div');
            var padV = (this.overlay.height() - ovc.outerHeight())/2;
            var padH = (this.overlay.width() - ovc.outerWidth())/2;

            this.overlay.children('div').css({
                top: padV,
                left: padH
            });
        }
    },
  
    dispose: function() {
        console.log('disposing:', this._className);
        $(window).unbind('resize', this._resizeHandler);
        $(this.element).unbind('resize', this._resizeHandler);
        this.unfreeze();
        this.element.html('');
    }
});
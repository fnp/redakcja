/*global View render_template panels */
var HTMLView = View.extend({
    _className: 'HTMLView',
    element: null,
    model: null,
    template: 'html-view-template',
  
    init: function(element, model, parent, template) {
        this._super(element, model, template);
        this.parent = parent;
    
        this.model
        .addObserver(this, 'data', this.modelDataChanged.bind(this))        
        .addObserver(this, 'state', this.modelStateChanged.bind(this));
      
        $('.htmlview', this.element).html(this.model.get('data'));

        this.$menuTemplate = $(render_template('html-view-frag-menu-template', this));
        
        this.modelStateChanged('state', this.model.get('state'));
        this.model.load();

        this.currentOpen = null;
        this.themeBoxes = [];
    },

    modelDataChanged: function(property, value) {
        $('.htmlview', this.element).html(value);
        this.updatePrintLink();
        var self = this;

        /* upgrade editable elements */
        $("*[x-editable]").each(function() {
            $(this).append( self.$menuTemplate.clone() );
        });

        var n = 5001;

        var doc_base = $('.htmlview .utwor', this.element);

        /* mark themes */
        $(".theme-ref").each(function() {
            var id = $(this).attr('x-theme-class');

            var end = $("span.theme-end[x-theme-class = " + id+"]");
            var begin = $("span.theme-begin[x-theme-class = " + id+"]");

            var h = $(this).outerHeight();

            h = Math.max(h, end.offset().top - begin.offset().top);
            $(this).css('height', h);
        }); 
    },

    updatePrintLink: function() {
        var base = this.$printLink.attr('ui:baseref');
        this.$printLink.attr('href', base + "?user="+this.model.document.get('user')+"&revision=" + this.model.get('revision'));
    },
  
    modelStateChanged: function(property, value) 
    {
        var self = $(this);

        if (value == 'synced' || value == 'dirty') {
            this.unfreeze();
        } else if (value == 'unsynced') {
            if(this.currentOpen) this.closeWithoutSave(this.currentOpen);
            this.freeze('Niezsynchronizowany...');
        } else if (value == 'loading') {
            this.freeze('Ładowanie...');
        } else if (value == 'saving') {
            this.freeze('Zapisywanie...');
        } else if (value == 'error') {
            this.freeze(this.model.get('error'));
            $('.xml-editor-ref', this.overlay).click(
            function(event) {
                console.log("Sending scroll rq.", this);
                try {
                    var href = $(this).attr('href').split('-');
                    var line = parseInt(href[1]);
                    var column = parseInt(href[2]);
                    
                    $(document).trigger('xml-scroll-request', {line:line, column:column});
                } catch(e) {
                    console.log(e);
                }
                
                return false;
            });
        }
    },

    render: function() {
        this.element.unbind('click');

        if(this.$printLink) this.$printLink.unbind();
        this._super();
        this.$printLink = $('.html-print-link', this.element);
        this.updatePrintLink();

        this.element.bind('click', this.itemClicked.bind(this));
        // this.element.bind('mouseover', this.itemHover.bind(this));
    },
  
    reload: function() {
        this.model.load(true);
    },
  
    dispose: function() {
        this.model.removeObserver(this);
        this._super();
    },

    itemClicked: function(event) 
    {
        var self = this;
        
        console.log('click:', event, event.ctrlKey, event.target);        
        var $e = $(event.target);

        if($e.hasClass('edit-button'))
            this.openForEdit( this.editableFor($e) );

        if($e.hasClass('accept-button'))
            this.closeWithSave( this.editableFor($e) );

        if($e.hasClass('reject-button'))
            this.closeWithoutSave( this.editableFor($e) );
    },

    closeWithSave: function($e) {
        var $edit = $e.data('edit-overlay');
        var newText = $('textarea', $edit).val();

        this.model.putXMLPart($e, newText, function($e, html) {
            this.renderPart($e, html);
            $edit.remove();
            $e.removeAttr('x-open');            
        }.bind(this) );
        this.currentOpen = null;
    },

    closeWithoutSave: function($e) {
        var $edit = $e.data('edit-overlay');
        $edit.remove();
        $e.removeAttr('x-open');
        this.currentOpen = null;
    },

    renderPart: function($e, html) {
            $e.html(html);
            $e.append( this.$menuTemplate.clone() );
    },

    editableFor: function($button) 
    {
        var $e = $button;
        var n = 0;
        
        while( ($e[0] != this.element[0]) && !($e.attr('x-editable')) && n < 50)
        {
            // console.log($e, $e.parent(), this.element);
            $e = $e.parent();
            n += 1;
        }

        if(!$e.attr('x-editable'))
            throw Exception("Click outside of editable")

        return $e;
    },

    openForEdit: function($origin)
    {       
        if(this.currentOpen && this.currentOpen != $origin) {
            this.closeWithSave(this.currentOpen);
            
        }
    
        // start edition on this node       
        var $overlay = $('<div class="html-editarea"><textarea></textarea></div>');

        var x = $origin[0].offsetLeft;
        var y = $origin[0].offsetTop;
        var w = $origin.outerWidth();
        var h = $origin.innerHeight();
        
        $overlay.css({position: 'absolute', height: h, left: x, top: y, width: '95%'});
        
            $origin.offsetParent().append($overlay);
            $origin.data('edit-overlay', $overlay);
                     
            this.model.getXMLPart($origin, function(path, data) {
                $('textarea', $overlay).val(data);
            });

            this.currentOpen = $origin;
            $origin.attr('x-open', 'open');
        
        
        return false;
    }
  
});

// Register view
panels['html'] = HTMLView;
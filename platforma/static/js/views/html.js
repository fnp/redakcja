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
        this.modelStateChanged('state', this.model.get('state'));
        this.model.load();       
    },

    modelDataChanged: function(property, value) {
        $('.htmlview', this.element).html(value);
        this.updatePrintLink();

        $("*[x-editable]").each(function() {
            var e = $('<span class="context-menu"><span class="edit-button">Edytuj</span><span>Przypisy</span></span>');
            e.appendTo(this);
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

    itemHover: function(event)
    {
        var $e = $(event.target);
        if( $e.attr('x-editable') == 'editable' ) {
            console.log('over:', $e[0]);
            $e.css({'background-color': 'grey'});
        }

    },

    itemClicked: function(event) 
    {
        var self = this;
        
        console.log('click:', event, event.ctrlKey, event.target);
        var editableContent = null;
        var $e = $(event.target);

        if($e.hasClass('edit-button'))
            this.openForEdit($e);
    },

    openForEdit: function($e)
    {
        var n = 0;        

        while( ($e[0] != this.element[0]) && !($e.attr('x-editable'))
            && n < 50)
        {
            // console.log($e, $e.parent(), this.element);
            $e = $e.parent();
            n += 1;
        }
      
        if(!$e.attr('x-editable'))
            return true;

        var $origin = $e;
        console.log("editable: ", $e);
    
        // start edition on this node       
        var $overlay = $(
        '<div class="html-editarea">\n\
            <p class="html-editarea-toolbar">\n\
                <button class="html-editarea-save-button" type="button">Zapisz</button>\n\
                <button class="html-editarea-cancel-button" type="button">Anuluj</button>\n\
            </p>\n\
            <textarea></textarea>\n\
        </div>');

        var x = $e[0].offsetLeft;
        var y = $e[0].offsetTop;
        var w = $e.outerWidth();
        var h = $e.innerHeight();
        $overlay.css({position: 'absolute', height: 1.2*h, left: x, top: y, width: w});
        // $e.offsetParent().append($overlay);

        
                        
        /* $('.html-editarea-cancel-button', $overlay).click(function() {
            $overlay.remove();
        });

        $('.html-editarea-save-button', $overlay).click(function() {
            $overlay.remove();

            // put the part back to the model
            self.model.putXMLPart($e, $('textarea', $overlay).val());
        }); */

        this.model.getXMLPart($e, function(path, data) {
            $('textarea', $overlay).val(data);
        });

        $origin.attr('x-open', 'open');
        return false;
    }
  
});

// Register view
panels['html'] = HTMLView;
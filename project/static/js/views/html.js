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

        var base = this.$printLink.attr('ui:baseref');
        this.$printLink.attr('href', base + "?revision=" + this.model.get('revision'));
    },
  
    modelStateChanged: function(property, value) {
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
        }
    },

    render: function() {
        this.element.unbind('click');

        if(this.$printLink) this.$printLink.unbind();
        this._super();

        this.$printLink = $('.html-print-link', this.element);

        if(this.$printLink) {
            var base = this.$printLink.attr('ui:baseref');
            this.$printLink.attr('href', base + "?revision=" + this.model.get('revision'));
        }

        this.element.bind('click', this.itemClicked.bind(this));
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
        var editableContent = null;
        var $e = $(event.target);

        var n = 0;

        while( ($e[0] != this.element[0]) && !($e.attr('wl2o:editable'))
            && n < 50)
        {
            // console.log($e, $e.parent(), this.element);
            $e = $e.parent();
            n += 1;
        }
      
        if(!$e.attr('wl2o:editable'))
            return true;
    
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
        $overlay.css({position: 'absolute', height: h, left: "5%", top: y, width: "90%"});
        $e.offsetParent().append($overlay);

        // load the original XML content
        console.log($e, $e.offsetParent(), $overlay);
                        
        $('.html-editarea-cancel-button', $overlay).click(function() {
            $overlay.remove();
        });

        $('.html-editarea-save-button', $overlay).click(function() {
            $overlay.remove();

            // put the part back to the model
            self.model.putXMLPart($e, $('textarea', $overlay).val());
        });

        $('textarea', $overlay).focus(function() {
            $overlay.css('z-index', 3000);
        }).blur(function() {
            $overlay.css('z-index', 2000);
        });

        this.model.getXMLPart($e, function(path, data) {
            $('textarea', $overlay).val(data);
        });
        
        return false;
    }
  
});

// Register view
panels['html'] = HTMLView;
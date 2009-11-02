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

        this.$menuTemplate = $(render_template('html-view-frag-menu-template', this));
        this.modelStateChanged('state', this.model.get('state'));
        this.modelDataChanged('data', this.model.get('data'));
                
        this.model.load();

        this.currentOpen = null;
        this.currentFocused = null;
        this.themeBoxes = [];
    },

    modelDataChanged: function(property, value) {
        $('.htmlview', this.element).html(value);
        this.updatePrintLink();
        var self = this;

        /* upgrade editable elements */
        $("*[x-editable]", this.$docbase).each(function() {
            $(this).append( self.$menuTemplate.clone() );
        });
        
        /* mark themes */
        /* $(".theme-ref", this.$docbase).each(function() {
            var id = $(this).attr('x-theme-class');

            var end = $("span.theme-end[x-theme-class = " + id+"]");
            var begin = $("span.theme-begin[x-theme-class = " + id+"]");

            var h = $(this).outerHeight();

            h = Math.max(h, end.offset().top - begin.offset().top);
            $(this).css('height', h);
        }); */
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
        if(this.$docbase)
            this.$docbase.unbind('click');

        if(this.$printLink) 
            this.$printLink.unbind();

        if(this.$addThemeButton)
            this.$addThemeButton.unbind();

        this._super();

        this.$printLink = $('.htmlview-toolbar .html-print-link', this.element);
        this.$docbase = $('.htmlview', this.element);
        this.$addThemeButton = $('.htmlview-toolbar .html-add-motive', this.element);

        this.updatePrintLink();
        this.$docbase.bind('click', this.itemClicked.bind(this));
        this.$addThemeButton.click( this.addTheme.bind(this) );
    },

    renderPart: function($e, html) {
        // exceptions aren't good, but I don't have a better idea right now
        if($e.attr('x-annotation-box')) {
            // replace the whole annotation
            var $p = $e.parent();
            $p.html(html);
            var $box = $('*[x-annotation-box]', $p);
            $box.append( this.$menuTemplate.clone() );

            if(this.currentFocused && $p[0] == this.currentFocused[0])
            {
                this.currentFocused = $p;
                $box.css({'display': 'block'});
            }

            return;
        }

        $e.html(html);
        $e.append( this.$menuTemplate.clone() );
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

        if($e.hasClass('annotation'))
        {
            if(this.currentOpen) return false;
            
            var $p = $e.parent();
            if(this.currentFocused) 
            {
                console.log(this.currentFocused, $p);
                if($p[0] == this.currentFocused[0]) {
                    console.log('unfocus of current');
                    this.unfocusAnnotation();
                    return false;
                }

                console.log('switch unfocus');
                this.unfocusAnnotation();                
            }

            this.focusAnnotation($p);
            return false;
        }

        /*
         * Clicking outside of focused area doesn't unfocus by default
         *  - this greatly simplifies the whole click check
         */

        if( $e.hasClass('theme-ref') )
        {
            console.log($e);
            this.selectTheme($e.attr('x-theme-class'));
        }

        /* other buttons */
        if($e.hasClass('edit-button'))
            this.openForEdit( this.editableFor($e) );

        if($e.hasClass('accept-button'))
            this.closeWithSave( this.editableFor($e) );

        if($e.hasClass('reject-button'))
            this.closeWithoutSave( this.editableFor($e) );        
    },

    unfocusAnnotation: function()
    {
        if(!this.currentFocused)
        {
            console.log('Redundant unfocus');
            return false;
        }

        if(this.currentOpen 
          && this.currentOpen.is("*[x-annotation-box]")
          && this.currentOpen.parent()[0] == this.currentFocused[0])
        {
            console.log("Can't unfocus open box");
            return false;
        }

        var $box = $("*[x-annotation-box]", this.currentFocused);
        $box.css({'display': 'none'});
        // this.currentFocused.removeAttr('x-focused');
        // this.currentFocused.hide();
        this.currentFocused = null;
    },

    focusAnnotation: function($e) {
        this.currentFocused = $e;
        var $box = $("*[x-annotation-box]", $e);
        $box.css({'display': 'block'});
        
        // $e.attr('x-focused', 'focused');        
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

        console.log("Trigger", $button, " yields editable: ", $e);
        return $e;
    },

    openForEdit: function($origin)
    {       
        if(this.currentOpen && this.currentOpen != $origin) {
            this.closeWithSave(this.currentOpen);    
        }
        
        var x = $origin[0].offsetLeft;
        var y = $origin[0].offsetTop;
        var w = $origin.outerWidth();
        var h = $origin.innerHeight();

        console.log("Editable:", $origin, " offsetParent:", $origin[0].offsetParent);
        console.log("Dimensions: ", x, y, w , h);

        // start edition on this node
        var $overlay = $('<div class="html-editarea"><textarea></textarea></div>');
        
        $overlay.css({position: 'absolute', height: h, left: x, top: y, width: '95%'});        
        $($origin[0].offsetParent).append($overlay);
        $origin.data('edit-overlay', $overlay);

        this.model.getXMLPart($origin, function(path, data) {
            $('textarea', $overlay).val(data);
        });      

        if($origin.is("*[x-annotation-box]"))
        {
            var $b =  $origin.parent();
            if(this.currentFocused) {
                // if some other is focused
                if($b[0] != this.currentFocused[0]) {
                    this.unfocusAnnotation();
                    this.focusAnnotation($b);
                }
                // already focues
            }
            else { // nothing was focused
                this.focusAnnotation($b);
            }
        }
        else { // this item is not focusable
            if(this.currentFocused) this.unfocusAnnotation();
        }

        this.currentOpen = $origin;
        $origin.attr('x-open', 'open');
                
        return false;
    },

    addTheme: function() 
    {
        var selection = document.getSelection();
        var n = selection.rangeCount;
        
        if(n == 0)
            window.alert("Nie zaznaczono żadnego obszaru");

        // for now allow only 1 range
        if(n > 1)
            window.alert("Zaznacz jeden obszar");

        // from this point, we will assume that the ranges are disjoint
        for(var i=0; i < n; i++) {
            var range = selection.getRangeAt(i);
            console.log(i, range.startContainer, range.endContainer);
            var date = Date.now();
            var random = Math.floor(4000000000*Math.random());
            var id = (''+date) + '-' + (''+random);

            var ipoint = document.createRange();            
            
            // Firefox alters the later node when inserting, so
            // insert from end
            ipoint.setStart(range.endContainer, range.endOffset);
            elem = $('<span class="theme-end" x-theme-class="'+id+'" id="e'+id+'"></span>')[0];
            ipoint.insertNode(elem);

            // insert theme-ref
            ipoint.setStart(range.startContainer, range.startOffset);
            var elem = $('<span class="theme-ref" x-theme-class="'+id+'" id="m'+id+'">Nowy motyw</span>')[0];
            ipoint.insertNode(elem);
            ipoint.setStartBefore(elem);

            // insert theme-begin
            elem = $('<span class="theme-begin" x-theme-class="'+id+'" id="b'+id+'"></span>')[0];
            ipoint.insertNode(elem);            
        }

        selection.removeAllRanges();
    },

    selectTheme: function(themeId)
    {
        var selection = document.getSelection();
        
        // remove current selection
        selection.removeAllRanges();

        var range = document.createRange();
        var s = $('#m'+themeId)[0];
        var e = $('#e'+themeId)[0];
        console.log('Selecting range:', themeId, range, s, e);

        if(s && e) {
            range.setStartAfter(s);
            range.setEndBefore(e);
            selection.addRange(range);
        }
    }
});

// Register view
panels['html'] = HTMLView;
/*global View render_template panels */
var HTMLView = View.extend({
    _className: 'HTMLView',
    element: null,
    model: null,
    template: 'html-view-template',
  
    init: function(element, model, parent, template) {
        var submodel = model.contentModels['html'];
        this._super(element, submodel, template);
        this.parent = parent;                
    
        this.model
        .addObserver(this, 'data', this.modelDataChanged.bind(this))
        .addObserver(this, 'state', this.modelStateChanged.bind(this));
        
        this.modelStateChanged('state', this.model.get('state'));
        this.modelDataChanged('data', this.model.get('data'));
                
        this.model.load();

        this.currentOpen = null;
        this.currentFocused = null;
        this.themeBoxes = [];
    },

    modelDataChanged: function(property, value)
    {
        if(!value) return;
       
        // the xml model changed
        var container = $('.htmlview', this.element);
        container.empty();
        container.append(value);
        
        this.updatePrintLink();
        
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
                    
                        $(document).trigger('xml-scroll-request', {
                            line:line,
                            column:column
                        });
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
        // this.$debugButton = $('.htmlview-toolbar .html-serialize', this.element);

        this.updatePrintLink();
        this.$docbase.bind('click', this.itemClicked.bind(this));
        this.$addThemeButton.click( this.addTheme.bind(this) );
        // this.$debugButton.click( this.serialized.bind(this) );
    },

    /* serialized: function() {
        this.model.set('state', 'dirty');
        console.log( this.model.serializer.serializeToString(this.model.get('data')) );        
    }, */

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
                $box.css({
                    'display': 'block'
                });
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

        if( $e.hasClass('motyw') )
        {
            console.log($e);
            this.selectTheme($e.attr('theme-class'));
            return false;
        }

        /* other buttons */
        try {
            if($e.hasClass('delete-button'))
                this.deleteElement( this.editableFor($e) );

            if($e.hasClass('edit-button'))
                this.openForEdit( this.editableFor($e) );

            if($e.hasClass('accept-button'))
                this.closeWithSave( this.editableFor($e) );

            if($e.hasClass('reject-button'))
                this.closeWithoutSave( this.editableFor($e) );
        } catch(e) {
            messageCenter.addMessage('error', "wlsave", 'Błąd:' + e.toString());
        }
        
        return false;
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
        $box.css({
            'display': 'none'
        });
        // this.currentFocused.removeAttr('x-focused');
        // this.currentFocused.hide();
        this.currentFocused = null;
    },

    focusAnnotation: function($e) {
        this.currentFocused = $e;
        var $box = $("*[x-annotation-box]", $e);
        $box.css({
            'display': 'block'
        });
        
    // $e.attr('x-focused', 'focused');
    },

    closeWithSave: function($e) {
        var $edit = $e.data('edit-overlay');
        var newText = $('textarea', $edit).val();
        var errors = null;
        
        errors = this.model.updateInnerWithWLML($e, newText);
        
        if(errors)
            messageCenter.addMessage('error', 'render', errors);
        else {
            $edit.remove();
            this.currentOpen = null;
        }
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
        
        var $box = null

        // annotations overlay their sub box - not their own box //
        if($origin.is(".annotation-inline-box"))
            $box = $("*[x-annotation-box]", $origin);
        else
            $box = $origin;
        
        var x = $box[0].offsetLeft;
        var y = $box[0].offsetTop;
        var w = $box.outerWidth();
        var h = $box.innerHeight();

        console.log("Edit origin:", $origin, " box:", $box);
        console.log("offsetParent:", $box[0].offsetParent);
        console.log("Dimensions: ", x, y, w , h);

        // start edition on this node
        var $overlay = $('<div class="html-editarea"><textarea></textarea></div>');

        h = Math.max(h, 2*parseInt($box.css('line-height')));
        
        $overlay.css({
            position: 'absolute',
            height: h,
            left: x,
            top: y,
            width: '95%'
        });
        
        try {
            $('textarea', $overlay).val( this.model.innerAsWLML($origin[0]) );

            if($origin.is(".annotation-inline-box"))
            {                
                if(this.currentFocused) {
                    // if some other is focused
                    if($origin[0] != this.currentFocused[0]) {
                        this.unfocusAnnotation();
                        this.focusAnnotation($origin);
                    }
                // already focues
                }
                else { // nothing was focused
                    this.focusAnnotation($origin);
                }
            }
            else { // this item is not focusable
                if(this.currentFocused) this.unfocusAnnotation();
            }

            $($box[0].offsetParent).append($overlay);
            $origin.data('edit-overlay', $overlay);
        
            this.currentOpen = $origin;
            $origin.attr('x-open', 'open');
        }
        catch(e) {
            console.log("Can't open", e);
        }
                
        return false;
    },
    
    deleteElement: function($editable)
    {
        var relatedThemes = $("*[x-node='begin'], *[x-node='end']", $editable);

        var themeMarks = relatedThemes.map(function() {
            return $(".motyw[theme-class='"+$(this).attr('theme-class')+"']");
        });

        if($editable.is("*.motyw"))
        {
            console.log($editable);
            var selector = "[theme-class='"+$editable.attr('theme-class')+"']";
            relatedThemes = relatedThemes.add("*[x-node='begin']"+selector+", *[x-node='end']"+selector);
        }
        
        console.log(relatedThemes, themeMarks);

        var del = confirm("Usunięcie elementu jest nieodwracalne.\n"
        +" Czy na pewno chcesz usunąć ten element, wraz z zawartymi motywami ?\n");
        
        if(del) {
            relatedThemes.remove();
            themeMarks.remove();
            $editable.remove();
        }
    },

    // Theme related stuff
    verifyThemeInsertPoint: function(node) {

        if(node.nodeType == 3) { // Text Node
            node = node.parentNode;
        }

        if(node.nodeType != 1) return false;

        console.log('Selection point:', node);
        
        node = $(node);
        var xtype = node.attr('x-node');

        if(!xtype || (xtype.search(':') >= 0) ||
                xtype == 'motyw' || xtype == 'begin' || xtype == 'end')
            return false;

        // this is hopefully redundant
        //if(! node.is('*.utwor *') )
        //    return false;
        
        // don't allow themes inside annotations
        if( node.is('*[x-annotation-box] *') )
            return false;

        return true;
    },

    addTheme: function() 
    {
        var selection = window.getSelection();
        var n = selection.rangeCount;

        console.log("Range count:", n);
        
        if(n == 0) {
            window.alert("Nie zaznaczono żadnego obszaru");
            return false;
        }

        // for now allow only 1 range
        if(n > 1) {
            window.alert("Zaznacz jeden obszar");
            return false;
        }

        // from this point, we will assume that the ranges are disjoint
        for(var i=0; i < n; i++) 
        {
            var range = selection.getRangeAt(i);
            console.log(i, range.startContainer, range.endContainer);

            // verify if the start/end points make even sense -
            // they must be inside a x-node (otherwise they will be discarded)
            // and the x-node must be a main text
            if(! this.verifyThemeInsertPoint(range.startContainer) ) {
                window.alert("Motyw nie może się zaczynać w tym miejscu.");
                return false;
            }

            if(! this.verifyThemeInsertPoint(range.endContainer) ) {
                window.alert("Motyw nie może się kończyć w tym miejscu.");
                return false;
            }

            
            var date = (new Date()).getTime();
            var random = Math.floor(4000000000*Math.random());
            var id = (''+date) + '-' + (''+random);

            var spoint = document.createRange();
            var epoint = document.createRange();

            spoint.setStart(range.startContainer, range.startOffset);
            epoint.setStart(range.endContainer, range.endOffset);

            var mtag, btag, etag, errors;

            // insert theme-ref            
            mtag = $('<span></span>');
            spoint.insertNode(mtag[0]);
            errors = this.model.updateWithWLML(mtag, '<motyw id="m'+id+'">Nowy Motyw</motyw>');
            if(errors) {
                messageCenter.addMessage('error', null, 'Błąd przy dodawaniu motywu :' + errors);
                return false;
            }

            // insert theme-begin
            btag = $('<span></span>');
            spoint.insertNode(btag[0]);
            errors = this.model.updateWithWLML(btag, '<begin id="b'+id+'" />');
            if(errors) {
                mtag.remove();
                messageCenter.addMessage('error', null, 'Błąd przy dodawaniu motywu :' + errors);
                return false;
            }

            
            etag = $('<span></span>');
            epoint.insertNode(etag[0]);
            result = this.model.updateWithWLML(etag, '<end id="e'+id+'" />');
            if(errors) {
                btag.remove();
                mtag.remove();
                messageCenter.addMessage('error', null, 'Błąd przy dodawaniu motywu :' + errors);
                return false;
            }
        }

        selection.removeAllRanges();
    },

    selectTheme: function(themeId)
    {
        var selection = window.getSelection();
        
        // remove current selection
        selection.removeAllRanges();

        var range = document.createRange();
        var s = $(".motyw[theme-class='"+themeId+"']")[0];
        var e = $(".end[theme-class='"+themeId+"']")[0];
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
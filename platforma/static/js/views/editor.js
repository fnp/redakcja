/*global View render_template panels */
var EditorView = View.extend({
    _className: 'EditorView',
    element: null,
    model: null,
    template: null,
  
    init: function(element, model, template) {
        this._super(element, model, template);
    
        this.quickSaveButton = $('#action-quick-save', this.element).bind('click.editorview', this.quickSave.bind(this));
        this.commitButton = $('#action-commit', this.element).bind('click.editorview', this.commit.bind(this));
        this.updateButton = $('#action-update', this.element).bind('click.editorview', this.update.bind(this));
        this.mergeButton = $('#action-merge', this.element).bind('click.editorview', this.merge.bind(this));
    
        this.model.addObserver(this, 'state', this.modelStateChanged.bind(this));
        this.modelStateChanged('state', this.model.get('state'));        

        this.splitView = new SplitView('#splitview', doc);
        
        // Inicjalizacja okien jQuery Modal
        this.commitDialog = new CommitDialog( $('#commit-dialog') );                  
        
    
        // $('#split-dialog').jqm({
        //      modal: true,
        //      onShow: $.fbind(self, self.loadSplitDialog)
        //  }).
        //  jqmAddClose('button.dialog-close-button');
    
        this.model.load();
    },
  
    quickSave: function(event) {
        this.model.saveDirtyContentModel();
    },
  
    commit: function(event) 
    {
        this.commitDialog.show( this.doCommit.bind(this) )
        
    },
  
    doCommit: function(message) {
        this.model.saveDirtyContentModel(message);
    },
  
    update: function(event) {
        this.model.update();
    },
  
    merge: function(event) {
        this.commitDialog.show( this.doMerge.bind(this) )        
    },
  
    doMerge: function(message) {
        this.model.merge(message);
    },
  
    /*loadRelatedIssues: function(hash) {
        var self = this;
        var c = $('#commit-dialog-related-issues');
        
        $('#commit-dialog').data('context', hash.t);

        $("div.loading-box", c).show();
        $("div.fatal-error-box", c).hide();
        $("div.container-box", c).hide();
    
        $.getJSON(c.attr('ui:ajax-src') + '?callback=?',
            function(data, status)
            {
                var fmt = '';
                $(data).each( function() {
                    fmt += '<label><input type="checkbox" checked="checked"';
                    fmt += ' value="' + this.id + '" />' + this.subject +'</label>\n';
                });
                $("div.container-box", c).html(fmt);
                $("div.loading-box", c).hide();
                $("div.container-box", c).show();
            });
    
        hash.w.show();
    }, */
  
    modelStateChanged: function(property, value) {
        // Uaktualnia stan przycisków
        if (value == 'dirty') {
            this.quickSaveButton.attr('disabled', null);
            this.commitButton.attr('disabled', null);
            this.updateButton.attr('disabled', 'disabled');
            this.mergeButton.attr('disabled', 'disabled');
        } else if (value == 'synced' || value == 'unsynced') {
            this.quickSaveButton.attr('disabled', 'disabled');
            this.commitButton.attr('disabled', 'disabled');
            this.updateButton.attr('disabled', null);
            this.mergeButton.attr('disabled', null);
            this.unfreeze();
        } else if (value == 'empty') {
            this.quickSaveButton.attr('disabled', 'disabled');
            this.commitButton.attr('disabled', 'disabled');
            this.updateButton.attr('disabled', 'disabled');
            this.mergeButton.attr('disabled', 'disabled');
        } else if (value == 'error') {
            this.freeze(this.model.get('error'));
            this.quickSaveButton.attr('disabled', 'disabled');
            this.commitButton.attr('disabled', 'disabled');
            this.updateButton.attr('disabled', 'disabled');
            this.mergeButton.attr('disabled', 'disabled');
            
        }
    },
  
    dispose: function() {
        $('#action-quick-save', this.element).unbind('click.editorview');
        $('#action-commit', this.element).unbind('click.editorview');
        $('#action-update', this.element).unbind('click.editorview');
        $('#action-merge', this.element).unbind('click.editorview');

        this.model.removeObserver(this);
        this._super();
    }    
});


var AbstractDialog = Class.extend({
    _className: 'AbstractDialog',

    init: function($element, modal, overlay)
    {
        this.$window = $element;
        this.$window.jqm({
            modal: modal || true,
            overlay: overlay || 80,
            // toTop: true,
            onShow: this.onShow.bind(this),
            onHide: this.onHide.bind(this)
        });

        this.reset();        

        $('.cancel-button', this.$window).click(this.cancel.bind(this));
        $('.save-button', this.$window).click(this.accept.bind(this));
    },

    onShow: function(hash)
    {
        hash.w.show();
    },

    onHide: function(hash)
    {
        hash.w.hide();
        hash.o.remove();
    },

    reset: function() {
        this.acceptCallback = null;
        this.cancelCallback = null;
        this.errors = [];
        
        $('.error-messages-box', this.$window).html('').hide();

        this.userData = {};
    },

    show: function(acall, ccall) {
        this.acceptCallback = acall;
        this.cancelCallback = ccall;

        // do the show
        this.$window.jqmShow();
    },

    cancel: function() {
        this.$window.jqmHide();
        if(this.cancelCallback) this.cancelCallback(this);
        this.reset();
    },

    accept: function()
    {
        this.errors = [];
        
        if(!this.validate()) {
            this.displayErrors();
            return;
        }

        this.$window.jqmHide();

        if(this.acceptCallback) 
            this.acceptCallback(this);

        this.reset();        
    },

    validate: function() {
        return true;
    },

    displayErrors: function() {
        var errorDiv = $('.error-messages-box', this.$window);
        if(errorDiv.length > 0) {
            var html = '';
            $.each(this.errors, function() {
                html += '<li>' + this + '</li>';
            });
            errorDiv.html('<ul>' + html + '</ul>');
            errorDiv.show();
            console.log('Validation errors:', html);
        }
        else
            throw this.errors;
    }

});

var CommitDialog = AbstractDialog.extend({
    _className: 'CommitDialog',

    validate: function()
    {
        var message = $('textarea.commit-message', this.$window).val();

        if( message.match(/^\s*$/) ) {
            this.errors.push("Message can't be empty.");
            return false;
        }

        // append refs
        $('.related-issues-fields input:checked', this.$window).each(function() {
            message += ' refs #' + $(this).val();
        });

        this.userData.message = message;
        return this._super();
     }
 });

 
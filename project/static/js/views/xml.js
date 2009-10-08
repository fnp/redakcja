/*global View CodeMirror ButtonToolbarView render_template panels */
var XMLView = View.extend({
    _className: 'XMLView',
    element: null,
    model: null,
    template: 'xml-view-template',
    editor: null,
    buttonToolbar: null,
  
    init: function(element, model, parent, template) {
        this._super(element, model, template);
        this.parent = parent;
        this.buttonToolbar = new ButtonToolbarView(
            $('.xmlview-toolbar', this.element),
            this.model.toolbarButtonsModel, parent);

        this.hotkeys = [];
        var self = this;

        $('.xmlview-toolbar', this.element).bind('resize.xmlview', this.resized.bind(this));
   
    
        this.parent.freeze('Ładowanie edytora...');
        this.editor = new CodeMirror($('.xmlview', this.element).get(0), {
            parserfile: 'parsexml.js',
            path: "/static/js/lib/codemirror/",
            stylesheet: "/static/css/xmlcolors.css",
            parserConfig: {
                useHTMLKludges: false
            },
            textWrapping: false,
            tabMode: 'spaces',
            indentUnit: 0,
            onChange: this.editorDataChanged.bind(this),
            initCallback: this.editorDidLoad.bind(this)
        });
    },
  
    resized: function(event) {
        var height = this.element.height() - $('.xmlview-toolbar', this.element).outerHeight();
        $('.xmlview', this.element).height(height);
    },
  
    reload: function() {
        this.model.load(true);
    },
  
    editorDidLoad: function(editor) {
        $(editor.frame).css({
            width: '100%',
            height: '100%'
        });
        this.model
        .addObserver(this, 'data', this.modelDataChanged.bind(this))
        .addObserver(this, 'state', this.modelStateChanged.bind(this))
        .load();
    
        this.parent.unfreeze();
      
        this.editor.setCode(this.model.get('data'));
        this.modelStateChanged('state', this.model.get('state'));
        
        editor.grabKeys(
            this.hotkeyPressed.bind(this),
            this.isHotkey.bind(this)
            );
    },
  
    editorDataChanged: function() {
        this.model.set('data', this.editor.getCode());
    },
  
    modelDataChanged: function(property, value) {
        if (this.editor.getCode() != value) {
            this.editor.setCode(value);
        }
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
    
    dispose: function() {
        this.model.removeObserver(this);
        $(this.editor.frame).remove();
        this._super();
    },    

    getHotkey: function(event) {
        var code = event.keyCode;
        if(!((code >= 97 && code <= 122)
           || (code >= 65 && code <= 90)) ) return null;

        var ch = String.fromCharCode(code & 0xff).toLowerCase();
        /* # console.log(ch.charCodeAt(0), '#', buttons); */

        var buttons = $('.buttontoolbarview-button[title='+ch+']', this.element);
        var mod = 0;
            
        if(event.altKey) mod |= 0x01;
        if(event.ctrlKey) mod |= 0x02;
        if(event.shiftKey) mod |= 0x04;

        if(buttons.length) {
            var match = null;

            buttons.each(function() {
                if( parseInt($(this).attr('ui:hotkey_mod')) == mod ) {
                    match = this;
                    return;
                }
            })

            return match;
        }
        else {
            return null;
        }
    },

    isHotkey: function() {
        /* console.log(arguments); */
        if(this.getHotkey.apply(this, arguments))
            return true;
        else
            return false;
    },

    hotkeyPressed: function() {
        var button = this.getHotkey.apply(this, arguments);
        this.buttonToolbar.buttonPressed({
            target: button
        });
    }

});

function Hotkey(code) {
    this.code = code;
    this.has_alt = ((code & 0x01 << 8) !== 0);
    this.has_ctrl = ((code & 0x01 << 9) !== 0);
    this.has_shift = ((code & 0x01 << 10) !== 0);
    this.character = String.fromCharCode(code & 0xff);
}

Hotkey.prototype.toString = function() {
    var mods = [];
    if(this.has_alt) mods.push('Alt');
    if(this.has_ctrl) mods.push('Ctrl');
    if(this.has_shift) mods.push('Shift');
    mods.push('"'+this.character+'"');
    return mods.join('+');
};

// Register view
panels['xml'] = XMLView;

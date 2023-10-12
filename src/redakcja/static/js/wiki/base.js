(function($)
{
    var noop = function() { };

    $.wiki = {
        perspectives: {},
        cls: {},
        state: {
            "version": 1,
            "perspectives": {
                "ScanGalleryPerspective": {
                    "show": true,
                    "page": undefined
                },
                "CodeMirrorPerspective": {}
                /*
                  "VisualPerspective": {},
                  "HistoryPerspective": {},
                  "SummaryPerspective": {}
                */
            }
        }
    };

    $.wiki.loadConfig = function() {
        if(!window.localStorage)
            return;

        try {
            var value = window.localStorage.getItem(CurrentDocument.id) || "{}";
            var config = JSON.parse(value);

            if (config.version == $.wiki.state.version) {
                $.wiki.state.perspectives = $.extend($.wiki.state.perspectives, config.perspectives);
            }
        } catch(e) {
            console.log("Failed to load config, using default.");
        }

        console.log("Loaded:", $.wiki.state, $.wiki.state.version);
    };

    $(window).bind('unload', function() {
        if(window.localStorage)
            window.localStorage.setItem(CurrentDocument.id, JSON.stringify($.wiki.state));
    })


    $.wiki.activePerspective = function() {
        return this.perspectives[$("#tabs li a.active").parent().attr('id')];
    };

    $.wiki.exitContext = function() {
        var ap = this.activePerspective();
        if(ap) ap.onExit();
        return ap;
    };

    $.wiki.enterContext = function(ap) {
        if(ap) ap.onEnter();
    };

    $.wiki.isDirty = function() {
        var ap = this.activePerspective();
        return (!!CurrentDocument && CurrentDocument.has_local_changes) || ap.dirty();
    };

    $.wiki.newTab = function(doc, title, klass, base_id) {
        var id = (''+klass)+'_' + base_id;
        var $tab = $('<li class="nav-item" id="'+id+'" data-ui-related="'+base_id+'" data-ui-jsclass="'+klass+'" ><a href="#" class="nav-link">'
                     + title + ' <span class="badge badge-danger tabclose">x</span></a></li>');
        var $view = $('<div class="editor '+klass+'" id="'+base_id+'"> </div>');

        this.perspectives[id] = new $.wiki[klass]({
            doc: doc,
            id: id,
            base_id: base_id,
        });

        $('#tabs').append($tab);
        $view.hide().appendTo('#editor');
        return {
            tab: $tab[0],
            view: $view[0],
        };
    };

    $.wiki.initTab = function(options) {
        var klass = $(options.tab).attr('data-ui-jsclass');

        let perspective = new $.wiki[klass]({
            doc: options.doc,
            id: $(options.tab).attr('id'),
        });
        $.wiki.perspectives[perspective.perspective_id] = perspective;
        return perspective;
    };

    $.wiki.perspectiveForTab = function(tab) { // element or id
        return this.perspectives[ $(tab).attr('id')];
    }

    $.wiki.exitTab = function(tab){
        var self = this;
        var $tab = $(tab);
        if (!('.active', $tab).length) return;
        $('.active', $tab).removeClass('active');
        self.perspectives[$tab.attr('id')].onExit();
        $('#' + $tab.attr('data-ui-related')).hide();
    }

    $.wiki.switchToTab = function(tab){
        var self = this;
        var $tab = $(tab);

        // Create dynamic tabs (for diffs).
        if ($tab.length != 1) {
            let parts = tab.split('_');
            if (parts.length > 1) {
                // TODO: register perspectives for it.
                if (parts[0] == '#DiffPerspective') {
                    $tab = $($.wiki.DiffPerspective.openId(parts[1]));
                }
            }
        }

        if($tab.length != 1)
            $tab = $(DEFAULT_PERSPECTIVE);

        var $old_a = $tab.closest('.tabs').find('.active');

        $old_a.each(function(){
            var tab = $(this).parent()
            $(this).removeClass('active');
            self.perspectives[tab.attr('id')].onExit();
            $('#' + tab.attr('data-ui-related')).hide();
        });

        /* show new */
        $('a', tab).addClass('active');
        $('#' + $tab.attr('data-ui-related')).show();

        console.log($tab);
        console.log($.wiki.perspectives);

        $.wiki.perspectives[$tab.attr('id')].onEnter();
    };

    /*
     * Basic perspective.
     */
    $.wiki.Perspective = class Perspective {
        constructor(options) {
            this.doc = options.doc;
            this.perspective_id = options.id || ''
        };

        config() {
            return $.wiki.state.perspectives[this.perspective_id];
        }

        toString() {
            return this.perspective_id;
        }

        dirty() {
            return true;
        }

        onEnter() {
            // called when perspective in initialized
            if (!this.noupdate_hash_onenter) {
                document.location.hash = '#' + this.perspective_id;
            }
        }

        onExit () {
            // called when user switches to another perspective
            if (!this.noupdate_hash_onenter) {
                document.location.hash = '';
            }
        }

        destroy() {
            // pass
        }
    }

    /*
     * Stub rendering (used in generating history)
     */
    $.wiki.renderStub = function(params)
    {
        params = $.extend({ 'filters': {} }, params);
        var $elem = params.stub.clone();
        $elem.removeClass('row-stub');
        params.container.append($elem);

        var populate = function($this) {
            var field = $this.attr('data-stub-value');

            var value = params.data[field];

            if(params.filters[field])
                value = params.filters[field](value);

            if(value === null || value === undefined) return;

            if(!$this.attr('data-stub-target')) {
                $this.text(value);
            }
            else {
                $this.attr($this.attr('data-stub-target'), value);
                $this.removeAttr('data-stub-target');
                $this.removeAttr('data-stub-value');
            }
        }
        if ($elem.attr('data-stub-value')) populate($elem);
        $('*[data-stub-value]', $elem).each(function() {populate($(this))});

        $elem.show();
        return $elem;
    };

    /*
     * Dialogs
     */
    class GenericDialog {
        constructor(element) {
            if(!element) return;

            var self = this;

            self.$elem = $(element);

            if(!self.$elem.attr('data-ui-initialized')) {
                console.log("Initializing dialog", this);
                self.initialize();
                self.$elem.attr('data-ui-initialized', true);
            }

            self.show();
        }

        /*
         * Steps to follow when the dialog in first loaded on page.
         */
        initialize(){
            var self = this;

            /* bind buttons */
            $('button[data-ui-action]', self.$elem).click(function(event) {
                event.preventDefault();

                var action = $(this).attr('data-ui-action');
                console.log("Button pressed, action: ", action);

                try {
                    self[action + "Action"].call(self);
                } catch(e) {
                    console.log("Action failed:", e);
                    // always hide on cancel
                    if(action == 'cancel')
                        self.hide();
                }
            });
        }

        /*
         * Prepare dialog for user. Clear any unnessary data.
         */
        show() {
            $.blockUI({
                message: this.$elem,
                css: {
                    'top': '25%',
                    'left': '25%',
                    'width': '50%',
                    'max-height': '75%',
                    'overflow-y': 'scroll'
                }
            });
        }

        hide() {
            $.unblockUI();
        }

        cancelAction() {
            this.hide();
        }

        doneAction() {
            this.hide();
        }

        clearForm() {
            $("*[data-ui-error-for]", this.$elem).text('');
        }

        reportErrors(errors) {
            var global = $("*[data-ui-error-for='__all__']", this.$elem);
            var unassigned = [];

            $("*[data-ui-error-for]", this.$elem).text('');
            for (var field_name in errors)
            {
                var span = $("*[data-ui-error-for='"+field_name+"']", this.$elem);

                if(!span.length) {
                    unassigned.push(errors[field_name]);
                    continue;
                }

                span.text(errors[field_name].join(' '));
            }

            if(unassigned.length > 0)
                global.text(
                    global.text() + 'Wystąpił błąd: ' + unassigned.join(', '));
        }
    }

    $.wiki.cls.GenericDialog = GenericDialog;

    $.wiki.showDialog = function(selector, options) {
        var elem = $(selector);

        if(elem.length != 1) {
            console.log("Failed to show dialog:", selector, elem);
            return false;
        }

        try {
            var klass = elem.attr('data-ui-jsclass');
            return new $.wiki.cls[klass](elem, options);
        } catch(e) {
            console.log("Failed to show dialog", selector, klass, e);
            return false;
        }
    };

    window.addEventListener("message", (event) => {
        event.source.close()

        $.ajax("/editor/editor-user-area/", {
            success: function(d) {
                $("#user-area")[0].innerHTML = d;
                $('#history-view-editor').toggleClass('can-approve', $('#user-area #pubmark_dialog').length > 0);
            }
        });
    }, false);

    $("#login").click(function (e) {
        e.preventDefault();
        let h = 600;
        let w = 500;
        let x = window.screenX + (window.innerWidth - w) / 2;
        let y = window.screenY + (window.innerHeight - h) / 2;
        window.open(
            "/accounts/login/?next=/editor/back",
            "login-window",
            "width=" + w + " height=" + h + " top=" + y + " left=" + x
        );
    });

})(jQuery);

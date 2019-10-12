(function($){

    /*
     * Perspective
     */
    function SearchPerspective(options){
        var old_callback = options.callback || function() { };

        this.vsplitbar = 'ZNAJDŹ I ZAMIEŃ';

        options.callback = function(){
            var self = this;

            this.editor = null;
            this.$element = $("#side-search");
            this.$searchInput = $('#search-input', this.$element);
            this.$replaceInput = $('#replace-input', this.$element);
            this.$searchButton = $('#search-button', this.$element);
            this.$replaceButton = $('#replace-button', this.$element);

            this.$replaceButton.attr("disabled","disabled");
            this.options = Array();

            // handlers
            this.$searchInput.change(function(event){
                self.searchCursor = null;
            });
            this.$replaceInput.change(function(event){
                self.searchCursor = null;
            });

            $("#side-search input:checkbox").each(function() {
                self.options[this.id] = this.checked;
            }).change(function(){
                self.options[this.id] = this.checked;
                self.searchCursor = null;
            });

            this.$searchButton.click(function(){
                if (!self.search())
                    alert('Brak wyników.');
            });

            this.$replaceButton.click(function(){
                self.replace();
            });

            old_callback.call(this);
        };

        $.wiki.SidebarPerspective.call(this, options);
    };

    SearchPerspective.prototype = new $.wiki.SidebarPerspective();

    SearchPerspective.prototype.search = function(){
        var self = this;
        var query = self.$searchInput.val();

        if (!self.editor)
            self.editor = $.wiki.perspectiveForTab('#CodeMirrorPerspective').codemirror

        if (!self.searchCursor) {
            var options = {};
            options.caseFold = !self.options['search-case-sensitive'];
            var start = 0;
            if (self.options['search-from-cursor']) {
                start = self.editor.getCursor();
            }
            self.searchCursor = self.editor.getSearchCursor(
                self.$searchInput.val(), 
                start,
                options
            );
        }
        if (self.searchCursor.findNext()) {
            self.editor.setSelection(self.searchCursor.from(), self.searchCursor.to());
            self.editor.scrollIntoView({from: self.searchCursor.from(), to: self.searchCursor.to()}, 20);
            self.$replaceButton.removeAttr("disabled");
            return true;
        }
        else {
            self.searchCursor = null;
            this.$replaceButton.attr("disabled","disabled");
            return false;
        }
    };

    SearchPerspective.prototype.replace = function(){
        var self = this;
        var query = self.$replaceInput.val();

        if (!self.searchCursor) {
            self.search();
        }
        else {}

        self.editor.setSelection(self.searchCursor.from(), self.searchCursor.to());
        self.editor.scrollIntoView({from: self.searchCursor.from(), to: self.searchCursor.to()}, 20);

        self.searchCursor.replace(query);
        if(self.search() && self.options['replace-all']) {
            self.replace();
        }
    };

    SearchPerspective.prototype.onEnter = function(success, failure){
        var self = this;

        $.wiki.SidebarPerspective.prototype.onEnter.call(this);
        self.$searchCursor = null;

        if ($.wiki.activePerspective() != 'CodeMirrorPerspective')
            $.wiki.switchToTab('#CodeMirrorPerspective');
    };

    SearchPerspective.prototype.onExit = function(success, failure) {

    };

    $.wiki.SearchPerspective = SearchPerspective;

})(jQuery);

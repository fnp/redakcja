(function($){

    /*
     * Perspective
     */
    function SearchPerspective(options){
        var old_callback = options.callback || function() { };

        this.noupdate_hash_onenter = true;
        this.vsplitbar = 'ZNAJDŹ&nbsp;I&nbsp;ZAMIEŃ';

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

        $.wiki.Perspective.call(this, options);
    };

    SearchPerspective.prototype = new $.wiki.Perspective();

    SearchPerspective.prototype.search = function(){
        var self = this;
        var query = self.$searchInput.val();

        if (!self.editor)
            self.editor = $.wiki.perspectiveForTab('#CodeMirrorPerspective').codemirror

        if (!self.searchCursor) {
            self.searchCursor = self.editor.getSearchCursor(
                self.$searchInput.val(), 
                self.options['search-from-cursor'], 
                !self.options['search-case-sensitive']
            );
        }
        if (self.searchCursor.findNext()) {
            self.searchCursor.select();
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
        self.searchCursor.select();
        self.searchCursor.replace(query);
        if(self.search() && self.options['replace-all']) {
            self.replace();
        }
    };

    SearchPerspective.prototype.onEnter = function(success, failure){
        var self = this;

        $.wiki.Perspective.prototype.onEnter.call(this);
        self.$searchCursor = null;

        $('.vsplitbar').not('.active').trigger('click');
        $(".vsplitbar-title").html("&darr;&nbsp;ZNAJDŹ&nbsp;I&nbsp;ZAMIEŃ&nbsp;&darr;");        
        
        if ($.wiki.activePerspective() != 'CodeMirrorPerspective')
            $.wiki.switchToTab('#CodeMirrorPerspective');
    };

    SearchPerspective.prototype.onExit = function(success, failure) {

    };

    $.wiki.SearchPerspective = SearchPerspective;

})(jQuery);
